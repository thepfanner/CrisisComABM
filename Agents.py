from Crisis import *
from classes import *

class Civilian:
    """ Class for civilian agents """
    def __init__(self, id, position, dead, shelter, food, medical, information, r_food):
        self.id = id
        self.position = position
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
            if self.medical is True:
                if random.random() <= 0.40:
                    self.dead = True

            if self.r_food < -20:
                self.dead = True
            else:
                self.r_food -= 5
                if self.r_food < 0:
                    self.food = True

            if self.shelter is True and self.food is True:
                if random.random() <= 0.10:
                    self.medical = True

    def share_information(self):
        """
        @return: civilans send information
        """
        return Information(self.id, self.pos_x, self.pos_y, self.shelter, self.medical, self.food)


class Information():
    """ information shared between civilians and responders """
    def __init__(self, source, position, shelter=False, medical=False, food=False, logistic=False):
        self.source = source
        self.position = position
        self.shelter = shelter
        self.medical = medical
        self.food = food
        self.logistic = logistic

    def __lt__(self, other):
        return self.source < other.source

class Responder_Information(Information):
    def __init__(self, source, position, direction, status, interest_shelter=False, interest_medical=False, interest_food=False, interest_logistic=False,
               shelter=False, medical=False, food=False, logistic=False):
        Information.__init__(self, source, position, shelter, medical, food, logistic)
        self.direction = direction
        self.status = status
        self.send_to = []

        self.interest_shelter = interest_shelter
        self.interest_medical = interest_medical
        self.interest_food = interest_food
        self.interest_logistic = interest_logistic


class Responder():
    """ global responding agents """
    def __init__(self, level=0, id=0, ties_up=[], ties_down=[], c=0):
        self.level = level
        self.id = id
        self.ties_up = ties_up
        self.ties_down = ties_down
        self.c = c
        self.local_em = False

        self.info = []
        self.interest_up = "all"

        self.information_rcvd_civ = []
        self.information_rcvd_low = []
        self.information_rcvd_low_shelter = []
        self.information_rcvd_low_medical = []
        self.information_rcvd_low_food = []

        self.information_pass_up = []
        self.information_pass_up_shelter = []
        self.information_pass_up_medical = []
        self.information_pass_up_food = []

        self.information_rcvd_high = []
        self.information_rcvd_high_shelter = []
        self.information_rcvd_high_medical = []
        self.information_rcvd_high_food = []
        self.information_rcvd_high_logistic = []

        self.information_pass_down = []
        self.information_pass_down_shelter = []
        self.information_pass_down_medical = []
        self.information_pass_down_food = []
        self.information_pass_down_logistic = []

        self.helped_list = []
        self.helped_list_shelter = []
        self.helped_list_medical = []
        self.helped_list_food = []
        self.helped_list_logistic = []

        self.new_info_rcvd_civ = False

        self.new_info_rcvd_low_ = False
        self.new_info_rcvd_low_shelter = False
        self.new_info_rcvd_low_medical = False
        self.new_info_rcvd_low_food = False
        self.new_info_rcvd_low_logistic = False

        self.new_info_rcvd_high = False
        self.new_info_rcvd_high_shelter = False
        self.new_info_rcvd_high_medical = False
        self.new_info_rcvd_high_food = False
        self.new_info_rcvd_high_logistic = False

        self.new_info_to_pass_up = False
        self.new_info_to_pass_up_shelter = False
        self.new_info_to_pass_up_medical = False
        self.new_info_to_pass_up_food = False
        self.new_info_to_pass_up_logistic = False

        self.new_info_to_pass_down = False
        self.new_info_to_pass_down_shelter = False
        self.new_info_to_pass_down_medical = False
        self.new_info_to_pass_down_food = False
        self.new_info_to_pass_down_logistic = False

        self.process_capacity = random.randint(12,30)
        self.count_incoming_low = 0

        self.deploy_range = Circle(0, 0, 0)

        self.deploy_position = Location(0, 0)
        # self.deploy_range = Location(0, 0)
        self.deploy_network = []
        self.can_deploy_instant = False

        self.c_shelter = self.c_medical = self.c_food = self.c_logistic = False
        self.r_shelter = self.r_medical = self.r_food = self.r_logistic = 0

        # set capabilities and resource level for capabilities
        if self.c == 0:
            self.c_shelter = True
            self.r_shelter = random.randint(10000,20000)
        elif self.c == 1:
            self.c_medical = True
            self.r_medical = random.randint(10000,20000)
        elif self.c == 2:
            self.c_food = True
            self.r_food = random.randint(10000,20000)
        elif self.c == 3:
            self.c_logistic = True
            self.r_logistic = random.randint(10000,20000)

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
        if self.level == 0:
            self.local_em = False
        elif self.level == 1:
            self.local_em = False
        elif self.level == 2 and random.random() < 0.05:
            self.local_em = True
        else:
            if random.random() < 0.10:
                self.local_em = True

    def set_deploy_position_random(self, x, y, r):
        self.deploy_position = Location(random.randint(0, x), random.randint(0, y))
        self.deploy_range = Location(r, r)

        self.deploy_position.x = int(self.deploy_position.x)
        self.deploy_position.y = int(self.deploy_position.y)
        self.deploy_range.x = int(self.deploy_range.x)
        self.deploy_range.y = int(self.deploy_range.y)
