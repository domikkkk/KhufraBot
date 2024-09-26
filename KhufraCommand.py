import discord
from discord.ext import commands
from discord import app_commands
from Common import ME, LOGINHASLO, LOGINHASLOZAJMOWACZY
from Ikariam.Islands import calc, Wyspy
from Jap.keyboard import parse_foreach
import time
from datetime import datetime
from Ikariam.Koszty import Composition, upkeep_h
import json
import asyncio
from Ikariam.api.Cookie import cookie
from Ikariam.api.session import rgBot


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


# logging.basicConfig(filename="Khufra.log", level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
Khufra = commands.Bot(command_prefix='?',
                      intents=intents)


async def error(interaction: discord.Interaction, e: Exception):
    member = interaction.client.get_user(ME)
    await interaction.response.send_message('Coś poszło nie tak ...',
                                            ephemeral=True)
    try:
        person = interaction.user.nick
    except Exception:
        person = interaction.user.name
    try:
        canal = interaction.channel.name
    except Exception:
        canal = interaction.channel_id
    function = interaction.command.name
    await member.send(f'Osoba {person} na kanale {canal}\
        miała problem z funkcją\
    {function} o godzinie {datetime.now()}:\n{e}')


@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(len(synced))
    global w
    w = Wyspy()
    Khufra.loop.create_task(check_generals())



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


@Khufra.tree.command(description="Wyznacza wyspy do miotłowania")
@app_commands.describe(x='Kordynat x', y='Kordynat y')
async def wyspy(interaction: discord.Interaction, x: int, y: int):
    global w
    try:
        res = w.find(x, y)
        res = json.dumps(res, indent=4, ensure_ascii=False)
        await interaction.response.send_message(f"```json\n{res}\n```")
    except Exception as ee:
        await error(interaction, ee)


async def check_generals():
    await Khufra.wait_until_ready()
    rg_bot = rgBot(cookie)
    while not Khufra.is_closed():
        res = rg_bot.analize_rg()
        user = await Khufra.fetch_user(ME)
        for every_palm in res:
            await user.send(f"{every_palm[0]} zszedł z urlopu. Stare rg: {every_palm[1]}")
        await asyncio.sleep(58)
