try:
    from Ikariam.Ships import *
except Exception:
    from Ships import *
from math import ceil, floor


class Composition():
    def __init__(self, t: float) -> None:
        self.comp = {
            Steam(): 100 + 15 * t * 4,
            Carrier(): 7 + 2 * t * 4,
            Ram(): 150 + 18 * t * 4,
            Rocket(): 30 + 11 * 2 * t,
            Mortar(): 42 * ceil(4 * t / 5),
            Paddle(): 30 * ceil(4 * t / 5),
            Tender(): 35,
            Fire(): 0
        }

    def reduce_ships(self, ship: Ship, count: int):
        for s in self.comp:
            if isinstance(s, ship):
                self.comp[s] -= count
                break
        return

    def __str__(self) -> str:
        res = {}
        for s in self.comp:
            res[str(s)] = self.comp[s]
            if self.comp[s] == 0:
                del res[str(s)]
        return f'{res}'


def upkeep_h(comp: Composition, lv: int=0):
    cost = 0
    for key in comp.comp:
        cost += key.ret_cost_of_n(comp.comp.get(key), lv)
    return round(cost, 2)


def upkeep_die(comp: Composition, t: float, lv: int=0):
    cost = 0
    for i in range(floor(t)):
        cost += upkeep_h(comp, lv)
        comp.reduce_ships(Steam, 60)
        comp.reduce_ships(Rocket, 16)
        comp.reduce_ships(Carrier, 8)
        comp.reduce_ships(Ram, 72)
    return round(cost)


def estimate_1D(lv: int=0, czy_24: bool=0, nu_siebie: int=0):
    comp_12 = Composition(12)
    if czy_24:
        comp_24 = Composition(24)
        cost_1D = upkeep_h(comp_12, lv) * (24 + 2 * nu_siebie) + (1 + nu_siebie) * \
            upkeep_die(comp_24, t=24, lv=lv) + upkeep_h(comp_24, lv) * (1 + nu_siebie)
        return round(cost_1D, 2)
    cost_1D = upkeep_h(comp_12, lv) * (36 + 2 * nu_siebie) + (2 + 2 * nu_siebie) * \
        upkeep_die(comp_12, t=12, lv=lv) + upkeep_h(comp_12, lv) * (2 + 2 * nu_siebie)
    return round(cost_1D, 2)


def estimate_nD(d: int=0, lv: int=0, czy_24: bool=0, nu_siebie: int=0):
    nu_siebie = min(max(nu_siebie, 0), 1)
    return round(d * estimate_1D(lv=lv, czy_24=czy_24, nu_siebie=nu_siebie), 2)

if __name__ == '__main__':
    print(estimate_nD(30, 12, 0, 1))
