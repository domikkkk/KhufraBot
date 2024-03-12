import discord
from discord.ext import commands
from discord import app_commands
from Common import ME
from Ikariam.Islands import calc, Wyspy
from Jap.keyboard import parse_foreach
import time
from datetime import datetime
from Ikariam.Koszty import Composition, upkeep_h
from Ikariam.Podkupowacz import Podkupowacz
from Ikariam.Podkupowacz.Podkupowacz import LOGINHASLO, LOGINHASLOZAJMOWACZY
import json
from mlbb.heroes import get_build, get_heroes, Heroes, Items
import asyncio


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
    guilds = Khufra.guilds
    global e
    global w
    e = Podkupowacz.Excel()
    w = Wyspy()
    # guilds = Khufra.guilds
    # guild = next((g for g in guilds if g.name == "Stare D-S"), None)
    Khufra.loop.create_task(update_per_day())


@Khufra.event
async def on_message(mes: discord.Message):
    global e
    if mes.author.id == Khufra.user.id:
        return
    if mes.author.bot and mes.author.id == 757993517145391213:
        mess = mes.content.lower()
        idx = mess.find('zszedł z urlopu')
        if idx == -1:
            return
        user = await Khufra.fetch_user(269481968461283328)
        await user.send(LOGINHASLO)
        await user.send(LOGINHASLOZAJMOWACZY)
        rg_name = mess[:idx-1].split(' ')[-1]
        for name in e.get_rg_keepers():
            if Podkupowacz.podciąg(name, rg_name) / max(len(name),
                                                        len(rg_name)) > 0.75:
                await mes.channel.send(e.describe(name))
                return
    return


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


@Khufra.tree.command()
async def update(interaction: discord.Interaction):
    global e
    try:
        e.update()
        await interaction.response.send_message("Pomyślnie zaktualizowano")
    except Exception as ee:
        await error(interaction, ee)


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


@Khufra.tree.command(description="Oblicza limit garnizonu lądowego")
@app_commands.describe(t="Poziom ratusza", w="Poziom muru")
async def lad(interaction: discord.Interaction, t: int, w: int):
    if t < 1 or w < 0:
        await interaction.response.send_message("Poziom ratusza nie może być mniejszy\
 od 1, zaś muru od 0", ephemeral=True)
        return
    land = 250 + (t + w) * 50
    await interaction.response.send_message(land)


@Khufra.tree.command(description="Oblicza limit garnizonu morskiego")
@app_commands.describe(m="Wyższy poziom stoczni lub portu")
async def mor(interaction: discord.Interaction, m: int):
    if m < 1:
        await interaction.response.send_message("Poziom nie może być mniejszy\
 od 1", ephemeral=True)
        return
    sea = 125 + m * 25
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


@Khufra.tree.command(description='Wypisuje znane skarbonki wroga')
async def all_enemy_rg(interaction: discord.Interaction):
    global e
    rg_keepers = e.get_rg_keepers()
    await interaction.response.send_message(f"```py\n{rg_keepers}\n```")


@Khufra.tree.command(description='Wypisuje podkupowacze na jakiego trzeba\
    się zalogować w zależności od podanej otwartej skarbonki')
@app_commands.describe(enemy_name='Nazwa wrogiej skarbonki')
async def podkupowacz(interaction: discord.Interaction, enemy_name: str):
    global e
    res = e.describe(enemy_name)
    await interaction.response.send_message(res)


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


@Khufra.tree.command()
@app_commands.describe(heroname='Nazwa Bohatera')
async def hero_info(interaction: discord.Interaction, heroname: str):
    heroes = Heroes()
    res = heroes.find(heroname)
    embeds = heroes.get_info()
    if embeds:
        await interaction.response.send_message(embeds=embeds)
    else:
        await interaction.response.send_message("Nie znaleziono podanego bohatera")


@Khufra.tree.command()
@app_commands.describe(itemname='Nazwa itemu')
async def item_info(interaction: discord.Interaction, itemname: str):
    items = Items()
    res = items.find(itemname)
    embed = items.get_info()
    if embed:
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Nie znaleziono podanego itemu")


async def update_per_day():
    await Khufra.wait_until_ready()
    while not Khufra.is_closed():
        hour = datetime.utcnow().hour
        if hour == 15:
            get_heroes()
            get_heroes(True)
            get_build()
        await asyncio.sleep(60 * 60)
