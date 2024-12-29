import discord.ext.commands
from Common import GENERAL_CM, TEST
from discord.ext import commands
from discord import app_commands
import discord
import random
from Common import ME
import discord.ext
from Ikariam.api.generalBot import General
from Ikariam.api.session import ExpiredSession
import asyncio
from typing import Dict
import json
from decorators import restrict_to_guilds
from table2ascii import table2ascii as t2a, PresetStyle
from datetime import datetime
from dataclasses import asdict


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


with open("config.json", 'r') as f:
    guilds: Dict[int, Dict] = {int(id): item for id, item in json.load(f).items()}


# logging.basicConfig(filename="Khufra.log", level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
General_Bot = commands.Bot(command_prefix='?', intents=intents)

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
    generals = {id: General(guilds[id]["cookie"], guilds[id]["id"]) for id in guilds}
    print(generals)
    General_Bot.loop.create_task(check_general())


@General_Bot.tree.command(description="Wypisuje stan wojsk w sojuszu")
@app_commands.describe(what="Stan lądu czy floty?")
@app_commands.choices(what=[
    app_commands.Choice(name="Ląd", value=True),
    app_commands.Choice(name="Flote", value=False),
])
@restrict_to_guilds(guilds)
async def get_units(interaction: discord.Interaction, what: app_commands.Choice[int]):
    global generals
    await interaction.response.defer()
    MAX_ROWS = 6
    try:
        units = generals[interaction.guild_id].check_alliance_units(what.value)
        header = ["Gracz"] + list(asdict(list(units.values())[0]).keys())
        body = [[player] + list(asdict(units[player]).values()) for player in units]
        chunks = [body[i:i + MAX_ROWS] for i in range(0, len(body), MAX_ROWS)]
        for chunk in chunks:
            output = t2a(
                header=header,
                body=chunk,
                style=PresetStyle.thin_compact
            )
            await interaction.followup.send(f"```\n{output}\n```")
    except ExpiredSession:
        await interaction.followup.send(f"<@{ME}> potrzebna nowa sesja.")
    except Exception as e:
        await error(interaction, e)


async def check_general():
    await General_Bot.wait_until_ready()
    global generals
    loop = asyncio.get_running_loop()
    channels = {id: General_Bot.get_channel(guilds[id]["general_warnings"]) for id in guilds}
    while not General_Bot.is_closed():
        await asyncio.sleep(300)
        for id in channels:
            try:
                attacks = await loop.run_in_executor(None, generals[id].analyse_attacks)
                for attack in attacks:
                    await channels[id].send(f"<t:{attack.when}:R> {attack.action} - {attack.who.name+' '+attack.who.f} => {attack.whom.name+' '+attack.whom.f} - units: {attack.units}")
            except ExpiredSession:
                await channels[id].send(f"<@{ME}> potrzebna nowa sesja.")
                break
            except Exception as e:
                with open("error1.txt", 'w') as f:
                    f.write(str(e))


General_Bot.run(GENERAL_CM)
