import discord
from discord.ext import commands
from discord import app_commands
from Common import ME, CHANNEL
from Ikariam.Islands import Map
from Ikariam.queue import calc
from Jap.keyboard import parse_foreach
import time
from datetime import datetime
from Ikariam.Koszty import Composition, upkeep_h
import asyncio
from Ikariam.api.Cookie import cookie
from Ikariam.api.session import ExpiredSession
from Ikariam.api.rgBot import rgBot
import random
import json
from typing import Dict
from decorators import restrict_to_guilds


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


# logging.basicConfig(filename="Khufra.log", level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
Khufra = commands.Bot(command_prefix='?', intents=intents)
get_color = lambda: random.randint(0, 0xffffff)%(0xffffff+1)

with open("config.json", 'r') as f:
    guilds: Dict[int, Dict] = {int(id): item for id, item in json.load(f).items()}


async def error(interaction: discord.Interaction, e: Exception):
    me = interaction.client.get_user(ME)
    message = f'Coś poszło nie tak ... {e}'
    if interaction.response.is_done():
        await interaction.followup.send(message, ephemeral=True)
    else:
        await interaction.response.send_message(message, ephemeral=True)
    person = interaction.user.global_name
    try:
        canal = interaction.channel.name
    except Exception:
        canal = interaction.channel_id
    function = interaction.command.name
    await me.send(f'Osoba {person} na kanale {canal} miała problem z funkcją\
    {function} o godzinie {datetime.now()}:\n{e}')


def create_maps() -> Dict[int, Dict]:
    maps: Dict[int, Map] = {}
    for id in guilds:
        maps[id] = Map(f"Ika_Map/{guilds[id]['id']}.json")
    return maps


maps: Dict[int, Map] = create_maps()


@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(len(synced))    
    global rg_bot
    rg_bot = rgBot(cookie, 62)
    Khufra.loop.create_task(check_generals())


