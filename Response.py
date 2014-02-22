from Agents import *
from classes import *
from Crisis import *
import networkx as nx
import math
from Tkinter import *

class Response_Network_Star():
    """
    Setting star response network

    """

    G = nx.Graph()
    rs = []
    local_em = []

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
        self.__draw_response_network()


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

    def __draw_response_network(self):
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

    def __check_network(self, deploy_network, civ_information):
        """
        check for help in response network

        @param deploy_network:
        @param civ_information:
        @return: true if successful

        """

        for i in range(len(deploy_network)):
            if civ_information.shelter is True:
                if self.rs[deploy_network[i].id].c == 0 and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    #print("Responder in my network can help SHELTER: respon_id - %d" % deploy_network[i].id)
                    return True

            if civ_information.medical is True:
                if self.rs[deploy_network[i].id].c == 1 and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    #print("Responder in my network can help MEDICAL: respon_id - %d" % deploy_network[i].id)
                    return True

            if civ_information.food is True:
                if self.rs[deploy_network[i].id].c == 2 and self.__check_in_circle(Circle(deploy_network[i].x, deploy_network[i].y, deploy_network[i].r), civ_information.position):
                    #print("Responder in my network can help FOOD: respon_id - %d" % deploy_network[i].id)
                        return True

    def __find_responder_to_help(self, deploy_network, civ_information, cap):
        """
        Search response network accessible from node
        for responder that satisfies capability, capacity and depoloy position.

        """

        if cap == "shelter":
            for i in range(len(deploy_network)):
                if civ_information.shelter == True and self.rs[deploy_network[i].id].c == 0\
                            and self.__check_in_circle(deploy_network[i], civ_information.position):
                            return deploy_network[i].id
                elif cap == "medical":
                    for i in range(len(deploy_network)):
                        if civ_information.medical == True and self.rs[deploy_network[i].id].c == 1\
                                and self.__check_in_circle(deploy_network[i], civ_information.position):
                            return deploy_network[i].id
                elif cap == "food":
                    for i in range(len(deploy_network)):
                        if civ_information.food == True and self.rs[deploy_network[i].id].c == 2\
                                and self.__check_in_circle(deploy_network[i], civ_information.position):
                            return deploy_network[i].id
                elif cap == "logistic":
                    for i in range(len(deploy_network)):
                            if civ_information.logistics == True and self.rs[deploy_network[i].id].c == 3\
                                    and self.__check_in_circle(deploy_network[i], civ_information.position):
                                return deploy_network[i].id
                else:
                    print("UKNOWN CAPABILITY!")

    def __send_information(self, sender, final_destination, information):
        if final_destination > 0:
            path = nx.shortest_path(self.G, self.rs[sender].id, final_destination)
            self.rs[path[1]].information_rcvd_high.append(information)
            self.rs[path[1]].new_info_rcvd_high = True
            return True
        else:
            return False



    def process_information(self):
        """
        Process information all responding agencies have received in the last
        time-step. Where possible, immediately deploy help. Otherwise look in
        network for potential help

        """

        # process each responder
        for i in range(len(self.rs)):
            tmp_list_helped = []

            # check if new information available for processing upstream
            if self.rs[i].new_info_rcvd_low is True:
                # for central unit information received from lower level ties, is processes and prepared to forward to responder that can deploy at location
                if self.rs[i].id is 0:
                    for j in range(len(self.rs[i].information_rcvd_low)):
                        if self.__check_network(self.rs[i].deploy_network, self.rs[i].information_rcvd_low[j]):
                            self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_low[j])
                            self.rs[i].new_info_to_pass_down = True
                            tmp_list_helped.append(j)
                            #print("NETWORK HELP FOUND @0: me_id %d --- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_low[j].source))
                        else:
                            print("@0 - NO NETWORK HELP FOUND FOR: civ_id %d" % self.rs[i].information_rcvd_low[j].source)

                # for other responders (not center) information from lower level is prepared to forward to next higher level
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
            if self.rs[i].new_info_rcvd_high is True:
                for j in range(len(self.rs[i].information_rcvd_high)):
                    if self.rs[i].information_rcvd_high[j].shelter is True and self.rs[i].c == 0\
                            and self.__check_in_circle(self.rs[i].deploy_range, self.rs[i].information_rcvd_high[j].position)\
                            and self.rs[i].r_shelter >= 10:
                        self.rs[i].r_shelter -= 10
                        self.rs[i].helped_list.append(self.rs[i].information_rcvd_high[j])
                        print("HELP SHELTER: me_id %d --- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source))
                        tmp_list_helped.append(j)

                    elif self.rs[i].information_rcvd_high[j].shelter is True and self.rs[i].c == 0 and self.rs[i].level < 3\
                            and self.__check_network(self.rs[i].deploy_network, self.rs[i].information_rcvd_high[j]):
                        #print("NETWORK HELP FOUND SHELTER: me_id %d ---- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source))
                        self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_high[j])
                        self.rs[i].new_info_to_pass_down = True
                        tmp_list_helped.append(j)
                        pass

                    if self.rs[i].information_rcvd_high[j].medical is True and self.rs[i].c == 1\
                            and self.__check_in_circle(self.rs[i].deploy_range, self.rs[i].information_rcvd_high[j].position)\
                            and self.rs[i].r_medical >= 10:
                        self.rs[i].r_medical -= 10
                        self.rs[i].helped_list.append(self.rs[i].information_rcvd_high[j])
                        print("HELP MEDICAL: me_id %d --- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source))
                        tmp_list_helped.append(j)

                    elif self.rs[i].information_rcvd_high[j].medical is True and self.rs[i].c == 1 and self.rs[i].level < 3\
                            and self.__check_network(self.rs[i].deploy_network, self.rs[i].information_rcvd_high[j]):
                        #print("NETWORK HELP FOUND MEDICAL: me_id %d ---- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source))
                        self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_high[j])
                        self.rs[i].new_info_to_pass_down = True
                        tmp_list_helped.append(j)
                        pass

                    if self.rs[i].information_rcvd_high[j].food is True and self.rs[i].c == 2\
                            and self.__check_in_circle(self.rs[i].deploy_range, self.rs[i].information_rcvd_high[j].position)\
                            and self.rs[i].r_food >= 10:
                        self.rs[i].r_food -= 10
                        self.rs[i].helped_list.append(self.rs[i].information_rcvd_high[j])
                        print("HELP FOOD: me_id %d --- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source))
                        tmp_list_helped.append(j)

                    elif self.rs[i].information_rcvd_high[j].food is True and self.rs[i].c == 2 and self.rs[i].level < 3\
                            and self.__check_network(self.rs[i].deploy_network, self.rs[i].information_rcvd_high[j]):
                        #print("NETWORK HELP FOUND FOOD: me_id %d ---- civ_id %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source))
                        self.rs[i].information_pass_down.append(self.rs[i].information_rcvd_high[j])
                        self.rs[i].new_info_to_pass_down = True
                        tmp_list_helped.append(j)
                        pass

            if self.rs[i].id == 0:
                if len(tmp_list_helped) > 0:
                    for j in xrange(len(self.rs[i].information_rcvd_low), -1, -1):
                        if j in tmp_list_helped:
                            self.rs[i].information_rcvd_low.pop(j)
                if len(self.rs[i].information_rcvd_low) == 0:
                    #print("NOTHING TO PROCESS: my_id %d" % self.rs[i].id)
                    self.rs[i].new_info_rcvd_low = False
                else:
                    for j in range(len(self.rs[i].information_rcvd_low)):
                        print("@ %d - no help for %d - Pos: %d , %d" % (self.rs[i].id, self.rs[i].information_rcvd_low[j].source, self.rs[i].information_rcvd_low[j].position.x, self.rs[i].information_rcvd_low[j].position.y))
            else:
                if len(tmp_list_helped) > 0:
                    for j in xrange(len(self.rs[i].information_rcvd_high), -1, -1):
                        if j in tmp_list_helped:
                            self.rs[i].information_rcvd_high.pop(j)
                if len(self.rs[i].information_rcvd_high) == 0:
                    #print("NOTHING TO PROCESS: my_id %d" % self.rs[i].id)
                    self.rs[i].new_info_rcvd_high = False
                else:
                    for j in range(len(self.rs[i].information_rcvd_high)):
                        pass
                        # print("@ %d - no help for %d - Pos: %d , %d" % (self.rs[i].id, self.rs[i].information_rcvd_high[j].source, self.rs[i].information_rcvd_high[j].position.x, self.rs[i].information_rcvd_high[j].position.y))

    def send_information_to_ties(self):
        """
        Sending information to ties within network

        """

        # Loop through all responding agents and send information if available
        for i in xrange(len(self.rs)-1, -1, -1):


            # First part is responsible for passing information from lower levels to higher levels.
            if self.rs[i].new_info_to_pass_up is True:
                for j in range(len(self.rs[i].ties_up)):
                    self.rs[self.rs[i].ties_up[j]].information_rcvd_low.extend(self.rs[i].information_pass_up)
                    self.rs[self.rs[i].ties_up[j]].new_info_rcvd_low = True
                    self.rs[i].new_info_to_pass_up = False
                    #print("UP: Responder %d sent information to Responder %d" % (self.rs[i].id, self.rs[self.rs[i].ties_up[j]].id))
                self.rs[i].information_pass_up = []

            # Second part is responsible for passing information to lower levels
            if self.rs[i].new_info_to_pass_down is True:
                 for j in range(len(self.rs[i].information_pass_down)):
                     if self.rs[i].information_pass_down[j].shelter == True:
                         responder_shelter = self.__find_responder_to_help(self.rs[i].deploy_network, self.rs[i].information_pass_down[j], "shelter")
                         if self.__send_information(i, responder_shelter, self.rs[i].information_pass_down[j]):
                             pass

                     if self.rs[i].information_pass_down[j].medical == True:
                         responder_medical = self.__find_responder_to_help(self.rs[i].deploy_network, self.rs[i].information_pass_down[j], "medical")
                         if self.__send_information(i, responder_medical, self.rs[i].information_pass_down[j]):
                             pass

                     if self.rs[i].information_pass_down[j].food == True:
                         responder_food = self.find__selective_deploy_destination(self.rs[i].deploy_network, self.rs[i].information_pass_down[j], "food")
                         if self.__send_information(i, responder_food, self.rs[i].information_pass_down[j]):
                             pass

                     if self.rs[i].information_pass_down[j].logistics == True:
                         responder_logistics = self.find__selective_deploy_destination(self.rs[i].deploy_network, self.rs[i].information_pass_down[j], "logistics")
                         if self.__send_information(i, responder_logistics, self.rs[i].information_pass_down[j]):
                             pass

            self.rs[i].information_pass_down = []