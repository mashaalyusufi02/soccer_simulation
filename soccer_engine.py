

import math
import random

CANVAS_SIZE = 400
SCALE = 7.5  # pxels

"""This class creates the hexagon, boundaries for the team areas, goals, corners, """
class Field():
    def __init__(self):
        self.diameter = 40
        self.centretocorner = self.diameter / 2
        self.sidelength = 23
        self.numsides = 6
        self.goalheight = 2
        self.goalwidth = 3
        self.centre = (0, 0)

    def hexagon(self):
        angle = (360 / self.numsides) * (math.pi / 180)
        coords = []
        for i in range(self.numsides):
            x = round(self.sidelength * math.cos(angle * i), 2)
            y = round(self.sidelength * math.sin(angle * i), 2)
            coords.append((x, y))
        return coords

    def dividepitchpossession(self):
        c = self.hexagon()
        return {
            "red_team_area": [self.centre, c[1], c[0], c[5]],
            "blue_team_area": [self.centre, c[5], c[4], c[3]],
            "green_team_area": [self.centre, c[3], c[4], c[1]],
        }

    def dividepitchboundaries(self):
        c = self.hexagon()
        return {
            "red_team_boundary": [c[2], c[3], c[5], c[0]],
            "blue_team_boundary": [c[5], c[4], c[2], c[1]],
            "green_team_boundary": [c[3], c[4], c[1], c[0]],
        }

    def drawgoalstart(self):
        c = self.hexagon()
        redx = (c[0][0] + c[1][0]) / 2
        redy = (c[0][1] + c[1][1]) / 2
        bluex = (c[2][0] + c[1][0]) / 2
        bluey = (c[2][1] + c[1][1]) / 2
        greenx = (c[3][0] + c[4][0]) / 2
        greeny = (c[3][1] + c[4][1]) / 2

        def rect(gx, gy):
            left = [gx - self.goalwidth / 2, gy]
            right = [gx + self.goalwidth / 2, gy]
            top_left = [gx + self.goalwidth / 2, gy + self.goalheight]
            top_right = [gx - self.goalwidth / 2, gy + self.goalheight]
            return [left, top_left, top_right, right]

        return {
            "red_team_goal_coords": rect(redx, redy),
            "blue_team_goal_coords": rect(bluex, bluey),
            "green_team_goal_coords": rect(greenx, greeny),
        }

    def draw_goal_lines_outside_goal(self):
        goal_rects = self.drawgoalstart()
        boundaries = self.dividepitchboundaries()
        final_segments = {}

        for color in ["red", "blue", "green"]:
            rect = goal_rects[f"{color}_team_goal_coords"]
            boundary_key = f"{color}_team_boundary"
            bottom_left, bottom_right = rect[0], rect[3]
            goal_mid = ((bottom_left[0] + bottom_right[0]) / 2, (bottom_left[1] + bottom_right[1]) / 2)

            candidates = {
                "left": [boundaries[boundary_key][0], rect[0]],
                "right": [boundaries[boundary_key][1], rect[1]],
            }

            distances = []
            for name, seg in candidates.items():
                (x1, y1), (x2, y2) = seg
                seg_mid = ((x1 + x2) / 2, (y1 + y2) / 2)
                dist = math.dist(seg_mid, goal_mid)
                distances.append((name, dist, seg_mid[1], seg))

            distances.sort(key=lambda item: (item[1], item[2]))
            final_segments[f"{color}_goal_lines"] = [
                {"name": distances[0][0], "segment": distances[0][3]},
                {"name": distances[1][0], "segment": distances[1][3]},
            ]

        return final_segments

 

"""This class creates the players, their attributes, the team, its attributes. The team must have between 3-5 players"""
class Player():
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

