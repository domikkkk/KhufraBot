import discord.ext.commands
from Common import TEST
from discord.ext import commands
from discord import app_commands
import discord
import random
from functools import wraps
from Common import ME
import discord.ext


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
    commands = Khufra.tree.get_commands()
    for c in commands:
        print(c.name)
    guild_id = discord.Object(id=1223055963813187625)
    await Khufra.tree.sync(guild=guild_id)
    synced = await Khufra.tree.sync()
    print(synced)


@Khufra.tree.command(name="yolo")
@restrict_to_guild_name("Testowanie bota")
async def yolo(interaction: discord.Interaction):
    await interaction.response.send_message("Witaj chuju")



Khufra.run(TEST)
