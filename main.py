import random
from Agents import *
from Crisis import *
from classes import *
import networkx as nx
import matplotlib.pyplot as plt
import math


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

        self.count_civ_message_total = self.count_civ_message_shelter = self.count_civ_message_medical = \
            self.count_civ_message_food = 0

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
        self.rs.append(Responder(0, 0, [], []))

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

        self.connection_reciprocity()
        self.connection_reciprocity_center()

        # define list of local emergency responders
        for self.i in range(len(self.rs)):
            if self.rs[self.i].local_em is True:
                self.local_em.append(self.rs[self.i].id)

        self.responder_location()

    # Method to compute and set the locations a responding agent can deploy its resources. Range is square and the
    # deploy_position.x and deploy_position.y of a responder indicate the top left corner. 
    # Full Range: deploy_position.x - deploy_position.x + range /// deploy_position.y - deploy_position.y + range

    def responder_location(self):
        count_shelter = count_medical = count_food = count_logistics = 0

        for i in range(len(self.rs)):
            if self.rs[i].level == self.levels-1:
                if self.rs[i].c_shelter is True:
                    count_shelter += 1
                if self.rs[i].c_medical is True:
                    count_medical += 1
                if self.rs[i].c_food is True:
                    count_food += 1
                if self.rs[i].c_logistic is True:
                    count_logistics += 1

        size_shelter = math.ceil(math.sqrt((self.spread_x * self.spread_y) / count_shelter))
        size_medical = math.ceil(math.sqrt((self.spread_x * self.spread_y) / count_medical))
        size_food = math.ceil(math.sqrt((self.spread_x * self.spread_y) / count_food))
        size_logistics = math.ceil(math.sqrt((self.spread_x * self.spread_y) / count_logistics))

        shelter_x = shelter_y = medical_x = medical_y = food_x = food_y = logistic_x = logistic_y = 0

        for i in range(len(self.rs)):
            if self.rs[i].level == self.levels-1 and self.rs[i].c_shelter is True:
                if shelter_x < self.spread_x:
                    self.rs[i].deploy_position.x = shelter_x
                    self.rs[i].deploy_position.y = shelter_y
                    self.rs[i].deploy_range = size_shelter
                    shelter_x += size_shelter
                else:
                    shelter_y += size_shelter
                    self.rs[i].deploy_position.x = 0
                    self.rs[i].deploy_position.y = shelter_y
                    self.rs[i].deploy_range = size_shelter
                    shelter_x = size_shelter
            if self.rs[i].level == self.levels-1 and self.rs[i].c_medical is True:
                if medical_x < self.spread_x:
                    self.rs[i].deploy_position.x = medical_x
                    self.rs[i].deploy_position.y = medical_y
                    self.rs[i].deploy_range = size_medical
                    medical_x += size_medical
                else:
                    medical_y += size_medical
                    self.rs[i].deploy_position.x = 0
                    self.rs[i].deploy_position.y = medical_y
                    self.rs[i].deploy_range = size_medical
                    medical_x = size_medical

            if self.rs[i].level == self.levels-1 and self.rs[i].c_food is True:
                if food_x < self.spread_x:
                    self.rs[i].deploy_position.x = food_x
                    self.rs[i].deploy_position.y = food_y
                    self.rs[i].deploy_range = size_food
                    food_x += size_food
                else:
                    food_y += size_food
                    self.rs[i].deploy_position.x = 0
                    self.rs[i].deploy_position.y = food_y
                    self.rs[i].deploy_range = size_food
                    food_x = size_food

            if self.rs[i].level == self.levels-1 and self.rs[i].c_logistic is True:
                if logistic_x < self.spread_x:
                    self.rs[i].deploy_position.x = logistic_x
                    self.rs[i].deploy_position.y = logistic_y
                    self.rs[i].deploy_range = size_logistics
                    logistic_x += size_logistics
                else:
                    logistic_y += size_logistics
                    self.rs[i].deploy_position.x = 0
                    self.rs[i].deploy_position.y = logistic_y
                    self.rs[i].deploy_range = size_logistics
                    logistic_x = size_logistics


    def connection_reciprocity(self):
        for i in range(len(self.rs)):
            if len(self.rs[i].ties_down) > 0:
                for j in range(len(self.rs[i].ties_down)):
                    tmp = self.rs[i].ties_down[j]
                    self.rs[tmp].ties_up = []
                    self.rs[tmp].ties_up.append(i)

    def connection_reciprocity_center(self):
        tmp_list = []
        for z in range(len(self.rs)):
            if len(self.rs[z].ties_up) > 0:
                for j in range(len(self.rs[z].ties_up)):
                    if self.rs[z].ties_up[j] == 0:
                        tmp_list.append(self.rs[z].id)
        self.rs[0].ties_down.extend(tmp_list)

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

    # ###########################################
    # Methods FOR FULL INFORMATION SHARING
    #
    #
    def civilian_to_responder_full(self):
        for i in range(len(self.civ)):
            if self.civ[i].dead is False and random.random() < 0.99:
                if self.civ[i].shelter is True or self.civ[i].medical is True or self.civ[i].food is True:
                    # randomly choose emergency contact
                    em_contact = self.local_em[random.randint(0, len(self.local_em)-1)]

                    #share information with emergency contact - creating Information instance
                    self.rs[em_contact].information_rcvd_low.append(Information(self.civ[i].id, self.civ[i].pos_x,
                                                                       self.civ[i].pos_y, self.civ[i].shelter,
                                                                       self.civ[i].medical, self.civ[i].food, False))
                    self.rs[em_contact].new_info_rcvd_low = True
                    #print("Civilian %d sent information to Responder %d" % (self.civ[i].id, self.rs[em_contact].id))
                    #if self.civ[i].shelter:
                    #    self.count_civ_message_shelter += 1
                    #if self.civ[i].food:
                    #    self.count_civ_message_food += 1
                    #if self.civ[i].medical:
                    #    self.count_civ_message_medical += 1

                    self.count_civ_message_total += 1

    def responder_to_responder_full(self):
        """
        @return: organisation shares information with ties
        """
        for i in xrange(len(self.rs)-1, -1, -1):
            if self.rs[i].new_info_to_pass_up is True:
                for j in range(len(self.rs[i].ties_up)):
                    self.rs[self.rs[i].ties_up[j]].information_rcvd_low.extend(self.rs[i].information_pass_up)
                    self.rs[self.rs[i].ties_up[j]].new_info_rcvd_low = True
                    self.rs[i].new_info_to_pass_up = False
                    #print("UP: Responder %d sent information to Responder %d" % (self.rs[i].id, self.rs[self.rs[i].ties_up[j]].id))
                self.rs[i].information_pass_up = []

            if self.rs[i].new_info_to_pass_down is True:
                for j in range(len(self.rs[i].ties_down)):
                    self.rs[self.rs[i].ties_down[j]].information_rcvd_high.extend(self.rs[i].information_pass_down)
                    self.rs[self.rs[i].ties_down[j]].new_info_rcvd_high = True
                    self.rs[i].new_info_to_pass_down = False
                    #print("DOWN: Responder %d sent information to Responder %d" % (self.rs[i].id, self.rs[self.rs[i].ties_down[j]].id))
                self.rs[i].information_pass_down = []

    def process_information_full(self):
        """
        @return: process information for sharing. Process received information constrained by capacity
        """
        for i in range(len(self.rs)):
            # check if new information available for processing upstream
            if self.rs[i].new_info_rcvd_low is True:
                if self.rs[i].id is 0:
                    for j in range(self.rs[i].process_capacity):
                        if len(self.rs[i].information_rcvd_low) > 0:
                            #print("I %d processed information for passing down" % (self.rs[i].id))
                            self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_low[0])
                            self.rs[i].information_rcvd_low.pop(0)
                            self.rs[i].new_info_to_pass_down = True
                            self.rs[i].count_incoming_low += 1
                    if len(self.rs[i].information_rcvd_low) == 0:
                        self.rs[i].new_info_rcvd_low = False
                else:
                    for j in range(self.rs[i].process_capacity):
                        # process information given capacity constraint
                        if len(self.rs[i].information_rcvd_low) > 0:
                            self.rs[i].information_pass_up.append(self.rs[i].information_rcvd_low[0])
                            self.rs[i].information_rcvd_low.pop(0)
                            self.rs[i].new_info_to_pass_up = True
                            if len(self.rs[i].information_rcvd_low) is 0:
                                self.rs[i].new_info_rcvd_low = False
                        #print("Responder %d activated information to pass on - remaining information = %d" % (self.rs[i].id, len(self.rs[i].information_rcvd_low)))

            # process information for sending to lower level ties
            if self.rs[i].new_info_rcvd_high is True and self.rs[i].level is not self.levels-1:
                for j in range(self.rs[i].process_capacity):
                    if len(self.rs[i].information_rcvd_high) > 0:
                        self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_high[0])
                        self.rs[i].information_rcvd_high.pop(0)
                        self.rs[i].new_info_to_pass_down = True
                    elif len(self.rs[i].information_rcvd_high) == 0:
                        self.rs[i].new_info_rcvd_high = False

    # ############################################
    # METHODS FOR SELECTIVE INFORMATION SHARING
    #
    #
    def civilian_to_responder_selective(self):
        for i in range(len(self.civ)):
            if self.civ[i].dead is False and random.random() < 0.99:
                if self.civ[i].shelter is True or self.civ[i].medical is True or self.civ[i].food is True:
                    # randomly choose emergency contact
                    em_contact = self.local_em[random.randint(0, len(self.local_em)-1)]

                    #share information with emergency contact - creating Information instance
                    self.rs[em_contact].information_rcvd_low.append(Information(self.civ[i].id, self.civ[i].pos_x,
                                                                       self.civ[i].pos_y, self.civ[i].shelter,
                                                                       self.civ[i].medical, self.civ[i].food, False))
                    self.rs[em_contact].new_info_rcvd_low = True
                    print("Civilian %d sent information to Responder %d ----- Needs Shelter %r - Medical %r - Food %r" % (self.civ[i].id, self.rs[em_contact].id, self.civ[i].shelter, self.civ[i].medical, self.civ[i].food))
                    if self.civ[i].shelter:
                        self.count_civ_message_shelter += 1
                    if self.civ[i].food:
                        self.count_civ_message_food += 1
                    if self.civ[i].medical:
                        self.count_civ_message_medical += 1

    def process_information_selective(self):
        """
        @return: process information for sharing. Process received information constrained by capacity
        """
        for i in range(len(self.rs)):
            # check if new information available for processing upstream
            if self.rs[i].new_info_rcvd_low is True:
                if self.rs[i].id is 0:
                    for j in range(self.rs[i].process_capacity):
                        if len(self.rs[i].information_rcvd_low) > 0:
                            #print("I %d processed information for passing down" % (self.rs[i].id))
                            self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_low[0])
                            self.rs[i].information_rcvd_low.pop(0)
                            self.rs[i].new_info_to_pass_down = True
                            self.rs[i].count_incoming_low += 1
                    if len(self.rs[i].information_rcvd_low) == 0:
                        self.rs[i].new_info_rcvd_low = False
                else:
                    for j in range(self.rs[i].process_capacity):
                        # process information given capacity constraint
                        if len(self.rs[i].information_rcvd_low) > 0:
                            self.rs[i].information_pass_up.append(self.rs[i].information_rcvd_low[0])
                            self.rs[i].information_rcvd_low.pop(0)
                            self.rs[i].new_info_to_pass_up = True
                            if len(self.rs[i].information_rcvd_low) is 0:
                                self.rs[i].new_info_rcvd_low = False
                        #print("Responder %d activated information to pass on - remaining information = %d" % (self.rs[i].id, len(self.rs[i].information_rcvd_low)))

            # process information for sending to lower level ties
            if self.rs[i].new_info_rcvd_high is True and self.rs[i].level is not self.levels-1:
                for j in range(self.rs[i].process_capacity):
                    if len(self.rs[i].information_rcvd_high) > 0:
                        self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_high[0])
                        self.rs[i].information_rcvd_high.pop(0)
                        self.rs[i].new_info_to_pass_down = True
                    elif len(self.rs[i].information_rcvd_high) == 0:
                        self.rs[i].new_info_rcvd_high = False

    def responder_to_responder_selective(self):
        """
        @return: organisation shares information with ties
        """
        for i in xrange(len(self.rs)-1, -1, -1):
            if self.rs[i].new_info_to_pass_up is True:
                for j in range(len(self.rs[i].ties_up)):
                    self.rs[self.rs[i].ties_up[j]].information_rcvd_low.extend(self.rs[i].information_pass_up)
                    self.rs[self.rs[i].ties_up[j]].new_info_rcvd_low = True
                    self.rs[i].new_info_to_pass_up = False
                    #print("UP: Responder %d sent information to Responder %d" % (self.rs[i].id, self.rs[self.rs[i].ties_up[j]].id))
                self.rs[i].information_pass_up = []

            if self.rs[i].new_info_to_pass_down is True:
                for j in range(len(self.rs[i].ties_down)):
                    for k in range(len(self.rs[i].information_pass_down)):
                        if self.rs[self.rs[i].ties_down[j]].c is 0 and self.rs[i].information_pass_down[k].shelter is True:
                            self.rs[self.rs[i].ties_down[j]].information_rcvd_high.append(self.rs[i].information_pass_down[k])
                            self.rs[self.rs[i].ties_down[j]].new_info_rcvd_high = True
                            self.rs[i].new_info_to_pass_down = False
                        if self.rs[self.rs[i].ties_down[j]].c is 1 and self.rs[i].information_pass_down[k].medical is True:
                            self.rs[self.rs[i].ties_down[j]].information_rcvd_high.append(self.rs[i].information_pass_down[k])
                            self.rs[self.rs[i].ties_down[j]].new_info_rcvd_high = True
                            self.rs[i].new_info_to_pass_down = False
                        if self.rs[self.rs[i].ties_down[j]].c is 2 and self.rs[i].information_pass_down[k].food is True:
                            self.rs[self.rs[i].ties_down[j]].information_rcvd_high.append(self.rs[i].information_pass_down[k])
                            self.rs[self.rs[i].ties_down[j]].new_info_rcvd_high = True
                            self.rs[i].new_info_to_pass_down = False
                        if self.rs[self.rs[i].ties_down[j]].c is 3 and self.rs[i].information_pass_down[k].logistics is True:
                            self.rs[self.rs[i].ties_down[j]].information_rcvd_high.append(self.rs[i].information_pass_down[k])
                            self.rs[self.rs[i].ties_down[j]].new_info_rcvd_high = True
                            self.rs[i].new_info_to_pass_down = False
                    print("DOWN: Responder %d sent information to Responder %d" % (self.rs[i].id, self.rs[self.rs[i].ties_down[j]].id))
                self.rs[i].information_pass_down = []

    def update_civilian_status(self):
        for self.i in range(len(self.civ)):
            self.civ[self.i].update_status()


