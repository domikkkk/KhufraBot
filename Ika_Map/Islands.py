import json
import numpy as np
from typing import Optional, Dict
import copy
import re


def read_file(filename):
    with open(filename, 'r') as f:
        res = json.load(f)
    return res


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


class Map:
    def __init__(self, file) -> None:
        self.filename = file
        self.read_file()
        self.players = {}
        self.different_letters = {
            'с': 'c',
            'і': 'i'
        }

    def read_file(self):
        self.map: Dict = read_file(self.filename)

    def scan_players(self):
        self.players = {}
        for x in self.map:
            for y in self.map[x]:
                for city in self.map[x][y]["cities"]:
                    if city["ownerName"] not in self.players:
                        self.players[city["ownerName"]] = []
                    self.players[city["ownerName"]].append(f"{x}:{y}")
        for player in self.players:
            self.players[player] = list(set(self.players[player]))

    def get_coords(self, nick):
        respond = []
        nick = self.get_mapped(nick)
        for player in self.players:
            score = podciąg(player, nick) / max(len(player), len(nick))
            if score > 0.85:
                respond.append((player, self.players[player], score))
        respond.sort(key=lambda x: x[2], reverse=True)
        return respond

    def get_cities_from_island(self, x, y, *, ally='') -> Optional[Dict]:
        y_cords = self.map.get(str(x), None)
        if not y_cords:
            return None
        island = copy.deepcopy(y_cords.get(str(y), None))
        if not island:
            return None
        if ally != '':
            cities = [city for city in island['cities'] if ally.lower() in self.get_mapped(city.get("ownerAllyTag", ''))]
            island['cities'] = cities
        return island

    def get_mapped(self, string: str):
        copy = ''
        for letter in string.lower():
            copy += self.different_letters.get(letter, letter)
        return copy.lower()
