"""
Soccer agent-based model engine - 3-sided football (Australian version).
 
Geometry and rules follow "3-sided football, Principles of play":
 
  * Hexagonal pitch, 23 m sides, goals on THREE ALTERNATING sides.
      blue  = top side            (side 1: c1 -> c2)
      green = lower-left side     (side 3: c3 -> c4)
      red   = lower-right side    (side 5: c5 -> c0)
  * A goal is 3 m wide, 2 m deep, centred on the midpoint of its goal line and
    sitting OUTSIDE the pitch.
  * Each team owns its goal line and the side opposite it ("sidelines").
  * Each team holds a "third": centre -> midpoints of the two sides next to its
    goal side.
  * A goal = ball crosses the goal line between the posts. The team whose goal
    it went into CONCEDES one point (least conceded wins).
  * Goal line crossed by non-owner  -> goal kick to the owner.
  * Goal line crossed by owner      -> corner to the owner of the adjacent sideline.
  * Sideline crossed by non-owner   -> throw-in to the sideline's owner.
  * Sideline crossed by the owner   -> throw-in to the team whose goal is closest.
 
Your alliance / betrayal mechanics are kept: the two teams that are NOT leading
(fewest concessions) gang up on the leader, and a player closer to their ally's
goal than the leader's goal may "betray" the alliance if their betrayal
probability beats their team's threshold.
 
Hexagon sides are numbered i = c[i] -> c[i+1]:
    0 upper-right, 1 top, 2 upper-left, 3 lower-left, 4 bottom, 5 lower-right
"""
 
import math
import random
 
CANVAS_SIZE = 400
SCALE = 7.5  # field metres -> canvas pixels
 
TEAM_COLORS = ("red", "blue", "green")
 
# ---------------------------------------------------------------------------
# Tunable behaviour constants (play with these to change how the match feels)
# ---------------------------------------------------------------------------
SHOOT_RANGE = 12.0     # m from the goal mouth within which a player may shoot
SHOOT_PROB = 0.35      # per-tick chance of shooting once in range
SAVE_PROB = 0.30       # chance an on-target shot is saved
PASS_PROB = 0.35       # chance of passing (instead of dribbling) when not shooting
LONG_PASS_PROB = 0.15  # chance a pass goes to a random teammate, not the nearest
DRIBBLE_FACTOR = 0.07  # metres moved per tick = speed * factor
TACKLE_RANGE = 2.0
TACKLE_PROB = 0.08
INTERCEPT_RANGE = 1.5
INTERCEPT_PROB = 0.25
CLEARANCE_RANGE = 8.0  # a player this close to their OWN goal may hoof the ball away
CLEARANCE_PROB = 0.30
DEFLECT_PROB = 0.35    # a wide shot that last touched a defender -> corner instead of goal kick
RESTART_INSET = 0.4    # restarts are placed this far inside the line
KEY_EVENT_TYPES = {"goal", "save", "throwin", "goal_kick", "corner_kick", "betrayal"}
 
 
# ---------------------------------------------------------------------------
# Small geometry helpers
# ---------------------------------------------------------------------------
def _segment_hit(p, q, a, b):
    """Where does the path p->q cross segment a->b?  Returns (t, point) or None."""
    rx, ry = q[0] - p[0], q[1] - p[1]
    sx, sy = b[0] - a[0], b[1] - a[1]
    denom = rx * sy - ry * sx
    if abs(denom) < 1e-12:
        return None
    apx, apy = a[0] - p[0], a[1] - p[1]
    t = (apx * sy - apy * sx) / denom
    u = (apx * ry - apy * rx) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return t, (p[0] + t * rx, p[1] + t * ry)
    return None
 
 
def _point_to_segment(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    seg2 = dx * dx + dy * dy
    t = 0 if seg2 == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / seg2))
    return math.dist(p, (ax + t * dx, ay + t * dy))
 
 
