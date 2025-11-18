from Common import GENERAL
from discord.ext import commands
from discord import app_commands
import discord
import random
from Common import ME
from Ikariam.api.generalBot import General
from Ikariam.api.session import ExpiredSession
from Ikariam.dataStructure import Attack
import asyncio
from typing import Dict, Tuple, List
import json
import decorators
from datetime import datetime
from dataclasses import asdict
import time
from views.AttackPages import AttackPages


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


with open("config.json", 'r') as f:
    guilds: Dict[int, Dict] = {int(id): item for id, item in json.load(f).items()}


# logging.basicConfig(filename="Khufra.log", level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
General_Bot = commands.Bot(command_prefix='?', intents=intents)

tasks: Dict[int, Tuple[asyncio.Task, int]] = {}
whom_timeout: List[str] = []

get_color = lambda: random.randint(0, 0xffffff)%(0xffffff+1)


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


@General_Bot.event
async def on_ready():
    synced = await General_Bot.tree.sync()
    print(synced)
    global generals
    generals = {id: General(guilds[id]["gf_token"], guilds[id]["nick"]) for id in guilds}
    General_Bot.loop.create_task(check_general())


@General_Bot.tree.command(description="Wypisuje stan wojsk w sojuszu")
@app_commands.describe(what="Stan lądu czy floty?")
@app_commands.choices(what=[
    app_commands.Choice(name="Ląd", value=True),
    app_commands.Choice(name="Flote", value=False),
])
@decorators.check_role(["olek"])
@decorators.restrict_to_guilds(guilds)
async def get_units(interaction: discord.Interaction, what: app_commands.Choice[int]):
    global generals
    await interaction.response.defer()
    try:
        units = generals[interaction.guild_id].check_alliance_units(what.value)
        units_names = list(asdict(list(units.values())[0]).keys())
        embed = discord.Embed(
            title="Ląd sojuszu" if what.value else "Flota sojuszu",
            color=get_color(),
            timestamp=datetime.now()
        )
        for player in units:
            to_see = ""
            for unit_name in units_names:
                player_units = asdict(units[player])
                to_see += unit_name+': ' + str(player_units[unit_name]) + ", " if player_units[unit_name] != 0 else ""
            embed.add_field(name=player, value=f"{to_see[:-2]}", inline=False)
        await interaction.followup.send(embed=embed)
    except ExpiredSession:
        await interaction.followup.send(f"<@{ME}> potrzebna nowa sesja.")
        exit(0)
    except Exception as e:
        await error(interaction, e)


@General_Bot.tree.command()
@decorators.check_role(["olek"])
@decorators.restrict_to_guilds(guilds)
async def get_stationed_units(interaction: discord.Interaction):
    global generals
    await interaction.response.defer()
    units = generals[interaction.guild_id].get_stationed_units()
    pages = AttackPages(interaction, units)
    await pages.send()


@General_Bot.tree.command(description="Tylko dla wtajemniczonych")
@app_commands.describe(duration="Czas na przerwę od ataków.")
@app_commands.choices(duration=[
    app_commands.Choice(name="3min", value=180),
    app_commands.Choice(name="5min", value=300),
    app_commands.Choice(name="10min", value=600),
    app_commands.Choice(name="15min", value=900),
    app_commands.Choice(name="1h", value=3600),
])
@decorators.check_role(["olek"])
@decorators.restrict_to_guilds(guilds)
async def disable(interaction: discord.Interaction, duration: app_commands.Choice[int]):
    stamper = round(time.time()) + duration.value
    user_id = interaction.user.id
    players = guilds[interaction.guild_id].get("players")
    player = players[str(user_id)]

    async def sleep_task():
        await asyncio.sleep(duration.value)
        await interaction.user.send(f"Skończył się czas obijania...")
        if user_id in tasks:
            whom_timeout.remove(player)
            del tasks[user_id]

    if user_id in tasks:
        stamp = tasks[user_id][1]
        date = datetime.fromtimestamp(stamp)
        await interaction.response.send_message(f"Już jesteś pominięty do {date}", ephemeral=True)
        return
    
    task = asyncio.create_task(sleep_task())
    tasks[user_id] = task, stamper
    whom_timeout.append(player)
    date = datetime.fromtimestamp(stamper)
    await interaction.response.send_message(f"Jesteś zbanowany do {date}", ephemeral=True)


async def check_general():
    await General_Bot.wait_until_ready()
    global generals
    loop = asyncio.get_running_loop()
    channels = {id: General_Bot.get_channel(guilds[id]["general_warnings"]) for id in guilds}
    while not General_Bot.is_closed():
        await asyncio.sleep(180)
        for id in channels:
            try:
                attacks = await loop.run_in_executor(None, generals[id].analyse_attacks)
                # players = guilds[id].get("players")
                for attack in attacks:
                    whom = attack.whom.name
                    if attack.who.name in "Barbarzyńcy" or attack.units == '1' or whom in whom_timeout:
                        continue
                    # if players is not None:
                    #     whom = f"<@{players.get(whom, whom)}>"
                    await channels[id].send(f"<t:{attack.when}:R> {attack.action} - {attack.who.name} {attack.who.f} => {whom} {attack.whom.f} - units: {attack.units}")
            except ExpiredSession:
                await channels[id].send(f"<@{ME}> potrzebna nowa sesja.")
                exit(0)
            except Exception as e:
                with open("general_error.txt", 'a') as f:
                    f.write(str(e))


General_Bot.run(GENERAL)
