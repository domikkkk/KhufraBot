class Ship:
    armor = None
    hp = None
    attack = None
    cost = None
    discount = 14
    rg = None
    name = None

    def ret_cost(self, l: int=0):
        l = min(25, l)
        l = max(0, l)
        return self.cost * (100 - self.discount - l * 2) / 100

    def ret_cost_of_n(self, n: int, l: int=0):
        return self.ret_cost(l) * n

    def __str__(self):
        return self.name

class Shoot(Ship):
    amo = None

class Steam(Ship):
    def __init__(self) -> None:
        self.cost = 45
        self.hp = 576
        self.armor = 22
        self.attack = 172
        self.rg = 24
        self.name = 'Parowy'


class Ram(Ship):
    def __init__(self) -> None:
        self.cost = 15
        self.hp = 154
        self.armor = 15
        self.attack = 81
        self.rg = 5
        self.name = 'Kajak'


class Mortar(Shoot):
    def __init__(self) -> None:
        self.amo = 5
        self.cost = 50
        self.hp = 154
        self.armor = 12
        self.attack = 75
        self.rg = 22.4
        self.name = 'Moski'


class Rocket(Shoot):
    def __init__(self) -> None:
        self.amo = 2
        self.cost = 55
        self.hp = 65
        self.armor = 12
        self.attack = 386
        self.rg = 28
        self.name = 'Rakiety'


class Paddle(Shoot):
    def __init__(self) -> None:
        self.amo = 5
        self.cost = 5
        self.hp = 20
        self.armor = 6
        self.attack = 18
        self.rg = 6.4
        self.name = 'Smig'


class Carrier(Shoot):
    def __init__(self) -> None:
        self.amo = 5
        self.cost = 100
        self.hp = 140
        self.armor = 6
        self.attack = 106
        self.rg = 28
        self.name = 'Balon'


class Tender(Ship):
    def __init__(self) -> None:
        self.cost = 100
        self.hp = 140
        self.armor = None
        self.attack = None
        self.rg = 16
        self.name = 'Pomoc'


class Fire(Ship):
    def __init__(self) -> None:
        self.cost = 25
        self.hp = 219
        self.armor = 14
        self.attack = 88
        self.rg = 6.2
        self.name = 'Miotla'


class Diving(Shoot):
    def __init__(self) -> None:
        self.amo = 4
        self.cost = 50
        self.hp = 110
        self.armor = 12
        self.attack = 129
        self.rg = 20.2
        self.name = 'Podwodny'
