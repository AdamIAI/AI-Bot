import discord
from discord import Intents
from discord import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command

from lib.db import db


class Welcome(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            db.execute("INSERT INTO exp (GuildID, UserID) VALUES (?, ?)",
                       member.guild.id, member.id)
        except:
            pass
        # if member.id == 536818739690340352:
        #     await self.bot.get_channel(836317763139665975).send(f"MY CREATOR {member.mention} HAS JOINED THE SERVER")
        if member.guild.id == 759091344617766933:
            await self.bot.get_channel(797135125661089822).send(f"Welcome **{member.mention}** to **{member.guild.name}**!")
        try:
            await member.send(f"Welcome to **{member.guild.name}**! Enjoy your stay!")

        except Forbidden:
            pass

    @Cog.listener()
    async def on_member_remove(self, member):
        try:
            if member.guild.id == 759091344617766933:
                await self.bot.get_channel(797135125661089822).send(f"**{member.display_name}** has left the server")
        except:
            pass


def setup(bot):
    bot.add_cog(Welcome(bot))
