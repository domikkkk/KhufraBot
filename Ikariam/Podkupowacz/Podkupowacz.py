import pandas as pd
import numpy as np
import os



CZAS_PLYNIECIA = 1200  # %s = 20min


def get_data():
    sheets = pd.read_excel(os.getcwd() +\
        "/Ikariam/Podkupowacz/Podkupowacze_1.xlsx", sheet_name=None)
    x =  dict(dict(sheets.get(list(sheets.keys())[0])))
    del x["Unnamed: 3"]
    return x


class Excel:
    def __init__(self) -> None:
        self.update()

    def update(self):
        self.sheet = get_data()
        keys = list(self.sheet.keys())
        self.ours = keys[3:6]
        self.theirs = keys[0:3]
        self.attention = keys[6]
        self.clear_from_nan()
        self.null_ally = ['\t  =>  Nie', 'ma nic', 'blisko. Trzeba skoczyć']
        return

    def clear_from_nan(self):
        for key in self.theirs + self.ours:
            self.sheet[key] = np.array([name for name in self.sheet[key] if str(name) != 'nan'])
        return

    def get_rg_keepers(self):
        names = []
        for name in self.sheet[self.theirs[0]]:
            if str(name) != 'nan':
                 names.append(name)
        return list(sorted(set(names)))

    def find_seller(self, enemy_rg_name):
        zipped = zip(self.sheet[self.theirs[0]],
                     self.sheet[self.theirs[1]],
                     self.sheet[self.theirs[2]])
        res = []
        for name, cords, city_name in zipped:
            if podciąg(enemy_rg_name, name) / max(len(name),
                                                  len(enemy_rg_name)) > 0.7:
                allies = self.find_allies(cords)
                if allies == []:
                    res.append([name, city_name, cords] + self.null_ally)
                    continue
                for ally in allies:
                    res.append([name, city_name, cords] + ally)
        return res

    def find_allies(self, cord):
        allies = []
        zipped = zip(self.sheet[self.ours[0]],
                     self.sheet[self.ours[1]],
                     self.sheet[self.ours[2]])
        for name, town_name, cor in zipped:
            if distance(cor, cord) < 3:
                if [name, town_name.lower(), cor] not in allies:
                    allies.append([name, town_name.lower(), cor])
        return allies
            

    def describe(self, enemy_rg_name):
        all = self.find_seller(enemy_rg_name)
        if not all:
            return 'Brak danych o tej skarbonce'
        ret = []
        for i in all:
            try:
                res = []
                dist = distance(i[2], i[5])
                t_time = round(dist * CZAS_PLYNIECIA)
                min_time, s_time = t_time // 60, t_time % 60
                res.append(f"{' '.join(i[:3]):<32} =>  Loguj {' '.join(i[3:]):<35}")
                res.append(f"\t  Śmig: {min_time if min_time != 0 else 10}min")
                res.append('\t' if s_time == 0 else f" {s_time}s")
                t_time = round(dist * CZAS_PLYNIECIA * 3 / 5)
                min_time, s_time = t_time // 60, t_time % 60
                res.append(f"  Handlowy: {min_time if min_time != 0 else 6}min")
                res.append('\n' if s_time == 0 else f" {s_time}s\n")
                ret.append(res)
            except Exception:
                ret.append(i)
        ret = sorted(ret, key=lambda x: x[-2])
        return ''.join([' '.join(i) for i in ret])


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
# print(e.describe("vandall"))
