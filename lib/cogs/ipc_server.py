#import discord
#from discord.errors import HTTPException, Forbidden
from discord.ext import commands, ipc
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from youtube_dl import YoutubeDL
#from music_cog import music_cog
# from keep_alive import keep_alive
from typing import Optional
import json
import os
import random
import math
import time
from decimal import Decimal


class MyBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipc = ipc.Server(self, secret_key="AI")

    async def on_ready(self):
        """Called upon the READY event"""
        print("Bot is ready.")

    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc server is ready.")

    async def on_ipc_error(self, endpoint, error):
        """Called upon an error being raised within an IPC route"""
        print(endpoint, "raised", error)

    @client.ipc.route()
    async def get_guild_count(data):
        # returns the len of the guilds to the client
        return len(client.guilds)

    @client.ipc.route()
    async def get_guild_ids(data):
        final = []
        for guild in client.guilds:
            final.append(guild.id)
        return final  # returns the guild ids to the client

    client.ipc.start()
