import requests
import numpy as np
from bs4 import BeautifulSoup


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


def get_fleet(html):
    soup = BeautifulSoup(html, 'html.parser')
    tab_ships_div = soup.find('div', id='tabShips')
    content = tab_ships_div.find_all('div', class_='contentBox01h')[0]
    tables = content.find_all('table', class_='militaryList') if tab_ships_div else []
    ships_data = {}
    for table in tables:
        header_row = table.find('tr', class_='title_img_row')
        # print(header_row, end='\n\n\n')
        headers = header_row.find_all('div', class_='tooltip') if header_row else []
        ships = [(header.text, header.find_parent('div').get('class')[1][1:]) for header in headers]
        count_row = table.find('tr', class_='count')
        counts = [int(td.text.strip()) for td in count_row.find_all('td')[1:]]
        for (name, ship_id), count in zip(ships, counts):
            ships_data[name] = {'id': ship_id, 'count': count}
    return ships_data


def get_fleet_foreign(html):
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find_all('div', class_='contentBox01h')[0]
    row_troops = content.find_all('td', class_='rowTroop')
    units = []
    for row in row_troops:
        army_buttons = row.find_all('div', class_='fleetbutton')
        for button in army_buttons:
            unit_name = button.get('title')
            unit_count = int(button.text.strip())
            units.append((unit_name, unit_count))
    return units


class IkaBot:
    def __init__(self, cookie) -> None:
        self.s = requests.Session()
        self.index = "https://s62-pl.ikariam.gameforge.com/index.php"
        self.link = "https://s62-pl.ikariam.gameforge.com"
        self.s.headers = {
            "cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }
        self.actionrequest = ''
        self.dict_of_cities = {}
        self.current_city_id = -1
        self.own_city_type = 'cityMilitary'
        self.foreign_city_type = "relatedCities"

    def set_action_request(self):
        data = {
            "highscoreType": "score", #"army_score_main",  # score
            "offset": -1,
            "view": "highscore",
            "sbm": "Submit",
            "searchUser": 'Furi',
            "backgroundView": "city",
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
            self.is_own = y[0][1]["headerData"]["relatedCity"]["owncity"]
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
            self.dict_of_cities[city_id] = city

    def get_island_id(self, x, y):
        data = {
            "action": "WorldMap",
            "function": "getJSONArea",
            "x_min": x,
            "x_max": x,
            "y_min": y,
            "y_max": y,
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.index, data=data)
            temp = res.json()
            temp = temp["data"]
            if len(temp) < 1:
                return -1
            island_id = temp[str(x)][str(y)][0]
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return int(island_id)

    def get_island_info(self, island_id):
        if island_id < 0:
            return None
        data = {
            "view": "updateGlobalData",
            "islandId": island_id,
            "backgroundView": "island",
            "currentIslandId": island_id,
            "actionRequest": self.actionrequest,
            "ajax": 1   
        }
        y = [[0, [0]]]
        try:
            x = self.s.post(self.index, data=data)
            y = x.json()
            cities = y[0][1]["backgroundData"]["cities"]
        except TypeError:
            if y[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)
        return cities

    def change_city(self, target_city_id):
        data = {
            "action": "header",
            "function": "changeCurrentCity",
            "actionRequest": self.actionrequest,
            "oldView": "city",
            "cityId": target_city_id,
            "currentCityId": self.current_city_id,
            "backgroundView": "city",
            "ajax": 1
        }
        temp = [[0, [0]]]
        try:
            res = self.s.post(self.index, data=data)
            temp = res.json()
            temp = temp[0][1]
            self.actionrequest = temp["actionRequest"]
            self.current_city_id = target_city_id
        except TypeError:
            if temp[0][1][0] == "error":
                raise ExpiredSession
        except Exception as e:
            print(e)

    def get_city_units(self, city_id):
        data = {
            "view": self.own_city_type if self.dict_of_cities[city_id]["relationship"] else self.foreign_city_type,
            "activeTab": "tabShips",
            "cityId": city_id,
            "backgroundView": "city",
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
            