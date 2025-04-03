from typing import Dict, Optional, List
import requests
import numpy as np
from functools import wraps
from Ikariam.dataStructure import City, CityIsland, UpdateData, SendResources
from Ikariam.dataStructure import HEPHAEUSTUS, CITY_VIEW, ISLAND_VIEW
from Ikariam.api.htmlparser import get_fleet, get_fleet_foreign
import time


class ExpiredSession(Exception):
    def __init__(self) -> None:
        super().__init__("Potrzebujesz nowej sesji")


def podciąg(s1: str, s2: str):
    s1 = s1.lower()
    s2 = s2.lower()
    m = len(s1)
    n = len(s2)
    L = np.zeros((m+1, n+1))
    for i in range(m):
        for j in range(n):
            if s1[i] == s2[j]:
                L[i+1, j+1] = 1 + L[i, j]
            else:
                L[i+1, j+1] = max(L[i+1, j], L[i, j+1])
    return L[m, n]


def ensure_action_request(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.actionrequest:
            self.set_action_request()
        return func(self, *args, **kwargs)
    return wrapper


class IkaBot:
    def __init__(self, cookie, server: int) -> None:
        self.s = requests.Session()
        self.index = f"https://s{server}-pl.ikariam.gameforge.com/index.php"
        self.link = f"https://s{server}-pl.ikariam.gameforge.com"
        self.s.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "Host": f"s{server}-pl.ikariam.gameforge.com",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Mode": "navigate",
            "Upgrade-Insecure-Requests": "1"
        }
        self.actionrequest: str = None
        self.dict_of_cities: Dict[int, City] = {}
        self.current_city_id: int = -1
        self.own_city_type = 'cityMilitary'
        self.foreign_city_type = "relatedCities"
        self.temple_positions: Dict[int, int] = {}
        self.data: UpdateData = None

    def set_action_request(self):
        data = {
            "highscoreType": "score", #"army_score_main",  # score
            "offset": -1,
            "view": "highscore",
            "sbm": "Submit",
            "searchUser": 'Furi',
            "backgroundView": CITY_VIEW,
            "currentCityId": '',
            "templateView": "highscore",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        y = [[0, [0]]]
        try:
            x = self.s.post(self.index, data=data)
            y = x.json()
            self.actionrequest = y[0][1]["actionRequest"]
            cities = y[0][1]["headerData"]["cityDropdownMenu"]
            self.update_cities(cities)
        except TypeError:
            if y[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)

    def update_cities(self, cities: dict):
        self.dict_of_cities = {}
        self.current_city_id = cities[cities["selectedCity"]]["id"]
        for city in cities.values():
            if not isinstance(city, dict):
                continue
            city_id = int(city["id"])
            city["relationship"] = city["relationship"] == "ownCity"
            self.dict_of_cities[city_id] = City(*city.values())

    @ensure_action_request
    def get_islands(self, x, y, radius=0):
        data = {
            "action": "WorldMap",
            "function": "getJSONArea",
            "x_min": x - radius,
            "x_max": x + radius,
            "y_min": y - radius,
            "y_max": y + radius,
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.index, data=data)
            temp = res.json()
            temp = temp["data"]
            return temp
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return None

    def get_island_id(self, x, y):
        island = self.get_islands(x, y, radius=0)
        if len(island) < 1:
                return -1
        island_id = island[str(x)][str(y)][0]
        return int(island_id)

    @ensure_action_request
    def get_island_info(self, island_id) -> Optional[List[CityIsland]]:
        if island_id < 0:
            return None
        data = {
            "view": "updateGlobalData",
            "islandId": island_id,
            "backgroundView": ISLAND_VIEW,
            "currentIslandId": island_id,
            "actionRequest": self.actionrequest,
            "ajax": 1   
        }
        y = [[0, [0]]]
        try:
            x = self.s.post(self.index, data=data)
            y = x.json()
            self.data = UpdateData(**y[0][1])
            return self.data.backgroundData.cities
        except TypeError:
            if y[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)

    @ensure_action_request
    def find_building(self, name: str) -> List[int]:
        # data = self.change_city(self.current_city_id)
        result: List[int] = []
        for i, position in enumerate(self.data.backgroundData.position):
            if position.building == name:
                result.append(i)
        return result

    @ensure_action_request
    def change_city(self, target_city_id) -> Optional[UpdateData]:
        data = {
            "action": "header",
            "function": "changeCurrentCity",
            "actionRequest": self.actionrequest,
            "oldView": CITY_VIEW,
            "cityId": target_city_id,
            "currentCityId": self.current_city_id,
            "backgroundView": CITY_VIEW,
            "ajax": 1
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.index, data=data)
            temp = res.json()
            self.data = UpdateData(**temp[0][1])
            self.actionrequest = self.data.actionRequest
            self.current_city_id = target_city_id
            return self.data
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return None

    @ensure_action_request
    def upgrade_building(self, position, old_level, building_name) -> Optional[UpdateData]:
        data = {
            "action": "CityScreen",
            "function": "upgradeBuilding",
            "actionRequest": self.actionrequest,
            "cityId": self.current_city_id,
            "position": position,
            "level": old_level,
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "templateView": building_name,
            "ajax": 1
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.link, data=data)
            temp = res.json()
            self.data = UpdateData(**temp[0][1])
            self.actionrequest = self.data.actionRequest
            return self.data
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return None

    @ensure_action_request
    def send_resources(self, param: SendResources) -> Optional[UpdateData]:
        data = {
            "action": "transportOperations",
            "function": "loadTransportersWithFreight",
            "destinationCityId": param.destCityId,
            "islandId": param.destIslandId,
            "transportDisplayPrice": 0,
            "premiumTransporter": 0,
            "normalTransportersMax": param.transporters,
            "usedFreightersShips": param.freighters,
            "cargo_resource": param.wood,
            "cargo_tradegood1": param.wine,
            "cargo_tradegood2": param.marble,
            "cargo_tradegood3": param.cristal,
            "cargo_tradegood4": param.sulfur,
            "capacity": param.capacity,
            "max_capacity": 5,
            "jetPropulsion": 0,
            "transporters": param.transporters,
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "templateView": "transport",
            "currentTab": "tabSendTransporter",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.index, data=data)
            temp = res.json()
            self.data = UpdateData(**temp[0][1])
            self.actionrequest = self.data.actionRequest
            return self.data
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return None

    @ensure_action_request
    def activate_miracle(self, type: str=HEPHAEUSTUS) -> Optional[UpdateData]:

        ## pewnie przelecieć po miastach i znaleźć, te którę się zgadzają z rodzajem cudu i znaleźć przy okazji największy lv
        data = {
            "action": "CityScreen",
            "cityId": self.current_city_id,
            "function": "activateWonder",
            "position": 3,
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "templateView": "temple",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }


    @ensure_action_request
    def get_city_units(self, city_id: int):
        data = {
            "view": self.own_city_type if self.dict_of_cities[city_id].is_own else self.foreign_city_type,
            "activeTab": "tabShips",
            "cityId": city_id,
            "backgroundView": CITY_VIEW,
            "currentCityId": city_id,
            "currentTab": "tabShips",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.index, data=data)
            temp = res.json()
            return get_fleet(temp[1][1][1])
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return None
            