import ctypes
import csv
import os

global c
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'C/ika.so'))
# print(file_path)
c = ctypes.CDLL(file_path)


class island(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int)
    ]


class miotly(ctypes.Structure):
    _fields_ = [
        ('i', ctypes.POINTER(island)),
        ('t', ctypes.c_float)
    ]

class pair(ctypes.Structure):
    _fields_ = [
        ('m', ctypes.POINTER(miotly)),
        ('n', ctypes.c_int)
    ]


def update_c():
    global c
    c = ctypes.CDLL('./Ikariam/C/ika.so')


class Bonus:
    def __init__(self) -> None:
        self.auto()
        self.counter = 0

    def auto(self):
        self.result = {
            0: [(0, 0), None],
            1: [(0, 1), None],
            2: [(0, 2), None],
            3: [(0, 3), None],
            4: [(0, 4), None],
            5: [(1, 0), None],
            6: [(1, 1), None],
            7: [(1, 2), None],
            8: [((1, 3), (2, 0)), None],
            9: [(1, 4), None],
            10: [(2, 1), None],
            11: [((2, 2), (3, 0)), None],
            12: [(2, 3), None],
            13: [(3, 1), None],
            14: [((2, 4), (4, 0)), None],
            15: [(3, 2), None],
            16: [(4, 1), None],
            17: [(3, 3), None],
            18: [((3, 4), (4, 2)), None],
            19: [(4, 3), None],
            20: [(4, 4), None]
        }
        return

    def _parse(self, cords: island):
        if cords.x == -1 and cords.y == -1:
            if not self.result[self.counter][1]:
                del self.result[self.counter]
            self.counter += 1
        else:
            if not self.result[self.counter][1]:
                self.result[self.counter][1] = []
            x = self.result[self.counter][1]
            x.append((cords.x, cords.y))

    def parse(self, arg):
        i = 0
        while arg[i].x != 0:
            self._parse(arg[i])
            i += 1
        if not self.result[self.counter][1]:
            del self.result[self.counter]
        return self.result


class Wyspy:
    def __init__(self) -> None:
        self.islands = read_file("./Ikariam/wyspy.csv")
        self.update()

    def update(self):
        self.n = len(self.islands)
        self.islands_p = (island * self.n)(*self.islands)
        return

    def add(self, isl: island):
        self.islands.append(isl)
        self.update()
        return

    def find(self, *args):
        if len(args) < 2:
            raise Exception("Za mało argumentów")
        arg = [int(s) for s in args]
        for arr in arg:
            if arr < 0:
                raise Exception("Nie mogą być ujemne")
        response = czasy(self.islands_p, self.n, island(arg[0], arg[1]))
        a = response.m
        res = {}
        i = 0
        while i < response.n:
            t_time = round(a[i].t, 2)
            res[f"[{a[i].i[0].x} {a[i].i[0].y}]"] = f"{int(t_time//60)}h {int(t_time%60)}min"
            i += 1
        return res
        

c.distance.argtypes = (island, island)
c.distance.restype = ctypes.c_float

c.calc_time.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_float)
c.calc_time.restype = ctypes.c_float

c.get_distances.argtypes = ()
c.get_distances.restype = ctypes.POINTER(ctypes.c_float)

c.find.argtypes = (island, ctypes.c_float)
c.find.restype = ctypes.POINTER(island)

c.czasy.argtypes = (ctypes.POINTER(island), ctypes.c_int, island)
c.czasy.restype = pair


# c.queue.argtypes = (ctypes.POINTER(island))

distance = c.distance
calc_time = c.calc_time
find = c.find
get_distances = c.get_distances
czasy = c.czasy


def calc(*args):
    if len(args) < 5:
        raise Exception("Za mało argumentów")
    arg = [int(s) for s in args]
    for arr in arg:
        if arr < 0:
            raise Exception("Nie mogą być ujemne")
    a = find(island(arg[0], arg[1]), calc_time(arg[2], arg[3], arg[4]))
    bonus = Bonus()
    a = bonus.parse(a)
    return a


def read_file(filename: str):
    with open(filename, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        islands = []
        for line in reader:
            islands.append(island(int(line[0]), int(line[1])))
        return islands
