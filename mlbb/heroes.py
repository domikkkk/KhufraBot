import requests
import json
import numpy as np
import discord
import io
import re


link = 'https://www.mlbb.ninja/_next/data/vH0BTjpFf0HJFczSlWOll'
link_build = lambda id: f'{link}/heroes/{id}.json?id={id}'


def get_item_image(name: str):
    args = name.split()
    image_link = 'https://www.mlbb.ninja/images/item_icons/{}.png'
    item = ''
    length = len(args)
    for i in range(length-1):
        item += args[i] + '%20'
    item += args[length - 1]
    return image_link.format(item)


def delete_tags(text: str):
    pattern = re.compile(r'<.*?>')
    return re.sub(pattern, '', text)


filtr = {
    False: ('heroData', 'id'),
    True: ('updateData', 'hero_id'),
}

lanes = ['is_gold', 'is_exp', 'is_jungle', 'is_roam', 'is_mid']


class Object:
    def find(self, data: list[dict], name: str):
        return next((i for i in data
                if podciag(i['name'], name)/max(len(i['name']), len(name)) > 0.8), None)


class X:
    def __init__(self, data: dict):
        self.name = data.get('name')
        self.lanes = [i for i in lanes if data.get(i) is not None and data.get(i) is True]
        self.tier = data.get('tier')
        self.description = data.get('description')
        self.stats = data.get('stats')
        self.role = data.get('role')
        self.pick_rate = data.get('pick_rate')


class Skill:
    def __init__(self, data: dict):
        self.name = data.get('name')
        self.description = delete_tags(data.get('description'))
        self.mana = data.get('mana_cost')
        self.cd = data.get('cooldown')
        self.is_passive = data.get('is_passive')
        self.image = data.get('icon_url')


class Heroes(Object):
    def __init__(self) -> None:
        data = read_heroes()
        for hero in data:
            hero['image_link'] = hero['image_link'].strip()
        self.herodata = data

    def find(self, heroname: str):
        self.hero = super().find(self.herodata, heroname)
        self.x = X(self.hero)
        return self.hero

    def get_image(self):
        if self.hero:
            return io.BytesIO(requests.get(self.hero['image_link']).content)

    def get_info(self):
        embed = discord.Embed(title=self.x.name, color=0x00b3ff)
        embed.set_thumbnail(url=self.hero['image_link'])
        x = requests.get(link_build(self.hero.get('id', 0))).json()
        skills = x['pageProps']['data']['heroSkillsData']
        for skill in skills:
            s = Skill(skill)
            embed.add_field(name=s.name, value=s.description)
        return embed


class Items(Object):
    def __init__(self) -> None:
        self.itemsdata: list[dict] = read_items()

    def find(self, itemname: str):
        self.item = super().find(self.itemsdata, itemname)
        self.x = X(self.item)
        return self.item

    def get_image(self):
        if self.item:
            return io.BytesIO(requests.get(get_item_image(self.item['name'])).content)

    def get_info(self):
        embed = discord.Embed(title=self.x.name)
        embed.set_image(url=get_item_image(self.x.name))
        return embed


def get_build():
    items: list[dict] = []
    x = requests.get(link_build(1)).json()
    y =  x['pageProps']['data']
    for item in y['itemDetails']:
        items.append(item)
    items = sorted(items, key=lambda x: x['name'])
    dump('mlbb/items.json', items)


def get_heroes(update=False):
    x = requests.get(link).json()
    typ, id = filtr[update]
    data = x['pageProps'][typ]
    data = sorted(data, key=lambda x: x[id])
    # if not update:
    #     for hero in data:
    #         x = requests.get(link_build(hero.get('id', 0))).json()
    #         y = x['pageProps']['data']['heroSkillsData']
    #         hero['heroSkillsData'] = y
    dump(f'mlbb/{typ}.json', data)


def read_items():
    filename = "mlbb/items.json"
    with open(filename, 'r') as f:
        data = json.load(f)
    return data


def read_heroes(heroUpdate=False):
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


if __name__ == "__main__":
    H = Heroes()
    I = Items()
    # print(H.find('miya'))
    # print(I.find('neckless of durance'))
    # print(link_build(119))
    get_heroes()
