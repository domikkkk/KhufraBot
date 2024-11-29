import json
import numpy as np
from typing import List, Optional, Dict, Tuple
import copy
from dataclasses import dataclass


@dataclass(frozen=True)
class Pos:
    x: int
    y: int


@dataclass(frozen=True)
class City:
    id: int
    name: str
    level: int
    ownerId: int
    owenrName: str
    AllyId: int
    AllyTag: str=None
    state: str=None


@dataclass(frozen=True)
class Player:
    name: str
    id: int
    cities: List[City]


@dataclass()
class Island:
    id: int
    name: str
    cities: List[City]
    pos: Pos


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
        self.players: Dict[str|List[Pos]] = {}
        self.different_letters = {
            'с': 'c',
            'і': 'i'
        }

    def read_file(self):
        return read_file(self.filename)

    def scan_map(self):
        self.players: Dict[str|List[Pos]] = {}
        map = read_file(self.filename)
        self.map: Dict[Pos|Island] = {}
        self.cities: Dict[int|Pos] = {}
        for x in map:
            for y in map[x]:
                pos = Pos(x, y)
                island = Island(map[x][y]["id"], map[x][y]["name"], None, pos)
                cities = []
                for city in map[x][y]["cities"]:
                    if city["ownerName"] not in self.players:
                        self.players[city["ownerName"]] = []
                    self.players[city["ownerName"]].append(pos)
                    self.cities[city["id"]] = pos
                    cities.append(City(
                        city["id"],
                        city["name"],
                        city["level"],
                        city["ownerId"],
                        city["ownerName"],
                        city["ownerAllyId"],
                        AllyTag=city.get("ownerAllyTag", ''),
                        state=city.get("state", '')
                    ))
                island.cities = cities
                self.map[pos] = island
        for player in self.players:
            self.players[player] = list(set(self.players[player]))

    def get_coords(self, nick) -> List[Tuple[str|List[Pos]]]:
        respond = []
        nick = self.get_mapped(nick)
        for player in self.players:
            score = podciąg(player, nick) / max(len(player), len(nick))
            if score > 0.85:
                respond.append((player, ["{}:{}".format(pos.x, pos.y) for pos in self.players[player]], score))
        respond.sort(key=lambda x: x[2], reverse=True)
        return respond

    def get_cities_from_island(self, x, y, *, ally='') -> Optional[Island]:
        island: Island = copy.deepcopy(self.map.get(Pos(x, y), None))
        if ally != '':
            cities = [city for city in island.cities if ally.lower() in self.get_mapped(city.AllyTag)]
            island.cities = cities
        return island

    def get_mapped(self, string: str):
        copy = ''
        for letter in string.lower():
            copy += self.different_letters.get(letter, letter)
        return copy.lower()
