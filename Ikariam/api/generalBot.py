from typing import List, Optional, Dict, Union
from Ikariam.api.session import ExpiredSession, IkaBot, ensure_action_request
from bs4 import BeautifulSoup, Tag
import requests
from http.client import IncompleteRead
from Ikariam.dataStructure import Attack, Attacks, Fleets, Troops, Player
import re
import time


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
        row: Tag
        if "No members of your alliance are being attacked at the moment." in row.text:
            break
        cells = row.find_all('td')
        date = get_date(cells[0])
        who = Player(*[clean_whitespace(x.text) for x in cells[3].find_all('a', class_="bold")])
        whom = Player(*[clean_whitespace(x.text) for x in cells[4].find_all('a', class_="bold")])
        attack = Attack(date, cells[1].text.strip(), cells[2].text.strip(), who, whom)
        attacks.append(attack)
    return attacks


def get_units(html, land=True) -> Dict[str, Optional[Union[Troops, Fleets]]]:
    soup = BeautifulSoup(html, 'html.parser')
    mainview = soup.find('div', id='mainview')
    tables = mainview.find_all('table', class_="table01 embassyTable troops")
    obj = Troops if land else Fleets
    units = {}
    for table in tables:
        for row in table.find_all('tr')[1:-1]:
            player_name = row.find('td', class_='left').find('a').get_text(strip=True)
            if not player_name in units:
                units[player_name] = []
            for td in row.find_all('td', class_='right'):
                units[player_name].append(int(td.get_text(strip=True).replace(',', '')))
    units = {name: obj(*units[name]) for name in units}
    return units


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
