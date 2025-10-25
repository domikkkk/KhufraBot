from typing import List, Optional, Dict, Union
from Ikariam.api.session import ExpiredSession, IkaBot, ensure_action_request
import requests
from http.client import IncompleteRead
from Ikariam.dataStructure import Attack, Attacks, Fleets, Troops, EMBASSY, CITY_VIEW
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

    @ensure_action_request
    def find_embassy(self) -> bool:
        ids = list(self.dict_of_cities.keys())
        for id in ids:
            if not self.dict_of_cities[id].is_own:
                continue
            self.change_city(id)
            position = self.find_building(EMBASSY)
            if len(position) != 0:
                self.embassy_position = position[0] # at most one embassy in city
                return True
        return False

    @ensure_embassy
    def get_attacks_to_Ally(self) -> Optional[List[Attack]]:
        data = {
            "view": "embassyGeneralAttacksToAlly",
            "cityId": self.current_city_id,
            "position": self.embassy_position,
            "activeTab": "tabEmbassy",
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id, 
            "templateView": EMBASSY,
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if self._send_request(data, get_html=True):
            return get_attacks(self.html[1])

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
        # occupation
        new_attacks = []
        for attack in attacks.occupy:
            if not attack in self.occupy:
                new_attacks.append(attack)
            self.occupy[attack] = True
        self.occupy = {attack: False for attack in self.occupy if self.occupy[attack]}
        # open battle
        for attack in attacks.open_battle:
            self.open_battle[attack] = True
        self.open_battle = {attack: False for attack in self.open_battle if self.open_battle[attack]}
        # station
        for attack in attacks.station:
            self.station[attack] = True
        self.station = {attack: False for attack in self.station if self.station[attack]}

        return new_attacks

    @ensure_embassy
    def check_alliance_units(self, land=True) -> Dict[str, Optional[Union[Troops, Fleets]]]:
        data = {
            "view": "embassyGeneralTroops",
            "cityId": self.current_city_id,
            "position": self.embassy_position,
            "activeTab": "tabEmbassy" if land else "tabShips",
            "backgroundView": CITY_VIEW,
            "currentCityId": self.current_city_id,
            "templateView": EMBASSY,
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        if self._send_request(data, get_html=True):
            return get_units(self.html[1])
