import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np
import os
import seaborn as sns
import matplotlib.patheffects as PathEffects
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
        self.speed = round(random.uniform(8,15),2)
        self.passes = 0
        self.unsuccessfulshots = 0
        self.goals = 0
        self.owngoals = 0
        self.posessiontime = 0.0

    

    def generate_teams(self):
        """Generate between 3 and 5 blue players for each team, based on user input."""
        
        while True:
            try:
                num = int(input("Generate 3, 4, or 5 players: "))
                if 3 <= num <= 5:
                    break
                else:
                    print("You must choose between 3 and 5 players inclusive")
            except ValueError:
                print("Please choose between 3 and 5 players inclusive")

        team = {}
        for i in range(1, num + 1):
            team[f"Player_{i}"] = {"teamcolor": self.teamcolor,"speed": self.speed,"passes": self.passes,"unsuccessfulshots":self.unsuccessfulshots,"goals": self.goals,"owngoals":self.owngoals,"posession":self.posessiontime}
        return team
    
"""Generate all 3 teams by calling the method generate_teams for the red, blue, and green team"""
blue_team = Players("blue").generate_teams()
green_team = Players("green").generate_teams()
red_team = Players("red").generate_teams()

print("blue Team:",blue_team)
print("green team:",green_team)
print("red team:",red_team)


class field():
    """Define boundaries of the field"""
    def __init__(self):
        self.diameter = 40
        self.centretocorner = (self.diameter)//2
        self.sidelength = 23
        self.numsides = 6
        self.goalheight = 2
        self.goalwidth = 3
        self.centre = (0,0)

    def hexagon(self):
        """"This method returns the xy coordinates of the regular hexagon consisting of 6 equilateral triangles"""
        """"Compute all angles in radians because math.cos() and math.sin() return radians"""
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
        #plt.hexbin()
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
        left_red_goal_xycoord = [redgoalxcoord - 1.5, redgoalycoord]
        right_red_goal_xycoord = [redgoalxcoord + 1.5, redgoalycoord]
        top_left_red_goal_xycoord = [redgoalxcoord+1.5,redgoalycoord+2]
        top_right_red_goal_xycoord = [redgoalxcoord-1.5,redgoalycoord+2]
        """Now obtain the 4 coordinates required to draw the rectangle of the blue goal"""
        left_blue_goal_xycoord = [bluegoalxcoord - 1.5, bluegoalycoord]
        right_blue_goal_xycoord = [bluegoalxcoord + 1.5, bluegoalycoord]
        top_left_blue_goal_xycoord = [bluegoalxcoord+1.5,bluegoalycoord+2]
        top_right_blue_goal_xycoord = [bluegoalxcoord-1.5,bluegoalycoord+2]
        """Now obtain the 4 coordinates required to draw the rectangle of the green goal"""
        left_green_goal_xycoord = [greengoalxcoord - 1.5, greengoalycoord]
        right_green_goal_xycoord = [greengoalxcoord + 1.5, greengoalycoord]
        top_left_green_goal_xycoord = [greengoalxcoord+1.5,greengoalycoord+2]
        top_right_green_goal_xycoord = [greengoalxcoord-1.5,greengoalycoord+2]
        return {"red_team_goal_coords":[left_red_goal_xycoord,top_left_red_goal_xycoord,top_right_red_goal_xycoord,right_red_goal_xycoord],
                "blue_team_goal_coords":[left_blue_goal_xycoord,top_left_blue_goal_xycoord,top_right_blue_goal_xycoord,right_blue_goal_xycoord],
                "green_team_goal_coords":[left_green_goal_xycoord ,top_left_green_goal_xycoord,top_right_green_goal_xycoord,right_green_goal_xycoord]}
    


    """Define possession for all 3 teams"""    
    def possession(self):
        pass
    """Define rules for corners"""
    def corners(self):
        pass
    """Define rules for throwins"""
    def throwin(self):
        pass
           
create_polygon = field().hexagon()
dividepitchforteams = field().dividepitchpossession()
dividepitchboundaries = field().dividepitchboundaries()
drawgoalstart = field().drawgoalstart()


print(create_polygon)
print(dividepitchforteams)
print(dividepitchboundaries)
print(drawgoalstart)

"""Demarkate the field into red, green, blue zones"""
"""Teams start within their third of the pitch:
Incorporate the triangle whose sides are measured from centre to corner as limits for player movement"""
 
        