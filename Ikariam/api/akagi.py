from ballon import Balonowanie
from session import ExpiredSession


def display_cities(cities):
    print("Wybierz miasto do balonowania:")
    for idx in cities:
        print(f"{idx}. miasto {cities[idx][1]} gracza {cities[idx][2]}")


def display_own_cities(cities: dict):
    cities_id = {}
    print("\nWybierz miasta, z których chcesz balonować:")
    for idx, city in enumerate(cities.values()):
        cities_id[idx] = city["id"]
        print(f'{idx}. {city["name"]} {city["coords"]}')
    return cities_id


def main():
    cookie = input("Podaj swoje cookie: ")
    bot = Balonowanie(cookie)
    print("Sprawdzanie...")
    try:
        bot.set_action_request()
        print("Ok")
    except ExpiredSession:
        print("Sesja nieaktywna. Sprawdź czy została dobrze skopiowana.")
        return
    cities = None
    while True:
        cin = input("Podaj kordy wyspy, którą chcesz zalać atakami. Np: 66 39\nx, y: ")
        try:
            x, y = cin.split(' ')
            cities = bot.get_cities(int(x), int(y))
            break
        except Exception as e:
            print(e)
            print("Podaj jeszcze raz")
    display_cities(cities)
    i = int(input("Wybierz numer: "))
    city = cities[i]
    print(f"Id miasta: {city[0]}")
    map_id = display_own_cities(bot.dict_of_cities)
    idxs = input("Wpisz numery miast. Np 0 1 4...\n").split(' ')
    ids = [map_id[int(i)] for i in idxs]
    print(ids)
    
    


if __name__ == "__main__":
    main()
    