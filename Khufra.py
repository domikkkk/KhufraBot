import discord
from discord.ext import commands
from discord import app_commands
from Common import TOKEN
from Ikariam.Islands import calc, distance, qsort, calc_time
from Jap.keyboard import parse, parse_foreach
import time
from Ikariam.Koszty import Composition, estimate_nD


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


Khufra = commands.Bot(command_prefix='?', intents=intents)

@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(len(synced))
    guilds = Khufra.guilds
    print(guilds)


@Khufra.tree.command()
@app_commands.describe(text = "To co chcesz dostać po japońsku w katakanie")
async def kana(interaction: discord.Interaction, text: str):
    try:
        res = parse_foreach(text)
        await interaction.response.send_message(res)
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)


@Khufra.tree.command()
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{Khufra.latency * 1000}ms")


@Khufra.tree.command()
@app_commands.describe(x = 'Kordynat x wyspy', y = "Kordynat y wyspy", h = "Godziny płynięcia", m = "Minuty płynięcia", s = "Sekundy płynięcia")
async def find(interaction: discord.Interaction, x: int, y:int, h:int, m:int, s:int):
    args = [x, y, h, m, s]
    try:
        res = calc(*args)
        await interaction.response.send_message(f"Searching from [{x} {y}] with time {h}:{m}:{s}\n")
        time.sleep(1)
        await interaction.channel.send(res)
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)


@Khufra.tree.command()
@app_commands.describe(dni = 'Ile dni?', lv = 'Poziom Żeglugi', czy_24 = 'Czy preferowany składy 24h. 12h w przeciwnym wypadku?', nu_siebie = 'Czy walka jest poza swoim portem?')
async def cost(interaction: discord.Interaction, dni:int, lv: int, czy_24: bool, nu_siebie: bool):
    try:
        cost = estimate_nD(d=dni, lv=lv, czy_24=czy_24, nu_siebie=nu_siebie)
        czy_24 = 'preferowane składy na {}h'.format(24 if czy_24 else 12)
        nu_siebie = '{} mi{}'.format('po za' if nu_siebie else 'u siebie w', 'astem' if nu_siebie else 'eście')
        res = f'# Przypuszczalny koszt przy następujących parametrach:\n* poziom żeglugi {lv},\n* na {dni} dni,\n* {czy_24},\n* {nu_siebie},\nto: {cost} złota'
        await interaction.response.send_message(res)
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)


Khufra.run(TOKEN)