# ---------------------------------------------------------------------------
# Field
# ---------------------------------------------------------------------------
class Field:
    GOAL_SIDE = {"blue": 1, "green": 3, "red": 5}
 
    def __init__(self):
        self.diameter = 40
        self.sidelength = 23
        self.numsides = 6
        self.goalheight = 2       # depth of the goal box, out from the line
        self.goalwidth = 3
        self.goalcircle_diameter = 5
        self.centre = (0.0, 0.0)
        self.apothem = self.sidelength * math.cos(math.pi / 6)  # centre -> side
 
        self.side_team = {s: t for t, s in self.GOAL_SIDE.items()}   # goal side -> team
        # a sideline belongs to the team whose goal is on the OPPOSITE side
        self.sideline_owner = {s: self.side_team[(s + 3) % 6] for s in (0, 2, 4)}
 
    # ----- basic shapes -----
    def hexagon(self):
        step = 2 * math.pi / self.numsides
        return [(self.sidelength * math.cos(step * i), self.sidelength * math.sin(step * i))
                for i in range(self.numsides)]
 
    def side(self, i):
        c = self.hexagon()
        return c[i % 6], c[(i + 1) % 6]
 
    def side_mid(self, i):
        a, b = self.side(i)
        return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
 
    def outward(self, i):
        """Unit vector from the pitch centre out through side i."""
        ang = math.radians(60 * i + 30)
        return (math.cos(ang), math.sin(ang))
 
    def tangent(self, i):
        """Unit vector along side i (c[i] -> c[i+1])."""
        a, b = self.side(i)
        length = math.dist(a, b)
        return ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
 
    def goal_mid(self, team):
        return self.side_mid(self.GOAL_SIDE[team])
 
    def inside(self, p, margin=0.0):
        return all(p[0] * self.outward(i)[0] + p[1] * self.outward(i)[1] <= self.apothem - margin
                   for i in range(6))
 
    def clamp_inside(self, p, margin=0.3):
        x, y = p
        for _ in range(3):
            for i in range(6):
                n = self.outward(i)
                over = x * n[0] + y * n[1] - (self.apothem - margin)
                if over > 0:
                    x -= over * n[0]
                    y -= over * n[1]
        return (x, y)
 
    # ----- goals -----
    def drawgoalstart(self):
        """Goal rectangles: mouth on the goal line, extending OUTWARD."""
        rects = {}
        for team, s in self.GOAL_SIDE.items():
            m, t, n = self.side_mid(s), self.tangent(s), self.outward(s)
            hw, d = self.goalwidth / 2, self.goalheight
            a = (m[0] - t[0] * hw, m[1] - t[1] * hw)
            b = (m[0] + t[0] * hw, m[1] + t[1] * hw)
            rects[f"{team}_team_goal_coords"] = [
                a, b, (b[0] + n[0] * d, b[1] + n[1] * d), (a[0] + n[0] * d, a[1] + n[1] * d)]
        return rects
 
    # ----- thirds, owned sides -----
    def dividepitchpossession(self):
        """Each team's third: centre, midpoint of the side before its goal side,
        the goal side's two corners, midpoint of the side after it."""
        c = self.hexagon()
        areas = {}
        for team, g in self.GOAL_SIDE.items():
            areas[f"{team}_team_area"] = [
                self.centre, self.side_mid(g - 1), c[g % 6], c[(g + 1) % 6], self.side_mid(g + 1)]
        return areas
 
    def dividepitchboundaries(self):
        """The two sides each team owns: its goal line and the side opposite."""
        return {f"{team}_team_boundary": [self.side(g), self.side(g + 3)]
                for team, g in self.GOAL_SIDE.items()}
 
    def third_lines(self):
        """Lines from the centre to the midpoints of the three sidelines (drop-penalty lines)."""
        lines = {}
        for s in (0, 2, 4):
            t1 = self.side_team[(s - 1) % 6]
            t2 = self.side_team[(s + 1) % 6]
            lines[f"{t1}_{t2}_third_line"] = [self.centre, self.side_mid(s)]
        return lines
 
    def third_owner(self, p):
        ang = math.degrees(math.atan2(p[1], p[0])) % 360
        best = None
        for team, s in self.GOAL_SIDE.items():
            diff = abs((ang - (60 * s + 30) + 180) % 360 - 180)
            if best is None or diff < best[0]:
                best = (diff, team)
        return best[1]
 
 
