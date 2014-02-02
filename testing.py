import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt



class Responder():
    """ global responding agents """
    def __init__(self, level=0, id=0, ties_up=[], ties_down=[], c=0):
        self.level = level
        self.id = id
        self.ties_up = ties_up
        self.ties_down = ties_down
        self.c = c

        self.c_shelter = self.c_medical = self.c_food = self.c_logistic = False
        self.r_shelter = self.r_medical = self.r_food = self.r_logistic = 0

        # set capabilities and resource level for capabilities
        if self.c == 0:
            self.c_shelter = True
            self.r_shelter = random.randint(0,100)
        elif self.c == 1:
            self.c_medical = True
            self.r_medical = random.randint(0,100)
        elif self.c == 2:
            self.c_food = True
            self.r_food = random.randint(0,100)
        elif self.c == 3:
            self.c_logistic = True
            self.r_logistic = random.randint(0,100)

        # set time to needed to deploy capability
        if self.level == 0:
            self.time_to_deploy = random.randint(5,10)
        elif self.level == 1:
            self.time_to_deploy = random.randint(4,10)
        elif self.level == 2:
            self.time_to_deploy = random.randint(3,10)
        else:
            self.time_to_deploy = random.randint(1,5)



NETWOR_TYPE = "star"
NETWORK_SIZE = 50
CAPABILITIES = 3
LEVELS = 3
MULTIPLE = 3
rs = []


# define center
rs.append(Responder(0,0,[1, 2, 3, 4]))

for c in range(CAPABILITIES):
    for l in range(LEVELS):
        if l == 0:
            t_down = []
            for t in range(MULTIPLE):
                t_down.append(len(rs)+t+1)
            rs.append(Responder(l, len(rs), [0], t_down, c))
        else:
            for m in range(MULTIPLE**l):
                t_down = []
                if l < LEVELS-1:
                    for t in range(MULTIPLE):
                        t_down.append(len(rs)+(MULTIPLE**l)-m+(MULTIPLE*m)+t)
                        t_up = []
                rs.append(Responder(l, len(rs), t_up, t_down, c))





# connection reciprocity
for i in range(len(rs)):
    if rs[i].ties_down > 0:
        for j in range(len(rs[i].ties_down)):
            tmp = rs[i].ties_down[j]
            rs[tmp].ties_up = []
            rs[tmp].ties_up.append(i)


print(len(rs))
for i in range(len(rs)):
    print("ID %d" % rs[i].id)
    print("Cap Shelter = %r - Cap Medical = %r - Cap Food = %r - Cap Log = %r"  % (rs[i].c_shelter, rs[i].c_medical, rs[i].c_food, rs[i].c_logistic))
    print("ResSh = %d - ResMed = %d - ResFood = %d - ResLog = %d" % (rs[i].r_shelter, rs[i].r_medical, rs[i].r_food, rs[i].r_logistic))

# Graph calculations
# G = nx.Graph()
# for i in range(len(rs)):
#     G.add_node(rs[i].id)
#     for j in range(len(rs[i].ties_down)):
#         G.add_edge(rs[i].id, rs[i].ties_down[j])
#
#
# nx.draw(G)
# plt.show()
