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

c.distance.argtypes = (island, island)
c.distance.restype = ctypes.c_float

c.calc_time.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.c_float)
c.calc_time.restype = ctypes.c_float

c.get_distances.argtypes = (ctypes.c_float,)
c.get_distances.restype = ctypes.POINTER(ctypes.c_float)

c.qqsort.argtypes = (ctypes.POINTER(ctypes.c_float), ctypes.c_int, ctypes.c_int)

c.find.argtypes = (island, ctypes.c_float, ctypes.c_float)
c.find.restype = ctypes.POINTER(island)

distance = c.distance
calc_time = c.calc_time
find = c.find
get_distances = c.get_distances
qsort = c.qqsort

print(distance(island(57, 10), island(96, 98))**2)
epsi = 0.02
for j in range(3):
    a = find(island(79, 10), calc_time(4, 24, 0), epsi)
    epsi += 0.01
    print(j)
    if a[0].x == 0 & a[0].y == 0:
        continue
    for i in range(100):
        if a[i].x == 0 & a[i].y == 0:
            break
        print(a[i].x, a[i].y) 

# a = get_distances(calc_time(1, 0, 0))


del ctypes
del island
