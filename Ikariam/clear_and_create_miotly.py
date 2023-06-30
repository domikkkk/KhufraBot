import csv
import datetime
import os


class File_csv:
    def __init__(self, filename) -> None:
        self._path = 'c:/users/domik/Ikariam/Boty na dc/Walki/' + filename + '.csv'
        self._data = []

    def read(self):
        with open(self._path, 'r') as file:
            reader = csv.DictReader(file)
            for line in reader:
                self._data.append([
                    line['runda'],
                    line['godzina_przybycia'],
                    line['czyje']
                ])

    def clear_and_create_file(self, date, n):
        clock = datetime.datetime.fromisoformat(date)
        r = datetime.timedelta(minutes=15)
        self._data = []
        with open(self._path, 'w', newline='') as file:
            header = ['runda', 'godzina_przybycia', 'czyje']
            writer = csv.DictWriter(file, header)
            writer.writeheader()
            for i in range(min(1000, n)):
                row = {
                    'runda': str(clock+r*i),
                    'godzina_przybycia': None,
                    'czyje': None
                }
                writer.writerow(row)
                self._data.append(list(row.values()))

    def delay(self, ile: str):
        if not os.path.exists(self._path):
            return 'Zly plik'
        ile = ile.split(':')
        ile = datetime.timedelta(minutes=int(ile[0]), seconds=int(ile[1]))
        for i in range(len(self._data)):
            row = self._data[i]
            new_time = datetime.datetime.fromisoformat(str(row[0]))
            self._data[i][0] = str(new_time + ile)

        with open(self._path, 'w', newline='') as file:
            header = ['runda', 'godzina_przybycia', 'czyje']
            writer = csv.DictWriter(file, header)
            writer.writeheader()
            for row in self._data:
                line = {
                    'runda': row[0],
                    'godzina_przybycia': row[1],
                    'czyje': row[2]
                }
                writer.writerow(line)

    def delete_id(self, id):
        if not os.path.exists(self._path):
            return 'Zly plik'
        self._data[id] = [self._data[id][0], None, None]
        with open(self._path, 'w', newline='') as file:
            header = ['runda', 'godzina_przybycia', 'czyje']
            writer = csv.DictWriter(file, header)
            writer.writeheader()
            for row in self._data:
                line = {
                    'runda': row[0],
                    'godzina_przybycia': row[1],
                    'czyje': row[2]
                }
                writer.writerow(line)

    def get_id(self, id):
        id = [int(x) for x in id.split('-')]
        return self._data[id[0]:id[-1]+1]

    def luki(self):
        current_t = str(datetime.datetime.now())
        current_t = datetime.datetime.fromisoformat(current_t)
        licznik = 0
        odp = []
        for runda in self._data:
            czas_rundy = datetime.datetime.fromisoformat(runda[0])
            minut15 = datetime.timedelta(minutes=15)
            if max(czas_rundy - current_t, current_t - czas_rundy) < minut15:
                break
            licznik += 1
        ile_wypisac = 0
        for i in range(licznik, len(self._data)):
            if not self._data[i][2] or self._data[i][2] == '':
                odp.append(self._data[i])
                ile_wypisac += 1
            if ile_wypisac == 10:
                break
        return odp
