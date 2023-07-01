import ctypes

try:
    c = ctypes.CDLL('./ika.so')
except Exception:
    c = ctypes.CDLL('./Ikariam/ika.so')
class island(ctypes.Structure):
    _fields_ = [
        ('x', ctypes.c_int),
        ('y', ctypes.c_int)
    ]


class Bonus:
    def __init__(self) -> None:
        self.auto()

    def auto(self):
        self.keys = {
            0: [(0, 0)],
            1: [(0, 1)],
            2: [(0, 2)],
            3: [(0, 3)],
            4: [(0, 4)],
            5: [(1, 0)],
            6: [(1, 1)],
            7: [(1, 2)],
            8: [(1, 3), (2, 0)],
            9: [(1, 4)],
            10:[(2, 1)],
            11:[(2, 2), (3, 0)],
            12:[(2, 3)],
            13:[(3, 1)],
            14:[(2, 4), (4, 0)],
            15:[(3, 2)],
            16:[(4, 1)],
            17:[(3, 3)],
            18:[(3, 4), (4, 2)],
            19:[(4, 3)],
            20:[(4, 4)]
        }
        return

    def parse(self, arg):
        ret = ""
        for a, b in arg:
            if a == 0:
                ret += f'Ładowność +{round(b/6*100, 1)}%, '
            elif a == 1:
                ret += f'Delfin +{100}% i ładowność +{round(b/6 * 100, 1)}%, '
            else:
                ret += f'Delfin +100%, tryton +{(a-1)*100}% i ładowność +{round(b/6*100, 1)}%, '
        return ret + ':'
            

c.distance.argtypes = (island, island)
c.distance.restype = ctypes.c_float

c.calc_time.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_float)
c.calc_time.restype = ctypes.c_float

c.get_distances.argtypes = ()
c.get_distances.restype = ctypes.POINTER(ctypes.c_float)

c.qqsort.argtypes = (ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int)

c.find.argtypes = (island, ctypes.c_float)
c.find.restype = ctypes.POINTER(island)

distance = c.distance
calc_time = c.calc_time
find = c.find
get_distances = c.get_distances
qsort = c.qqsort


import sys
def f():
    arg = sys.argv[1:]
    arg = [int(s) for s in arg]
    b = 0
    a = find(island(arg[0], arg[1]), calc_time(arg[2], arg[3], arg[4]))
    bonus = Bonus()
    for x in range(100):
        if a[x].x == 0:
            break
        if a[x].x != -1:
            print(f"{a[x].x}, {a[x].y}")
        else:
            b += 1
            print(f'{bonus.parse(bonus.keys[b])}')

f()

del ctypes
del island
del sys
