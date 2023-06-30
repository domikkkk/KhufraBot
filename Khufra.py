import discord
from discord.ext import commands
from Ikariam.clear_and_create_miotly import File_csv
from Ikariam.miotlowanie import save_in_miotly
import Common



intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
khufra = commands.Bot(command_prefix='?', intents=intents)
khufra.remove_command('help')


# n = [
#     'Podaj nazwę walki, skąd i opcjonalnie poziom aktywnego delfina.',
#     'przykład: ?m rezi26-72 74-34 5',
#     'jak się nie poda delfina to domyślnie jest 0'
# ]
a = [
    'Parametry: ilość godzin na jaką chcemy flotę',
    'opcjonalnie poziom przyszłości żeglugi',
    'przykłady: ?fleet 24 5 lub ?fleet 24.5h'
]
# c = [
#     'Podaj nazwę walki oraz przedział id, które chcesz zobaczyć z danej walki',
#     'przykład: ?get rezi26-72 13-15 lub ?get rezi26-72 12'
# ]
# b = 'Usuwa wpis z walki\nprzykład: ?delete rezi26-72 40'
# d = 'Podaj nazwę walki\nwypisuje najbliższe 10 luk w danej walce'
# e = [
#     'Parametry: -nazwa pliku do walki jaki chcesz stworzyć',
#     'Uwaga: ostatnie 5 znaków muszą być postaci XX-YY, czyli kordy wyspy gdzie jest walka',
#     '-data z godzina rundy od której chcesz stworzyć plik',
#     'Uwaga: koniecznie format ISO czyli postać: YYYY-MM-DD hh:mm:ss',
#     '-ilość wierszy (rund) na ile chcesz początkowo stworzyć.',
#     'Proponowane 1k, czyli na 1000 rund',
#     'przykład: ?create miki24-05 2022-04-28 19:40:50 100'
# ]
# f = [
#     'Przesuwa czas rund w podanej walce',
#     'przykład: ?przesun rezi26-72 1:1',
#     'przesunie czas rund od 1 min i 1s'
# ]
embed = discord.Embed(title="help", description="commands", color=0xff00ff)
embed.add_field(name='?help', value="pokazuje komendy", inline=True)
# embed.add_field(name='?m', value='\n'.join(n), inline=False)
embed.add_field(name='?fleet', value='\n'.join(a), inline=False)
# embed.add_field(name='?get', value='\n'.join(c), inline=False)
# embed.add_field(name='?delete', value=b, inline=False)
# embed.add_field(name='?luki', value=d, inline=False)
# embed.add_field(name='?create', value='\n'.join(e), inline=False)
# embed.add_field(name='?przesun', value='\n'.join(f), inline=False)


@khufra.command()
async def help(x):
    await x.send(embed=embed)


@khufra.command()
async def delete(x, filename: str, id: int):
    file = File_csv(filename)
    file.read()
    file.delete_id(id)
    await x.channel.send('Usunięto!')


@khufra.command()
async def get(x, filename: str, id: str):
    file = File_csv(filename)
    file.read()
    rundy = file.get_id(id)
    message = '```cs\n'
    licznik = 0
    for runda in rundy:
        godzina_rundy, przybycie, czyje = runda
        message += f'{godzina_rundy},{przybycie},{czyje}\n'
        if licznik == 15:
            message += '```'
            await x.channel.send(message)
            message = '```cs\n'
            licznik = 0
        licznik += 1
    message += '```'
    await x.channel.send(message)


@khufra.command()
async def luki(x, filename: str):
    file = File_csv(filename)
    file.read()
    rundy = file.luki()
    message = '```cs\n'
    for runda in rundy:
        godzina_rundy, przybycie, czyje = runda
        message += f'{godzina_rundy},{przybycie},{czyje}\n'
    message += '```'
    await x.channel.send(message)


@khufra.command()
async def create(x, filename: str, day: str, clock: str, rows=0):
    rows = int(rows)
    data = ' '.join([day, clock])
    file = File_csv(filename)
    file.clear_and_create_file(data, rows)
    await x.channel.send('Stworzono nowy plik!')


@khufra.command()
async def m(x, filename: str, fromm: str, delfin='0'):
    who_str = str(x.author)
    frommm = fromm.split('-')
    mail = save_in_miotly(filename, frommm, who_str, delfin)
    await x.send(f'{mail}')


@khufra.command()
async def przesun(x, filename: str, time: str):
    time1 = time.split(':')
    if len(time1) != 2 or time1[0] == '' or time1[1] == '':
        await x.send('Musisz podać minuty i sekundy')
        return
    file = File_csv(filename)
    file.read()
    file.delay(time)
    w = 'Pomyślnie przesunięto czas rund o'
    await x.send(f'{w} {int(time1[0])}min i {int(time1[1])}s.')


# @khufra.command()
# async def joke(x):
#     joke = jokes()
#     await x.send(f'{joke}')


@khufra.command()
async def fleet(x, y, z=0):
    flota = {
        18: '<:taran:952499734461964318>',  # zwykle
        15: '<:parowy:952499832717725716>',  # parowe
        6: '<:smigi:952499748298964994>',  # smigi
        5.5: '<:rakieta:952499762756718712>',  # rakiety
        2: '<:balon:952499894831153172>',  # balony
        8.4: '<:mosek:953341250063437934>'  # mośki
    }
    dod = {
        18: 36,  # zwykle
        15: 35,  # parowe
        6: 0,  # smigi
        5.5: 15,  # rakiety
        2: 6,  # balony
        8.4: 0  # mośki
    }
    wydatki = [
        15,
        45,
        5,
        55,
        100,
        50
    ]
    y = y.replace(',', '.')
    try:
        y = float(y)
    except ValueError:
        y = float(y[:-1])
    mail = f'Skład na {y}h z przyszłością żeglugi {z}\n'
    kasa = 0
    y *= 4
    i = 0
    for ship in flota:
        mail += f'{int(y*ship + dod[ship])} {flota[ship]}\n'
        kasa += int(y*ship + dod[ship]) * wydatki[i]
        i += 1
    kasa = round(kasa * (1 - (7 + z) / 50), 2)
    mail += f'Utrzymanie: {kasa} golda\nPo za miastem: {kasa * 2}'
    await x.send(mail)


khufra.run(Common.TOKKEN)
