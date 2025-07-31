from Common import GENERAL_CM, TEST
from discord.ext import commands
from discord import app_commands
import discord
import random
from Common import ME
from Ikariam.api.generalBot import General
from Ikariam.api.session import ExpiredSession
import asyncio
from typing import Dict
import json
from decorators import restrict_to_guilds
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
    try:
        units = generals[interaction.guild_id].check_alliance_units(what.value)
        units_names = list(asdict(list(units.values())[0]).keys())
        # body = [[player] + list(asdict(units[player]).values()) for player in units]
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
                players = guilds[id].get("players")
                for attack in attacks:
                    if attack.who.name in "Barbarzyńcy" or attack.units == '1':
                        continue
                    whom = attack.whom.name
                    if players is not None:
                        whom = f"<@{players.get(whom, whom)}>"
                    await channels[id].send(f"<t:{attack.when}:R> {attack.action} - {attack.who.name} {attack.who.f} => {whom} {attack.whom.f} - units: {attack.units}")
            except ExpiredSession:
                await channels[id].send(f"<@{ME}> potrzebna nowa sesja.")
                break
            except Exception as e:
                with open("general_error.txt", 'w') as f:
                    f.write(str(e))


General_Bot.run(GENERAL_CM)
