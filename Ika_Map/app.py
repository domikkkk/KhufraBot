from flask import Flask, jsonify
from flask_cors import CORS
import random
from Ikariam.api.session import IkaBot, ExpiredSession
from Cookie import cookie
import json
import time


def generate_map():
    size = 100
    return [[random.choice([0, 1]) for _ in range(size)] for _ in range(size)]


class App:
    @property
    def app(self):
        return self._app

    @app.setter
    def app(self, app: Flask):
        self._app = app

    def __init__(self):
            self.app = Flask(__name__)
            self.app.secret_key = "yoloholoiho"
            CORS(self.app)
            # self.bot = IkaBot(cookie)
            self.setup_routes()

    def setup_routes(self):
        self.app.add_url_rule(rule="/api/map", endpoint="get_map", methods=["GET"], view_func=self.get_map)

    def get_map(self):
        with open("stronka/islands.json", "r") as f:
            res = json.load(f)
        map_data = [[0 for _ in range(100)] for _ in range(100)]
        for x in res:
            for y in res[x]:
                map_data[int(y)-1][int(x)-1] = res[x][y]
        return jsonify(map_data)

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)
    

if __name__ == '__main__':
    # app = App()
    # app.run(host="0.0.0.0", port=1090, debug=True)
    with open("stronka/islands.json", "r") as f:
        res = json.load(f)
    bot = IkaBot(cookie)
    bot.set_action_request()
    print(bot.actionrequest)
    for x in res:
        was = False
        for y in res[x]:
            if res[x][y]["checked"]:
                continue
            was = True
            id = int(res[x][y]["id"])
            try:
                time.sleep(random.randint(8, 12))
                cities = bot.get_island_info(id)
            except Exception as e:
                with open("stronka/islands.json", "w") as f:
                    json.dump(res, f, indent=4)
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
            res[x][y]["cities"] = cities
            res[x][y]["checked"] = 1
            print(x, y, "Zaktualizowano")
        if was:
            with open("stronka/islands.json", "w") as f:
                json.dump(res, f, indent=4)
