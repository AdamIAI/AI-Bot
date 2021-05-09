from asyncio import sleep
from datetime import datetime
from glob import glob
from discord.commands.ext import Cog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions

IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


class Info(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cogs are ready")


def setup(client):
    client.add_cog(Info(client))
