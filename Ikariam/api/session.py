from typing import Dict, Optional, List, Tuple
import requests
import numpy as np
from functools import wraps
from Ikariam.dataStructure import City, CityIsland, UpdateData, SendResources
from Ikariam.dataStructure import HEPHAEUSTUS, CITY_VIEW, ISLAND_VIEW, TEMPLE, RELATED_CITY, MIL_VIEW, WONDER
from Ikariam.api.htmlparser import get_fleet, get_fleet_foreign, get_wonder_lv
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
        self.current_island_id: int = -1
        self.temple_positions: Dict[int, int] = {}
        self.data: UpdateData = None
        self.html = None
        self.updateTemplateData = None
        self.wonders: Dict[str, Tuple[int]] = {}  # słownik cudów - [id miasta, pozycja świątyni]

    def _send_request(self,
                     data: Dict,
                     index: bool=True,
                     get_html: bool=False,
                     update_cities: bool=False
                     ) -> bool:
        result = [[0, [0]]]
        link = self.index if index else self.link
        time.sleep(0.5)
        try:
            result = self.s.post(link, data=data).json()
            self.data = UpdateData(**result[0][1])
            if self.data.actionRequest is not None:
                self.actionrequest = self.data.actionRequest
            if get_html:
                self.updateTemplateData = result[2][1]
                self.html = result[1][1]
            if update_cities:
                cities = result[0][1]["headerData"]["cityDropdownMenu"]
                self.update_cities(cities)
            return True
        except TypeError:
            if result[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return False

    def set_action_request(self) -> None:
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
        self._send_request(data, update_cities=True)

    def update_cities(self, cities: dict) -> None:
        self.dict_of_cities = {}
        self.current_city_id = cities[cities["selectedCity"]]["id"]
        self.current_island_id = self.data.backgroundData.islandId
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

    def get_island_id(self, x, y) -> int:
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
        if self._send_request(data):
            return self.data.backgroundData.cities

    @ensure_action_request
    def find_building(self, name: str) -> List[int]:  # list of positions of this building
        # data = self.change_city(self.current_city_id)
        result: List[int] = []
        for i, position in enumerate(self.data.backgroundData.position):
            if position.building == name:
                result.append(i)
        return result

    @ensure_action_request
    def change_city(self, target_city_id: int, view: str=CITY_VIEW) -> Optional[UpdateData]:
        data = {
            "action": "header",
            "function": "changeCurrentCity",
            "actionRequest": self.actionrequest,
            "oldView": view,
            "cityId": target_city_id,
            "currentCityId": self.current_city_id,
            "backgroundView": view,
            "templateView": "townHall",
            "ajax": 1
        }
        if self._send_request(data):
            self.current_city_id = target_city_id
            self.current_island_id = self.data.backgroundData.islandId
            return self.data

    @ensure_action_request
    def upgrade_building(self, position, old_level, building_name) -> Optional[UpdateData]:
        data = {
            "action": "UpgradeExistingBuildingn",
            "actionRequest": self.actionrequest,
            "cityId": self.current_city_id,
            "position": position,
            "level": old_level,
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "templateView": building_name,
            "ajax": 1
        }
        if self._send_request(data, index=False):
            return self.data

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
        if self._send_request(data):
            return self.data


    def find_highest_wonder_lv(self, wonder: str=HEPHAEUSTUS) -> bool:
        ids = list(self.dict_of_cities.keys())
        highest_lv = 0
        pos = -1
        for id in ids:
            if not self.dict_of_cities[id].is_own:
                continue
            self.change_city(id)
            result = self.find_building(TEMPLE)
            if len(result) == 0:
                continue
            pos = result[0]
            self.view_on_island(WONDER)
            if self.data.backgroundData.wonder == wonder:
                lv = get_wonder_lv(self.html[1])
                if highest_lv < lv:
                    highest_lv = lv
            if highest_lv == 5:
                break
        if pos != -1:
            self.wonders[wonder] = (self.current_city_id, pos)
            return True
        return False


    @ensure_action_request
    def view_on_island(self, view: str):
        data = {
            "view": view,
            "islandId:": self.current_island_id,
            "backgroundView": ISLAND_VIEW,
            "currentIslandId": self.current_island_id,
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if not self._send_request(data, index=False, get_html=True):
            print("Error")
    
    @ensure_action_request
    def view_building(self, view: str, pos: int) -> str:
        data = {
            "view": view,
            "cityId": self.current_city_id,
            "position": pos,
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if self._send_request(data, index=False, get_html=True):
            return self.html[1]


    @ensure_action_request
    def activate_miracle(self, wonder: str) -> Optional[UpdateData]:
        if wonder not in self.wonders:
            if not self.find_highest_wonder_lv(wonder):
                return None
        cityId, pos = self.wonders[wonder]
        if cityId != self.current_city_id:
            self.change_city(cityId)
        data = {
            "action": "CityScreen",
            "cityId": self.current_city_id,
            "function": "activateWonder",
            "position": pos,
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "templateView": TEMPLE,
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if self._send_request(data):
            return self.data
        return None

# ---------------------------------------------------------------------------------------

    @ensure_action_request
    def get_city_units(self, city_id: int):
        data = {
            "view": MIL_VIEW if self.dict_of_cities[city_id].is_own else RELATED_CITY,
            "activeTab": "tabShips",
            "cityId": city_id,
            "backgroundView": CITY_VIEW,
            "currentCityId": city_id,
            "currentTab": "tabShips",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if self._send_request(data, get_html=True):
            return get_fleet(self.html[1])
            