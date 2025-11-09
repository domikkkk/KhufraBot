import discord
from functools import wraps
from typing import Dict, List


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


def check_role(allowed_roles: List[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            user = interaction.user
            if user.guild_permissions.administrator:
                return await func(interaction, *args, **kwargs)
            user_roles = [role.name for role in user.roles]
            if not any(role in user_roles for role in allowed_roles):
                await interaction.response.send_message(
                    "Nie masz wymaganej rangi ani uprawnień administratora, aby użyć tej komendy.",
                    ephemeral=True
                )
                return
            return await func(interaction, *args, **kwargs)
        return wrapper
    return decorator
