from Agents import *
from classes import *
from Crisis import *
import networkx as nx
import math
import copy
from Tkinter import *

class Response_Network_Star():
    """
    Setting star response network

    """

    G = nx.Graph()
    rs = []
    local_em = []
    help_shelter = help_medical = help_food = 0
    helped_shelter = []
    helped_medical = []
    helped_food = []

    def __init__(self, capabilities, levels, multiple, env_width, env_height):
        self.capabilities = capabilities
        self.levels = levels
        self.multiple = multiple
        self.env_width = env_width
        self.env_height = env_height

        # set center response unit
        self.rs.append(Responder(0, 0, [], []))

        # create responding agencies for each level and for each capability
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

        # assure connection reciprocity
        for i in range(len(self.rs)):
            if len(self.rs[i].ties_down) > 0:
                for j in range(len(self.rs[i].ties_down)):
                    tmp = self.rs[i].ties_down[j]
                    self.rs[tmp].ties_up = []
                    self.rs[tmp].ties_up.append(i)

        # connection reciprocity for center unit
        tmp_list = []
        for z in range(len(self.rs)):
            if len(self.rs[z].ties_up) > 0:
                for j in range(len(self.rs[z].ties_up)):
                    if self.rs[z].ties_up[j] == 0:
                        tmp_list.append(self.rs[z].id)
        self.rs[0].ties_down.extend(tmp_list)

        # populate list with local emergency responders
        for self.i in range(len(self.rs)):
            if self.rs[self.i].local_em is True:
                self.local_em.append(self.rs[self.i].id)

        self.__set_responder_location()
        self.__set_responder_network_range()
        self.__create_response_network()


    #################
    #
    # INTERNAL FUNCTIONS NEEDED TO CREATE RESPONSE NETWORK

    def __set_responder_location(self):
        """
        Calculate and set the physical deploy position of responders
        in response network

        """

        def find__products(no_responder):
            def is__no_prime(no):
                for i in range(2, no):
                    if no % i == 0:
                        return True

            list_products = []

            if is__no_prime(no_responder) is True:
                for i in range(int(no_responder)):
                    for j in range(int(no_responder)):
                        if i * j == no_responder:
                            list_products.append(Products(i, j))

                dff = 100
                a = 0
                b = 0

                # find products with min difference
                for i in range(len(list_products)):
                    if list_products[i].a >= list_products[i].b:
                        tmp_dff = list_products[i].a - list_products[i].b
                    elif list_products[i].a < list_products[i].b:
                        tmp_dff = list_products[i].b - list_products[i].a

                    if tmp_dff <= dff:
                        dff = tmp_dff
                        a = list_products[i].a
                        b = list_products[i].b

                return(Products(a, b))
            else:
                print("%d is prime" % no_responder)


        no_shelter = no_medical = no_food = no_logistic = 0

        for i in range(len(self.rs)):
            if self.rs[i].level == self.levels-1:
                if self.rs[i].c == 0:
                    no_shelter += 1
                elif self.rs[i].c == 1:
                    no_medical += 1
                elif self.rs[i].c == 2:
                    no_food += 1
                elif self.rs[i].c == 3:
                    no_logistic += 1

        product_shelter = find__products(no_shelter)
        product_medical = find__products(no_medical)
        product_food = find__products(no_food)
        product_logistic = find__products(no_logistic)

        opt_w_shelter = math.ceil(self.env_width / product_shelter.a)
        opt_h_shelter = math.ceil(self.env_height / product_shelter.b)
        opt_w_medical = math.ceil(self.env_width / product_medical.a)
        opt_h_medical = math.ceil(self.env_height / product_medical.b)
        opt_w_food = math.ceil(self.env_width / product_food.a)
        opt_h_food = math.ceil(self.env_height / product_food.b)
        opt_w_logistic = math.ceil(self.env_width / product_logistic.a)
        opt_h_logistic = math.ceil(self.env_height / product_logistic.b)

        side_shelter = max(opt_w_shelter, opt_h_shelter)
        side_medical = max(opt_w_medical, opt_h_medical)
        side_food = max(opt_w_food, opt_h_food)
        side_logistic = max(opt_w_logistic, opt_h_logistic)

        list_responder_shelter = []
        list_responder_medical = []
        list_responder_food = []
        list_responder_logistic = []

        for i in range(len(self.rs)):
            if self.rs[i].level == self.levels-1:
                if self.rs[i].c == 0:
                    list_responder_shelter.append(i)
                elif self.rs[i].c == 1:
                    list_responder_medical.append(i)
                elif self.rs[i].c == 2:
                    list_responder_food.append(i)
                elif self.rs[i].c == 3:
                    list_responder_logistic.append(i)


        # Set deploy position for Shelter Responders
        x = 0
        y = 0

        for i in range(len(self.rs)):
            if i in list_responder_shelter:
                if x <= self.env_width:
                    self.rs[i].deploy_range.x = x+(side_shelter/2)
                    self.rs[i].deploy_range.y = y+(side_shelter/2)
                    self.rs[i].deploy_range.r = (side_shelter*(1/math.sqrt(2.0)))*random.uniform(0.9,1.4)
                    x += opt_w_shelter
                else:
                    x = 0
                    y += side_shelter
                    self.rs[i].deploy_range.x = x+(side_shelter/2)
                    self.rs[i].deploy_range.y = y+(side_shelter/2)
                    self.rs[i].deploy_range.r = (side_shelter*(1/math.sqrt(2.0)))*random.uniform(0.9,1.8)
                    x += opt_w_shelter

        # Set deploy position for Medical Responders
        x = 0
        y = 0

        for i in range(len(self.rs)):
            if i in list_responder_medical:
                if x <= self.env_width:
                    self.rs[i].deploy_range.x = x+(side_medical/2)
                    self.rs[i].deploy_range.y = y+(side_medical/2)
                    self.rs[i].deploy_range.r = (side_medical*(1/math.sqrt(2.0)))*random.uniform(0.9,1.4)
                    x += opt_w_medical
                else:
                    x = 0
                    y += side_medical
                    self.rs[i].deploy_range.x = x+(side_medical/2)
                    self.rs[i].deploy_range.y = y+(side_medical/2)
                    self.rs[i].deploy_range.r = (side_medical*(1/math.sqrt(2.0)))*random.uniform(0.9,1.8)
                    x += opt_w_medical

        # Set deploy position for Food Responders
        x = 0
        y = 0

        for i in range(len(self.rs)):
            if i in list_responder_food:
                if x <= self.env_width:
                    self.rs[i].deploy_range.x = x+(side_food/2)
                    self.rs[i].deploy_range.y = y+(side_food/2)
                    self.rs[i].deploy_range.r = (side_food*(1/math.sqrt(2.0)))*random.uniform(0.9,1.4)
                    x += opt_w_food
                else:
                    x = 0
                    y += side_food
                    self.rs[i].deploy_range.x = x+(side_food/2)
                    self.rs[i].deploy_range.y = y+(side_food/2)
                    self.rs[i].deploy_range.r = (side_food*(1/math.sqrt(2.0)))*random.uniform(0.9,1.8)
                    x += opt_w_food

        # Set deploy position for Food Responders
        x = 0
        y = 0

        for i in range(len(self.rs)):
            if i in list_responder_logistic:
                if x <= self.env_width:
                    self.rs[i].deploy_range.x = x+(side_logistic/2)
                    self.rs[i].deploy_range.y = y+(side_logistic/2)
                    self.rs[i].deploy_range.r = (side_logistic*(1/math.sqrt(2.0)))*random.uniform(0.9,1.4)
                    x += opt_w_logistic
                else:
                    x = 0
                    y += side_logistic
                    self.rs[i].deploy_range.x = x+(side_logistic/2)
                    self.rs[i].deploy_range.y = y+(side_logistic/2)
                    self.rs[i].deploy_range.r = (side_logistic*(1/math.sqrt(2.0)))*random.uniform(0.9,1.8)
                    x += opt_w_logistic


        # Set deploy position for responders that are not on the base level
        for i in range(len(self.rs)):
            if self.rs[i].level < self.levels-1:
                self.rs[i].deploy_range.x = random.randint(0, self.env_width)
                self.rs[i].deploy_range.y = random.randint(0, self.env_height)
                self.rs[i].deploy_range.r = ((side_shelter + side_food + side_logistic + side_medical)/4)*random.uniform(0.9,1.4)


        # ref = 30
        # master = Tk()
        # master2 = Tk()
        # master3 = Tk()
        # master4 = Tk()
        #
        # w = Canvas(master, width=self.env_width*1.5, height=self.env_height*1.5)
        # v = Canvas(master2, width=self.env_width*1.5, height=self.env_height*1.5)
        # u = Canvas(master3, width=self.env_width*1.5, height=self.env_height*1.5)
        # t = Canvas(master4, width=self.env_width*1.5, height=self.env_height*1.5)
        #
        # w.pack()
        # v.pack()
        # u.pack()
        # t.pack()
        #
        # w.create_rectangle(ref, ref, ref+self.env_width, ref+self.env_height, fill="yellow")
        # v.create_rectangle(ref, ref, ref+self.env_width, ref+self.env_height, fill="yellow")
        # u.create_rectangle(ref, ref, ref+self.env_width, ref+self.env_height, fill="yellow")
        # t.create_rectangle(ref, ref, ref+self.env_width, ref+self.env_height, fill="yellow")
        #
        # for i in list_responder_shelter:
        #     w.create_oval(ref+self.rs[i].deploy_range.x-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.x+self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y+self.rs[i].deploy_range.r)
        #
        # for i in list_responder_medical:
        #     v.create_oval(ref+self.rs[i].deploy_range.x-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.x+self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y+self.rs[i].deploy_range.r)
        #
        # for i in list_responder_food:
        #     u.create_oval(ref+self.rs[i].deploy_range.x-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.x+self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y+self.rs[i].deploy_range.r)
        #
        # for i in list_responder_logistic:
        #     t.create_oval(ref+self.rs[i].deploy_range.x-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y-self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.x+self.rs[i].deploy_range.r, ref+self.rs[i].deploy_range.y+self.rs[i].deploy_range.r)
        #
        # mainloop()

    def __set_responder_network_range(self):
        """
        Sets the possible network range each responder has through his ties

        """

        for i in xrange(len(self.rs)-1, -1, -1):
            if len(self.rs[i].ties_down) > 0 and self.rs[i].level < self.levels-1:
                for j in range(len(self.rs[i].ties_down)):
                    if self.rs[self.rs[i].ties_down[j]].level == self.levels-1:
                        self.rs[i].deploy_network.append(Network_Range_Circle(self.rs[self.rs[i].ties_down[j]].deploy_range.x,
                                                                              self.rs[self.rs[i].ties_down[j]].deploy_range.y,
                                                                              self.rs[self.rs[i].ties_down[j]].deploy_range.r,
                                                                              self.rs[self.rs[i].ties_down[j]].id))
                    else:
                        self.rs[i].deploy_network.extend(self.rs[self.rs[i].ties_down[j]].deploy_network)
                        self.rs[i].deploy_network.append(Network_Range_Circle(self.rs[self.rs[i].ties_down[j]].deploy_range.x,
                                                                              self.rs[self.rs[i].ties_down[j]].deploy_range.y,
                                                                              self.rs[self.rs[i].ties_down[j]].deploy_range.r,
                                                                              self.rs[self.rs[i].ties_down[j]].id))

    def __create_response_network(self):
        """
        Use networkx to create social network graph for response network

        """

        for self.i in range(len(self.rs)):
            self.G.add_node(self.rs[self.i].id)
            for self.j in range(len(self.rs[self.i].ties_down)):
                self.G.add_edge(self.rs[self.i].id, self.rs[self.i].ties_down[self.j])

    ###################
    #
    # INTERNAL FUNCTIONS TO ASSIST INFORMATION PROCESSING AND INFORMATION TRANSFER

    def __check_in_circle(self, circle, point):
        """
        check if a given point lies within a circle
        @return: if successful True

        """

        # calculate squared distance of point to circle center
        dist_sq = (abs(circle.x - point.x)**2) + (abs(circle.y - point.y) **2)

        # compare with circle radius to check if point is in circle
        if dist_sq < (circle.r ** 2):
            return True

    def __check_network(self, deploy_network, civ_information, cap):
        """
        check for help in response network

        @param deploy_network:
        @param civ_information:
        @return: true if successful

        """

        if cap == "shelter" and civ_information.shelter is True:
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_shelter is True and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    #print("Responder in my network can help SHELTER: respon_id - %d" % deploy_network[i].id)
                    return True

        elif cap == "medical" and civ_information.medical is True:
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_medical is True and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    #print("Responder in my network can help MEDICAL: respon_id - %d" % deploy_network[i].id)
                    return True

        elif cap == "food" and civ_information.food is True:
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_food is True and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    #print("Responder in my network can help FOOD: respon_id - %d" % deploy_network[i].id)
                    return True

        elif cap == "logistic" and civ_information.logistic is True:
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_logistic is True and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    return True

    def __send_to_who(self, sender, deploy_network, civ_information, cap):
        """
        Function to populate list to whom information should be sent

        """
        send_to = []

        if cap == "shelter":
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_shelter is True and self.__check_in_circle(self.rs[deploy_network[i].id].deploy_range, civ_information.position):
                    path = nx.shortest_path(self.G, sender, deploy_network[i].id)
                    send_to.append(path[1])
        elif cap == "medical":
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_medical is True and self.__check_in_circle(self.rs[deploy_network[i].id].deploy_range, civ_information.position):
                    path = nx.shortest_path(self.G, sender, deploy_network[i].id)
                    send_to.append(path[1])
        elif cap == "food":
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_food is True and self.__check_in_circle(self.rs[deploy_network[i].id].deploy_range, civ_information.position):
                    path = nx.shortest_path(self.G, sender, deploy_network[i].id)
                    send_to.append(path[1])
        elif cap == "logistic":
            for i in range(len(deploy_network)):
                if self.rs[deploy_network[i].id].c_logistic is True and self.__check_in_circle(self.rs[deploy_network[i].id].deploy_range, civ_information.position):
                    path = nx.shortest_path(self.G, sender, deploy_network[i].id)
                    send_to.append(path[1])

        return send_to


    def __find_responder_to_help(self, deploy_network, civ_information, cap):
        """
        Search response network accessible from node
        for responder that satisfies capability, capacity and depoloy position.

        """

        if cap == "shelter":
            for i in range(len(deploy_network)):
                if civ_information.shelter == True and self.rs[deploy_network[i].id].c == 0\
                            and self.__check_in_circle(deploy_network[i], civ_information.position) and self.rs[deploy_network[i].id].r_shelter > 10:
                            return deploy_network[i].id
        elif cap == "medical":
            for i in range(len(deploy_network)):
                if civ_information.medical == True and self.rs[deploy_network[i].id].c == 1\
                        and self.__check_in_circle(deploy_network[i], civ_information.position) and self.rs[deploy_network[i].id].r_medical > 10:
                    return deploy_network[i].id
        elif cap == "food":
            for i in range(len(deploy_network)):
                if civ_information.food == True and self.rs[deploy_network[i].id].c == 2\
                        and self.__check_in_circle(deploy_network[i], civ_information.position) and self.rs[deploy_network[i].id].r_food > 10:
                    return deploy_network[i].id
        elif cap == "logistic":
            for i in range(len(deploy_network)):
                    if civ_information.logistics == True and self.rs[deploy_network[i].id].c == 3\
                            and self.__check_in_circle(deploy_network[i], civ_information.position) and self.rs[deploy_network[i].id].r_logistics > 10:
                        return deploy_network[i].id
        else:
            print("UNKNOWN CAPABILITY!")

    def __send_information(self, sender, final_destination, information, type):
        if final_destination > 0:
            path = nx.shortest_path(self.G, self.rs[sender].id, final_destination)
            self.rs[path[1]].information_rcvd_high.append(information)
            if type == "shelter":
                self.rs[path[1]].information_rcvd_high_shelter.append(information)
                self.rs[path[1]].new_info_rcvd_high_shelter = True
            elif type == "medical":
                self.rs[path[1]].information_rcvd_high_medical.append(information)
                self.rs[path[1]].new_info_rcvd_high_medical = True
            elif type == "food":
                self.rs[path[1]].information_rcvd_high_food.append(information)
                self.rs[path[1]].new_info_rcvd_high_food = True
            elif type == "logistic":
                self.rs[path[1]].information_rcvd_high_logistic.append(information)
                self.rs[path[1]].new_info_rcvd_high_logistic= True
            print("sent info down: my_id %d     dest_id %d    civ_id %d     type: %s" % (sender, path[1], information.source, type))
            return True
        else:
            return False

    def process_information(self):
        for i in range(len(self.rs)):
            if self.rs[i].id == 0:
                for j in range(len(self.rs[i].info)):
                    processed_shelter = False
                    processed_medical = False
                    processed_food = False
                    processed_logistic = False

                    if self.rs[i].info[j].status == "process":
                        if self.rs[i].info[j].direction == "up":
                            if self.__check_in_circle(self.rs[i].deploy_range, self.rs[i].info[j].position):
                                if self.rs[i].info[j].shelter is True and self.rs[i].c_shelter is True:
                                    print("HELPED SHELTER: my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    processed_shelter = True
                                if self.rs[i].info[j].medical is True and self.rs[i].c_medical is True:
                                    print("HELPED MEDICAL my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    processed_medical = True
                                if self.rs[i].info[j].food is True and self.rs[i].c_food is True:
                                    print("HELPED FOOD my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    processed_food = True
                                if self.rs[i].info[j].logistic is True and self.rs[i].c_logistic is True:
                                    print("HELPED LOGISTIC my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    processed_logistic = True

                            if processed_shelter is False:
                                if self.rs[i].info[j].shelter is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "shelter"):
                                        print("Shelter network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "shelter"))
                                        processed_shelter = True
                                else:
                                    processed_shelter = True

                            if processed_medical is False:
                                if self.rs[i].info[j].medical is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "medical"):
                                        print("Medical network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "medical"))
                                        processed_medical = True
                                else:
                                    processed_medical = True

                            if processed_food is False:
                                if self.rs[i].info[j].food is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "food"):
                                        print("Food network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "food"))
                                        processed_food = True
                                else:
                                    processed_food = True

                            if processed_logistic is False:
                                if self.rs[i].info[j].logistic is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "logistic"):
                                        print("Logistic network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "logistic"))
                                        processed_logistic = True
                                else:
                                    processed_logistic = True

                            if processed_shelter is True and processed_medical is True and processed_food is True and processed_logistic is True:
                                self.rs[i].info[j].status = "processed"
                            else:
                                if processed_shelter is True:
                                    self.rs[i].info[j].status = "processed"
                                else:
                                    print("@ %d NO HELP SEHLTER FOR %d" % (self.rs[i].id, self.rs[i].info[j].source))

                                if processed_medical is True:
                                    self.rs[i].info[j].status = "processed"
                                else:
                                    print("@ %d NO HELP MEDICAL FOR %d" % (self.rs[i].id, self.rs[i].info[j].source))

                                if processed_food is True:
                                    self.rs[i].info[j].status = "processed"
                                else:
                                    print("@ %d NO HELP FOOD FOR %d" % (self.rs[i].id, self.rs[i].info[j].source))

                                if processed_logistic is True:
                                    self.rs[i].info[j].status = "processed"
                                else:
                                    print("@ %d NO HELP LOGISTIC FOR %d" % (self.rs[i].id, self.rs[i].info[j].source))

                    elif self.rs[i].info[j].status == "processed":
                        print("my_id %d     source: %d" % (self.rs[i].id, self.rs[i].info[j].source))
                        if len(self.rs[i].info[j].send_to) > 0:
                            self.rs[i].info[j].send_to = list(set(self.rs[i].info[j].send_to))

                            for k in range(len(self.rs[i].info[j].send_to)):
                                tmp_info = copy.deepcopy(self.rs[i].info[j])
                                tmp_info.status = "process"
                                tmp_info.direction = "down"
                                tmp_info.send_to = []
                                print(self.rs[i].info[j].send_to[0])
                                #print("want to send: my_id %d   dest_id %d" % (self.rs[i].id, self.rs[self.rs[i].info[j].send_to[k]].id))
                                self.rs[self.rs[i].info[j].send_to[k]].info.append(tmp_info)
                                print("sent info: my_id %d      dest_id %d      civ_id %d" % (self.rs[i].id, self.rs[i].info[j].send_to[k], tmp_info.source))

                                self.rs[i].info[j].status = "sent"



            else:
                for j in range(len(self.rs[i].info)):

                    # process information received from civilians
                    if self.rs[i].info[j].status == "civ":
                        if self.rs[i].info[j].direction == "up":
                            for k in range(len(self.rs[i].ties_up)):
                                if self.rs[self.rs[i].ties_up[k]].interest_up == "all":
                                    self.rs[i].info[j].send_to.append(self.rs[i].ties_up[k])
                                    self.rs[i].info[j].status = "processed"
                                elif self.rs[i].ties_up[k].interest_up == "selective":
                                    print("shouldn't be here")
                                    #TODO: fix selective interest

                    # process information received from other responding agencies that need processing
                    elif self.rs[i].info[j].status == "process":
                        if self.rs[i].info[j].direction == "up":
                            for k in range(len(self.rs[i].ties_up)):
                                if self.rs[self.rs[i].ties_up[k]].interest_up == "all":
                                    self.rs[i].info[j].send_to.append(self.rs[i].ties_up[k])
                                    self.rs[i].info[j].status = "processed"
                                    print("I PROCESSED NEW INFORMATION")
                                elif self.rs[i].ties_up[k].interest_up == "selective":
                                    print("shouldn't be here")
                                    #TODO: fix selective interest

                        elif self.rs[i].info[j].direction == "down":

                            # check if able to help self
                            if self.__check_in_circle(self.rs[i].deploy_range, self.rs[i].info[j].position):
                                if self.rs[i].info[j].shelter is True and self.rs[i].c_shelter is True:
                                    print("HELPED SHELTER: my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    self.rs[i].info[j].status = "processed"
                                if self.rs[i].info[j].medical is True and self.rs[i].c_medical is True:
                                    print("HELPED MEDICAL my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    self.rs[i].info[j].status = "processed"
                                if self.rs[i].info[j].food is True and self.rs[i].c_food is True:
                                    print("HELPED FOOD my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    self.rs[i].info[j].status = "processed"
                                if self.rs[i].info[j].logistic is True and self.rs[i].c_logistic is True:
                                    print("HELPED LOGISTIC my_id %d - civ_id %d" % (i, self.rs[i].info[j].source))
                                    self.rs[i].info[j].status = "processed"

                            # check if network is able to help
                            else:
                                if self.rs[i].info[j].shelter is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "shelter"):
                                        print("Shelter network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "shelter"))
                                        self.rs[i].info[j].status = "processed"

                                if self.rs[i].info[j].medical is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "medical"):
                                        print("Medical network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "medical"))
                                        self.rs[i].info[j].status = "processed"

                                if self.rs[i].info[j].food is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "food"):
                                        print("Food network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "food"))
                                        self.rs[i].info[j].status = "processed"

                                if self.rs[i].info[j].logistic is True:
                                    if self.__check_network(self.rs[i].deploy_network, self.rs[i].info[j], "logistic"):
                                        print("Logistic network help found: my_id %d     civ_id %d" % (i, self.rs[i].info[j].source))
                                        self.rs[i].info[j].send_to.extend(self.__send_to_who(self.rs[i].id, self.rs[i].deploy_network, self.rs[i].info[j], "logistic"))
                                        self.rs[i].info[j].status = "processed"

                    elif self.rs[i].info[j].status == "processed":
                        #print("my_id %d     source: %d" % (self.rs[i].id, self.rs[i].info[j].source))
                        if len(self.rs[i].info[j].send_to) > 0:
                            self.rs[i].info[j].send_to = list(set(self.rs[i].info[j].send_to))
                            for k in range(len(self.rs[i].info[j].send_to)):
                                tmp_info = copy.deepcopy(self.rs[i].info[j])
                                tmp_info.status = "process"
                                tmp_info.send_to = []
                                print(self.rs[i].info[j].send_to[0])
                                #print("want to send: my_id %d   dest_id %d" % (self.rs[i].id, self.rs[self.rs[i].info[j].send_to[k]].id))
                                self.rs[self.rs[i].info[j].send_to[k]].info.append(tmp_info)
                                print("sent info: my_id %d      dest_id %d      civ_id %d" % (self.rs[i].id, self.rs[i].info[j].send_to[k], tmp_info.source))

                                self.rs[i].info[j].status = "sent"