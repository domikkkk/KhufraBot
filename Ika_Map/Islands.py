import json
import numpy as np


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
        self.map = read_file(file)
        self.players = {}

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
        for player in self.players:
            score = podciąg(player, nick) / max(len(player), len(nick))
            if score > 0.85:
                respond.append((player, self.players[player], score))
        respond.sort(key=lambda x: x[2], reverse=True)
        return respond
