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

print(distance(island(56, 10), island(3, 85)))

a = find(island(56, 10), calc_time(4, 35, 31))
for x in range(100):
    if a[x].x == 0:
        break
    print(a[x].x, a[x].y)


del ctypes
del island
