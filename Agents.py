from Crisis import *
from classes import *

class Civilian:
    """ Class for civilian agents """
    def __init__(self, id, pos_x, pos_y, dead, shelter, food, medical, information, r_food):
        self.id = id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dead = dead
        self.shelter = shelter
        self.food = food
        self.medical = medical
        self.information = information
        self.r_food = r_food
        self.shared_info = False

    def status(self):
        if self.dead is False:
            if self.food == True or self.shelter == True or self.medical == True:
                print("Help!! I am at %d / %d and my name is %d" % (self.pos_x, self.pos_y, self.id))

    def update_status(self):
        """
        updates status for civilians - Dead, Food, Medical, Shelter
        """
        if self.dead is False:
            if random.random() <= 0.30:
                self.dead = True
            else:
                if self.r_food < -20:
                    self.dead = True
                else:
                    self.r_food -= 5
                    if self.r_food < 0:
                        self.food = True
                if random.random() <= 0.05:
                    self.medical = True

    def share_information(self):
        """
        @return: civilans send information
        """
        return Information(self.id, self.pos_x, self.pos_y, self.shelter, self.medical, self.food)


class Information():
    """ information shared between civilians and responders """
    def __init__(self, source, pos_x, pos_y, shelter=False, medical=False, food=False, logistics=False):
        self.source = source
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.shelter = shelter
        self.medical = medical
        self.food = food
        self.logistics = logistics

class Responder():
    """ global responding agents """
    def __init__(self, level=0, id=0, ties_up=[], ties_down=[], c=0):
        self.level = level
        self.id = id
        self.ties_up = ties_up
        self.ties_down = ties_down
        self.c = c
        self.local_em = False
        self.information_rcvd_low = []
        self.information_pass_up = []
        self.information_rcvd_high = []
        self.information_pass_down = []
        self.new_info_rcvd_low = False
        self.new_info_rcvd_high = False
        self.new_info_to_pass_up = False
        self.new_info_to_pass_down = False
        self.process_capacity = random.randint(12,30)
        self.count_incoming_low = 0

        self.deploy_position = Location(0,0)
        self.deploy_range = 0
        self.can_deploy_instant = False

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

        # set capabilities depending on level
        if self.level == 0:
            self.time_to_deploy = random.randint(5,10)
        elif self.level == 1:
            self.time_to_deploy = random.randint(4,10)
        elif self.level == 2:
            if random.random() < 0.400:
                self.can_deploy_instant = True
                self.time_to_deploy = random.randint(3,10)
        else:
            if random.random() < 0.900:
                self.can_deploy_instant = True
                self.time_to_deploy = random.randint(1,5)

        # set local emergency
        if self.level == 0 and random.random() < 0.001:
            self.local_em = True
        elif self.level == 1 and random.random() < 0.005:
            self.local_em = True
        elif self.level == 2 and random.random() < 0.05:
            self.local_em = True
        else:
            if random.random() < 0.10:
                self.local_em = True
            else:
                pass
