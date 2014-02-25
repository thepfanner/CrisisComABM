__author__ = 'sp'


class Location:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Location_ID:
    def __init__(self, id, direct, x, y, range):
        self.id = id
        self.direct = direct
        self.x = x
        self.y = y
        self.range = range


class Products():
    def __init__(self, a, b):
        self.a = a
        self.b = b

class Circle():
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

class Network_Range_Circle(Circle):
    def __init__(self, x=0, y=0, r=0, id=0):
        Circle.__init__(self, x, y, r)
        self.id = id