# ---------------------------------------------------------------------------
# Players
# ---------------------------------------------------------------------------
class Player:
    def __init__(self, teamcolor):
        self.teamcolor = teamcolor
        self.speed = round(random.uniform(8, 15), 2)
        self.numpass = 0
        self.unsuccessfulshots = 0
        self.goals = 0
        self.owngoals = 0
        self.posessiontime = 0.0
        self.xcor = None
        self.ycor = None
        self.betrayal_prob = round(random.uniform(0, 1), 2)
 
    def make_team(self, color, num_players):
        if not (3 <= num_players <= 5):
            raise ValueError("Each team must have 3 to 5 players.")
        team = {}
        for i in range(1, num_players + 1):
            p = Player(color)
            team[f"Player_{i}"] = {
                "teamcolor": p.teamcolor,
                "speed": p.speed,
                "passes": p.numpass,
                "unsuccessfulshots": p.unsuccessfulshots,
                "goals": p.goals,
                "owngoals": p.owngoals,
                "posession": p.posessiontime,
                "betrayal_probability": p.betrayal_prob,
                "xcor": p.xcor,
                "ycor": p.ycor,
            }
        return team
 
 
# ---------------------------------------------------------------------------
# The match
# ---------------------------------------------------------------------------
class Team:
    def __init__(self, num_blue=3, num_red=3, num_green=3, betrayal_thresholds=None):
        self.field = Field()
        self.dividepitchforteams = self.field.dividepitchpossession()
        self.dividepitchboundaries = self.field.dividepitchboundaries()
        self.drawgoalstart = self.field.drawgoalstart()
 
        self.blueplayers = Player("blue").make_team("blue", num_blue)
        self.redplayers = Player("red").make_team("red", num_red)
        self.greenplayers = Player("green").make_team("green", num_green)
        self.teams_dict = {
            "blue_team": self.blueplayers,
            "red_team": self.redplayers,
            "green_team": self.greenplayers,
        }
 
        self.ball_coordinates = [0.0, 0.0]
        self.concessions = {"red": 0, "blue": 0, "green": 0}
 
        betrayal_thresholds = betrayal_thresholds or {}
        self.team_betrayal_threshold = {
            c: betrayal_thresholds.get(c, random.uniform(0, 1)) for c in TEAM_COLORS}
        self.team_pressure_probability = random.uniform(0.1, 1)
 
        self.current_tick = 0
        self.last_event = {"type": "kickoff", "detail": None}
        self.key_events = []
        self.last_touch = None          # (team_name, player_name) of the last kicker
        self.pending_kickoff = None     # colour that kicks off after a goal
        self._skip_tackle = False
 
    # ------------------------------------------------------------------
    # Setup / kickoff
    # ------------------------------------------------------------------
    def spawn_player_before_kickoff(self, kicking_team=None):
        """Put every team in its own third; the kicking team's player starts on the centre spot."""
        for color in TEAM_COLORS:
            area = self.dividepitchforteams[f"{color}_team_area"]
            cx = sum(p[0] for p in area) / len(area)
            cy = sum(p[1] for p in area) / len(area)
            for attrs in self.teams_dict[f"{color}_team"].values():
                attrs["xcor"] = cx + random.uniform(-3, 3)
                attrs["ycor"] = cy + random.uniform(-3, 3)
 
        kicking_team = kicking_team or random.choice(TEAM_COLORS)
        kicker = random.choice(list(self.teams_dict[f"{kicking_team}_team"]))
        k = self.teams_dict[f"{kicking_team}_team"][kicker]
        k["xcor"], k["ycor"] = 0.0, 0.0
        self.ball_coordinates = [0.0, 0.0]
        self.last_touch = (f"{kicking_team}_team", kicker)
        self._skip_tackle = True
        return self.teams_dict
 
    # ------------------------------------------------------------------
    # Possession / alliance helpers (your original logic)
    # ------------------------------------------------------------------
    def possession(self):
        best, best_d = None, None
        for team_name, players in self.teams_dict.items():
            for player_name, a in players.items():
                d = math.dist((a["xcor"], a["ycor"]), self.ball_coordinates)
                if best_d is None or d < best_d:
                    best, best_d = (team_name, player_name), d
        return best, best_d
 
    def determine_alliance(self):
        """(leader, second, third) by goals conceded, fewest first."""
        s = sorted(self.concessions.items(), key=lambda x: x[1])
        return s[0][0], s[1][0], s[2][0]
 
    def _ally_of(self, color):
        """The other non-leading team (only meaningful when `color` is not the leader)."""
        leader = self.determine_alliance()[0]
        return next(c for c in TEAM_COLORS if c not in (leader, color))
 
    def _pos(self, team_name, player_name):
        a = self.teams_dict[team_name][player_name]
        return (a["xcor"], a["ycor"])
 
    def apply_team_pressure(self, player_team, player_name):
        leader = self.determine_alliance()[0]
        color = player_team.split("_")[0]
        a = self.teams_dict[f"{color}_team"][player_name]
        if color == leader:
            return a["betrayal_probability"]
        a["betrayal_probability"] = max(a["betrayal_probability"], self.team_pressure_probability)
        return a["betrayal_probability"]
 
    def evaluate_betrayal(self, player_team, player_name):
        """Non-leaders betray when nearer their ally's goal than the leader's AND
        their (pressure-boosted) betrayal probability beats their team threshold."""
        color = player_team.split("_")[0]
        leader = self.determine_alliance()[0]
        if color == leader:
            return False
        ally = self._ally_of(color)
        pos = self._pos(f"{color}_team", player_name)
        dist_ally = math.dist(pos, self.field.goal_mid(ally))
        dist_enemy = math.dist(pos, self.field.goal_mid(leader))
        prob = self.apply_team_pressure(color, player_name)
        return dist_ally < dist_enemy and prob > self.team_betrayal_threshold[color]
 
    # ------------------------------------------------------------------
    # Ball travel + the out-of-play / goal rules from the PDF
    # ------------------------------------------------------------------
    def _travel(self, start, end):
        """Move the ball in a straight line; report the first hexagon side it crosses."""
        best = None
        for i in range(6):
            a, b = self.field.side(i)
            hit = _segment_hit(start, end, a, b)
            if hit and (best is None or hit[0] < best[0]):
                best = (hit[0], hit[1], i)
        return None if best is None else {"side": best[2], "point": best[1]}
 
    def _resolve_crossing(self, crossing, via):
        f = self.field
        side, pt = crossing["side"], crossing["point"]
        kicker = self.last_touch[0].split("_")[0]
 
        if side in f.side_team:                                   # a goal line
            owner = f.side_team[side]
            m, t = f.side_mid(side), f.tangent(side)
            offset = (pt[0] - m[0]) * t[0] + (pt[1] - m[1]) * t[1]
            if abs(offset) <= f.goalwidth / 2:                    # between the posts
                if via == "shot" and random.random() < SAVE_PROB:
                    return self._save(owner)
                return self._goal(owner, pt)
            if via == "shot" and random.random() < DEFLECT_PROB:
                kicker = owner                                    # deflected out by a defender
            return self._goal_line_out(side, pt, kicker)
        return self._sideline_out(side, pt, kicker)
 
    def goal(self):
        """Is the ball sitting in a goal box right now? (kept for compatibility)"""
        bx, by = self.ball_coordinates
        for team, rect in self.drawgoalstart.items():
            xs, ys = [p[0] for p in rect], [p[1] for p in rect]
            if min(xs) <= bx <= max(xs) and min(ys) <= by <= max(ys):
                return {"goal_scored": True, "team": team.split("_")[0]}
        return {"goal_scored": False}
 
    def _goal(self, conceding, pt):
        self.concessions[conceding] += 1
        s_team, s_player = self.last_touch
        scorer_color = s_team.split("_")[0]
        own_goal = scorer_color == conceding
        self.teams_dict[s_team][s_player]["owngoals" if own_goal else "goals"] += 1
 
        side = self.field.GOAL_SIDE[conceding]
        n = self.field.outward(side)
        self.ball_coordinates = [pt[0] + n[0] * 0.8, pt[1] + n[1] * 0.8]   # ball in the net
        self.pending_kickoff = conceding                                    # conceding team restarts
        return {"type": "goal", "detail": {
            "goal_scored": True, "team": conceding, "scorer": s_player, "scorer_team": scorer_color,
            "own_goal": own_goal, "ball_coordinates": list(self.ball_coordinates),
            "new_concessions": dict(self.concessions)}}
 
    def _place_taker(self, color, point):
        """Nearest player of `color` takes the restart at `point`."""
        team_name = f"{color}_team"
        name = min(self.teams_dict[team_name],
                   key=lambda p: math.dist(self._pos(team_name, p), point))
        a = self.teams_dict[team_name][name]
        a["xcor"], a["ycor"] = point
        self.ball_coordinates = [point[0], point[1]]
        self.last_touch = (team_name, name)
        self._skip_tackle = True
        return name
 
    def _push_back_opponents(self, color, point, radius=5.0):
        for team_name, players in self.teams_dict.items():
            if team_name == f"{color}_team":
                continue
            for a in players.values():
                d = math.dist((a["xcor"], a["ycor"]), point)
                if d < radius:
                    ux, uy = ((a["xcor"] - point[0]) / d, (a["ycor"] - point[1]) / d) if d else (0, 1)
                    a["xcor"], a["ycor"] = self.field.clamp_inside(
                        (point[0] + ux * radius, point[1] + uy * radius))
 
    def _inside_goal_circle(self, owner):
        side = self.field.GOAL_SIDE[owner]
        m, n = self.field.side_mid(side), self.field.outward(side)
        return (m[0] - n[0] * 1.5, m[1] - n[1] * 1.5)
 
    def _save(self, owner):
        spot = self._inside_goal_circle(owner)
        shooter = self.last_touch
        taker = self._place_taker(owner, spot)
        self._push_back_opponents(owner, spot)
        return {"type": "save", "detail": {
            "team": owner, "player": taker, "shooter": shooter[1], "shooter_team": shooter[0].split("_")[0],
            "ball_coordinates": list(self.ball_coordinates)}}
 
    def _goal_line_out(self, side, pt, kicker):
        f = self.field
        owner = f.side_team[side]
        if kicker != owner:                                        # goal kick to the owner
            spot = self._inside_goal_circle(owner)
            taker = self._place_taker(owner, spot)
            self._push_back_opponents(owner, spot)
            return {"type": "goal_kick", "detail": {
                "restart": "goal_kick", "team_awarded": owner, "player": taker,
                "kick_location": list(spot), "last_touch_team": kicker}}
 
        a, b = f.side(side)                                        # owner put it out -> corner
        vertex_idx = side if math.dist(pt, a) <= math.dist(pt, b) else (side + 1) % 6
        adjacent_side = (side - 1) % 6 if vertex_idx == side else (side + 1) % 6
        awarded = f.sideline_owner[adjacent_side]
        v = f.hexagon()[vertex_idx]
        spot = (v[0] * (1 - 0.7 / f.sidelength), v[1] * (1 - 0.7 / f.sidelength))  # within 1 m of corner
        taker = self._place_taker(awarded, spot)
        return {"type": "corner_kick", "detail": {
            "restart": "corner_kick", "team_awarded": awarded, "player": taker,
            "corner_vertex": list(v), "kick_location": list(spot), "last_touch_team": kicker}}
 
    def _sideline_out(self, side, pt, kicker):
        f = self.field
        owner = f.sideline_owner[side]
        if kicker != owner:
            awarded = owner                                        # non-owner put it out
        else:                                                      # owner put it out
            awarded = min(TEAM_COLORS, key=lambda c: math.dist(pt, f.goal_mid(c)))
        n = f.outward(side)
        spot = (pt[0] - n[0] * RESTART_INSET, pt[1] - n[1] * RESTART_INSET)
        taker = self._place_taker(awarded, spot)
        return {"type": "throwin", "detail": {
            "throwin": True, "awarded_to_team": awarded, "player": taker, "boundary_owner": owner,
            "last_touch_team": kicker, "ball_new_coordinates": list(spot)}}
 
    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------
    def _shoot(self, team_name, player_name, target):
        f = self.field
        a = self.teams_dict[team_name][player_name]
        start = (a["xcor"], a["ycor"])
        s = f.GOAL_SIDE[target]
        m, t, n = f.side_mid(s), f.tangent(s), f.outward(s)
        d = math.dist(start, m)
        off = random.gauss(0, 0.7 + 0.1 * d)                       # aim error grows with distance
        aim = (m[0] + t[0] * off, m[1] + t[1] * off)
        end = (aim[0] + n[0] * 3, aim[1] + n[1] * 3)               # carry the ball through the line
        self.last_touch = (team_name, player_name)
        crossing = self._travel(start, end)
        event = self._resolve_crossing(crossing, "shot") if crossing else None
        if event is None or event["type"] != "goal":
            a["unsuccessfulshots"] += 1
        return event
 
    def _choose_receiver(self, team_name, player_name):
        color = team_name.split("_")[0]
        pos = self._pos(team_name, player_name)
        mates = {(team_name, p): math.dist(pos, self._pos(team_name, p))
                 for p in self.teams_dict[team_name] if p != player_name}
        best = min(mates, key=mates.get)
        if color != self.determine_alliance()[0]:                  # non-leaders may pass to their ally
            ally_name = f"{self._ally_of(color)}_team"
            allies = {(ally_name, p): math.dist(pos, self._pos(ally_name, p))
                      for p in self.teams_dict[ally_name]}
            best_ally = min(allies, key=allies.get)
            if allies[best_ally] < mates[best]:
                return best_ally
        if random.random() < LONG_PASS_PROB:
            return random.choice(list(mates))
        return best
 
    def _pass(self, team_name, player_name):
        r_team, r_player = self._choose_receiver(team_name, player_name)
        start = self._pos(team_name, player_name)
        target = self._pos(r_team, r_player)
        sigma = 0.3 + 0.07 * math.dist(start, target)
        end = (target[0] + random.gauss(0, sigma), target[1] + random.gauss(0, sigma))
        self.teams_dict[team_name][player_name]["passes"] += 1
        self.last_touch = (team_name, player_name)
 
        crossing = self._travel(start, end)
        if crossing:
            return self._resolve_crossing(crossing, "pass")
 
        for opp_team, players in self.teams_dict.items():          # interception along the pass line
            if opp_team == team_name:
                continue
            for opp, a in players.items():
                if (_point_to_segment((a["xcor"], a["ycor"]), start, end) < INTERCEPT_RANGE
                        and random.random() < INTERCEPT_PROB):
                    self.ball_coordinates = [a["xcor"], a["ycor"]]
                    self.last_touch = (opp_team, opp)
                    return {"type": "interception", "detail": {
                        "player": opp, "team": opp_team.split("_")[0], "how": "pass",
                        "ball_coordinates": list(self.ball_coordinates)}}
 
        self.ball_coordinates = [end[0], end[1]]
        return {"type": "pass", "detail": {
            "team": team_name.split("_")[0], "passer": player_name, "receiver": r_player,
            "receiver_team": r_team.split("_")[0], "ball_coordinates": list(self.ball_coordinates)}}
 
    def _dribble(self, team_name, player_name, target):
        f = self.field
        a = self.teams_dict[team_name][player_name]
        goal = f.goal_mid(target)
        dx, dy = goal[0] - a["xcor"], goal[1] - a["ycor"]
        dist = math.hypot(dx, dy) or 1
        move = max(0.0, min(a["speed"] * DRIBBLE_FACTOR, dist - 3.0))   # stop 3 m from the goal
        x, y = f.clamp_inside((a["xcor"] + dx / dist * move, a["ycor"] + dy / dist * move))
        a["xcor"], a["ycor"] = x, y
        self.ball_coordinates = [x, y]
        self.last_touch = (team_name, player_name)
        return {"type": "dribble", "detail": {
            "player": player_name, "team": team_name.split("_")[0], "target_team": target,
            "ball_coordinates": list(self.ball_coordinates)}}
 
    def _clear(self, team_name, player_name):
        """Long clearance away from the player's own goal. It can run out of play,
        which is what produces corners (owner kicks it over own goal line) and throw-ins."""
        f = self.field
        color = team_name.split("_")[0]
        pos = self._pos(team_name, player_name)
        own = f.goal_mid(color)
        away = math.atan2(pos[1] - own[1], pos[0] - own[0])
        ang = away + random.uniform(-math.pi / 2, math.pi / 2)
        dist = random.uniform(10, 26)
        end = (pos[0] + math.cos(ang) * dist, pos[1] + math.sin(ang) * dist)
        self.last_touch = (team_name, player_name)
        crossing = self._travel(pos, end)
        if crossing:
            return self._resolve_crossing(crossing, "clearance")
        self.ball_coordinates = [end[0], end[1]]
        return {"type": "clearance", "detail": {
            "player": player_name, "team": color, "ball_coordinates": list(self.ball_coordinates)}}
 
    def _try_tackle(self, team_name, player_name):
        if self._skip_tackle:
            self._skip_tackle = False
            return None
        pos = self._pos(team_name, player_name)
        best, best_d = None, None
        for opp_team, players in self.teams_dict.items():
            if opp_team == team_name:
                continue
            for opp in players:
                d = math.dist(pos, self._pos(opp_team, opp))
                if best_d is None or d < best_d:
                    best, best_d = (opp_team, opp), d
        if best_d is not None and best_d < TACKLE_RANGE and random.random() < TACKLE_PROB:
            self.ball_coordinates = list(self._pos(*best))
            self.last_touch = best
            return {"type": "interception", "detail": {
                "player": best[1], "team": best[0].split("_")[0], "how": "tackle",
                "ball_coordinates": list(self.ball_coordinates)}}
        return None
 
    def _attack(self, team_name, player_name):
        f = self.field
        color = team_name.split("_")[0]
        leader = self.determine_alliance()[0]
        betraying = self.evaluate_betrayal(team_name, player_name)
 
        if betraying:
            target = self._ally_of(color)                           # betrayal: go for the ally's goal
        elif color == leader:
            pos = self._pos(team_name, player_name)                 # leader: nearest opponent goal
            target = min((c for c in TEAM_COLORS if c != color),
                         key=lambda c: math.dist(pos, f.goal_mid(c)))
        else:
            target = leader                                         # alliance: attack the leader
 
        pos = self._pos(team_name, player_name)
        if math.dist(pos, f.goal_mid(color)) < CLEARANCE_RANGE and random.random() < CLEARANCE_PROB:
            return self._clear(team_name, player_name)
 
        dist_to_goal = math.dist(pos, f.goal_mid(target))
        if dist_to_goal <= SHOOT_RANGE and random.random() < SHOOT_PROB:
            if betraying:
                self._record({"type": "betrayal", "detail": {
                    "betrayal": "shot_at_ally_goal", "player": player_name,
                    "team": color, "target_team": target}})
            return self._shoot(team_name, player_name, target)
        if random.random() < PASS_PROB:
            return self._pass(team_name, player_name)
        return self._dribble(team_name, player_name, target)
 
    def _move_players(self):
        """Off-ball movement: opponents chase the ball, team-mates support it."""
        holder, _ = self.possession()
        bx, by = self.ball_coordinates
        for team_name, players in self.teams_dict.items():
            for name, a in players.items():
                if (team_name, name) == holder:
                    continue
                chase = 0.03 if team_name == holder[0] else 0.06
                step = a["speed"] * chase
                dx, dy = bx - a["xcor"], by - a["ycor"]
                dist = math.hypot(dx, dy) or 1
                x = a["xcor"] + dx / dist * step + random.uniform(-1, 1) * step * 0.5
                y = a["ycor"] + dy / dist * step + random.uniform(-1, 1) * step * 0.5
                a["xcor"], a["ycor"] = self.field.clamp_inside((x, y))
 
    # ------------------------------------------------------------------
    # One tick of the simulation
    # ------------------------------------------------------------------
    def _record(self, event):
        if event["type"] in KEY_EVENT_TYPES:
            self.key_events.append({"tick": self.current_tick, **event})
            self.key_events = self.key_events[-8:]
 
    def step(self):
        self.current_tick += 1
 
        if self.pending_kickoff:                                   # restart after a goal
            team = self.pending_kickoff
            self.pending_kickoff = None
            self.spawn_player_before_kickoff(kicking_team=team)
            self.last_event = {"type": "kickoff", "detail": {"team": team}}
            return self.last_event
 
        (team_name, player_name), _ = self.possession()
        self.teams_dict[team_name][player_name]["posession"] += 1
 
        event = self._try_tackle(team_name, player_name) or self._attack(team_name, player_name)
        self.last_event = event
        self._record(event)
        if not self.pending_kickoff:
            self._move_players()
        return event
 
    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _to_px(point):
        x, y = point
        return [CANVAS_SIZE / 2 + x * SCALE, CANVAS_SIZE / 2 - y * SCALE]
 
    def get_state(self):
        teams_px = {}
        for team_name, players in self.teams_dict.items():
            teams_px[team_name] = {}
            for player_name, attrs in players.items():
                px, py = self._to_px((attrs["xcor"], attrs["ycor"]))
                teams_px[team_name][player_name] = {**attrs, "xcor": px, "ycor": py}
 
        return {
            "tick": self.current_tick,
            "hex": [self._to_px(p) for p in self.field.hexagon()],
            "goals": {k: [self._to_px(p) for p in v] for k, v in self.drawgoalstart.items()},
            # the three "third" lines (centre -> sideline midpoints), drawn dashed by simulation.js
            "boundaries": {k: [self._to_px(p) for p in v] for k, v in self.field.third_lines().items()},
            "teams": teams_px,
            "ball": self._to_px(self.ball_coordinates),
            "concessions": dict(self.concessions),
            "last_event": self.last_event,
            "key_events": self.key_events,
        }
