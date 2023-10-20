import pandas as pd
import numpy as np
import os


LOGINHASLO = 'agrafia55@wp.plStefanek2020'
LOGINHASLOZAJMOWACZY = 'kontawuja@interia.plKontaWujka1234'


def get_data():
    sheets = pd.read_excel(os.getcwd() +\
        "/Ikariam/Podkupowacz/Podkupowacze_1.xlsx", sheet_name=None)
    x =  dict(dict(sheets.get(list(sheets.keys())[0])))
    del x["Unnamed: 3"]
    return x


class Excel:
    def __init__(self) -> None:
        self.sheet = get_data()
        keys = list(self.sheet.keys())
        self.ours = keys[3:6]
        self.theirs = keys[0:3]
        self.attention = keys[6]
        self.clear_from_nan()

    def clear_from_nan(self):
        for key in self.theirs + self.ours:
            self.sheet[key] = np.array([name for name in self.sheet[key] if str(name) != 'nan'])

    def get_rg_keepers(self):
        names = []
        for name in self.sheet[self.theirs[0]]:
            if str(name) != 'nan':
                 names.append(name)
        return list(sorted(set(names)))

    def find_potential_client(self, enemy_rg_name):
        zipped = zip(self.sheet[self.theirs[0]],
                     self.sheet[self.theirs[1]],
                     self.sheet[self.theirs[2]])
        res = []
        for name, cords, city_name in zipped:
            if podciąg(enemy_rg_name, name) / max(len(name),
                                                  len(enemy_rg_name)) > 0.7:
                res.append([name, cords, city_name] + self.find_ally(cords))
        return res

    def find_ally(self, cord):
        ans = []
        zipped = zip(self.sheet[self.ours[0]],
                     self.sheet[self.ours[1]],
                     self.sheet[self.ours[2]])
        for name, town_name, cor in zipped:
            if distance(cor, cord) < 4:
                return [name, town_name, cor]
        return ans

    def describe(self, enemy_rg_name):
        all = self.find_potential_client(enemy_rg_name)
        if not all:
            return 'Brak danych o tej skarbonce'
        res = ""
        for i in all:
            res += f"{' '.join(i[:3])} => Loguj {' '.join(i[3:])}\n"
        return res[:-1]


def distance(isl1: str, isl2: str):
    x1, y1 = isl1.split(';')
    x2, y2 = isl2.split(';')
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    return ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)


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


# e = Excel()
# print(e.describe('dabem'))
