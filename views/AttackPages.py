import discord
from discord.ui import View
from typing import List
from Ikariam.dataStructure import Attack
from datetime import datetime
import random


def format_(a: Attack) -> str:
    return (
        f"⚔️ {a.action}\n"
        f"ilość: {a.units}\n"
        f"od kiedy: {datetime.fromtimestamp(int(a.when))}\n"
    )

def chunk_attacks(attacks: List[Attack], size=5):
    for i in range(0, len(attacks), size):
        yield attacks[i:i+size]


class AttackPages(View):
    def __init__(self, interaction: discord.Interaction, attacks: List[Attack]):
        super().__init__(timeout=180)
        self.interaction: discord.Interaction = interaction
        self.attacks = list(chunk_attacks(attacks))
        self.page = 0
        self.message = None

    def get_embed(self):
        embed = discord.Embed(
            title=f"Stacjonujące jednostki — strona {self.page+1}/{len(self.attacks)}",
            color= (lambda: random.randint(0, 0xffffff)%(0xffffff+1))()
        )
        for a in self.attacks[self.page]:
            embed.add_field(
                name=f"{a.who.name} {a.who.f} → {a.whom.name} {a.whom.f}",
                value=format_(a),
                inline=False
            )
        return embed

    async def send(self):
        if not self.attacks:   # <-- PUSTA LISTA
            await self.interaction.followup.send(
                "Brak stacjonujących jednostek.",
                ephemeral=True
            )
            return

        self.message = await self.interaction.followup.send(
            embed=self.get_embed(),
            view=self
        )

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button):
        self.page = (self.page - 1) % len(self.attacks)
        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button):
        self.page = (self.page + 1) % len(self.attacks)
        await interaction.response.edit_message(
            embed=self.get_embed(),
            view=self
        )