def selective_information_diffusion():
    """
    Function for selective information diffusion:
    Simulation Model is active, until organisations with relevant capabilities have received information!
    """

    step_count = 0
    check = False

    while check is False:
        env.process_information_selective()
        env.responder_to_responder_selective()
        step_count += 1

        check = True

        for i in range(len(env.rs)):
            if env.rs[i].level == LEVELS-1:
                if env.rs[i].c == 0 and len(env.rs[i].information_rcvd_high) == env.count_civ_message_shelter:
                    print("Civ_Shelter: %d ----- Responder %d has info on shelter %d" % (env.count_civ_message_shelter, env.rs[i].id, len(env.rs[i].information_rcvd_high)))
                elif env.rs[i].c == 1 and len(env.rs[i].information_rcvd_high) == env.count_civ_message_medical:
                    pass
                    print("Civ_Medical: %d ----- Responder %d has info on medical %d" % (env.count_civ_message_medical, env.rs[i].id, len(env.rs[i].information_rcvd_high)))
                elif env.rs[i].c == 2 and len(env.rs[i].information_rcvd_high) == env.count_civ_message_food:
                    pass
                    print("Civ_Food: %d ----- Responder %d has info on food %d" % (env.count_civ_message_food, env.rs[i].id, len(env.rs[i].information_rcvd_high)))
                elif env.rs[i].c == 3:
                    pass
                else:
                    check = False

        print(step_count)


