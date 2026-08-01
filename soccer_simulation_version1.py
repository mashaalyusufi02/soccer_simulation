import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np
import os
import statistics
import seaborn as sns
import matplotlib.patheffects as PathEffects


class field():
    def __init__(self):
        self.diameter = 40
        self.centretocorner = (self.diameter)/2
        self.sidelength = 23
        self.numsides = 6
        self.goalheight = 2
        self.goalwidth = 3
        self.centre = (0,0)

    def hexagon(self):
        """This method returns the xy coordinates of the regular hexagon consisting of 6 equilateral triangles"""
        """Compute all angles in radians because math.cos() and math.sin() return radians"""
        #convert 60 degrees to radians
        angle = (360 / self.numsides) * (math.pi / 180)
        #polygoncoordinates stores the cartesian coordinates of the hexagon
        polygoncoordinates = []
        #generate 6 pairs of vertices for the hexagon using the loop
        for i in range(0,self.numsides):
            x = round((self.sidelength * math.cos(angle*i)),2)
            y = round((self.sidelength * math.sin(angle*i)),2)
            polygoncoordinates.append((x,y))
        return polygoncoordinates
    
    """Return the each team's area coordinates which dictate centre kicks"""
    def dividepitchpossession(self):
        coordinates = self.hexagon()
        return {"red_team_area" : [self.centre, coordinates[1],coordinates[0],coordinates[5]],
         "blue_team_area" : [self.centre, coordinates[5],coordinates[4],coordinates[3]],
         "green_team_area" : [self.centre, coordinates[3],coordinates[4],coordinates[1]]}
        #COORDINATES OF THE HEXAGON SHOULD ROUGHLY BE
        #[[-11.5,-20],[-11.5,20],[11.5,-20],[11.5,20],[23,0]]

    """Return the boundary coordinates which dictate throw in's"""
    def dividepitchboundaries(self):
        coordinates = self.hexagon()
        return {"red_team_boundary" : [coordinates[2],coordinates[3],coordinates[5],coordinates[0]],
         "blue_team_boundary" : [coordinates[5],coordinates[4],coordinates[2],coordinates[1]],
         "green_team_boundary" : [coordinates[3],coordinates[4],coordinates[1],coordinates[0]]}
    

    """Return the rectangular xy coordinates for each goal. Start by computing the starting point of each goal which is the midpoint of the boundary. Then add and subtract 1.5 and 2 to get the 4 rectangular coordinates of the goal"""
    def drawgoalstart(self):
        coordinates = self.hexagon()
        redgoalxcoord = (coordinates[0][0] + coordinates[1][0])//2
        redgoalycoord = (coordinates[0][1] + coordinates[1][1])//2
        bluegoalxcoord = (coordinates[2][0] + coordinates[1][0])//2
        bluegoalycoord = (coordinates[2][1] + coordinates[1][1])//2
        greengoalxcoord = (coordinates[3][0] + coordinates[4][0])//2
        greengoalycoord = (coordinates[3][1] + coordinates[4][1])//2
        starting_pointcoords = [[redgoalxcoord,redgoalycoord],[bluegoalxcoord,bluegoalycoord],[greengoalxcoord,greengoalycoord]]
        """Now obtain the 4 coordinates required to draw the rectangle of the red goal"""
        left_red_goal_xycoord = [redgoalxcoord - ((self.goalwidth)/2), redgoalycoord]
        right_red_goal_xycoord = [redgoalxcoord + ((self.goalwidth)/2), redgoalycoord]
        top_left_red_goal_xycoord = [redgoalxcoord+((self.goalwidth)/2),redgoalycoord+self.goalheight]
        top_right_red_goal_xycoord = [redgoalxcoord-((self.goalwidth)/2),redgoalycoord+self.goalheight]
        """Now obtain the 4 coordinates required to draw the rectangle of the blue goal"""
        left_blue_goal_xycoord = [bluegoalxcoord - ((self.goalwidth)/2), bluegoalycoord]
        right_blue_goal_xycoord = [bluegoalxcoord + ((self.goalwidth)/2), bluegoalycoord]
        top_left_blue_goal_xycoord = [bluegoalxcoord+((self.goalwidth)/2),bluegoalycoord+self.goalheight]
        top_right_blue_goal_xycoord = [bluegoalxcoord-((self.goalwidth)/2),bluegoalycoord+self.goalheight]
        """Now obtain the 4 coordinates required to draw the rectangle of the green goal"""
        left_green_goal_xycoord = [greengoalxcoord - ((self.goalwidth)/2), greengoalycoord]
        right_green_goal_xycoord = [greengoalxcoord + ((self.goalwidth)/2), greengoalycoord]
        top_left_green_goal_xycoord = [greengoalxcoord+((self.goalwidth)/2),greengoalycoord+self.goalheight]
        top_right_green_goal_xycoord = [greengoalxcoord-((self.goalwidth)/2),greengoalycoord+self.goalheight]
        return {"red_team_goal_coords":[left_red_goal_xycoord,top_left_red_goal_xycoord,top_right_red_goal_xycoord,right_red_goal_xycoord],
                "blue_team_goal_coords":[left_blue_goal_xycoord,top_left_blue_goal_xycoord,top_right_blue_goal_xycoord,right_blue_goal_xycoord],
                "green_team_goal_coords":[left_green_goal_xycoord ,top_left_green_goal_xycoord,top_right_green_goal_xycoord,right_green_goal_xycoord]}
    
    def draw_goal_lines_outside_goal(self):
        goal_boundaries = self.drawgoalstart()
        team_boundaries = self.dividepitchboundaries()
        goal_lines = {"red_line_segment_right": [team_boundaries['red_team_boundary'][3], goal_boundaries['red_team_goal_coords'][3]],
                      "red_line_segment_left": [team_boundaries['red_team_boundary'][2], goal_boundaries['red_team_goal_coords'][0]],
                      "green_line_segment_right": [team_boundaries['green_team_boundary'][1], goal_boundaries['green_team_goal_coords'][2]],
                      "green_line_segment_left": [team_boundaries['green_team_boundary'][3], goal_boundaries['green_team_goal_coords'][3]],
                      "blue_line_segment_right": [team_boundaries['blue_team_boundary'][2], goal_boundaries['blue_team_goal_coords'][3]],
                      "blue_line_segment_left": [team_boundaries['blue_team_boundary'][2], goal_boundaries['blue_team_goal_coords'][0]]
                      }
        return goal_lines
        #sorted_by_ycoord_goalcoords = {team: sorted (goal_coords, key=lambda point:point[1]) for team, goal_coords in self.drawgoalstart().items()}

    def draw_goal_lines_outside_goal(self):
        goal_rects = self.drawgoalstart()
        boundaries = self.dividepitchboundaries()

        final_segments = {}

        for color in ["red", "blue", "green"]:
            goal_key = f"{color}_team_goal_coords"
            boundary_key = f"{color}_team_boundary"

            rect = goal_rects[goal_key]

        # Goal rectangle bottom edge midpoint
            bottom_left = rect[0]
            bottom_right = rect[3]
            goal_mid = ((bottom_left[0] + bottom_right[0]) / 2,(bottom_left[1] + bottom_right[1]) / 2)

        # Candidate segments (boundary vertex → goal rectangle bottom vertex)
            if color == "red":
                candidates = {
                "left":  [boundaries["red_team_boundary"][0], rect[0]],
                "right": [boundaries["red_team_boundary"][1], rect[1]]}
            elif color == "blue":
                candidates = {
                "left":  [boundaries["blue_team_boundary"][0], rect[0]],
                "right": [boundaries["blue_team_boundary"][1], rect[1]]}
            else:  # green
                candidates = {
                "left":  [boundaries["green_team_boundary"][0], rect[0]],
                "right": [boundaries["green_team_boundary"][1], rect[1]]}

        # Compute distance from segment midpoint → goal midpoint
            distances = []
            for name, seg in candidates.items():
                (x1, y1), (x2, y2) = seg
                seg_mid = ((x1 + x2) / 2, (y1 + y2) / 2)
                dist = math.dist(seg_mid, goal_mid)
                distances.append((name, dist, seg_mid[1], seg))

        # Sort by distance, then by y-value
            distances.sort(key=lambda item: (item[1], item[2]))

        # Return BOTH segments, ordered by closeness
            final_segments[f"{color}_goal_lines"] = [
                {"name": distances[0][0], "segment": distances[0][3]},
                {"name": distances[1][0], "segment": distances[1][3]}]

        return final_segments


        

