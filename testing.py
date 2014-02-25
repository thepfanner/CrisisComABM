from Tkinter import*
import random
import math
import matplotlib.pyplot as plt

class Location():
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r




class Civilian():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y


def find__products(no_responder):
    def is__no_prime(no):
        for i in range(2, no):
            if no % i == 0:
                return True

    if is__no_prime(no_responder) is True:
        for i in range(int(no_responder)):
            for j in range(int(no_responder)):
                if i * j == no_responder:
                    list_products.append(Products(i, j))

        for i in range(len(list_products)):
            print("a: %d - b: %d" % (list_products[i].a, list_products[i].b))


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

def check__in_circle(point, circle):
    square_dist = ((abs(circle.x - point.x)) ** 2)+((abs(circle.y - point.y)) ** 2)
    square_radius = circle.r ** 2

    if square_dist < square_radius:
        return True


island_width = 800.00
island_height = 400.00

civ = []

for i in range(250):
    civ.append(Civilian(i, random.randint(0, island_width), random.randint(0, island_height)))

civ.append(Civilian(288, 900, 480))

no_responder = 27
list1 = []
list_products = []

area_to_cover = island_width * island_height

prod = find__products(no_responder)

print(prod.a)
print(prod.b)

opt_w = math.ceil(island_width / prod.a)
opt_h = math.ceil(island_height / prod.b)

print(opt_w)
print(opt_h)

side = max(opt_w, opt_h)

print(side)

x = 0
y = 0

for i in range(no_responder):
    if x <= island_width:
        list1.append(Location(x, y, side))
        x += opt_w
    else:
        x = 0
        y += side
        list1.append(Location(x, y, side))
        x += opt_w

for i in range(len(list1)):
    print("ID: %d ++++ X: %d - %d / Y: %d - %d" % (i, list1[i].x, list1[i].x + list1[i].r, list1[i].y, list1[i].y + list1[i].r))


l2 = []

for i in range(len(list1)):
    l2.append(Location((list1[i].x+(list1[i].r / 2)), (list1[i].y+(list1[i].r / 2)), (list1[i].r * (1 / math.sqrt(2.0))))) #*random.uniform(0.9, 1.4)))


check_circle_var = []

for i in range(len(civ)):
    for j in range(len(l2)):
        if check__in_circle(civ[i], l2[j]):
            print("IN CIRCLE: civ_id: %d --- respon_id: %d" % (i, j))
            check_circle_var.append(i)

print(check_circle_var)
new_list = list(set(check_circle_var))

print(len(new_list))
print(len(civ))


ref = 30

master = Tk()

w = Canvas(master, width=island_width*1.5, height=island_height*1.5)
w.pack()

w.create_rectangle(ref, ref, ref+island_width, ref+island_height, fill="yellow")

for i in range(len(list1)):
    rand = random.randint(0,3)
    if rand == 0:
        out = "black"
    elif rand == 1:
        out = "red"
    elif rand == 2:
        out = "green"
    elif rand == 3:
        out = "blue"

    rand2 = random.randint(0,3)
    if rand2 == 0:
        line = 2
    elif rand2 == 1:
        line = 4
    elif rand2 == 2:
        line = 1
    elif rand2 == 3:
        line = 6

    #w.create_rectangle(ref+list1[i].x, ref+list1[i].y, ref+list1[i].x+list1[i].r, ref+list1[i].y+list1[i].r, outline=out, width=line)
    w.create_oval(ref+l2[i].x-l2[i].r, ref+l2[i].y-l2[i].r, ref+l2[i].x+l2[i].r, ref+l2[i].y+l2[i].r, outline=out, width=line)


for i in range(len(civ)):
    w.create_line(ref+civ[i].x-1, ref+civ[i].y-1, ref+civ[i].x+1, ref+civ[i].y+1)
    w.create_line(ref+civ[i].x-1, ref+civ[i].y+1, ref+civ[i].x+1, ref+civ[i].y-1)

#w.create_line(ref+civ[250].x-10, ref+civ[250].y-10, ref+civ[250].x+10, ref+civ[250].y+10, width="5")
#w.create_line(ref+civ[250].x-10, ref+civ[250].y+10, ref+civ[250].x+10, ref+civ[250].y-10, width="5")

mainloop()



# class Type():
#
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#
#     def __lt__(self, other):
#         return self.x < other.x
#
#
#
# class Vehicle():
#
#     def __init__(self, colour, category):
#         self.colour = colour
#         self.category = category
#
# class Car(Vehicle):
#     def __init__(self, colour, brand, category):
#         Vehicle.__init__(self, colour, category)
#         self.brand = brand
#
# brands = ['BMW', 'VW', 'AUDI']
# colours = ['black', 'white', 'blue']
#
# vehicle_list = []
#
# veh_list2 = []
#
# for i in range(10):
#     vehicle_list.append(Car(colours[random.randint(0,2)], brands[random.randint(0,2)], random.randint(0,5)))
#
# for i in range(len(vehicle_list)):
#     print("%d : Brand: %s    Colour %s" % (i, vehicle_list[i].brand, vehicle_list[i].colour))
#
# for i in range(5):
#     veh_list2.append(Vehicle(colours[random.randint(0,2)], random.randint(0,5)))
#
# for i in range(len(veh_list2)):
#     print("%d: Colour: %s    category %d" % (i, veh_list2[i].colour, veh_list2[i].category))


