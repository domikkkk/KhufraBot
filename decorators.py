import discord
from functools import wraps
from typing import Dict


def restrict_to_guilds(guilds_id: Dict):
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if not interaction.guild:
                await interaction.response.send_message("Ta komenda nie jest dostępna w wiadomościach prywatnych.")
                return
            if interaction.guild.id not in guilds_id:
                await interaction.response.send_message("Nie masz dostępu do tej komendy na tym serwerze.", ephemeral=True)
                return
            return await func(interaction, *args, **kwargs)
        return wrapper
    return decorator