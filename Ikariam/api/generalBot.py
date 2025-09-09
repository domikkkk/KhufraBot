from typing import List, Optional, Dict, Union
from Ikariam.api.session import ExpiredSession, IkaBot, ensure_action_request
import requests
from http.client import IncompleteRead
from Ikariam.dataStructure import Attack, Attacks, Fleets, Troops
from Ikariam.api.htmlparser import get_attacks, get_units


def ensure_embassy(func):
    def wrapper(self, *args, **kwargs):
        if self.embassy_position == -1:
            if not self.find_embassy():
                raise ValueError("Nie znaleziono ambasady!")
        return func(self, *args, **kwargs)
    return wrapper


class General(IkaBot):
    def __init__(self, cookie, server: int) -> None:
        super().__init__(cookie, server)
        self.embassy_position: int = -1
        self.occupy = {}
        self.open_battle = {}
        self.station = {}

    @ensure_embassy
    def get_attacks_to_Ally(self) -> Optional[List[Attack]]:
        data = {
            "view": "embassyGeneralAttacksToAlly",
            "cityId": self.current_city_id,
            "position": self.embassy_position,
            "activeTab": "tabEmbassy",
            "backgroundView": "city",
            "currentCityId": self.current_city_id, 
            "templateView": "embassy",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        response = [[0, [0]]]
        try:
            response = self.s.post(self.link, data=data).json()
            self.actionrequest = response[0][1]["actionRequest"]
            return get_attacks(response[1][1][1])
        except requests.exceptions.RequestException:
            return None
        except IncompleteRead:
            return None
        except TypeError:
            if response[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)

    @ensure_action_request
    def find_embassy(self) -> bool:
        ids = list(self.dict_of_cities.keys())
        for id in ids:
            if not self.dict_of_cities[id].is_own:
                continue
            self.change_city(id)
            position = self.find_building("embassy")
            if len(position) != 0:
                self.embassy_position = position[0]
                return True
        return True

    def get_attacks(self) -> Optional[Attacks]:
        attacks = self.get_attacks_to_Ally()
        if not attacks:
            return None
        occupy = []
        open_battle = []
        station = []
        for attack in attacks:
            if "open battle" in attack.action.lower():
                open_battle.append(attack)
            elif "occupy" in attack.action.lower() or "pillage" in attack.action.lower():
                occupy.append(attack)
            else:
                station.append(attack)
        return Attacks(occupy, open_battle, station)

    def analyse_attacks(self) -> List[Attack]:
        attacks = self.get_attacks()
        if not attacks:
            return []
        to_show = []
        for attack in attacks.occupy:
            if not attack in self.occupy:
                to_show.append(attack)
            self.occupy[attack] = True
        self.occupy = {attack: False for attack in self.occupy if self.occupy[attack]}
        return to_show

    @ensure_embassy
    def check_alliance_units(self, land=True) -> Dict[str, Optional[Union[Troops, Fleets]]]:
        data = {
            "view": "embassyGeneralTroops",
            "cityId": self.current_city_id,
            "position": self.embassy_position,
            "activeTab": "tabEmbassy" if land else "tabShips",
            "backgroundView": "city",
            "currentCityId": self.current_city_id,
            "templateView": "embassy",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        response = [[0, [0]]]
        try:
            response = self.s.post(self.link, data=data).json()
            self.actionrequest = response[0][1]["actionRequest"]
            return get_units(response[1][1][1], land)
        except requests.exceptions.RequestException:
            return None
        except IncompleteRead:
            return None
        except TypeError:
            if response[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
