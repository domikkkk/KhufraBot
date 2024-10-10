from Ikariam.api.session import IkaBot, ExpiredSession, podciąg
import json
import requests
import re
from http.client import IncompleteRead


class rgBot(IkaBot):
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
        y = [[0, [0]]]
        try:
            x = self.s.post(self.index, data=data, timeout=(5, 10))
            y = x.json()
            self.actionrequest = y[0][1]['actionRequest']
            return y[1][1][1]
        except requests.exceptions.RequestException:
            return None
        except IncompleteRead:
            return None
        except TypeError:
            if y[0][1][0] == "error":
                raise ExpiredSession
            return None
        except Exception:
            return None
        

    def put_match(self, match):
        palmtree = True if 'This player is currently on vacation' in match or 'Gracz jest obecnie na urlopie' in match else False
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
                "palm": palmtree,
                "whose": None
            }
        else:
            if not palmtree:
                res = [name, score]
            else:
                res = [name, -1]
            self.rg_info[name]["score"] = score
            self.rg_info[name]["palm"] = palmtree
        return res

    def analize_rg(self, top=200, user=''):
        if self.actionrequest == '':
            self.set_action_request()
        pattern = r'<tr class="[^"]*".*?</tr>'
        every_not_on_palm = []
        i = 0
        while i < int(top) // 50:
            html = self.get_rg_highscore(i * 50, user)
            if not html:
                continue
            matches = re.findall(pattern, html, re.DOTALL)
            for match in matches:
                res = self.put_match(match)
                if res is not None:
                    owner_name = self.rg_info[res[0]]["whose"]
                    res.append(owner_name)
                    every_not_on_palm.append(res)
            if len(matches) < 50:
                break
            i += 1
        return every_not_on_palm

    def guess_rg_holder(self, name):
        for rg_name in self.rg_info.keys():
            if podciąg(rg_name, name) / max(len(rg_name), len(name)) > 0.85:
                return rg_name
        return None

    def load_owners(self, text: str):
        bugs = []
        for line in text.split('\n'):
            line1 = line.split(' - ')
            if len(line1) != 2:
                bugs.append(line)
                continue
            name, owner = line1
            rg_name = self.guess_rg_holder(name)
            if not rg_name:
                bugs.append(line)
                continue
            self.rg_info[rg_name]["whose"] = owner
        return bugs
            

    def save_as(self):
        with open("rg_info.json", "w") as f:
            json.dump(self.rg_info, f, indent=4)
