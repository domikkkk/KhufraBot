import pandas as pd
import numpy as np


def get_data():
    sheets = dict(pd.read_excel("Podkupowacze_1.xlsx", sheet_name=None))
    x =  dict(sheets.get(list(sheets.keys())[0]))
    del x["Unnamed: 3"]
    return x

class Excel:
    def __init__(self, sheet) -> None:
        self.sheet = sheet
        keys = list(sheet.keys())
        self.ours = keys[3:6]
        self.theirs = keys[0:3]
        self.attention = keys[6]

    def get_indexs(self, name, k: bool=0):
        if k:
            lista = np.array(self.sheet[self.ours[0]])
        else:
            lista = np.array(self.sheet[self.theirs[0]])
        odp = []
        for i, s1 in enumerate(lista):
            if podciąg(str(s1), name) / len(str(s1)) > 0.7:
                odp.append(i)
        return odp

    def get_info(self, name, cordy, k: bool=0):
        indexes = self.get_indexs(name, k)
        for idx in indexes:
            if cordy == np.array(self.sheet[self.theirs[1]])[idx]:
                return np.array(self.sheet[self.theirs[0]])[idx], np.array(self.sheet[self.theirs[2]])[idx], cordy


def distance(isl1: str, isl2: str):
    x1, y1 = isl1.split(';')
    x2, y2 = isl2.split(';')
    return ((x1-x2)**2 + (y1-y2)**2)**0.5


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


e = Excel(get_data())
print(e.get_info('dabe,', '25;46'))
