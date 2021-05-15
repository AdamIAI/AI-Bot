from discord import Member
from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions
import time
from time import sleep
from db import db


class Misc(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="addban")
    @has_permissions(manage_guild=True)
    async def addban_command(self, ctx, targets: Greedy[Member]):
        if not targets:
            await ctx.send("No targets specified")
            time.sleep(3)
            await ctx.channel.purge(limit=2)
        else:
            self.bot.banlist.extend([t.id for t in targets])
            await ctx.send("Done")
            time.sleep(3)
            await ctx.channel.purge(limit=2)

    @command(name="delban", aliases=["rmban"])
    @has_permissions(manage_guild=True)
    async def delban_command(self, ctx, targets: Greedy[Member]):
        if not targets:
            await ctx.send("No targets specified")

        else:
            for target in targets:
                self.bot.banlist.remove(target.id)
            await ctx.send("Done")
            time.sleep(3)
            await ctx.channel.purge(limit=2)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("misc")


def setup(bot):
    bot.add_cog(Misc(bot))
