import discord
from discord.ext import commands


categories = [1164940024693928017]


def has_role(role_name: str):
    def predicate(ctx: commands.Context):
        role = discord.utils.get(ctx.author.roles, name=role_name)
        print(ctx.author.roles)
        return role in ctx.author.roles
    return commands.check(predicate)


class Bolki:
    def __init__(self, guild: discord.Guild) -> None:
        self._guild = guild
        self._members = guild.members
        self.members_id = {}
        for member in self._members:
            self.members_id[member.id] = member

    def send_mess_everywhere(self, categories):
        for category in self._guild.categories:
            if category.id in categories:
                name = ''.join(filter(str.isalnum), category.name)
                print(name)
