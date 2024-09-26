import requests
import json
import re


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
            "searchUser": '',
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
        x = self.s.post(self.index, data=data)
        try:
            x = x.json()
        except Exception:
            raise Exception("Bruh")
        self.actionrequest = x[0][1]['actionRequest']
        return x[1][1][1]

    def put_match(self, match):
        pattern = r'<span class="avatarName".*?</span>'
        name = re.findall(pattern, match, re.DOTALL)[0]
        pattern = r'<td class="score".*?</td>'
        score = re.findall(pattern, match, re.DOTALL)[0]
        palmtree = True if 'title="This player is currently on vacation"' in match else False
        if name not in self.rg_info:
            self.rg_info[name] = {
                "score": score,
                "palm": palmtree
            }
        else:
            palm = self.rg_info[name]["palm"]
            oldscore = self.rg_info[name]["score"]
            if not palm:
                self.send_warning(name, oldscore)
            self.rg_info[name] = {
                "score": score,
                "palm": palmtree
            }

    def analize_rg(self, top=200, user=''):
        if self.actionrequest == '':
            self.set_action_request()
        pattern = r'<tr class="[^"]*".*?</tr>'
        for i in range(int(top // 50)):
            html = self.get_rg_highscore(i * 50, user)
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                self.put_match(match)
            if len(matches) < 50:
                break

    def send_warning(self, name, oldscore):
        pass

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


if __name__ == "__main__":
    s = session("")
    s.get_action_request()
