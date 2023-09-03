from Ships import *
from math import ceil


def composition(t: float):
    return {
        Steam(): 100 + 15 * t * 4,
        Carrier(): 10 + 2 * t * 4,
        Ram(): 150 + 18 * t * 4,
        Rocket(): 30 + 11 * 2 * t,
        Mortar(): 42 * ceil(4 * t / 5),
        Paddle(): 30 * ceil(4 * t / 5),
        Tender(): 35,
        Fire(): 0
        
    }


def upkeep_h(comp: dict[Ship], lv: int=0, ):
    cost = 0
    for key in comp:
        cost += key.ret_cost_of_n(comp.get(key), lv)
    return round(cost, 2)


print(upkeep_h(24, 27)) 