create_polygon = field().hexagon()
print(create_polygon)
dividepitchforteams = field().dividepitchpossession()
print(dividepitchforteams)
dividepitchboundaries = field().dividepitchboundaries()
print(dividepitchboundaries)
drawgoalstart = field().drawgoalstart()
print(drawgoalstart)

goal_line_segments = field().draw_goal_lines_outside_goal()
print(goal_line_segments)

"""
Each team must consist of a minimum of 3 players and a maximum of 5 players
create a dictionary where each players team is assigned to them
Every time the game is initialized, there must be a minimum of 3 players and the user
has the option to choose between 3-5 players
"""

class Players():
        """Define attributes of players"""
        def __init__(self,teamcolor):
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
                player_template = Players(color)  # Create fresh player for each
                team[f"Player_{i}"] = {
                    "teamcolor": player_template.teamcolor,
                    "speed": player_template.speed,
                    "passes": player_template.numpass,
                    "unsuccessfulshots": player_template.unsuccessfulshots,
                    "goals": player_template.goals,
                    "owngoals": player_template.owngoals,
                    "posession": player_template.posessiontime,
                    "betrayal_probability": player_template.betrayal_prob,
                    "xcor": player_template.xcor,
                    "ycor": player_template.ycor
                }
            return team



        

    
