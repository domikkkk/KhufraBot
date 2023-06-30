import datetime
import csv
import numpy as np
import os


dolphin = {
    '0': 0,
    '1': 0.1,
    '2': 0.3,
    '3': 0.5,
    '4': 0.7,
    '5': 1
}


def tii(fromm, to, temple='0'):
    boost = dolphin[temple] + 1
    v1 = np.array([int(i) for i in fromm])
    v2 = np.array([int(i) for i in to])
    v = v1 - v2
    T = (v[0]**2 + v[1]**2)**0.5*30
    T = max(15, T) / boost
    t = datetime.timedelta(minutes=T)
    current_t = datetime.datetime.now()
    return current_t + t


def read_from_miotly(filename):
    path = 'c:/users/domik/Ikariam/Boty na dc/Walki/' + filename + '.csv'
    with open(path, 'r') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            data.append((
                row['runda'],
                row['godzina_przybycia'],
                row['czyje']
                ))
        return data


def find_time(filename, fromm, who, temple='0'):
    too = filename[-5:].split('-')
    data = read_from_miotly(filename)
    id = -1
    data1 = []
    t = str(tii(fromm, too, temple)).split('.')[0]
    t = datetime.datetime.fromisoformat(t)
    odp = 'Coś nie pstrykło, ale nie wiem co'
    for runda in data:
        id += 1
        czas_rundy = datetime.datetime.fromisoformat(runda[0])
        minut15 = datetime.timedelta(minutes=15)
        zero = datetime.timedelta(minutes=0)
        roznica = czas_rundy - t
        if roznica < minut15 and roznica > zero and not runda[2]:
            ilosc = str(roznica).split(':')
            data1.append([czas_rundy, t, who])
            odp = f'Zdążą {ilosc[1]}min i {ilosc[2]}s przed rundą.\nid={id}\nrunda:{str(czas_rundy)}'
        elif roznica < minut15 and roznica > zero and runda[2]:
            data1.append(runda)
            ilosc = str(roznica).split(':')
            czas_opu = datetime.timedelta(minutes=int(ilosc[1]), seconds=int(ilosc[2]))
            hm = id + 1
            while data[hm][2]:
                czas_opu += datetime.timedelta(minutes=15)
                hm += 1
            current_t = datetime.datetime.now()
            time = current_t + czas_opu
            time_od = str(datetime.datetime.fromisoformat(str(time).split('.')[0])).split(' ')[1]
            time_do = str(datetime.datetime.fromisoformat(str(time+minut15).split('.')[0])).split(' ')[1]
            odp = f'Wyślij od {time_od} do {time_do} z tego miejsca.'
        else:
            data1.append(runda)
    return data1, odp


def save_in_miotly(filename: str, fromm, who, temple='0'):
    path = 'c:/users/domik/Ikariam/Boty na dc/Walki/' + filename + '.csv'
    if not os.path.exists(path):
        return 'Zly plik'
    y = find_time(filename, fromm, who, temple)
    data = y[0]
    with open(path, 'w', newline='') as file:
        header = ['runda', 'godzina_przybycia', 'czyje']
        writer = csv.DictWriter(file, header)
        writer.writeheader()
        for x in data:
            writer.writerow({
                'runda': x[0],
                'godzina_przybycia': x[1],
                'czyje': x[2]
            })
    return y[1]
