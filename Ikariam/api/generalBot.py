from typing import List, Optional
from Ikariam.api.session import ExpiredSession, IkaBot, ensure_action_request
from bs4 import BeautifulSoup
import requests
from http.client import IncompleteRead
from dataclasses import dataclass
import re
import time


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


def get_date(html):
    script_tag = html.find('script', string=True).get_text()
    match = re.search(r'enddate:\s*(\d+)', script_tag)
    return int(match.group(1))


def clean_whitespace(text):
    return re.sub(r'\s+', ' ', text.strip())


def get_attacks(html) -> List[Attack]:
    soup = BeautifulSoup(html, 'html.parser')
    mainview = soup.find('div', id='mainview')
    table = mainview.find('table', class_="embassyTable")
    attacks = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        date = get_date(cells[0])
        who = Player(*[clean_whitespace(x.text) for x in cells[3].find_all('a', class_="bold")])
        whom = Player(*[clean_whitespace(x.text) for x in cells[4].find_all('a', class_="bold")])
        attack = Attack(date, cells[1].text.strip(), cells[2].text.strip(), who, whom)
        attacks.append(attack)
    return attacks


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
            with open("res.html", 'w') as f:
                f.write(response[1][1][1])
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
    def find_embassy(self):
        ids = list(self.dict_of_cities.keys())
        cities = len(ids)
        i = 0
        while cities > 0:
            try:
                cityId = ids[i]
                data = self.change_city(cityId)
                positions = data["backgroundData"]["position"]
                i += 1
                cities -= 1
            except Exception:
                continue
            finally:
                time.sleep(1)
            for position, building in enumerate(positions):
                if building["building"] == "embassy":
                    self.embassy_position = position
                    return True
        return False

    def get_attacks(self) -> Optional[Attacks]:
        attacks = self.get_attacks_to_Ally()
        if not attacks:
            return None
        attacks = Attacks(
            [attack for attack in attacks if "occupy" in attack.action.lower() or "pillage" in attack.action.lower()],
            [attack for attack in attacks if "open battle" in attack.action.lower()],
            [attack for attack in attacks if "station" in attack.action.lower()]
        )
        return attacks

    def analize_attacks(self) -> List[Attack]:
        attacks = self.get_attacks()
        to_show = []
        for attack in attacks.occupy:
            if not attack in self.occupy:
                to_show.append(attack)
            self.occupy[attack] = True
        self.occupy = {attack: False for attack in self.occupy if self.occupy[attack]}
        return to_show
