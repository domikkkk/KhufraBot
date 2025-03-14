from dataclasses import dataclass
from typing import List, Any, Dict


@dataclass
class Rg_Keeper:
    rg: str
    palm: bool
    whose: str=None


@dataclass(frozen=True)
class Player:
    name: str
    f: str


@dataclass(frozen=True)
class Attack:
    when:str
    action: str
    units: str
    who: Player
    whom: Player


@dataclass(frozen=True)
class Attacks:
    occupy: List[Attack]
    open_battle: List[Attack]
    station: List[Attack]


@dataclass
class Troops:
    hoplici: int
    giganty: int
    oszczepy: int
    wojownicy: int
    procarze: int
    lucznicy: int
    strzelcy: int
    tarany: int
    katapulty: int
    mozdzierze: int
    zyrki: int
    balony: int
    kucharze: int
    medycy: int
    spartanie: int


@dataclass
class Fleets:
    miotacze: int
    parowy: int
    taranki: int
    balisty: int
    katapulty: int
    mozdzierze: int
    rakiety: int
    podwodne: int
    smigi: int
    balony: int
    pomoce: int


@dataclass
class City:
    id: int
    name: str
    coords: str
    tradegood: int
    is_own: bool
    extra: List[Any]

    def __init__(self, *args):
        self.id = args[0]
        self.name = args[1]
        self.coords = args[2]
        self.tradegood = args[3]
        self.is_own = args[4]
        self.extra = list(args[5:])  # Wszystko, co nadmiarowe


@dataclass
class CityIsland:
    type: str
    name: str
    id: int
    level: int
    ownerId: int
    ownerName: str
    ownerAllyId: int
    ownerAllyTag: str
    state: str

    def __init__(self, **kwargs):
        self.type = kwargs.get("type")
        self.name = kwargs.get("name")
        self.id = kwargs.get("id")
        self.level = kwargs.get("level")
        self.ownerId = kwargs.get("ownerId")
        self.ownerName = kwargs.get("ownerName")
        self.ownerAllyId = kwargs.get("ownerAllyId")
        self.ownerAllyTag = kwargs.get("ownerAllyTag")
        self.state = kwargs.get("state")


@dataclass
class CitiesIsland:
    all: List[CityIsland]

    def __init__(self, *args):
        self.all = [CityIsland(**city) for city in args if city.get("id", -1) != -1]

    def __getitem__(self, index) -> CityIsland:
        return self.all[index]

    def to_dict(self):
        return [vars(city) for city in self.all]


################################################################################
#                           DANE ZWRACANE Z INNYMI                             #
################################################################################

@dataclass
class Position:
    building: str  # name ale po ang
    name: str  # zależy od ustawionego języka
    buildingId: int
    canUpgrade: bool
    level: int
    groundId: int

    def __init__(self, **kwargs):
        self.building = kwargs.get("building")
        self.name = kwargs.get("name")
        self.buildingId = kwargs.get("buildingId")
        self.canUpgrade = kwargs.get("canUpgrade")
        self.level = kwargs.get("level")
        self.groundId = kwargs.get("groundId")


@dataclass
class backGroundData:
    position: List[Position]  # lista budynków, a raczej pól
    id: int
    isCapital: bool
    islandId: int
    islandName: str
    islandXCoord: int
    islandYCoord: int
    name: str
    underContruction: int  # index pola gdzie się coś ulepsza
    startUpgradeTime: int  # kiedy zaczęto

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.isCapital = kwargs.get("isCapital")
        self.islandId = kwargs.get("islandId")
        self.islandName = kwargs.get("islandName")
        self.islandXCoord = kwargs.get("islandXCoord")
        self.islandYCoord = kwargs.get("islandYCoord")
        self.name = kwargs.get("name")
        self.underContruction = kwargs.get("underContruction", -1)
        self.startUpgradeTime = kwargs.get("startUpgradeTime", -1)
        self.position = [Position(**pos) for pos in kwargs.get("position", [])]


@dataclass
class curResources:
    citizens: float  # citizens < population ludzie nie w kopalniach itp
    population: float  # ludzie
    wood: int  # resource
    wine: int  # 1
    marble: int   # 2
    cristal: int  # 3
    sulfur: int  # 4

    def __init__(self, **kwargs):
        self.citizens = kwargs.get("citizens")
        self.population = kwargs.get("population")
        self.wood = kwargs.get("resource")
        self.wine = kwargs.get("1")
        self.marble = kwargs.get("2")
        self.cristal = kwargs.get("3")
        self.sulfur = kwargs.get("4")


@dataclass
class headerData:
    freeFreighters: int  # transportowce
    freeTransporters: int  # handlowe
    gold: str
    godGoldResult: float
    income: float
    maxActionPoints: int
    currentResources: curResources
    producedTradegood: int
    wineSpendings: int
    maxResources: int
    upkeep: float

    def __init__(self, **kwargs):
        self.freeFreighters = kwargs.get("freeFreighters")
        self.freeTransporters = kwargs.get("freeTransporters")
        self.gold = kwargs.get("gold")
        self.godGoldResult = kwargs.get("godGoldResult")
        self.income = kwargs.get("income")
        self.maxActionPoints = kwargs.get("maxActionPoints")
        self.producedTradegood = kwargs.get("producedTradegood")
        self.wineSpendings = kwargs.get("wineSpendings")
        self.maxResources = kwargs.get("maxResources", {"0":0})["0"]
        self.upkeep = kwargs.get("upkeep")
        self.currentResources = curResources(**kwargs.get("currentResources"))


@dataclass
class UpdateData:
    actionRequest: str
    backgroundData: backGroundData
    headerdata: headerData

    def __init__(self, **kwargs):
        self.actionRequest = kwargs.get("actionRequest")
        self.backgroundData = backGroundData(**kwargs.get("backgroundData"))
        self.headerdata = headerData(**kwargs.get("headerData"))



@dataclass
class SendResources:
    destCityId: int
    destIslandId: int
    transporters: int
    freighters: int
    capacity: int  # od 1 do 5 jako ładowność
    wood: int
    wine: int
    marble: int
    cristal: int
    sulfur: int

    def __init__(self, destCityId=-1, destIslandId=-1, **kwargs):
        self.destCityId = destCityId
        self.destIslandId = destIslandId
        self.transporters = kwargs.get("transporters", 0)
        self.freighters = kwargs.get("freighters", 0)
        self.capacity = kwargs.get("capacity", 5)
        self.wood = kwargs.get("wood", 0)
        self.wine = kwargs.get("wine", 0)
        self.marble = kwargs.get("marble", 0)
        self.cristal = kwargs.get("cristal", 0)
        self.sulfur = kwargs.get("sulfur", 0)