"""Generate all 3 teams by calling the method generate_teams for the red, blue, and green team"""
blue_team = Players("blue").make_team("blue",3)
print("blue Team:",blue_team)
green_team = Players("green").make_team("green",3)
print("green team:",green_team)
red_team = Players("red").make_team("red",3)
print("red team:",red_team)


"""Demarkate the field into red, green, blue zones"""
"""Teams start within their third of the pitch:
Incorporate the triangle whose sides are measured from centre to corner as limits for player movement"""
 


class Team():
    def __init__(self, num_blue=3, num_red=3, num_green=3):
        self.field = field()
        self.dividepitchforteams = self.field.dividepitchpossession()
        self.dividepitchboundaries = self.field.dividepitchboundaries()
        self.drawgoalstart = self.field.drawgoalstart()

        self.blueplayers = Players("blue").make_team("blue", num_blue)
        self.redplayers = Players("red").make_team("red", num_red)
        self.greenplayers = Players("green").make_team("green", num_green)

        self.teams_dict = {
            "blue_team": self.blueplayers,
            "red_team": self.redplayers,
            "green_team": self.greenplayers
        }

        self.ball_coordinates = [0.0, 0.0]
        self.concessions = {"red": 0, "blue": 0, "green": 0}
        self.leading_team = min(self.concessions, key=self.concessions.get)
        self.leading_team_goals = self.concessions[self.leading_team]
        self.team_betrayal_threshold = {"red": random.uniform(0,1),"green": random.uniform(0,1),"blue": random.uniform(0,1)}
        self.current_tick = 0
        self.team_pressure_probability = random.uniform(0.1,1)
        

    """Spawn players on the field within their area boundaries. Refer to divide self.pitchforteams dict"""
    def spawn_player_before_kickoff(self):
        for team in ["red", "blue", "green"]:
            area = self.dividepitchforteams[f"{team}_team_area"]
            xcoords = [x[0] for x in area]
            ycoords = [y[1] for y in area]
            for player in self.teams_dict[f"{team}_team"]:
                self.teams_dict[f"{team}_team"][player]["xcor"] = random.choice(xcoords)
                self.teams_dict[f"{team}_team"][player]["ycor"] = random.choice(ycoords)
        return self.teams_dict
          
            

    """return the the team of the player and player themselves who last touched the ball"""
    def possession(self):
        distance_between_player_ball = {}
        for team_name, team_players in self.teams_dict.items():
            for player_name, attrs in team_players.items():
                px, py = attrs["xcor"], attrs["ycor"]
                dist = math.dist((px, py), self.ball_coordinates)
                distance_between_player_ball[(team_name, player_name)] = dist

        closest = min(distance_between_player_ball, key=distance_between_player_ball.get)
        return closest, distance_between_player_ball[closest]
    
    """ball kicked from the centre"""
    def kickoff(self):
        self.spawn_player_before_kickoff()

        team_name = random.choice(list(self.teams_dict.keys()))
        team_players = self.teams_dict[team_name]

 
        passer = random.choice(list(team_players.keys()))

        possible_receivers = [p for p in team_players.keys() if p != passer]
        receiver = random.choice(possible_receivers)

    
        team_players[passer]["passes"] += 1

  
        self.ball_coordinates = [team_players[receiver]["xcor"], team_players[receiver]["ycor"]]

        return [team_name, passer, receiver, self.ball_coordinates]

        
    """ball passed between teammates based on who is closest from own team"""
    def passing(self):
        (team_name, player_name), distance = self.possession()


        team_players = self.teams_dict[team_name]

    # choose receiver based on distance
        distances = {}
        for other_player, attrs in team_players.items():
            if other_player != player_name:
                px, py = attrs["xcor"], attrs["ycor"]
                dist = math.dist((px, py), self.ball_coordinates)
                distances[other_player] = dist

    # closest teammate receives the ball
        receiver = min(distances, key=distances.get)

    # update passes
        team_players[player_name]["passes"] += 1

    # move ball
        self.ball_coordinates = [
        team_players[receiver]["xcor"],
        team_players[receiver]["ycor"]
    ]

        return {
            "team": team_name,
            "passer": player_name,
            "receiver": receiver,
            "ball_coordinates": self.ball_coordinates}

    """ball passed towards the ally goal this can be the team with the median amount of goals or a team with less goals"""
    def ally_pass(self):
        team_name, passer, receiver, coords = self.kickoff()
        sorted_teams = sorted(self.concessions.items(), key=lambda x: x[1])
        ally_team = sorted_teams[1][0]   # middle team

    # If ally team is same as current team, choose weakest instead
        if ally_team == team_name:
            ally_team = sorted_teams[0][0]   # lowest concessions

    # Choose a random player from ally team
        receivers_team = self.teams_dict[f"{ally_team}_team"]
        player_name = random.choice(list(receivers_team.keys()))
        player_dict = receivers_team[player_name]

    # Update passes
        player_dict["passes"] += 1

    # Move ball
        self.ball_coordinates = [player_dict["xcor"], player_dict["ycor"]]

        return {
        "new_ball_coordinates": self.ball_coordinates,
        "receiver_player": player_name,
        "receiver_team": ally_team}

        
    """when a ball crosses the goal boundary within the goal area"""
    def goal(self):
        ball_x, ball_y = self.ball_coordinates
        goal_rects = self.drawgoalstart
        goal_lines = self.field.draw_goal_lines_outside_goal()

    # Check each team's goal rectangle
        for team, rect in goal_rects.items():
        # rect = [bottom_left, top_left, top_right, bottom_right]
            xs = [p[0] for p in rect]
            ys = [p[1] for p in rect]

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

        # Check if ball is inside the rectangular goal area
            inside_goal_area = (min_x <= ball_x <= max_x) and (min_y <= ball_y <= max_y)

            if inside_goal_area:
            # Now check if ball crossed the goal line segment
                line_left, line_right = goal_lines[f"{team.split('_')[0]}_line_segment_left"], \
                                    goal_lines[f"{team.split('_')[0]}_line_segment_right"]

            
                lx1, ly1 = line_left
                lx2, ly2 = line_right

           
                crossed_line = ball_y < min(ly1, ly2) or ball_y > max(ly1, ly2)

                if crossed_line:
                    scoring_team = team.split("_")[0]
                    self.concessions[scoring_team] += 1

                    return {"goal_scored": True,"team": scoring_team,"ball_coordinates": self.ball_coordinates,"new_concessions": self.concessions}

            return {"goal_scored": False, "ball_coordinates": self.ball_coordinates}
        

    """when a ball crosses the sideline and is thrown in by the team that owns the boundary"""
    #track the ball coordinates to see if they fall outside a boundary
    #check the team and player that kicked the ball out. 
    #If the player's team color and the team that owns the boundary is the same: the throwin is awarded to the team whose boundary is the closest
    #assign a random player from the closest boundary team the throwin. Update their xcor and ycor to the ball's coordinates
    #update the ball's coordinates
    #If the player's team color and the team that own the boundary are different: the throwin is awarded to the team whose boundary it is
    #make a random player from the relevant team take the throwin. Update their xcor and ycor using the ball's coordinates
    
    #update the ball's coordinates to be somewhere random inside the polygon
    def throwin_restart(self):
        ball_x, ball_y = self.ball_coordinates

    # 1. Identify which boundary the ball crossed
        crossed_boundary = None
        for team, boundary in self.dividepitchboundaries.items():
            xs = [p[0] for p in boundary]
            ys = [p[1] for p in boundary]

            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)

        # Ball is outside this boundary polygon
            if not (min_x <= ball_x <= max_x and min_y <= ball_y <= max_y):
                crossed_boundary = team   # e.g. "red_team_boundary"
                break

            if crossed_boundary is None:
                return {"throwin": False, "reason": "Ball still inside field"}

    # Normalize team name: "red_team_boundary" → "red"
        boundary_team = crossed_boundary.split("_")[0]

    # 2. Identify who last touched the ball
        (last_team, last_player), _ = self.possession()
        last_team = last_team.split("_")[0]  # for example turn"red_team" to "red"

    # 3. Decide who gets the throw-in
        if last_team == boundary_team:
        # Same team kicked it out → throw-in goes to nearest boundary team
        # Find nearest boundary team by distance to ball
            distances = {}
            for team, boundary in self.dividepitchboundaries.items():
                bx = sum([p[0] for p in boundary]) / len(boundary)
                by = sum([p[1] for p in boundary]) / len(boundary)
                dist = math.dist((ball_x, ball_y), (bx, by))
                distances[team] = dist

            nearest_boundary = min(distances, key=distances.get)
            throwin_team = nearest_boundary.split("_")[0]

        else:
        # Different team kicked it out → throw-in awarded to boundary owner
            throwin_team = boundary_team

    # 4. Select a random player from the throw-in team
        receivers_team = self.teams_dict[f"{throwin_team}_team"]
        player_name = random.choice(list(receivers_team.keys()))
        player_dict = receivers_team[player_name]

    # 5. Update player coordinates to ball location (taking the throw-in)
        player_dict["xcor"] = ball_x
        player_dict["ycor"] = ball_y

    # 6. Move ball somewhere random inside the hexagon after throw-in
        hex_coords = self.field.hexagon()
        xs = [p[0] for p in hex_coords]
        ys = [p[1] for p in hex_coords]

        new_x = random.uniform(min(xs), max(xs))
        new_y = random.uniform(min(ys), max(ys))
        self.ball_coordinates = [new_x, new_y]

        return {
        "throwin": True,
        "awarded_to_team": throwin_team,
        "player": player_name,
        "player_new_coordinates": [player_dict["xcor"], player_dict["ycor"]],
        "ball_new_coordinates": self.ball_coordinates
    }


    
    
    """when a ball crosses the goalline outside of the goal, depending on who last touched it"""
    # If put across the line by the team that does not own the goal, play stops and a goal kick is awarded to the team who owns the goal. 
    #Play recommences from within the goal circle and opposing players must retreat 5m from the player taking the kick.
    #If deflected or kicked out of play by the team that owns the goal line, play stops and a corner kick is awarded to the team who owns the adjacent sideline to the side of the goal the ball crossed the line. 

    def goalkick_or_corner_kick(self):
    # 1. Who last touched the ball?
        (last_team, last_player), _ = self.possession()
        last_team = last_team.split("_")[0]   # for example turn red team to red

        ball_x, ball_y = self.ball_coordinates

    # 2. Get all goal line segments (both left & right per team)
        goal_lines = self.field.draw_goal_lines_outside_goal()

    # 3. Detect which goal line the ball crossed
        crossed_team = None
        crossed_segment = None

        for color in ["red", "blue", "green"]:
            segments = goal_lines[f"{color}_goal_lines"]

            for seg_info in segments:
                (x1, y1), (x2, y2) = seg_info["segment"]

            # Check if ball is beyond the y-range of the segment
                seg_min_y = min(y1, y2)
                seg_max_y = max(y1, y2)

            # Ball must be horizontally near the segment
                seg_min_x = min(x1, x2)
                seg_max_x = max(x1, x2)

                horizontally_near = seg_min_x - 1 <= ball_x <= seg_max_x + 1
                vertically_crossed = ball_y < seg_min_y or ball_y > seg_max_y

                if horizontally_near and vertically_crossed:
                    crossed_team = color
                    crossed_segment = seg_info["segment"]
                    break

            if crossed_team:
                break

        if crossed_team is None:
            return {"restart": False, "reason": "Ball has not crossed any goal line"}

    # 4. Apply the rule:
    # If last_team != crossed_team → GOAL KICK
    # If last_team == crossed_team → CORNER KICK

        if last_team != crossed_team:
        
        #           GOAL KICK
        
        # Restart from inside the goal circle (use goal rectangle midpoint)
            rect = self.drawgoalstart[f"{crossed_team}_team_goal_coords"]
            bottom_left = rect[0]
            bottom_right = rect[3]

            goal_mid_x = (bottom_left[0] + bottom_right[0]) / 2
            goal_mid_y = (bottom_left[1] + bottom_right[1]) / 2

        # Ball placed inside goal circle (2m radius)
            kick_x = goal_mid_x + random.uniform(-2, 2)
            kick_y = goal_mid_y + random.uniform(-2, 2)

            self.ball_coordinates = [kick_x, kick_y]

            return {
                "restart": "goal_kick",
                "team_awarded": crossed_team,
                "kick_location": self.ball_coordinates,
                "last_touch_team": last_team}

        else:

        #          CORNER KICK
        
        # Find boundary vertices for this team
            boundary_vertices = self.dividepitchboundaries[f"{crossed_team}_team_boundary"]

        # Find closest boundary vertex to crossing point
            distances = {
            vertex: math.dist(vertex, (ball_x, ball_y))
            for vertex in boundary_vertices
        }

            corner_vertex = min(distances, key=distances.get)

        # Kick must be taken within 1m of the corner
            kick_x = corner_vertex[0] + random.uniform(-1, 1)
            kick_y = corner_vertex[1] + random.uniform(-1, 1)

            self.ball_coordinates = [kick_x, kick_y]

            return {
            "restart": "corner_kick",
            "team_awarded": crossed_team,
            "corner_vertex": corner_vertex,
            "kick_location": self.ball_coordinates,
            "last_touch_team": last_team
        }

    """Teams collaborate against the winning team"""
    def determine_alliance(self):
        #teams sorted by values of concessions dictionary. Winning team has the fewest concessions
        sorted_teams = sorted(self.concessions.items(), key=lambda x: x[1])
        winning_team = sorted_teams[0][0] #returns (team_name, concessions) as tuple
        alliance_teams_med_concessions = sorted_teams[1][0]
        alliance_team_lowest_concessions = sorted_teams[2][0]
        return winning_team, alliance_teams_med_concessions, alliance_team_lowest_concessions

    """compute distance between closest teammate versus closest player from ally team and make a pass based on the minimum distance"""
    def compute_pass_distances(self,team_name,player_name,alliance_teams_med_concessions,alliance_team_lowest_concessions):
            px, py = self.teams_dict[team_name][player_name]["xcor"], self.teams_dict[team_name][player_name]["ycor"]

            # --- Teammates ---
            teammate_distances = {}
            for other_player, attrs in self.teams_dict[team_name].items():
                if other_player != player_name:
                    dist = math.dist((px, py), (attrs["xcor"], attrs["ycor"]))
                    teammate_distances[other_player] = dist

            closest_teammate = min(teammate_distances, key=teammate_distances.get)
            closest_teammate_dist = teammate_distances[closest_teammate]

            #--- Allies ---
            ally_distances = {}
            for ally in [alliance_teams_med_concessions,alliance_team_lowest_concessions]:
                ally_team_key = f"{ally}_team"
                for ally_player, attrs in self.teams_dict[ally_team_key].items():
                    dist = math.dist((px, py), (attrs["xcor"], attrs["ycor"]))
                    ally_distances[(ally, ally_player)] = dist

            closest_ally = min(ally_distances, key=ally_distances.get)
            closest_ally_dist = ally_distances[closest_ally]

            return (closest_teammate_dist, closest_teammate,closest_ally_dist, closest_ally)

    def decide_pass_type(self):
    # Who has possession?
        (team_name, player_name), _ = self.possession()
        team_color = team_name.split("_")[0]
    # Determine alliances
        winning_team, alliance_teams_med_concessions, alliance_teams_lowest_concessions = self.determine_alliance()
    # If possessing team is the winning team, pass within own team
        if team_color == winning_team:
            return self.passing()
    # Compute distances — unpack matches compute_pass_distances return order:
    # (closest_teammate_dist, closest_teammate, closest_ally_dist, closest_ally)
        (closest_teammate_dist, closest_teammate,closest_ally_dist, closest_ally) = self.compute_pass_distances(team_name, player_name,alliance_teams_med_concessions,alliance_teams_lowest_concessions)
    # If teammate is closer, do a normal pass; otherwise make a strategic ally pass
        if closest_teammate_dist < closest_ally_dist:
            return self.passing()
        else:
            return self.ally_pass()
    
        
    """Team Pressure by players own team not to score against ally team. Function returns betrayal probability or pressure factor depending on which is greater"""
    def apply_team_pressure(self,player_team,player_name):
        winning_team, ally1, ally2 = self.determine_alliance() #('red','blue','green')
        player_team = player_team.split("_")[0]
        # If team is NOT collaborating then no pressure applied
        if player_team == winning_team:
            return self.teams_dict[f"{player_team}_team"][player_name]["betrayal_probability"]
    
        # Pressure factor: teams with more concessions apply more pressure
        concessions = self.concessions[player_team]
        pressure_factor = self.team_pressure_probability  
        current_prob = self.teams_dict[f"{player_team}_team"][player_name]["betrayal_probability"]
        new_prob = max(current_prob,pressure_factor)
    
        # Update player probability
        self.teams_dict[f"{player_team}_team"][player_name]["betrayal_probability"] = new_prob
    
        return new_prob
    

    """Evaluate if betrayal should occur based on distance between player and winning team goal vs player and ally goal. 
    If this function returns True, then one of the teams betrays its ally. If it returns False, then no betrayal happens"""
    def evaluate_betrayal(self, player_team, player_name):
        player_team = player_team.split("_")[0]
        winning_team, ally1, ally2 = self.determine_alliance()

        if player_team == winning_team:
            return False

        ally_team = ally1 if ally2 == player_team else ally2

        px = self.teams_dict[f"{player_team}_team"][player_name]["xcor"]
        py = self.teams_dict[f"{player_team}_team"][player_name]["ycor"]

    
        ally_goal_rect = self.drawgoalstart[f"{ally_team}_team_goal_coords"]
        enemy_goal_rect = self.drawgoalstart[f"{winning_team}_team_goal_coords"]

        ally_goal_mid = ((ally_goal_rect[0][0] + ally_goal_rect[3][0]) / 2,(ally_goal_rect[0][1] + ally_goal_rect[3][1]) / 2)

        enemy_goal_mid = (
        (enemy_goal_rect[0][0] + enemy_goal_rect[3][0]) / 2,
        (enemy_goal_rect[0][1] + enemy_goal_rect[3][1]) / 2)

        dist_to_ally_goal = math.dist((px, py), ally_goal_mid)
        dist_to_enemy_goal = math.dist((px, py), enemy_goal_mid)

        betrayal_prob = self.apply_team_pressure(player_team, player_name)

        if dist_to_ally_goal < dist_to_enemy_goal and betrayal_prob > self.team_betrayal_threshold[player_team]:
            return True
        return False


    """Betrayal action"""
    def perform_betrayal(self,player_team,player_name):
        player_team = player_team.split("_")[0] #returns red, blue, or green
        winning_team, ally1, ally2 = self.determine_alliance() #('red','blue','green')
        ally_team = ally1 if ally2 == player_team else ally2

        # Player coordinates
        px = self.teams_dict[f"{player_team}_team"][player_name]["xcor"]
        py = self.teams_dict[f"{player_team}_team"][player_name]["ycor"]

        #winning team goal midpoint
        enemy_goal_rect = self.drawgoalstart[f"{winning_team}_team_goal_coords"]
        enemy_goal_mid = ((enemy_goal_rect[0][0] + enemy_goal_rect[3][0]) / 2,
                             (enemy_goal_rect[0][1] + enemy_goal_rect[3][1]) / 2)
        # Ally goal midpoint
        ally_goal_rect = self.drawgoalstart[f"{ally_team}_team_goal_coords"]
        ally_goal_mid = ((ally_goal_rect[0][0] + ally_goal_rect[3][0]) / 2,
                     (ally_goal_rect[0][1] + ally_goal_rect[3][1]) / 2)

        # Distance to ally goal and enemy goal
        dist_to_ally_goal = math.dist((px, py), ally_goal_mid)
        dist_to_enemy_goal = math.dist((px, py), enemy_goal_mid)

        # If close enough shoot at ally goal
        if dist_to_ally_goal > dist_to_enemy_goal:  # threshold can be tuned
            self.ball_coordinates = [ally_goal_mid[0], ally_goal_mid[1]]
            self.teams_dict[f"{player_team}_team"][player_name]["unsuccessfulshots"] += 1
            return {
            "betrayal": "shot_at_ally_goal",
            "player": player_name,
            "target_team": ally_team,
            "ball_coordinates": self.ball_coordinates}

        # Otherwise pass to winning team
        receivers_team = self.teams_dict[f"{winning_team}_team"]
        receiver = random.choice(list(receivers_team.keys()))
        rx = receivers_team[receiver]["xcor"]
        ry = receivers_team[receiver]["ycor"]

        self.ball_coordinates = [rx, ry]

        return {
        "betrayal": "pass_to_enemy_team",
        "player": player_name,
        "receiver": receiver,
        "receiver_team": winning_team,
        "ball_coordinates": self.ball_coordinates}

 