#
#
# print(list1)
# print("")
# print("to remove")
# print(list_rem)
#
# for i in xrange(len(list1), -1, -1):
#     if i in list_rem:
#         list1.pop(i)
# print("")
# print(list1)






#def foo(x, y, z):
#    if x in range(y, z):
#        return True
#    else:
#        return False

#def bar(x, y, z):
#    if foo(x, y, z):
#        print("In the range --- True")
#    else:
#        print("Not in the range --- False")

#y = 2
#z = 10

#for i in range(15):
#    bar(i, y, z)

# class Responder():
#      global responding agents
#     def __init__(self, level=0, id=0, ties_up=[], ties_down=[], c=0):
#         self.level = level
#         self.id = id
#         self.ties_up = ties_up
#         self.ties_down = ties_down
#         self.c = c
#
#         self.c_shelter = self.c_medical = self.c_food = self.c_logistic = False
#         self.r_shelter = self.r_medical = self.r_food = self.r_logistic = 0
#
#         # set capabilities and resource level for capabilities
#         if self.c == 0:
#             self.c_shelter = True
#             self.r_shelter = random.randint(0,100)
#         elif self.c == 1:
#             self.c_medical = True
#             self.r_medical = random.randint(0,100)
#         elif self.c == 2:
#             self.c_food = True
#             self.r_food = random.randint(0,100)
#         elif self.c == 3:
#             self.c_logistic = True
#             self.r_logistic = random.randint(0,100)
#
#         # set time to needed to deploy capability
#         if self.level == 0:
#             self.time_to_deploy = random.randint(5,10)
#         elif self.level == 1:
#             self.time_to_deploy = random.randint(4,10)
#         elif self.level == 2:
#             self.time_to_deploy = random.randint(3,10)
#         else:
#             self.time_to_deploy = random.randint(1,5)
#
#
#
# NETWOR_TYPE = "star"
# NETWORK_SIZE = 50
# CAPABILITIES = 3
# LEVELS = 3
# MULTIPLE = 3
# rs = []
#
#
# # define center
# rs.append(Responder(0,0,[1, 2, 3, 4]))
#
# for c in range(CAPABILITIES):
#     for l in range(LEVELS):
#         if l == 0:
#             t_down = []
#             for t in range(MULTIPLE):
#                 t_down.append(len(rs)+t+1)
#             rs.append(Responder(l, len(rs), [0], t_down, c))
#         else:
#             for m in range(MULTIPLE**l):
#                 t_down = []
#                 if l < LEVELS-1:
#                     for t in range(MULTIPLE):
#                         t_down.append(len(rs)+(MULTIPLE**l)-m+(MULTIPLE*m)+t)
#                         t_up = []
#                 rs.append(Responder(l, len(rs), t_up, t_down, c))
#
#
#
#
#
# # connection reciprocity
# for i in range(len(rs)):
#     if rs[i].ties_down > 0:
#         for j in range(len(rs[i].ties_down)):
#             tmp = rs[i].ties_down[j]
#             rs[tmp].ties_up = []
#             rs[tmp].ties_up.append(i)
#
#
# print(len(rs))
# for i in range(len(rs)):
#     print("ID %d" % rs[i].id)
#     print("Cap Shelter = %r - Cap Medical = %r - Cap Food = %r - Cap Log = %r"  % (rs[i].c_shelter, rs[i].c_medical, rs[i].c_food, rs[i].c_logistic))
#     print("ResSh = %d - ResMed = %d - ResFood = %d - ResLog = %d" % (rs[i].r_shelter, rs[i].r_medical, rs[i].r_food, rs[i].r_logistic))
#
# # Graph calculations
# # G = nx.Graph()
# # for i in range(len(rs)):
# #     G.add_node(rs[i].id)
# #     for j in range(len(rs[i].ties_down)):
# #         G.add_edge(rs[i].id, rs[i].ties_down[j])
# #
# #
# # nx.draw(G)
# # plt.show()
#
# for i in range(len(list1)):
#     list2.append(Location(list1[i].x+(list1[i].r / 2),list1[i].y+(list1[i].r / 2),math.ceil(math.sqrt(list1[i].r**list1[i].r+list1[i].r**list1[i].r))))
#
#
# ref = 20
#
# protege = Tk()
#
# v = Canvas(protege, width=island_width, height=island_height)
# v.pack()
#
# v.create_rectangle(ref, ref, ref+island_width, ref+island_height, fill="green")
#
# for i in range(len(list2)):
#     v.create_oval(ref+list1[i].x-list1[i].r, ref+list1[i].y-list1[i].r, ref+list1[i].x+list1[i].r, ref+list1[i].y+list1[i].r)
