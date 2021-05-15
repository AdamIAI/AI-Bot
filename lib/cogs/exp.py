from datetime import datetime, timedelta
from random import randint
from typing import Optional

from discord import Member, Embed, member
from discord.ext.menus import Menu, MenuPages, MenuError, ListPageSource
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from lib.db import db


class HelpMenu(ListPageSource):
    def __init__(self, ctx, data):
        self.ctx = ctx

        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(title="Leveling XP Leaderboard",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.me.avatar_url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} of {len_data:,} members")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page*self.per_page) + 1

        fields = []
        table = ("\n".join(
            f"{idx+offset}. {self.ctx.bot.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | Level: {entry[2]})" for idx, entry in enumerate(entries)))

        fields.append(("Ranks", table))

        return await self.write_page(menu, offset, fields)


class exp(Cog):
    def __init__(self, bot):
        self.bot = bot

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
                     ((member.id,) for member in self.guild.members if not member.bot))

        db.execute("INSERT OR IGNORE INTO bank (GuildID, UserID) VALUES",
                   ((member.guild.id, member.id) for member in self.members if not member.bot))

        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                     ((id_,) for id_ in to_remove))

        db.commit()

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

    @ command(name="level")
    async def display_level(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        xp, lvl = db.record(
            "SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (None, None)
        if xp > 0:
            await ctx.send(f"**{target.display_name}** is on level {lvl:,} with {xp:,} xp")
        else:
            await ctx.send(f"**{target.display_name}** isn't ranked yet")

    @ command(name="rank")
    async def display_rank(self, ctx, target: Optional[Member]):
        target = target or ctx.author

        ids = db.column("SELECT UserID FROM exp ORDER BY XP DESC")
        try:
            await ctx.send(f"**{target.display_name}** is rank **#{idx.index(target.id)+1}** of {len(ids)} people in **{ctx.author.guild.name}**")
        except ValueError:
            await ctx.send(f"**{target.display_name}** is not tracked by the leveling system")
            self.update_db()

    @ command(name="leaderboardxp", aliases=["leadxp"])
    async def display_leaderboard(self, ctx):
        records = db.records(
            "SELECT UserID, XP, Level FROM exp ORDER BY XP DESC")

        menu = MenuPages(source=HelpMenu(ctx, records),
                         clear_reactions_after=True, delete_message_after=60.0, timeout=60.0)
        await menu.start(ctx)

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