game = Team(num_blue=3, num_red=3, num_green=3)

team_pos = game.spawn_player_before_kickoff()
print(team_pos)

possession = game.possession()
print(possession) #(('red_team', 'Player_1'), 0.0)

kick = game.kickoff()
print(kick) #['blue_team', 'Player_2', 'Player_3', [11.5, -19.92]]

general_passing = game.passing()
print(general_passing) #{'team': 'blue_team', 'passer': 'Player_3', 'receiver': 'Player_1', 'ball_coordinates': [-11.5, 0.0]}

ally = game.ally_pass()
print(ally) #{'new_ball_coordinates': [0, -19.92], 'receiver_player': 'Player_2', 'receiver_team': 'blue'}

goal = game.goal()
print(goal) #{'goal_scored': False, 'ball_coordinates': [0, -19.92]}

throwin = game.throwin_restart() #{'throwin': False, 'reason': 'Ball still inside field'}
print(throwin)

goalkick_and_cornerkick = game.goalkick_or_corner_kick()
print(goalkick_and_cornerkick) #{'restart': 'goal_kick', 'team_awarded': 'red', 'kick_location': [16.712994202662276, 9.721805232011901], 'last_touch_team': 'blue'}

alliances = game.determine_alliance()
print(alliances)
 #('red', 'blue', 'green')
alliance = game.decide_pass_type()
print(alliance) #{'team': 'red_team', 'passer': 'Player_3', 'receiver': 'Player_2', 'ball_coordinates': [11.5, 19.92]}

betrayal_evaluation = game.evaluate_betrayal(possession[0][0], possession[0][1])
print(betrayal_evaluation)

team_pressure = game.apply_team_pressure(possession[0][0], possession[0][1])
print(team_pressure)

betrayal_action = game.perform_betrayal(possession[0][0], possession[0][1])
print(betrayal_action)