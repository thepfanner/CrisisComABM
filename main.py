import random
from Agents import *
from Crisis import *
import networkx as nx
import matplotlib.pyplot as plt


class Environment:
    """ Class for world / environment  """

    civ = []
    rs = []
    G = nx.Graph()

    def __init__(self, population_size, spread_x, spread_y, crisis_center_x,
                 crisis_center_y, crisis_strength, crisis_wave1, crisis_wave2,
                 crisis_wave3, capabilities, levels, multiple):

        self.population_size = population_size
        self.spread_x = spread_x
        self.spread_y = spread_y

        self.count_civ_message = 0

        self.cri = Crisis(crisis_center_x, crisis_center_y, crisis_strength,
                                crisis_wave1, crisis_wave2, crisis_wave3)

        for i in range(self.population_size):
            self.civ.append(Civilian(i, random.randrange(0, self.spread_x),
                                           random.randrange(0, self.spread_y), False,
                                           False, False, False, False, random.randint(40, 100)))

        # create response network
        self.capabilities = capabilities
        self.levels = levels
        self.multiple = multiple

        # list for local emergency
        self.local_em = []

        # define center
        self.rs.append(Responder(0,0,[], [1, 2, 3, 4]))

        for self.c in range(self.capabilities):
            for self.l in range(self.levels):
                if self.l == 0:
                    self.t_down = []
                    for self.t in range(self.multiple):
                        self.t_down.append(len(self.rs)+self.t+1)
                    self.rs.append(Responder(self.l, len(self.rs), [0], self.t_down, self.c))
                else:
                    for self.m in range(self.multiple**self.l):
                        self.t_down = []
                        if self.l < self.levels-1:
                            for self.t in range(self.multiple):
                                self.t_down.append(len(self.rs)+(self.multiple**self.l)-self.m+(self.multiple*self.m)+self.t)
                                self.t_up = []
                        self.rs.append(Responder(self.l, len(self.rs), self.t_up, self.t_down, self.c))

        # connection reciprocity
        for self.i in range(len(self.rs)):
            if self.rs[self.i].ties_down > 0:
                for self.j in range(len(self.rs[self.i].ties_down)):
                    self.tmp = self.rs[self.i].ties_down[self.j]
                    self.rs[self.tmp].ties_up = []
                    self.rs[self.tmp].ties_up.append(self.i)

        # define list of local emergency responders
        for self.i in range(len(self.rs)):
            if self.rs[self.i].local_em is True:
                self.local_em.append(self.rs[self.i].id)

    def draw_response_network(self):
        for self.i in range(len(self.rs)):
            self.G.add_node(self.rs[self.i].id)
            for self.j in range(len(self.rs[self.i].ties_down)):
                self.G.add_edge(self.rs[self.i].id, self.rs[self.i].ties_down[self.j])
        nx.draw(self.G)
        plt.show()

    def set_crisis(self):
        for i in range(self.population_size):
            self.civ[i].dead = self.cri.crisis_affect(0, self.civ[i].pos_x, self.civ[i].pos_y)
            self.civ[i].shelter = self.cri.crisis_affect(1, self.civ[i].pos_x, self.civ[i].pos_y)
            self.civ[i].medical = self.cri.crisis_affect(2, self.civ[i].pos_x, self.civ[i].pos_y)
            self.civ[i].food = self.cri.crisis_affect(3, self.civ[i].pos_x, self.civ[i].pos_y)

    def civilian_to_responder(self):
        for i in range(len(self.civ)):
            if self.civ[i].dead is False and random.random() < 0.99:
                if self.civ[i].shelter is True or self.civ[i].medical is True or self.civ[i].food is True:
                    # randomly choose emergency contact
                    em_contact = self.local_em[random.randint(0, len(self.local_em)-1)]

                    #share information with emergency contact - creating Information instance
                    self.rs[em_contact].information_rcvd_low.append(Information(self.civ[i].id, self.civ[i].pos_x,
                                                                       self.civ[i].pos_y, self.civ[i].shelter,
                                                                       self.civ[i].medical, self.civ[i].food, False))
                    self.rs[em_contact].new_info_rcvd = True
                    #print("Civilian %d sent information to Responder %d" % (self.civ[i].id, self.rs[em_contact].id))
                    self.count_civ_message += 1

    def responder_to_responder_up(self):
        """
        @return: organisation shares information with ties
        """
        for i in xrange(len(self.rs)-1, -1, -1):
            if self.rs[i].new_info_to_pass_up is True:
                for j in range(len(self.rs[i].ties_up)):
                    self.rs[self.rs[i].ties_up[j]].information_rcvd_low.extend(self.rs[i].information_pass_up)
                    self.rs[self.rs[i].ties_up[j]].new_info_rcvd = True
                    self.rs[i].new_info_to_pass_up = False
                    self.rs[i].information_pass_up = []
                    #print("Responder %d sent information to Responder %d" % (self.rs[i].id, self.rs[self.rs[i].ties_up[j]].id))

    def process_information(self):
        """
        @return: process information for sharing. Process received information along capacity line
        """
        for i in range(len(self.rs)):
            # check if new information available for processing
            if self.rs[i].new_info_rcvd is True and self.rs[i].id is not 0:
                for j in range(self.rs[i].process_capacity):
                    # process information given capacity constraint
                    if len(self.rs[i].information_rcvd_low) > 0:
                        self.rs[i].information_pass_up.append(self.rs[i].information_rcvd_low[0])
                        self.rs[i].information_rcvd_low.pop(0)
                        self.rs[i].new_info_to_pass_up = True
                        #print("Responder %d activated information to pass on - remaining information = %d" % (self.rs[i].id, len(self.rs[i].information_rcvd_low)))

    def update_civilian_status(self):
        for self.i in range(len(self.civ)):
            self.civ[i].update_status()



