from dataclasses import dataclass, field
from typing import List, Any, Dict


HEPHAEUSTUS = "1"
HADES = "2"
DEMETER = "3"
ATHENA = "4"
HERMES = "5"
ARES = "6"
POSEIDON = "7"
COLOSSUS = "8"


WINE = "1"
MARBLE = "2"
CRISTAL = "3"
SULFUR = "4"


CITY_VIEW = "city"
CITY_VIEW_TEMPLATE = "townHall"
ISLAND_VIEW = "island"
ISLAND_VIEW_TEMPLATE = ""


TEMPLE = "temple"
WONDER = "wonder"
EMBASSY = "embassy"

MIL_VIEW = "cityMilitary"
RELATED_CITY = "relatedCities"



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
    # extra: List[Any]

    def __init__(self, kwargs: dict):
        self.id: int = kwargs.get("id")
        self.name: str = kwargs.get("name")
        self.coords: str = kwargs.get("coords")
        self.tradegood: int = kwargs.get("tradegood")
        self.is_own: bool = kwargs.get("is_own")
        # self.extra: List[Any] = List(kwargs.values())  # Wszystko``


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

    def __init__(self, kwargs: dict):
        self.type = kwargs.get("type")
        self.name = kwargs.get("name")
        self.id = kwargs.get("id")
        self.level = kwargs.get("level")
        self.ownerId = kwargs.get("ownerId")
        self.ownerName = kwargs.get("ownerName")
        self.ownerAllyId = kwargs.get("ownerAllyId")
        self.ownerAllyTag = kwargs.get("ownerAllyTag")
        self.state = kwargs.get("state")


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

    def __init__(self, kwargs: dict):
        self.building = kwargs.get("building")  # nazwa po ang
        self.name = kwargs.get("name")  # nazwa w języku
        self.buildingId = kwargs.get("buildingId")  # id budynku
        self.canUpgrade = kwargs.get("canUpgrade")  # czy można ulepszyć
        self.level = kwargs.get("level")  # lv budynku
        self.groundId = kwargs.get("groundId") # useless


@dataclass
class backGroundData:
    position: List[Position]  # lista budynków, a raczej pól
    id: int  # id miasta, wyspy?
    isCapital: bool
    islandId: int  # id wyspy
    islandName: str  # nazwa wyspy
    islandXCoord: int  # x
    islandYCoord: int  # y
    name: str  # nazwa miasta albo wyspy, zależy od poglądu
    underContruction: int  # index pola gdzie się coś ulepsza
    startUpgradeTime: int  # kiedy zaczęto

    # Dane z wyspy
    cities: List[CityIsland]  # miasta na wyspie
    island: int  # id wyspy
    tradegood: int
    type: int  # typ wyspy?
    wonder: str  # rodzaj cudu
    wonderLevel: int  # lv cudu
    wonderName: str  # nazwa po chuj?



    def __init__(self, kwargs: dict):
        self.id = kwargs.get("id", -1)
        self.isCapital = kwargs.get("isCapital")
        self.islandId = kwargs.get("islandId")
        self.islandName = kwargs.get("islandName")
        self.islandXCoord = kwargs.get("islandXCoord")
        self.islandYCoord = kwargs.get("islandYCoord")
        self.name = kwargs.get("name")
        self.underContruction = kwargs.get("underConstruction", -1)
        self.startUpgradeTime = kwargs.get("startUpgradeTime", -1)
        self.position = [Position(pos) for pos in kwargs.get("position", [])]

        self.cities = [CityIsland(city) for city in kwargs.get("cities", [])]
        self.island = kwargs.get("island", -1)
        self.tradegood = kwargs.get("tradegood")
        self.type = kwargs.get("type")
        self.wonder = kwargs.get("wonder")
        self.wonderLevel = int(kwargs.get("wonderLevel", -1))
        self.wonderName = kwargs.get("wonderName")


@dataclass
class curResources:
    citizens: float  # citizens < population ludzie nie w kopalniach itp
    population: float  # ludzie
    wood: int  # resource
    wine: int  # 1
    marble: int   # 2
    cristal: int  # 3
    sulfur: int  # 4

    def __init__(self, kwargs: dict):
        self.citizens = kwargs.get("citizens")
        self.population = kwargs.get("population")
        self.wood = kwargs.get("resource")
        self.wine = kwargs.get(WINE)
        self.marble = kwargs.get(MARBLE)
        self.cristal = kwargs.get(CRISTAL)
        self.sulfur = kwargs.get(SULFUR)


@dataclass
class headerData:
    freeFreighters: int  # transportowce
    freeTransporters: int  # handlowe
    gold: float
    godGoldResult: float
    income: float
    maxActionPoints: int
    currentResources: curResources
    producedTradegood: int
    wineSpendings: int
    maxResources: int
    upkeep: float

    def __init__(self, kwargs: dict):
        self.freeFreighters = kwargs.get("freeFreighters")
        self.freeTransporters = kwargs.get("freeTransporters")
        self.gold = float(kwargs.get("gold", "0"))
        self.godGoldResult = kwargs.get("godGoldResult")
        self.income = kwargs.get("income")
        self.maxActionPoints = kwargs.get("maxActionPoints")
        self.producedTradegood = kwargs.get("producedTradegood")
        self.wineSpendings = kwargs.get("wineSpendings")
        self.maxResources = kwargs.get("maxResources", {"0":0})["0"]
        self.upkeep = kwargs.get("upkeep")
        self.currentResources = curResources(kwargs.get("currentResources"))


@dataclass
class UpdateData:
    actionRequest: str
    backgroundData: backGroundData
    headerdata: headerData

    def __init__(self, kwargs: dict):
        if isinstance(kwargs, list):
            return
        self.actionRequest = kwargs.get("actionRequest")
        self.backgroundData = backGroundData(kwargs.get("backgroundData"))
        self.headerdata = headerData(kwargs.get("headerData"))
    

    # Dorobić w backgrounddate dane jak mamy widok wyspy

@dataclass
class SendResources:
    destCityId: int | None = None
    destIslandId: int | None = None
    transporters: int = 0
    freighters: int = 0
    capacity: int = 5  # od 1 do 5 jako ładowność
    wood: int = 0
    wine: int = 0
    marble: int = 0
    cristal: int = 0
    sulfur: int = 0

    def __post_init__(self):
        assert self.wood + self.wine + self.marble + self.cristal + self.sulfur <= (
            self.transporters * 500 + self.freighters * 50000
        ) * self.capacity / 5, "Can't send"


@dataclass
class PlantColony(SendResources):
    desiredPosition: int = field(default=0)
        