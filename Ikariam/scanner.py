from Ikariam.api.session import IkaBot
import time
import random
import json


class Scanner:
    def __init__(self, bot: IkaBot, path: str) -> None:
        self.bot = bot
        self.bot.set_action_request()
        self.path = path
        self.different_letters = {
            'с': 'c',
            'і': 'i'
        }

    def run(self, again=False):
        if again:
            with open(self.path, 'r') as f:
                islands = json.load(f)
        else:
            islands = self.bot.get_islands(50, 50, 50)
        bugs = []
        for x in islands:
            skipped = False
            for y in islands[x]:
                if again and isinstance(islands[x][y], dict):
                    skipped = True
                    continue
                id = int(islands[x][y][0])
                name = islands[x][y][1]
                islands[x][y] = {
                    "id": id,
                    "name": name,
                    "cities": []
                }
                try:
                    time.sleep(random.randint(8, 12))
                    cities = self.bot.get_island_info(id)
                    cities = [city for city in cities if city.id != -1]
                    islands[x][y]["cities"] = [vars(city) for city in cities]
                except Exception as e:
                    bugs.append((x, y))
                    print(x, y, e)
                    continue
            if not skipped:
                with open(self.path, "w") as f:
                    json.dump(islands, f, indent=4)
        return bugs

    def correct(self, bugs):
        with open(self.path, 'r') as f:
            islands = json.load(f)
        for bug in bugs:
            x, y = bug
            id = int(islands[x][y]["id"])
            try:
                time.sleep(random.randint(8, 12))
                cities = self.bot.get_island_info(id)
                cities = [city for city in cities if city.id != -1]
                islands[x][y]["cities"] = [vars(city) for city in cities]
            except Exception as e:
                print(x, y, e)
                with open(self.path, 'w') as f:
                    json.dump(islands, f, indent=4)
                continue
        with open(self.path, 'w') as f:
            json.dump(islands, f, indent=4)

    def get_mapped(self, string: str):
        copy = ''
        for letter in string.lower():
            copy += self.different_letters.get(letter, letter)
        return copy.lower()
