import discord
from discord.ext import commands
from discord import app_commands
from Common import TOKEN
from Ikariam.Islands import calc
from Jap.keyboard import parse_foreach
import time
import datetime
from Ikariam.Koszty import Composition, estimate_nD, upkeep_h
from Ikariam.Podkupowacz import Podkupowacz


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


Khufra = commands.Bot(command_prefix='?', intents=intents)


async def error(interaction: discord.Interaction, e: Exception):
    member = interaction.client.get_user(687957649635147888)
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
    {function} o godzinie {datetime.datetime.now()}:\n{e}')


@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(len(synced))
    guilds = Khufra.guilds
    print(guilds)
    global e
    e = Podkupowacz.Excel()
    # guilds = Khufra.guilds
    # guild = next((g for g in guilds if g.name == "Bolki"), None)
    # names = []
    # for member in guild.get_channel(914664266118873118).members:
    #     if member.bot:
    #         continue
    #     name = member.nick if member.nick is not None else member.global_name
    #     if not name:
    #         name = member.name
    #     names.append(name.lower())
    # for name in sorted(names):
    #     print(name)


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


@Khufra.tree.command(description="Przewiduje koszty 1 walki w określonym\
    czasie")
@app_commands.describe(dni='Ile dni?', lv='Poziom Żeglugi', czy_24='Czy\
    preferowany składy 24h. 12h w przeciwnym wypadku?', nu_siebie='Czy\
        walka jest poza swoim portem?')
async def cost(interaction: discord.Interaction, dni: int, lv: int,
               czy_24: bool, nu_siebie: bool):
    try:
        cost = estimate_nD(d=dni, lv=lv, czy_24=czy_24, nu_siebie=nu_siebie)
        czy_24 = 'preferowane składy na {}h'.format(24 if czy_24 else 12)
        nu_siebie = '{} mi{}'.format('po za' if nu_siebie else 'u siebie w',
                                     'astem' if nu_siebie else 'eście')
        res = f'# Przypuszczalny koszt przy następujących parametrach:\n*\
            poziom żeglugi {lv},\n* na {dni} dni,\n* {czy_24},\n*\
                {nu_siebie},\nto: {cost} złota'
        await interaction.response.send_message(res)
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


@Khufra.tree.command(description="Oblicza limit garnizonu lądowego")
@app_commands.describe(t="Poziom ratusza", w="Poziom muru")
async def lad(interaction: discord.Interaction, t: int, w: int):
    land = 250 + (t + w) * 50
    await interaction.response.send_message(land)


@Khufra.tree.command(description="Oblicza limit garnizonu morskiego")
@app_commands.describe(m="Wyższy poziom stoczni lub portu")
async def mor(interaction: discord.Interaction, m: int):
    sea = 125 + m * 25
    await interaction.response.send_message(sea)


@Khufra.tree.command(description="Wyznacza ilość punktów akcji dla podanego\
    poziomu ratusza")
@app_commands.describe(r="Poziom ratusza")
async def a_p(interaction: discord.Interaction, r: int):
    if r < 1:
        await interaction.response.send_message("Poziom nie może być mniejszy\
            od 1", ephemeral=True)
    p = 3 + r // 4
    await interaction.response.send_message(f"{p} / {p-2}")


@Khufra.tree.command(description='Wypisuje znane skabonki wroga')
async def all_enemy_rg(interaction: discord.Interaction):
    global e
    rg_keepers = e.get_rg_keepers()
    await interaction.response.send_message(f"```py\n{rg_keepers}\n```")


@Khufra.tree.command(description='Wypisuje podkupowacze na jakie trzeba\
    się zalogować w zależności od podanej otawrtej skarbonki')
@app_commands.describe(enemy_name='Nazwa wrogiej skarbonki')
async def enemy_rg(interaction: discord.Interaction, enemy_name: str):
    global e
    res = e.describe(enemy_name)
    await interaction.response.send_message(res)


Khufra.run(TOKEN)
