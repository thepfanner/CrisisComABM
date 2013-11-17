import random
from Agents import *
from Crisis import *


class Environment:
    """ Class for world / environment  """

    civilians = []
    # local_responsers = []
    # global_responders = []

    def __init__(self, population_size, spread_x, spread_y, crisis_center_x,
                 crisis_center_y, crisis_strength, crisis_wave1, crisis_wave2,
                 crisis_wave3):
        self.population_size = population_size
        self.spread_x = spread_x
        self.spread_y = spread_y

        self.cri = Crisis(crisis_center_x, crisis_center_y, crisis_strength,
                                crisis_wave1, crisis_wave2, crisis_wave3)
        self.cri_db = []

        for i in range(self.population_size):
            self.civilians.append(Civilian(i, random.randrange(0, self.spread_x),
                                           random.randrange(0, self.spread_y), False,
                                           False, False, False, False))

    def set_crisis(self):
        for i in range(self.population_size):
            self.civilians[i].dead = self.cri.crisis_affect(0, self.civilians[i].pos_x, self.civilians[i].pos_y)
            self.civilians[i].shelter = self.cri.crisis_affect(1, self.civilians[i].pos_x, self.civilians[i].pos_y)
            self.civilians[i].medical = self.cri.crisis_affect(2, self.civilians[i].pos_x, self.civilians[i].pos_y)
            self.civilians[i].food = self.cri.crisis_affect(3, self.civilians[i].pos_x, self.civilians[i].pos_y)

    def add_crisis_information(self):
        self.cri_db.append()



# Define size of the world and population
POPULATION_SIZE = 100
SPREAD_X = 100
SPREAD_Y = 50

# Define the location, strength and reach of crisis event
CRISIS_CENTER_X = 23
CRISIS_CENTER_Y = 47
CRISIS_STRENGTH = 1     # Crisis strength can be from 0 (severe) to 3 (light)
CRISIS_WAVE1 = 5
CRISIS_WAVE2 = 10
CRISIS_WAVE3 = 15


STEPS = 10

env = Environment(POPULATION_SIZE, SPREAD_X, SPREAD_Y, CRISIS_CENTER_X, CRISIS_CENTER_Y,
                  CRISIS_STRENGTH, CRISIS_WAVE1, CRISIS_WAVE2, CRISIS_WAVE3)

env.set_crisis()



# OUTPUT TO CHECK ON FUNCTIONALITY - NO IMPORTANCE FOR PROGRAM INTEND

count_dead = 0
count_none = 0
count_food = 0
count_medical = 0
count_shelter = 0

for i in range(len(env.civilians)):
    env.civilians[i].status()

    if env.civilians[i].dead == True:
        count_dead += 1
    if env.civilians[i].food == True:
        count_food += 1
    if env.civilians[i].medical == True:
        count_medical += 1
    if env.civilians[i].shelter == True:
        count_shelter += 1

print("There are %d dead, %d homeless, %d need food and %d need medical support" % (count_dead, count_shelter,
                                                                                     count_food, count_medical))

