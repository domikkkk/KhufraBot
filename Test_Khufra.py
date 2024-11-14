import discord.ext.commands
from Common import TEST, TEST_CHANNEL
from discord.ext import commands
import discord
import random
from functools import wraps
from Common import ME
import discord.ext
from Ikariam.api.generalBot import General
from Ikariam.api.session import ExpiredSession
from Ikariam.api.Cookie import gencookie
import asyncio


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


# logging.basicConfig(filename="Khufra.log", level=logging.DEBUG, format='%(levelname)s - %(asctime)s - %(message)s')
Khufra = commands.Bot(command_prefix='?', intents=intents)

get_color = lambda: random.randint(0, 0xffffff)%(0xffffff+1)


def restrict_to_guild_name(guild_name: str=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if interaction.user.id != ME:
                await interaction.response.send_message("Yolo")
                return
            if not interaction.guild:
                await interaction.response.send_message("Ta komenda nie jest dostępna w wiadomościach prywatnych.", ephemeral=True)
                return
            if guild_name is not None and interaction.guild.name != guild_name:
                await interaction.response.send_message("Nie masz dostępu do tej komendy na tym serwerze.", ephemeral=True)
                return
            return await func(interaction, *args, **kwargs)
        return wrapper
    return decorator


@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(synced)
    global general
    general = General(gencookie, 62)
    Khufra.loop.create_task(check_general())


async def check_general():
    await Khufra.wait_until_ready()
    global general
    loop = asyncio.get_running_loop()
    channel = Khufra.get_channel(TEST_CHANNEL)
    while not Khufra.is_closed():
        try:
            await asyncio.sleep(60)
            attacks = await loop.run_in_executor(None, general.analize_attacks)
            for attack in attacks:
                await channel.send(f"<t:{attack.when}:R> {attack.action} - {attack.who.name+' '+attack.who.f} => {attack.whom.name+' '+attack.whom.f} - units: {attack.units}")
        except ExpiredSession:
            await channel.send(f"<@{ME}> potrzebna nowa sesja.")
            break
        except Exception as e:
            with open("error.txt", 'w') as f:
                f.write(str(e))

Khufra.run(TEST)
