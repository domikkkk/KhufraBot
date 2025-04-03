import discord.ext.commands
from Common import TEST, ME
from discord.ext import commands
import discord
from discord import app_commands
import discord.ext
from Ikariam.api.session import ExpiredSession, IkaBot
import decorators



intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True

Khufra = commands.Bot(command_prefix='?', intents=intents)

class Data:
    def __init__(self):
        self._limit = 1000000  # Tworzymy _limit w instancji
        self.old = 0
        self.max_limit = 7000000

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, new_limit):
        self.old = self._limit
        self._limit = new_limit


@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(synced)
    global data 
    data = Data()
    # global bot 
    # bot = IkaBot()
    

@Khufra.tree.command()
async def get_limit(interaction: discord.Interaction):
    global data
    await interaction.response.send_message(data.limit)


@Khufra.tree.command()
@app_commands.describe(new_limit="Nowa wartość po której przekroczeniu odpala się hades")
@decorators.check_rank([691566329177702432, ME])
async def set_limit(interaction: discord.Interaction, new_limit: int):
    global data
    if new_limit < 1000000 or new_limit > data.max_limit:
        await interaction.response.send_message(f"Ustaw wartość z zakresu 1000000, {data.max_limit}")
        return
    data.limit = new_limit
    await interaction.response.send_message(f"Ustawiono nowy limit z {data.old} na {data.limit}")


Khufra.run(TEST)