def full_information_diffusion():
    """
    Function for full information diffusion:
    Simulation Model is active, until all organising agencies in the network have the same information!

    """

    step_count = 0                              # steps needed for full diffusion of information
    check = False

    while check is False:
        env.process_information_full()               # responding organisations process information
        env.responder_to_responder_full()           # responding organisations share information
        step_count += 1

        check = True

        for i in range(len(env.rs)):
            if env.rs[i].level == LEVELS-1:
                if env.count_civ_message_total == len(env.rs[i].information_rcvd_high):
                    pass
                else:
                    check = False

    print("Steps needed for full information diffusion: %d" % step_count)
    print(" CHECKSUM: Start: %d -------- End: %d" % (env.count_civ_message_total, env.rs[0].count_incoming_low))


# Define size of the world and population
POPULATION_SIZE = 1000
SPREAD_X = 600
SPREAD_Y = 300

# Define the location, strength and reach of crisis event
CRISIS_CENTER_X = random.randint(0, SPREAD_X)
CRISIS_CENTER_Y = random.randint(0, SPREAD_Y)
CRISIS_STRENGTH = 0     # Crisis strength can be from 0 (severe) to 3 (light)
CRISIS_WAVE1 = 5
CRISIS_WAVE2 = 10
CRISIS_WAVE3 = 15

# Define response network
NETWORK_TYPE = "star"
NETWORK_SIZE = 50
CAPABILITIES = 4
LEVELS = 3+1
MULTIPLE = 3


STEPS = 40

env = Environment(POPULATION_SIZE, SPREAD_X, SPREAD_Y, CRISIS_CENTER_X, CRISIS_CENTER_Y,
                  CRISIS_STRENGTH, CRISIS_WAVE1, CRISIS_WAVE2, CRISIS_WAVE3, CAPABILITIES, LEVELS, MULTIPLE)

env.set_crisis()

env.civilian_to_responder_selective()

selective_information_diffusion()





#for i in range(len(env.rs)):
#    if env.rs[i].level == 3:
#        print("ID: %d ------ data points received: %d" % (env.rs[i].id, len(env.rs[i].information_rcvd_high)))


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

