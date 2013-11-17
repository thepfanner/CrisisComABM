import numpy as np
import random


class Crisis:
    """ Crisis event - defines the crisis event and calculates the affect on world """
    def __init__(self, center_x, center_y, strength, wave1, wave2, wave3):
        self.center_x = center_x
        self.center_y = center_y
        self.strength = strength
        self.wave1 = wave1
        self.wave2 = wave2
        self.wave3 = wave3

        self.wave1_range_x = range(self.center_x - self.wave1, self.center_x + self.wave1)
        self.wave1_range_y = range(self.center_y - self.wave1, self.center_y + self.wave1)
        self.wave2_range_x = range(self.center_x - self.wave1 - self.wave2,
                                   self.center_x + self.wave1 + self.wave2)
        self.wave2_range_y = range(self.center_y - self.wave1 - self.wave2,
                                   self.center_y + self.wave1 + self.wave2)
        self.wave3_range_x = range(self.center_x - self.wave1 - self.wave2 - self.wave3,
                                   self.center_x + self.wave1 + self.wave2 + self.wave3)
        self.wave3_range_y = range(self.center_y - self.wave1 - self.wave2 - self.wave3,
                                   self.center_y + self.wave1 + self.wave2 + self.wave3)

        self.prob = np.array([[[0.9, 0.8, 0.7], [0.5, 0.25, 0.1], [0.2, 0.05, 0.001]],     # Probability for being alive
                              [[0.8, 0.6, 0.5], [0.5, 0.4, 0.3], [0.3, 0.2, 0.05]],        # Probability for having shelter
                              [[0.8, 0.65, 0.55], [0.4, 0.2, 0.2], [0.2, 0.1, 0.01]],      # Probability for needing medical support
                              [[0.85, 0.5, 0.45], [0.7, 0.5, 0.3], [0.3, 0.2, 0.1]]])      # Probability for having food

    def crisis_affect(self, type, pos_x, pos_y):
        luck = random.random()

        if pos_x in self.wave1_range_x and pos_y in self.wave1_range_y:
            if luck <= self.prob[type][self.strength][0]:
               return True
            else:
                return False
        elif pos_x in self.wave2_range_x and pos_y in self.wave2_range_y:
            if luck <= self.prob[type][self.strength][1]:
                return True
            else:
                return False
        elif pos_x in self.wave3_range_x and pos_y in self.wave3_range_y:
            if luck <= self.prob[type][self.strength][2]:
                return True
            else:
                return False
        else:
            return False


class CrisisInformation:
    """ Class for crisis information at a specific geographic location  """
    def __init__(self):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dead = dead
        self.shelter = shelter
        self.food = food
        self.medical = medical
        self.sources = []