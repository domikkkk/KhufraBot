import discord
from discord.ext import commands
from discord import app_commands
from Common import TOKEN
from Ikariam.Islands import calc, distance, qsort, calc_time
from Jap.keyboard import parse, parse_foreach


intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True


Khufra = commands.Bot(command_prefix='?', intents=intents)

@Khufra.event
async def on_ready():
    synced = await Khufra.tree.sync()
    print(synced)


# @Khufra.hybrid_command()
# async def sync(ctx: commands.Context):
#     synced = await Khufra.tree.sync()
#     await ctx.send(f"Synced {len(synced)}")


@Khufra.tree.command()
@app_commands.describe(text = "To co chcesz dostać po japońsku")
async def kana(interaction: discord.Interaction, text: str):
    res = parse_foreach(text)
    await interaction.response.send_message(res)


@Khufra.hybrid_command()
async def ping(ctx: commands.Context):
    await ctx.send(f"{round(Khufra.latency * 1000)}ms")


@Khufra.tree.command()
@app_commands.describe(x = 'Kordynat x wyspy', y = "Kordynat y wyspy", h = "Godziny płynięcia", m = "Minuty płynięcia", s = "Sekundy płynięcia")
async def find(interaction: discord.Interaction, x: int, y:int, h:int, m:int, s:int):
    args = [x, y, h, m, s]
    mes = f"Searching from [{x} {y}] with time {h}:{m}:{s}\n"
    try:
        res = calc(*args)
        await interaction.response.send_message(f"{mes}{res}")
    except Exception as e:
        await interaction.response.send_message(e, ephemeral=True)


Khufra.run(TOKEN)
