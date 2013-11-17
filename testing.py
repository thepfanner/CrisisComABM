import random
import numpy as np

class A:
    def __init__(self):
        self.alive = True
        self.food = False
        self.medical = False
        self.pos_x = random.randrange(0, 200)
        self.pos_y = random.randrange(0, 200)

class B:
    def __init__(self):
        self.range_x = range(10, 100)
        self.range_y = range(20, 200)

    def set(self, pos_x, pos_y):
        if pos_x in self.range_x and pos_y in self.range_y:
             return False, True
        else:
            return True, False

civ = []
cr = B()

for i in range(10):
    civ.append(A())
    print(civ[i].alive)
print('Deploying Crisis')

for i in range(len(civ)):
    civ[i].alive = cr.set(civ[i].pos_x, civ[i].pos_y)
    print(civ[i].alive)

x = 12

if x in range(5, 20):
    print "I am in the first range"
elif x in range(2,25):
    print "I am in the second range"
elif x in range (0, 100):
    print "I am in the third range"
else:
    print "I am outside the range"


a = np.array([[["X0Y0Z0", "X1Y0Z0", "X2Y0Z0"], ["X0,Y1Z0", "X1Y1Z0", "X2Y1Z0"]],
              [["X0Y0Z1", "X1Y0Z1", "X2Y0Z1"], ["X0Y1Z1", "X1Y1Z1", "X2Y1Z1"]]])

print a[0,1,2]