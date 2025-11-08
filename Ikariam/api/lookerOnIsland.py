from Ikariam.api.session import IkaBot
from Ikariam.dataStructure import PlantColony
import time
import random


class Planter(IkaBot):
    def __init__(self, gf_token: str, nick: str):
        super().__init__(gf_token, nick)

    def choose_city(self, how_many_spots=1):
        self.set_action_request()

        print("Szukam wyspy z której puścić")

        for city in self.dict_of_cities.values():
            data = self.change_city(city.id)

            print(f"Sprawdzam miasto {city.name}")

            if not data:
                raise ValueError
            wood = data.headerdata.currentResources.wood
            free_people = data.headerdata.currentResources.citizens
            gold = data.headerdata.gold
            free_transporters = data.headerdata.freeTransporters
            if wood > 1250 * how_many_spots and free_people > 40 * how_many_spots and gold > 9000 * how_many_spots and free_transporters > 3 * how_many_spots:

                print(f"Znaleziona: {city.coords} - {city.name}")

                return True
            time.sleep(1)
        return False

    def lookAfter(self, x, y, how_many_spots=1):
        if not self.choose_city(how_many_spots):
            return

        islandId = self.get_island_id(x, y)
        time.sleep(1)

        while how_many_spots > 0:
            try:
                cities = self.get_island_info(islandId)
                for i, city in enumerate(cities):
                    if city.id == -1 and i != 16:
                        self.plant_colony(PlantColony(desiredPosition=i, transporters=3, destIslandId=islandId))
                        how_many_spots -= 1
                        time.sleep(1)
            except Exception:
                pass
            finally:
                time.sleep(random.randint(8, 12))
