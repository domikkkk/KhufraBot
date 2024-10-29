from Ikariam.api.session import ExpiredSession, IkaBot
import requests
from Cookie import cookie4


class Balonowanie(IkaBot):
    def __init__(self, cookie) -> None:
        super().__init__(cookie)
        self.destination_city_id = -1

    def set_destination_city(self, id):
        self.destination_city_id = id

    def get_cities(self, x, y, palm=False):
        island_id = self.get_island_id(x, y)
        if island_id == -1:
            raise Exception("Nie ma takiej wyspy")
        cities = self.get_island_info(island_id)
        posibilities = {}
        i = 0
        for city in cities:
            if palm and city["state"] != "":
                continue
            posibilities[i] = (city["id"], city["name"], city["ownerName"])
            i += 1
        return posibilities


if __name__ == "__main__":
    bot = Balonowanie(cookie4)
    bot.set_action_request()
    print(bot.get_city_units(664))
        