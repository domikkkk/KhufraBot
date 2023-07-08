import discord
from discord.ext import commands
from discord import app_commands
from Common import TOKEN
from Ikariam.Islands import calc, distance, qsort, calc_time



intents = discord.Intents().default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.reactions = True



# @khufra.event
# async def on_message(mess: discord.Message):
#     if mess.author == khufra.user:
#         return
#     if mess.content.startswith(khufra.command_prefix):
#         await khufra.process_commands(mess)
#         return
#     await mess.channel.send(mess.content)



# @khufra.command()
# async def delete(x, filename: str, id: int):
#     file = File_csv(filename)
#     file.read()
#     file.delete_id(id)
#     await x.channel.send('Usunięto!')


# @khufra.command()
# async def get(x, filename: str, id: str):
#     file = File_csv(filename)
#     file.read()
#     rundy = file.get_id(id)
#     message = '```cs\n'
#     licznik = 0
#     for runda in rundy:
#         godzina_rundy, przybycie, czyje = runda
#         message += f'{godzina_rundy},{przybycie},{czyje}\n'
#         if licznik == 15:
#             message += '```'
#             await x.channel.send(message)
#             message = '```cs\n'
#             licznik = 0
#         licznik += 1
#     message += '```'
#     await x.channel.send(message)


# @khufra.command()
# async def luki(x, filename: str):
#     file = File_csv(filename)
#     file.read()
#     rundy = file.luki()
#     message = '```cs\n'
#     for runda in rundy:
#         godzina_rundy, przybycie, czyje = runda
#         message += f'{godzina_rundy},{przybycie},{czyje}\n'
#     message += '```'
#     await x.channel.send(message)


# @khufra.command()
# async def create(x, filename: str, day: str, clock: str, rows=0):
#     rows = int(rows)
#     data = ' '.join([day, clock])
#     file = File_csv(filename)
#     file.clear_and_create_file(data, rows)
#     await x.channel.send('Stworzono nowy plik!')


# @khufra.command()
# async def m(x, filename: str, fromm: str, delfin='0'):
#     who_str = str(x.author)
#     frommm = fromm.split('-')
#     mail = save_in_miotly(filename, frommm, who_str, delfin)
#     await x.send(f'{mail}')


# @khufra.command()
# async def przesun(x, filename: str, time: str):
#     time1 = time.split(':')
#     if len(time1) != 2 or time1[0] == '' or time1[1] == '':
#         await x.send('Musisz podać minuty i sekundy')
#         return
#     file = File_csv(filename)
#     file.read()
#     file.delay(time)
#     w = 'Pomyślnie przesunięto czas rund o'
#     await x.send(f'{w} {int(time1[0])}min i {int(time1[1])}s.')


Khufra = commands.Bot(command_prefix='?', intents=intents)


@Khufra.command(
    name="find",
    description="Coś tam coś tam",
    help="Zwraca możliwe kordy dokąd może płynąć handel",
)
async def tag(ctx: commands.Context, *args):
    try:
        res = calc(*args)
        await ctx.channel.send(res)
    except Exception as e:
        await ctx.channel.send(e)


Khufra.run(TOKEN)
