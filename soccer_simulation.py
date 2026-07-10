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


class field(Players):
    """Define boundaries of the field"""
    def __init__(self):
        self.diameter = 40
        self.centretocorner = (self.diameter)//2
        self.sidelength = 23
        self.numsides = 6
        self.goalheight = 2
        self.goalwidth = 3
        self.centre = [0,0]

    def hexagon(self):
        """"Compute all angles in radians because math.cos() and math.sin() return radians"""
        #convert 60 degrees to radians
        angle = (360 / self.numsides) * (math.pi / 180)
        #polygoncoordinates stores the cartesian coordinates of the hexagon
        polygoncoordinates = []
        for i in range(0,self.sidelength):
            x = polygoncoordinates[0] + self.sidelength * math.cos(angle*i)
            y = polygoncoordinates[1] + self.sidelength * math.sin(angle*i)
            polygoncoordinates.append((x,y))
        return polygoncoordinates
    

    def dividepitch(self):
        coordinates = self.hexagon()
        return {"red_team" : [self.centre, coordinates[0],coordinates[1],coordinates[2]],
         "blue_team" : [self.centre, coordinates[3],coordinates[4],coordinates[5]],
         "green_team" : [self.centre, coordinates[7],coordinates[8],coordinates[9]]}
        #plt.hexbin()
        #[[-11.5,-20],[-11.5,20],[11.5,-20],[11.5,20],[23,0],]

    """Return the rectangle that is the goal"""
    def goal(self):
        goalarea = self.goalheight * self.goalwidth 
        return goalarea
    
    def goalscoring(self):
        pass
    
    """Define possession for all 3 teams"""    
    def possession(self):
        pass
    """Define rules for corners"""
    def corners(self):
        pass
    """Define rules for throwins"""
    def throwin(self):
        pass
           

"""Demarkate the field into red, green, blue zones"""
"""Teams start within their third of the pitch:
Incorporate the triangle whose sides are measured from centre to corner as limits for player movement"""
 
        