"""This class calls the field class and player class and creates the team. It defines the betrayal thresholds for teams, spawns players, defines possession, kickoff, passing to your own team or passing to the team you choose to team up with against a third team"""
class Team():
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
        self.leading_team = min(self.concessions, key=self.concessions.get)
        self.leading_team_goals = self.concessions[self.leading_team]

        betrayal_thresholds = betrayal_thresholds or {}
        self.team_betrayal_threshold = {
            "red": betrayal_thresholds.get("red", random.uniform(0, 1)),
            "green": betrayal_thresholds.get("green", random.uniform(0, 1)),
            "blue": betrayal_thresholds.get("blue", random.uniform(0, 1)),
        }
        self.current_tick = 0
        self.team_pressure_probability = random.uniform(0.1, 1)
        self.last_event = {"type": "kickoff", "detail": None}

    def spawn_player_before_kickoff(self):
        for team in ["red", "blue", "green"]:
            area = self.dividepitchforteams[f"{team}_team_area"]
            xcoords = [p[0] for p in area]
            ycoords = [p[1] for p in area]
            cx = sum(xcoords) / len(xcoords)
            cy = sum(ycoords) / len(ycoords)
            for player in self.teams_dict[f"{team}_team"]:
                self.teams_dict[f"{team}_team"][player]["xcor"] = cx + random.uniform(-3, 3)
                self.teams_dict[f"{team}_team"][player]["ycor"] = cy + random.uniform(-3, 3)
        self.ball_coordinates = [0.0, 0.0]
        return self.teams_dict

    def possession(self):
        distances = {}
        for team_name, players in self.teams_dict.items():
            for player_name, attrs in players.items():
                dist = math.dist((attrs["xcor"], attrs["ycor"]), self.ball_coordinates)
                distances[(team_name, player_name)] = dist
        closest = min(distances, key=distances.get)
        return closest, distances[closest]

    def kickoff(self):
        self.spawn_player_before_kickoff()
        team_name = random.choice(list(self.teams_dict.keys()))
        team_players = self.teams_dict[team_name]
        passer = random.choice(list(team_players.keys()))
        receiver = random.choice([p for p in team_players.keys() if p != passer])
        team_players[passer]["passes"] += 1
        self.ball_coordinates = [team_players[receiver]["xcor"], team_players[receiver]["ycor"]]
        return [team_name, passer, receiver, self.ball_coordinates]

    def passing(self):
        (team_name, player_name), _ = self.possession()
        team_players = self.teams_dict[team_name]
        distances = {
            other: math.dist((attrs["xcor"], attrs["ycor"]), self.ball_coordinates)
            for other, attrs in team_players.items() if other != player_name
        }
        receiver = min(distances, key=distances.get)
        team_players[player_name]["passes"] += 1
        self.ball_coordinates = [team_players[receiver]["xcor"], team_players[receiver]["ycor"]]
        return {"team": team_name, "passer": player_name, "receiver": receiver, "ball_coordinates": self.ball_coordinates}

    def ally_pass(self):
        team_name, passer, receiver, coords = self.kickoff()
        sorted_teams = sorted(self.concessions.items(), key=lambda x: x[1])
        ally_team = sorted_teams[1][0]
        if ally_team == team_name:
            ally_team = sorted_teams[0][0]
        receivers_team = self.teams_dict[f"{ally_team}_team"]
        player_name = random.choice(list(receivers_team.keys()))
        player_dict = receivers_team[player_name]
        player_dict["passes"] += 1
        self.ball_coordinates = [player_dict["xcor"], player_dict["ycor"]]
        return {"new_ball_coordinates": self.ball_coordinates, "receiver_player": player_name, "receiver_team": ally_team}
    
    """goal() checks every team's goal box instead of bailing out after the first one, and reads the goal line segments dictionary values using the keys draw_goal_lines_outside_goal() returns."""
    def goal(self):
        #notes x,y coordinates of ball
        ball_x, ball_y = self.ball_coordinates
        #notes the minimum and maximum xy coordinates of the goal boundaries
        for team, rect in self.drawgoalstart.items():
            xs = [p[0] for p in rect]
            ys = [p[1] for p in rect]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            #if the ball is within the goal boundaries, increment the concession count for that team and update the scorer's goal count if necessary
            if min_x <= ball_x <= max_x and min_y <= ball_y <= max_y:
                color = team.split("_")[0]
                self.concessions[color] += 1
                scorer_team, scorer_player = self.possession()[0]
                if scorer_team.split("_")[0] != color:
                    self.teams_dict[scorer_team][scorer_player]["goals"] += 1
                return {
                    "goal_scored": True,
                    "team": color,
                    "ball_coordinates": self.ball_coordinates,
                    "new_concessions": self.concessions}
        #if no goal was scored return false and the ball coordinates
        return {"goal_scored": False, "ball_coordinates": self.ball_coordinates}

    def throwin_restart(self):
        ball_x, ball_y = self.ball_coordinates
        crossed_boundary = None

        for team, boundary in self.dividepitchboundaries.items():
            xs = [p[0] for p in boundary]
            ys = [p[1] for p in boundary]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            if not (min_x <= ball_x <= max_x and min_y <= ball_y <= max_y):
                crossed_boundary = team
                break

        if crossed_boundary is None:
            return {"throwin": False, "reason": "Ball still inside field"}

        boundary_team = crossed_boundary.split("_")[0]
        (last_team, last_player), _ = self.possession()
        last_team = last_team.split("_")[0]

        if last_team == boundary_team:
            distances = {}
            for team, boundary in self.dividepitchboundaries.items():
                bx = sum(p[0] for p in boundary) / len(boundary)
                by = sum(p[1] for p in boundary) / len(boundary)
                distances[team] = math.dist((ball_x, ball_y), (bx, by))
            throwin_team = min(distances, key=distances.get).split("_")[0]
        else:
            throwin_team = boundary_team

        receivers_team = self.teams_dict[f"{throwin_team}_team"]
        player_name = random.choice(list(receivers_team.keys()))
        player_dict = receivers_team[player_name]
        player_dict["xcor"] = ball_x
        player_dict["ycor"] = ball_y

        hex_coords = self.field.hexagon()
        xs = [p[0] for p in hex_coords]
        ys = [p[1] for p in hex_coords]
        new_x = random.uniform(min(xs), max(xs)) * 0.6
        new_y = random.uniform(min(ys), max(ys)) * 0.6
        self.ball_coordinates = [new_x, new_y]

        return {
            "throwin": True,
            "awarded_to_team": throwin_team,
            "player": player_name,
            "player_new_coordinates": [player_dict["xcor"], player_dict["ycor"]],
            "ball_new_coordinates": self.ball_coordinates,
        }

    def goalkick_or_corner_kick(self):
        (last_team, last_player), _ = self.possession()
        last_team = last_team.split("_")[0]
        ball_x, ball_y = self.ball_coordinates
        goal_lines = self.field.draw_goal_lines_outside_goal()

        crossed_team = None
        for color in ["red", "blue", "green"]:
            for seg_info in goal_lines[f"{color}_goal_lines"]:
                (x1, y1), (x2, y2) = seg_info["segment"]
                seg_min_x, seg_max_x = min(x1, x2), max(x1, x2)
                seg_min_y, seg_max_y = min(y1, y2), max(y1, y2)
                horizontally_near = seg_min_x - 1 <= ball_x <= seg_max_x + 1
                vertically_crossed = ball_y < seg_min_y or ball_y > seg_max_y
                if horizontally_near and vertically_crossed:
                    crossed_team = color
                    break
            if crossed_team:
                break

        if crossed_team is None:
            return {"restart": False, "reason": "Ball has not crossed any goal line"}

        if last_team != crossed_team:
            rect = self.drawgoalstart[f"{crossed_team}_team_goal_coords"]
            goal_mid_x = (rect[0][0] + rect[3][0]) / 2
            goal_mid_y = (rect[0][1] + rect[3][1]) / 2
            self.ball_coordinates = [goal_mid_x + random.uniform(-2, 2), goal_mid_y + random.uniform(-2, 2)]
            return {"restart": "goal_kick", "team_awarded": crossed_team, "kick_location": self.ball_coordinates, "last_touch_team": last_team}
        else:
            boundary_vertices = self.dividepitchboundaries[f"{crossed_team}_team_boundary"]
            distances = {v: math.dist(v, (ball_x, ball_y)) for v in boundary_vertices}
            corner_vertex = min(distances, key=distances.get)
            self.ball_coordinates = [corner_vertex[0] + random.uniform(-1, 1), corner_vertex[1] + random.uniform(-1, 1)]
            return {"restart": "corner_kick", "team_awarded": crossed_team, "corner_vertex": corner_vertex, "kick_location": self.ball_coordinates, "last_touch_team": last_team}

    def determine_alliance(self):
        sorted_teams = sorted(self.concessions.items(), key=lambda x: x[1])
        return sorted_teams[0][0], sorted_teams[1][0], sorted_teams[2][0]

    def compute_pass_distances(self, team_name, player_name, med_team, low_team):
        px, py = self.teams_dict[team_name][player_name]["xcor"], self.teams_dict[team_name][player_name]["ycor"]
        teammate_distances = {
            other: math.dist((px, py), (attrs["xcor"], attrs["ycor"]))
            for other, attrs in self.teams_dict[team_name].items() if other != player_name
        }
        closest_teammate = min(teammate_distances, key=teammate_distances.get)

        ally_distances = {}
        for ally in [med_team, low_team]:
            for ally_player, attrs in self.teams_dict[f"{ally}_team"].items():
                ally_distances[(ally, ally_player)] = math.dist((px, py), (attrs["xcor"], attrs["ycor"]))
        closest_ally = min(ally_distances, key=ally_distances.get)

        return teammate_distances[closest_teammate], closest_teammate, ally_distances[closest_ally], closest_ally

    def decide_pass_type(self):
        (team_name, player_name), _ = self.possession()
        team_color = team_name.split("_")[0]
        winning_team, med_team, low_team = self.determine_alliance()
        if team_color == winning_team:
            return self.passing()
        teammate_dist, _, ally_dist, _ = self.compute_pass_distances(team_name, player_name, med_team, low_team)
        return self.passing() if teammate_dist < ally_dist else self.ally_pass()

    def apply_team_pressure(self, player_team, player_name):
        winning_team, _, _ = self.determine_alliance()
        player_team = player_team.split("_")[0]
        if player_team == winning_team:
            return self.teams_dict[f"{player_team}_team"][player_name]["betrayal_probability"]
        current_prob = self.teams_dict[f"{player_team}_team"][player_name]["betrayal_probability"]
        new_prob = max(current_prob, self.team_pressure_probability)
        self.teams_dict[f"{player_team}_team"][player_name]["betrayal_probability"] = new_prob
        return new_prob

    """Evaluate whether a player should betray their team based on their position relative to the ally and enemy goals"""
    """A player will betray their the team they are allying with if they are closer to their ally's goal than towards the enemy's goal and if their betrayal probability exceeds the team's betrayal probability threshold."""
    def evaluate_betrayal(self, player_team, player_name):
        player_team = player_team.split("_")[0]
        winning_team, ally1, ally2 = self.determine_alliance()
        if player_team == winning_team:
            return False
        ally_team = ally1 if ally2 == player_team else ally2
        px = self.teams_dict[f"{player_team}_team"][player_name]["xcor"]
        py = self.teams_dict[f"{player_team}_team"][player_name]["ycor"]
        ally_rect = self.drawgoalstart[f"{ally_team}_team_goal_coords"]
        enemy_rect = self.drawgoalstart[f"{winning_team}_team_goal_coords"]
        ally_mid = ((ally_rect[0][0] + ally_rect[3][0]) / 2, (ally_rect[0][1] + ally_rect[3][1]) / 2)
        enemy_mid = ((enemy_rect[0][0] + enemy_rect[3][0]) / 2, (enemy_rect[0][1] + enemy_rect[3][1]) / 2)
        dist_ally = math.dist((px, py), ally_mid)
        dist_enemy = math.dist((px, py), enemy_mid)
        betrayal_prob = self.apply_team_pressure(f"{player_team}_team", player_name)
        return dist_ally < dist_enemy and betrayal_prob > self.team_betrayal_threshold[player_team]

    def perform_betrayal(self, player_team, player_name):
        player_team = player_team.split("_")[0]
        winning_team, ally1, ally2 = self.determine_alliance()
        ally_team = ally1 if ally2 == player_team else ally2
        px = self.teams_dict[f"{player_team}_team"][player_name]["xcor"]
        py = self.teams_dict[f"{player_team}_team"][player_name]["ycor"]
        enemy_rect = self.drawgoalstart[f"{winning_team}_team_goal_coords"]
        ally_rect = self.drawgoalstart[f"{ally_team}_team_goal_coords"]
        enemy_mid = ((enemy_rect[0][0] + enemy_rect[3][0]) / 2, (enemy_rect[0][1] + enemy_rect[3][1]) / 2)
        ally_mid = ((ally_rect[0][0] + ally_rect[3][0]) / 2, (ally_rect[0][1] + ally_rect[3][1]) / 2)
        dist_ally = math.dist((px, py), ally_mid)
        dist_enemy = math.dist((px, py), enemy_mid)

        if dist_ally > dist_enemy:
            self.ball_coordinates = [ally_mid[0], ally_mid[1]]
            self.teams_dict[f"{player_team}_team"][player_name]["unsuccessfulshots"] += 1
            return {"betrayal": "shot_at_ally_goal", "player": player_name, "target_team": ally_team, "ball_coordinates": self.ball_coordinates}

        receivers_team = self.teams_dict[f"{winning_team}_team"]
        receiver = random.choice(list(receivers_team.keys()))
        self.ball_coordinates = [receivers_team[receiver]["xcor"], receivers_team[receiver]["ycor"]]
        return {"betrayal": "pass_to_enemy_team", "player": player_name, "receiver": receiver, "receiver_team": winning_team, "ball_coordinates": self.ball_coordinates}
    
    """Nudge every player slightly toward the ball, plus some randomness,so there's visible motion on screen between discrete events."""
    def _jitter_players(self):
        bx, by = self.ball_coordinates
        max_r = self.field.sidelength
        for players in self.teams_dict.values():
            for attrs in players.values():
                step = attrs["speed"] * 0.04
                dx, dy = bx - attrs["xcor"], by - attrs["ycor"]
                dist = math.hypot(dx, dy) or 1
                ux, uy = dx / dist, dy / dist
                new_x = attrs["xcor"] + ux * step * 0.35 + random.uniform(-1, 1) * step * 0.5
                new_y = attrs["ycor"] + uy * step * 0.35 + random.uniform(-1, 1) * step * 0.5
                r = math.hypot(new_x, new_y)
                if r > max_r:
                    new_x *= max_r / r
                    new_y *= max_r / r
                attrs["xcor"], attrs["ycor"] = new_x, new_y

    """Advance the simulation by one tick. Returns a description of whatever event happened this tick."""
    def step(self):
        self.current_tick += 1
        (team_name, player_name), _ = self.possession()

        goal_event = self.goal()
        if goal_event["goal_scored"]:
            self.ball_coordinates = [0.0, 0.0]
            self.spawn_player_before_kickoff()
            self.last_event = {"type": "goal", "detail": goal_event}
            self._jitter_players()
            return self.last_event

        throwin_event = self.throwin_restart()
        if throwin_event["throwin"]:
            self.last_event = {"type": "throwin", "detail": throwin_event}
            self._jitter_players()
            return self.last_event

        restart_event = self.goalkick_or_corner_kick()
        if restart_event["restart"]:
            self.last_event = {"type": restart_event["restart"], "detail": restart_event}
            self._jitter_players()
            return self.last_event

        pass_event = self.decide_pass_type()
        self.last_event = {"type": "pass", "detail": pass_event}

        betrayal = self.evaluate_betrayal(team_name, player_name)
        if betrayal:
            result = self.perform_betrayal(team_name, player_name)
            self.last_event = {"type": "betrayal", "detail": result}

        self._jitter_players()
        return self.last_event

    """Helper functions to convert coordinates to canvas pixels for visualization
       _to_px(point) scales a set of x,y coordinates to canvas pixels and returns them as x,y coordinates in a list 
       get_state() returns a JSON-serializable snapshot with coordinates already converted to canvas pixels."""

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
            "boundaries": {k: [self._to_px(p) for p in v] for k, v in self.dividepitchboundaries.items()},
            "teams": teams_px,
            "ball": self._to_px(self.ball_coordinates),
            "concessions": self.concessions,
            "last_event": self.last_event,
        }


