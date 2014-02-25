from Agents import *
from Crisis import *
from Response import *
from classes import *
import random
import networkx as nx
import matplotlib.pyplot as plt
import math
from Tkinter import *


class Environment:
    """ Class for world / environment  """

    civ = []
    rs = []
    G = nx.Graph()

    fail_list = []

    def __init__(self, population_size, spread_x, spread_y, crisis_center_x,
                 crisis_center_y, crisis_strength, crisis_wave1, crisis_wave2,
                 crisis_wave3, capabilities, levels, multiple):

        self.population_size = population_size
        self.spread_x = spread_x
        self.spread_y = spread_y

        self.count_civ_message_total = self.count_civ_message_shelter = self.count_civ_message_medical = \
            self.count_civ_message_food = 0
        self.civ_list_shelter = []
        self.civ_list_medical = []
        self.civ_list_food = []

        self.stat_absolute_civilian = self.stat_absolute_shelter = self.stat_absolute_medical = self.stat_absolute_food = 0

        self.cri = Crisis(crisis_center_x, crisis_center_y, crisis_strength,
                                crisis_wave1, crisis_wave2, crisis_wave3)

        for i in range(self.population_size):
            self.civ.append(Civilian(i, Location(random.randrange(0, self.spread_x),
                                           random.randrange(0, self.spread_y)), False,
                                           False, False, False, False, random.randint(40, 100)))

        # create response network
        self.capabilities = capabilities
        self.levels = levels
        self.multiple = multiple

        self.nw = Response_Network_Star(self.capabilities, self.levels, self.multiple, self.spread_x, self.spread_y)

    def set_crisis(self):
        for i in range(self.population_size):
            self.civ[i].dead = self.cri.crisis_affect(0, self.civ[i].position.x, self.civ[i].position.y)
            self.civ[i].shelter = self.cri.crisis_affect(1, self.civ[i].position.x, self.civ[i].position.y)
            self.civ[i].medical = self.cri.crisis_affect(2, self.civ[i].position.x, self.civ[i].position.y)
            self.civ[i].food = self.cri.crisis_affect(3, self.civ[i].position.x, self.civ[i].position.y)

    def draw_environment(self):

        ref = 30

        master = Tk()

        w = Canvas(master, width=SPREAD_X*1.2, height=SPREAD_Y*1.2)
        w.pack()

        w.create_rectangle(ref, ref, ref+SPREAD_X, ref+SPREAD_Y)

        for i in range(len(env.civ)):
            if env.civ[i].dead == True:
                w.create_line(ref+env.civ[i].position.x-1, ref+env.civ[i].position.y-1, ref+env.civ[i].position.x+1, ref+env.civ[i].position.y+1, fill='red')
                w.create_line(ref+env.civ[i].position.x-1, ref+env.civ[i].position.y+1, ref+env.civ[i].position.x+1, ref+env.civ[i].position.y-1, fill='red')
            elif env.civ[i].shelter == True or env.civ[i].medical == True or env.civ[i].food == True:
                w.create_line(ref+env.civ[i].position.x-1, ref+env.civ[i].position.y-1, ref+env.civ[i].position.x+1, ref+env.civ[i].position.y+1, fill='green')
                w.create_line(ref+env.civ[i].position.x-1, ref+env.civ[i].position.y+1, ref+env.civ[i].position.x+1, ref+env.civ[i].position.y-1, fill='green')
            else:
                w.create_line(ref+env.civ[i].position.x-1, ref+env.civ[i].position.y-1, ref+env.civ[i].position.x+1, ref+env.civ[i].position.y+1)
                w.create_line(ref+env.civ[i].position.x-1, ref+env.civ[i].position.y+1, ref+env.civ[i].position.x+1, ref+env.civ[i].position.y-1)

        w.create_oval(ref+CRISIS_CENTER_X-CRISIS_WAVE3*2, ref+CRISIS_CENTER_Y-CRISIS_WAVE3*2, ref+CRISIS_CENTER_X+CRISIS_WAVE3*2, ref+CRISIS_CENTER_Y+CRISIS_WAVE3*2, outline='blue', width=5)

        mainloop()


    def civilian_to_responder(self):
        for i in range(len(self.civ)):
            if self.civ[i].dead is False:
                if self.civ[i].shelter is True or self.civ[i].medical is True or self.civ[i].food is True and random.random() < 0.99:
                    # randomly choose emergency contact
                    em_contact = self.nw.local_em[random.randint(0, len(self.nw.local_em)-1)]

                    #share information with emergency contact - creating Information instance
                    self.nw.rs[em_contact].info.append(Responder_Information(self.civ[i].id, self.civ[i].position, "up", "civ", False, False, False, False,
                                                                                self.civ[i].shelter, self.civ[i].medical,
                                                                                self.civ[i].food, False, ))

                    print("Civilian %d sent information to Responder %d ----- Needs Shelter %r - Medical %r - Food %r" % (self.civ[i].id, self.nw.rs[em_contact].id, self.civ[i].shelter, self.civ[i].medical, self.civ[i].food))

                    self.stat_absolute_civilian += 1

                    if self.civ[i].shelter is True:
                        self.stat_absolute_shelter += 1
                        self.civ_list_shelter.append(i)
                    if self.civ[i].medical is True:
                        self.stat_absolute_medical += 1
                        self.civ_list_medical.append(i)
                    if self.civ[i].food is True:
                        self.stat_absolute_food += 1
                        self.civ_list_food.append(i)







    def update_civilian_status(self):
        # TODO: check for civilian auto update functionality!
        for self.i in range(len(self.civ)):
            self.civ[self.i].update_status()





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
POPULATION_SIZE = 100000
SPREAD_X = 500
SPREAD_Y = 180

# Define the location, strength and reach of crisis event
CRISIS_CENTER_X = random.randint(0, SPREAD_X)
CRISIS_CENTER_Y = random.randint(0, SPREAD_Y)
CRISIS_STRENGTH = 0     # Crisis strength can be from 0 (severe) to 3 (light)
CRISIS_WAVE1 = 50
CRISIS_WAVE2 = 100
CRISIS_WAVE3 = 150

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

env.civilian_to_responder()

for i in range(30):
    env.nw.process_information()
    #env.nw.process_information()

    print("")
    print("STEP %d" % i)
    print("##################################")

print(len(env.nw.rs[0].info))
print(env.stat_absolute_civilian)





#env.draw_environment()
