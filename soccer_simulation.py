import math
import random
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
        self.baseline = 40
        self.centretobaseline = (self.baseline)//2
        self.centretocorner = 23
        self.goalheight = 2
        self.goalwidth = 3
        self.distancefromgoaltocentre = 20

        def goalscoring(self):
            pass

"""Demarkate the field into red, green, blue zones"""
"""Teams start within their third of the pitch:
Incorporate the triangle whose sides are measured from centre to corner as limits for player movement"""
            
        