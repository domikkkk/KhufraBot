from Ikariam.api.session import IkaBot, ExpiredSession, ensure_action_request, podciąg
import json
import requests
from http.client import IncompleteRead
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import re


def extract_brackets(content):
    return re.findall(r'\[(.*?)\]', content)


@dataclass
class Rg_Keeper:
    rg: str
    palm: bool
    whose: str=None


class rgBot(IkaBot):
    def __init__(self, cookie, server) -> None:
        super().__init__(cookie, server)
        self.rg_keepers: Dict[str, Rg_Keeper] = {}

    @ensure_action_request
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

    def put_match(self, row: Tag):
        title = row.get('title')
        palmtree = True if 'This player is currently on vacation' == title or 'Gracz jest obecnie na urlopie' == title else False
        name = row.find('span', class_="avatarName").text
        if name in self.rg_keepers:
            if palmtree == self.rg_keepers[name].palm:
                return None
        rg = row.find('td', class_="score").get('title')
        res = None
        if name not in self.rg_keepers:
            self.rg_keepers[name] = Rg_Keeper(rg, palmtree)
        else:
            self.rg_keepers[name].rg = rg
            self.rg_keepers[name].palm = palmtree
            if not palmtree:
                res = [name, rg]
            else:
                res = [name, -1]
        return res

    def analize_page(self, html) -> List[List]:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', class_='table01 highscore')
        every_changed = []
        trs: List[Tag] = table.find_all('tr')
        for row in trs[1:]:
            res = self.put_match(row)
            if res is not None:
                owner_name = self.rg_keepers[res[0]].whose
                res.append(owner_name)
                every_changed.append(res)
        return every_changed

    def analize_rg(self, place, user=''):
        html = self.get_rg_highscore(place, user)
        if not html:
            return []
        every_changed = self.analize_page(html)
        return every_changed

    def guess_rg_holder(self, name) -> list[tuple[str, int]]:
        possibilities = []
        for rg_name in self.rg_keepers.keys():
            score = podciąg(rg_name, name) / max(len(rg_name), len(name))
            if score > 0.85:
                possibilities.append((rg_name, score))
        possibilities.sort(key=lambda x: x[1], reverse=True)
        return possibilities

    def load_owners(self, rg_keeper: str, owner: str) -> Tuple[Optional[Tuple], Optional[Tuple]]:
        rg_names = self.guess_rg_holder(rg_keeper)
        if len(rg_names) == 0:
            return None, (rg_keeper, owner)
        rg_name = rg_names[0][0]
        self.rg_keepers[rg_name].whose = owner
        return (owner, rg_name), None

    def save_as(self):
        with open("rg_info.json", "w") as f:
            json.dump(self.rg_keepers, f, indent=4)

    def get_ranking(self) -> Dict[str, int]:
        ranking: Dict[str, int] = {}
        for rg_keeper in self.rg_keepers.values():
            if not rg_keeper.whose:
                continue
            whose = extract_brackets(rg_keeper.whose)
            if not whose:
                continue
            rg = int(rg_keeper.rg.replace(',', ''))
            for every in whose:
                every = every.lower()
                if not every in ranking:
                    ranking[every] = 0
                ranking[every] += rg
        return dict(sorted(ranking.items(), key=lambda item: item[1], reverse=True))
