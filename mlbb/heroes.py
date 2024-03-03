import requests
import json
import numpy as np


link = 'https://www.mlbb.ninja/_next/data/vH0BTjpFf0HJFczSlWOll'
link_build = lambda id: f'{link}/heroes/{id}.json?id={id}'
filtr = {
    False: ('heroData', 'id'),
    True: ('updateData', 'hero_id'),
}


def read_heroes(update=False):
    x = requests.get(link).json()
    typ, id = filtr[update]
    data = x['pageProps'][typ]
    data = sorted(data, key=lambda x: x[id])
    dump(f'mlbb/{typ}.json', data)


def read(heroUpdate=False):
    filename = f"mlbb/{filtr[heroUpdate][0]}.json"
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def dump(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def podciag(s1: str, s2: str):
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
