import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np
import os
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

        

      


            

        

            


create_polygon = field().hexagon()
print(create_polygon)
dividepitchforteams = field().dividepitchpossession()
print(dividepitchforteams)
dividepitchboundaries = field().dividepitchboundaries()
print(dividepitchboundaries)
drawgoalstart = field().drawgoalstart()
print(drawgoalstart)

"""
Each team must consist of a minimum of 3 players and a maximum of 5 players
create a dictionary where each players team is assigned to them
Every time the game is initialized, there must be a minimum of 3 players and the user
has the option to choose between 3-5 players
"""

class Players():
    """Define attributes of players"""
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

    def _make_team(self, color, num_players):
        if not 3 <= num_players <= 5:
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
#blue_team = Players("blue").generate_teams()
#green_team = Players("green").generate_teams()
#red_team = Players("red").generate_teams()


#print("blue Team:",blue_team)
#print("green team:",green_team)
#print("red team:",red_team)


"""Demarkate the field into red, green, blue zones"""
"""Teams start within their third of the pitch:
Incorporate the triangle whose sides are measured from centre to corner as limits for player movement"""
 

class Simulation():
    def __init__(self, num_blue=3, num_red=3, num_green=3):
        self.field = field()
        self.dividepitchforteams = self.field.dividepitchpossession()
        self.dividepitchboundaries = self.field.dividepitchboundaries()
        self.drawgoalstart = self.field.drawgoalstart()

        self.Players = Players()
        self.blueplayers = self.Players._make_team("blue", num_blue)
        self.redplayers = self.Players._make_team("red", num_red)
        self.greenplayers = self.Players_make_team("green", num_green)

        self.teams_dict = {
            "blue": self.blueplayers,
            "red": self.redplayers,
            "green": self.greenplayers
        }

        self.ball_coordinates = [0.0, 0.0]
        self.last_touch = None
        self.concessions = {"red": 0, "blue": 0, "green": 0}
        self.leading_team = min(self.concessions, key=self.concessions.get)
        self.leading_team_goals = self.concessions[self.leading_team]

    def _make_team(self, color, num_players):
        if not 3 <= num_players <= 5:
            raise ValueError("Each team must have 3 to 5 players.")
        team = {}
        for i in range(1, num_players + 1):
            player_template = Players(color)
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



    def ally_team(self,betraying_team):
        other_teams = [t for t in ["red", "blue", "green"] if t != betraying_team]
        return min(other_teams,key=lambda t:self.concessions[t])
    
    def spawn_player_before_kickoff(self):
        for team in ["red", "blue", "green"]:
            area = self.dividepitchforteams[f"{team}_team_area"]
            xcoords = [x[0] for x in area]
            ycoords = [y[1] for y in area]
            for player in self.teams_dict[team]:
                self.teams_dict[team][player]["xcor"] = random.choice(xcoords)
                self.teams_dict[team][player]["ycor"] = random.choice(ycoords)
        self.ball_coordinates = [0,0]
        self.last_touch = None
        return self.teams_dict
    
    """Iterates through coordinates to find the player index closest to self.ball_coordinates()."""
    """Returns the shortest distance between ball and goal, team and player index of the player closest to the ball. The player that kicked the ball"""
    def get_player_with_ball(self):
        distances = []
        for team, players in self.teams_dict.items():
            for player, attributes in players.items():
                if attributes["xcor"] is None or attributes["ycor"] is None:
                    continue
                dist = math.dist((attributes["xcor"], attributes["ycor"]), tuple(self.ball_coordinates))
                distances.append([dist, team, player])

        if not distances:
            return None

        distances.sort(key=lambda x: x[0])
        return distances[0]
    
    def closest_goal_team(self, ball_coordinates):
        distance_between_ball_and_goal = []
        for team, goal_coords in self.drawgoalstart.items():
            xcoords = [x[0] for x in goal_coords]
            ycoords = [y[1] for y in goal_coords]
            midpoint_x = sum(xcoords) / len(xcoords)
            midpoint_y = sum(ycoords) / len(ycoords)
            dist = math.dist((midpoint_x, midpoint_y), (ball_coordinates[0], ball_coordinates[1]))
            distance_between_ball_and_goal.append((dist, team))

        shortest_dist_dict = sorted(distance_between_ball_and_goal, key=lambda x: x[0])
        return shortest_dist_dict[0][1].split("_")[0]

    def _point_on_segment(self, p, a, b, eps=1e-6):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        if (min(x1, x2) - eps <= x <= max(x1, x2) + eps) and (min(y1, y2) - eps <= y <= max(y1, y2) + eps):
            cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
            return abs(cross) <= eps
        return False
    
    def _point_in_polygon(self, point, polygon):
        x, y = point
        inside = False
        n = len(polygon)
        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            if self._point_on_segment(point, (x1, y1), (x2, y2)):
                return True
            if ((y1 > y) != (y2 > y)):
                xinters = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1
                if xinters > x:
                    inside = not inside
        return inside
    
    def _boundary_from_point(self, point):
        for goal_key, goal_coords in self.drawgoalstart.items():
            if self._point_in_polygon(point, goal_coords):
                return goal_key, goal_key.split("_")[0], "goal"

        for boundary_key, boundary_coords in self.dividepitchboundaries.items():
            if self._point_in_polygon(point, boundary_coords):
                return boundary_key, boundary_key.split("_")[0], "boundary"

        return None, None, None

    
    def get_boundary_owner(self, boundary):
        if isinstance(boundary, str) and boundary in self.dividepitchboundaries:
            return boundary.split("_")[0]
        if isinstance(boundary, (list, tuple)) and len(boundary) == 2:
            _, owner, _ = self._boundary_from_point(tuple(boundary))
            return owner if owner is not None else "unknown"
        return "unknown"
    


        

    def kick_ball_at_ally_goal(self, betraying_team):
        target_team = self.ally_team(betraying_team)
        target_team_goal = self.drawgoalstart[f"{target_team}_team_goal_coords"]
        xcoords = [x[0] for x in target_team_goal]
        ycoords = [y[1] for y in target_team_goal]
        return random.choice(xcoords), random.choice(ycoords)


    def kickoff(self):
        self.spawn_player_before_kickoff()
        team = random.choice(["red", "blue", "green"])
        passer = random.choice(list(self.teams_dict[team].keys()))
        receiver = random.choice([p for p in self.teams_dict[team].keys() if p != passer])

        self.teams_dict[team][passer]["passes"] += 1
        self.last_touch = (team, passer)
        self.ball_coordinates = [
            self.teams_dict[team][receiver]["xcor"],
            self.teams_dict[team][receiver]["ycor"]
        ]
        return team, passer, receiver, tuple(self.ball_coordinates)

    def determine_restart(self, point):
        boundary_key, owner, kind = self._boundary_from_point(point)

        if kind == "goal":
            return {
                "type": "goal",
                "award_to": owner,
                "location": tuple(point)
            }

        if kind == "boundary":
            if self.last_touch is None:
                return {
                    "type": "throwin",
                    "award_to": owner,
                    "location": tuple(point)
                }

            last_team = self.last_touch[0]

            if last_team != owner:
                return {
                    "type": "throwin",
                    "award_to": owner,
                    "location": tuple(point)
                }

            return {
                "type": "throwin",
                "award_to": self.closest_goal_team(point),
                "location": tuple(point)
            }

        return {
            "type": "unknown",
            "award_to": None,
            "location": tuple(point)
        }
    
    def goalscoring(self):
        player_info = self.get_player_with_ball()
        if player_info is None:
            return {"type": "no_player"}

        shortest_distance, scoring_team, scoring_player = player_info
        if shortest_distance > 1.5:
            self.teams_dict[scoring_team][scoring_player]["unsuccessfulshots"] += 1
            return {"type": "no_goal", "reason": "too_far"}

        losing_team = self.closest_goal_team(self.ball_coordinates)

        if losing_team == scoring_team:
            self.teams_dict[scoring_team][scoring_player]["owngoals"] += 1
            event_type = "own_goal"
        else:
            self.teams_dict[scoring_team][scoring_player]["goals"] += 1
            event_type = "goal"

        self.concessions[losing_team] += 1
        self.leading_team = min(self.concessions, key=self.concessions.get)
        self.leading_team_goals = self.concessions[self.leading_team]

        return {
            "type": event_type,
            "scoring_team": scoring_team,
            "scorer": scoring_player,
            "conceded_by": losing_team
        }

    def pass_event(self):
        player_info = self.get_player_with_ball()
        if player_info is None:
            return {"type": "no_possessor"}

        _, team, player = player_info
        player_data = self.teams_dict[team][player]

        if player_data["is_betray"]:
            new_x, new_y = self.kick_ball_at_ally_goal(team)
            self.last_touch = (team, player)
            self.ball_coordinates = [new_x, new_y]
            return {"type": "betray_pass", "from": (team, player), "ball": tuple(self.ball_coordinates)}

        teammates = [p for p in self.teams_dict[team].keys() if p != player]
        if not teammates:
            return {"type": "no_teammates"}

        receiver = random.choice(teammates)
        self.teams_dict[team][player]["passes"] += 1
        self.last_touch = (team, player)
        self.ball_coordinates = [
            self.teams_dict[team][receiver]["xcor"],
            self.teams_dict[team][receiver]["ycor"]
        ]
        return {"type": "pass", "from": (team, player), "to": (team, receiver), "ball": tuple(self.ball_coordinates)}

    def step(self):
        event = self.pass_event()
        boundary_key, owner, kind = self._boundary_from_point(tuple(self.ball_coordinates))

        if kind == "goal":
            return {"event": "goal", "result": self.goalscoring()}

        if kind == "boundary":
            restart = self.determine_restart(tuple(self.ball_coordinates))
            return {"event": "out_of_play", "boundary": boundary_key, "restart": restart, "last_event": event}

        return {"event": "in_play", "detail": event}

               
            
            

import unittest
from soccer_simulation import Simulation, Players, field

class TestGameFlow(unittest.TestCase):
    
    def setUp(self):
        self.sim = Simulation(num_blue=3, num_red=3, num_green=3)
    
    def test_kickoff_starts_game(self):
        """Test that kickoff initializes the game"""
        team, passer, receiver, ball_pos = self.sim.kickoff()
        self.assertIn(team, ["red", "blue", "green"])
        self.assertIsNotNone(ball_pos)
        self.assertEqual(len(ball_pos), 2)
    
    def test_step_returns_valid_event(self):
        """Test that step() produces valid game events"""
        self.sim.kickoff()
        for _ in range(5):
            result = self.sim.step()
            self.assertIn("event", result)
            self.assertIn(result["event"], ["in_play", "out_of_play", "goal"])
    
    def test_goal_increments_concessions(self):
        """Test that goals are recorded"""
        self.sim.kickoff()
        initial_concessions = self.sim.concessions.copy()
        result = self.sim.goalscoring()
        if result["type"] in ["goal", "own_goal"]:
            self.assertGreater(sum(self.sim.concessions.values()), sum(initial_concessions.values()))

if __name__ == "__main__":
    unittest.main()            
        