from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from lib.db import db


class exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def process_xp(self, message):
        xp, lvl, xplock = db.record(
            "SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.utcnow() > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, message, xp, lvl):
        xp_to_add = randint(15, 25)
        new_lvl = int(((xp + xp_to_add)//28) ** 0.35)

        db .execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
                    xp_to_add, new_lvl, (datetime.utcnow()+timedelta(seconds=60)).isoformat(), message.author.id)

        if new_lvl > lvl:
            await message.channel.send(f"GG {message.author.mention}, you have levelled up to Level {new_lvl:,}!")

    @command(name="level")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record(
            "SELECT XP, Level FROM exp WHERE UserID = ?", target.id)

        await ctx.send(f"{target.display_name} is on level {lvl:,} with {xp:,} xp")

    @command(name="rank")
    async def display_rank(self, ctx, target: Optional[Member]):
        pass

    @ Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("exp")

    @ Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await self.process_xp(message)


def setup(bot):
    bot.add_cog(exp(bot))
