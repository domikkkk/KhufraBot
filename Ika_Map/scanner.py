from Ikariam.api.session import IkaBot
from Cookie import cookie
import time
import random
import json


class Scanner:
    def __init__(self, bot: IkaBot, path: str) -> None:
        self.bot = bot
        self.bot.set_action_request()
        self.path = path

    def run(self):
        islands = self.bot.get_islands(50, 50, 50)
        bugs = []
        for x in islands:
            for y in islands[x]:
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
                except Exception as e:
                    bugs.append((x, y))
                    print(x, y, e)
                    continue
                for city in cities:
                    city.pop("abyssalAmbushOverlay", None)
                    city.pop("type", None)
                    city.pop("hasTreaties", None)
                    city.pop("actions", None)
                    city.pop("viewAble", None)
                    city.pop("infestedByPlague", None)
                cities = [city for city in cities if city["id"] != -1]
                islands[x][y]["cities"] = cities
        with open(self.path, "w") as f:
            json.dump(islands, f, indent=4)
        return bugs

    def correct(self, bugs):
        with open(self.path, 'r') as f:
            res = json.load(f)
        for bug in bugs:
            x, y = bug
            id = int(res[x][y]["id"])
            try:
                time.sleep(random.randint(8, 12))
                cities = self.bot.get_island_info(id)
            except Exception as e:
                print(x, y, e)
                with open(self.path, 'w') as f:
                    json.dump(res, f, indent=4)
                continue
            for city in cities:
                city.pop("abyssalAmbushOverlay", None)
                city.pop("type", None)
                city.pop("hasTreaties", None)
                city.pop("actions", None)
                city.pop("viewAble", None)
                city.pop("infestedByPlague", None)
            cities = [city for city in cities if city["id"] != -1]
            res[x][y]["cities"] = cities
        with open(self.path, 'w') as f:
            json.dump(res, f, indent=4)


if __name__ == "__main__":
    bot = IkaBot(cookie)
    s = Scanner(bot, "Ika_Map/islands.json")
    bugs = s.run()
    s.correct(bugs)