@Khufra.tree.command()
@app_commands.describe(what="Co zaktualizować?")
@app_commands.choices(what=[
    app_commands.Choice(name="Graczy", value=True),
    app_commands.Choice(name="Skarbonki", value=False),
])
@restrict_to_guilds(guilds)
async def update(interaction: discord.Interaction, what: app_commands.Choice[int]):
    global maps
    global rg_bot
    if what.value:
        maps[interaction.guild_id].scan_map()
        await interaction.response.send_message("Zaktualizowano graczy z pliku")
    else:
        if guilds[interaction.guild_id]["name"] != "Meduza":
            await interaction.response.send_message(f"Nie ma tu skarbonek", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            me = Khufra.get_user(ME)
            bugs = []
            with open("HH.txt", "r") as f:
                text = [line.rstrip("\n") for line in f]
                for line in text:
                    rg_keeper, owner = line.split(' - ')
                    _, bug = rg_bot.load_owners(rg_keeper, owner)
                    if bug is not None:
                        bugs.append(bug)
            await interaction.followup.send("Zaktualizowano skarbony")
            if len(bugs) > 0:
                for i in range(len(bugs)//5):
                    await me.send(bugs[5*i:5*i+5])
        except Exception as e:
            await error(interaction, e)


@Khufra.tree.command(description="Stara się zamienić tekst romaji na zapis w\
    katakanie")
@app_commands.describe(text="To co chcesz dostać po japońsku w katakanie")
async def kana(interaction: discord.Interaction, text: str):
    try:
        res = parse_foreach(text)
        await interaction.response.send_message(res)
    except Exception as e:
        await error(interaction, e)


@Khufra.tree.command(description="To chyba oczywiste...")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"{round(Khufra.latency * 1000,1)}ms")


@Khufra.tree.command(description="Szuka możliwych koordynatów skąd przeciwnik\
    może skupować rg")
@app_commands.describe(x='Kordynat x wyspy', y="Kordynat y wyspy", h="Godziny\
    płynięcia", m="Minuty płynięcia", s="Sekundy płynięcia")
async def find(interaction: discord.Interaction, x: int, y: int, h: int,
               m: int, s: int):
    args = [x, y, h, m, s]
    content = f"Searching from [{x} {y}] with time {h}:{m}:{s}\n"
    try:
        res = calc(*args)
        await interaction.response.send_message(content)
        time.sleep(1)
        await interaction.channel.send(res)
    except Exception as e:
        await error(interaction, e)


@Khufra.tree.command(description="Wyznacza skład na podany czas z zapasem na\
    około 1h")
@app_commands.describe(t='Na ile h flota?', lv='Poziom przyszłości żeglugi?')
async def ships(interaction: discord.Interaction, t: int, lv: int = 0):
    try:
        fleet = Composition(t)
        upkeep = upkeep_h(fleet, lv)
        content = f'{fleet}\n Koszt utrzymania na 1h: {upkeep}'
        await interaction.response.send_message(content)
    except Exception as e:
        await error(interaction, e)


@Khufra.tree.command(description="Discordowy licznik")
@app_commands.describe(t="Ile chcesz odliczać w s?")
async def timer(interaction: discord.Interaction, t: int = 0):
    utc = round(time.time()) + t
    await interaction.response.send_message(f"<t:{utc}:R>")


@Khufra.tree.command(description="Oblicza limit garnizonu lądowego lub morskiego")
@app_commands.describe(land="Czy garnizon lądowy?", args="Dla lądowego poziom ratusza i muru,\
    dla morskiego max poziomu budynków morskich")
@app_commands.choices(land=[
    app_commands.Choice(name=True, value=True),
    app_commands.Choice(name=False, value=False),
])
async def garrison(interaction: discord.Interaction, land: app_commands.Choice[int], args: str):
    args = [int(x) for x in args.split()]
    if land.value:
        if len(args) != 2:
            await interaction.response.send_message("Podaj poziom ratusza i muru.")
            return
        if args[0] < 1 or args[1] < 0:
            await interaction.response.send_message("Poziom ratusza nie może być mniejszy\
    od 1, zaś muru od 0", ephemeral=True)
            return
        land = 250 + sum(args) * 50
        await interaction.response.send_message(land)
        return
    else:
        if len(args) != 1:
            await interaction.response.send_message("Podaj wyższy poziom budynku morskiego.")
            return
        if args[0] < 1:
            await interaction.response.send_message("Poziom nie może być mniejszy\
    od 1", ephemeral=True)
            return
        sea = 125 + args[0] * 25
        await interaction.response.send_message(sea)


@Khufra.tree.command(description="Wyznacza ilość punktów akcji dla podanego\
    poziomu ratusza")
@app_commands.describe(r="Poziom ratusza")
async def a_p(interaction: discord.Interaction, r: int):
    if r < 1:
        await interaction.response.send_message("Poziom nie może być mniejszy\
 od 1", ephemeral=True)
        return
    p = 3 + r // 4
    await interaction.response.send_message(f"{p} / {p-2}")



@Khufra.tree.command(description="Przypisuje właścicieli do skarbonek")
@app_commands.describe(rg_keeper="Nazwa skarbonki, którą chcemy przypisać", owner="Właściciel")
@restrict_to_guilds(guilds)
async def assign(interaction: discord.Interaction, rg_keeper: str, owner: str):
    global rg_bot
    await interaction.response.defer()
    try:
        res, bugs = rg_bot.load_owners(rg_keeper, owner)
        if bugs is not None:
            await interaction.followup.send(f"Nie znaleziono takiej skarbonki {bugs[0]}")
        else:
            await interaction.followup.send(f"Pomyślnie przypisano {res[0]} do {res[1]}")
    except Exception as e:
        await error(interaction, e)


@Khufra.tree.command(description="Wypisuje znane kordy podane gracza")
@app_commands.describe(nick="Gracz, którego kordy chcemy poznać")
@restrict_to_guilds(guilds)
async def player(interaction: discord.Interaction, nick: str):
    global maps
    await interaction.response.defer()
    try:
        players = maps[interaction.guild_id].get_coords(nick)
        if len(players) == 0:
            res = f'Nie znaleziono żadnego podobnego gracza o podanym nicku: {nick}'
        else:
            res = ''
            for player, coords, _ in players:
                res += f'{player}: {coords}\n'
        await interaction.followup.send(res)
    except Exception as e:
        await error(interaction, e)


@Khufra.tree.command(description="Wypisuje dane miast z podanej wyspy")
@app_commands.describe(x="Kordynat x", y="Kordynat y", ally="Sojusz, z którego graczy chcemy wypisać na podanej wyspie. Domyślnie wszystkich wypisze")
@restrict_to_guilds(guilds)
async def island(interaction: discord.Interaction, x: int, y: int, ally: str=''):
    global maps
    await interaction.response.defer()
    try:
        island = maps[interaction.guild_id].get_cities_from_island(x, y, ally=ally)
        if not island:
            await interaction.followup.send(f"Nie ma wyspy o podanych kordach {x}:{y}")
            return
        cities = island.cities
        embed = discord.Embed(
            title=f"Info o wyspie {x}:{y}",
            description=f"{island.name} {island.id}",
            color=get_color(),
            timestamp=datetime.now()
        )
        for i, city in enumerate(cities):
            name = f"{i+1}: {city.name}"
            ally = city.AllyTag
            description = f"{city.owenrName}"
            if ally:
                description += f" [{ally}]"
            embed.add_field(name=name, value=description, inline=True)
        await interaction.followup.send(embed=embed)
    except Exception as e:
        await error(interaction, e)


async def check_generals():
    await Khufra.wait_until_ready()
    global rg_bot
    loop = asyncio.get_running_loop()
    channel = Khufra.get_channel(CHANNEL)
    top = 300
    i = 0
    while not Khufra.is_closed():
        try:
            res = await loop.run_in_executor(None, rg_bot.analize_rg, 50 * i)
            for every_palm in res:
                if every_palm[1] == -1:
                    await channel.send(f"{every_palm[0]} poszedł pod :palm_tree:")
                else:
                    mes = f"{every_palm[0]} zszedł z urlopu. Rg: {every_palm[1]}."
                    if every_palm[2]:
                        mes += f" Czyje: {every_palm[2]}"
                    await channel.send(mes)
            i += 1
            i = i % (top//50)
        except ExpiredSession:
            await channel.send(f"<@{ME}> potrzebna nowa sesja.")
            break
        except Exception as e:
            with open("error.txt", 'w') as f:
                f.write(str(e))
        finally:
            await asyncio.sleep(random.randint(8, 12))
