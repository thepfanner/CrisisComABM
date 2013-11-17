class Civilian:
    """ Class for civilian agents """
    def __init__(self, id, pos_x, pos_y, dead, shelter, food, medical, information):
        self.id = id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dead = dead
        self.shelter = shelter
        self.food = food
        self.medical = medical
        self.information = information

    def status(self):
        if self.dead == False:
            if self.food == True or self.shelter == True or self.medical == True:
                print("Help!! I am at %d / %d and my name is %d" % (self.pos_x, self.pos_y, self.id))

class Responder:
    """ Class for crisis responding agents """
    def ___init__(self, id):
        self.id = id
        self.information = CrisisInformation()