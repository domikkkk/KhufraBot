import requests
import json
import re
from http.client import IncompleteRead


class session:
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
        x = self.s.post(self.index, data=data)
        try:
            x = x.json()
        except Exception:
            raise Exception("Bruh")
        self.actionrequest = x[0][1]["actionRequest"]


class rgBot(session):
    def __init__(self, cookie) -> None:
        super().__init__(cookie)
        self.rg_info = {}

    def get_rg_highscore(self, place, user=''):
        data = {
            "highscoreType": "army_score_main",  # score
            "offset": place,
            "view": "highscore",
            "sbm": "Submit",
            "searchUser": user,
            "backgroundView": "city",
            "currentCityId": '',
            "templateView": "highscore",
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        try:
            x = self.s.post(self.index, data=data, timeout=(5, 10))
            print(x.status_code, end=' ')
            x = x.json()
        except requests.exceptions.RequestException as e:
            return None
        except IncompleteRead:
            return None
        self.actionrequest = x[0][1]['actionRequest']
        return x[1][1][1]

    def put_match(self, match):
        palmtree = True if 'This player is currently on vacation' or 'Gracz jest obecnie na urlopie' in match else False
        pattern = r"<span class='avatarName'>(.*?)</span>"
        name = re.findall(pattern, match, re.DOTALL)[0]
        if name in self.rg_info:
            if palmtree == self.rg_info[name]['palm']:
                return None
        pattern = r'<td class="score">(.*?)</td>'
        score = re.findall(pattern, match, re.DOTALL)[0]
        res = None
        if name not in self.rg_info:
            self.rg_info[name] = {
                "score": score,
                "palm": palmtree
            }
        else:
            if not palmtree:
                res = (name, self.rg_info[name]["score"])
            else:
                res = (name, -1)
                self.rg_info[name] = {
                    "score": score,
                    "palm": palmtree
                }
        return res

    def analize_rg(self, top=200, user=''):
        if self.actionrequest == '':
            self.set_action_request()
            print(self.actionrequest)
        pattern = r'<tr class="[^"]*".*?</tr>'
        every_not_on_palm = []
        i = 0
        while i < int(top // 50):
            html = self.get_rg_highscore(i * 50, user)
            if not html:
                print("Error while downloading data is detected. Contining...")
                continue
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                res = self.put_match(match)
                if res is not None:
                    every_not_on_palm.append(res)
            if len(matches) < 50:
                break
            i += 1
        print()
        return every_not_on_palm

    def save_as(self):
        with open("rg_info.json", "w") as f:
            json.dump(self.rg_info, f, indent=4)


class IkaBot(session):
    def __init__(self, cookie) -> None:
        super().__init__(cookie)

    def update_data(self, city_id):
        data = {
            "view": "updateGlobalData",
            "cityId": city_id,
            "backgroundView": "city",
            "currentCityId": city_id,
            "actionRequest": self.actionrequest,
            "ajax": 1
        }
        x = self.s.post(self.link, data=data)
        try:
            x = x.json()
        except Exception:
            raise Exception("Bruh")