# Define size of the world and population
POPULATION_SIZE = 1000000
SPREAD_X = 600
SPREAD_Y = 300

# Define the location, strength and reach of crisis event
CRISIS_CENTER_X = 23
CRISIS_CENTER_Y = 47
CRISIS_STRENGTH = 0     # Crisis strength can be from 0 (severe) to 3 (light)
CRISIS_WAVE1 = 5
CRISIS_WAVE2 = 10
CRISIS_WAVE3 = 15

# Define response network
NETWORK_TYPE = "star"
NETWORK_SIZE = 50
CAPABILITIES = 4
LEVELS = 3
MULTIPLE = 3


STEPS = 40

env = Environment(POPULATION_SIZE, SPREAD_X, SPREAD_Y, CRISIS_CENTER_X, CRISIS_CENTER_Y,
                  CRISIS_STRENGTH, CRISIS_WAVE1, CRISIS_WAVE2, CRISIS_WAVE3, CAPABILITIES, LEVELS, MULTIPLE)

env.set_crisis()

env.civilian_to_responder()

center_message = 0
completion = 0.1
step_count = 0

while completion < 1:
    #print("")
    env.process_information()
    #print("")
    env.responder_to_responder_up()
    step_count += 1

    completion = len(env.rs[0].information_rcvd_low) / env.count_civ_message

print(step_count)
print("Start: %d -------- End: %d" % (env.count_civ_message, len(env.rs[0].information_rcvd_low)))

# for i in range(42):
#     count_dead = count_food = count_medical = count_shelter = 0
#     for j in range(len(env.civ)):
#         if env.civ[j].dead:
#             count_dead += 1
#         if env.civ[j].food:
#             count_food += 1
#         if env.civ[j].medical:
#             count_medical += 1
#         if env.civ[j].shelter:
#             count_shelter += 1
#     print("At Time %d - There are %d dead, %d homeless, %d need food and %d need medical support" % (i, count_dead, count_shelter,
#                                                                                      count_food, count_medical))
#     env.update_civilian_status()

#env.draw_response_network()
#env.add_crisis_information()



# OUTPUT TO CHECK ON FUNCTIONALITY - NO IMPORTANCE FOR PROGRAM INTEND


# for i in range(len(env.rs)):
#     print(env.rs[i].id)
#     print(env.rs[i].ties_down)
#     print(env.rs[i].ties_up)
#     print("%d - %d - %d - %d" % (env.rs[i].r_shelter, env.rs[i].r_medical, env.rs[i].r_food, env.rs[i].r_logistic))
#     print("=======================")

