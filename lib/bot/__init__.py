from asyncio import sleep
import datetime as dt
from glob import glob
import sqlite3
import json

import discord
from discord import Intents
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel
from discord.colour import Color
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions
from discord.ext.commands.converter import _get_from_guilds
from discord.flags import MemberCacheFlags
from lib.db import db

OWNER_IDS = [536818739690340352]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f" {cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self, *args, **kwargs):
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        try:
            with open("./data/banlist.txt", "r", encoding="utf-8") as f:
                self.banlist = [int(line.strip()) for line in f.readlines()]
        except FileNotFoundError:
            self.banlist = []

        db.autosave(self.scheduler)
        super().__init__(command_prefix=get_prefix,
                         owner_ids=OWNER_IDS, intents=discord.Intents.all(), case_insensitive=True)

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        # db.multiexec("INSERT OR IGNORE INTO exp (GuildID) VALUES (?)",
        # ((guild.id,) for guild in self.guilds))

       # db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
        # ((member.id,) for member in self.guild.members if not member.bot))

        # db.multiexec("INSERT OR IGNORE INTO bank (GuildID, UserID) VALUES (?, ?)",
        #              ((guild.id,) for guild in self.guilds), (member.id,) for member in self.guild.members if not member.bot)

        for guild in self.guilds:
            for member in guild.members:
                if not member.bot:
                    db.execute(
                        "INSERT OR IGNORE INTO exp (GuildID, UserID) VALUES (?, ?)", guild.id, member.id)

                    db.execute(
                        "INSERT OR IGNORE INTO bank (GuildID, UserID) VALUES (?, ?)", guild.id, member.id)

        db.multiexec("INSERT OR IGNORE INTO members (UserID) VALUES (?)", ((
            member.id,) for member in self.guild.members if not member.bot))

        db.commit()

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if message.author.id in self.banlist:
                await ctx.send("You are banned from using commands")

            elif not self.ready:
                await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")

            else:
                await self.invoke(ctx)

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        await self.stdout.send("An error occured.")
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments are missing.")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")

        elif hasattr(exc, "original"):
            # if isinstance(exc.original, HTTPException):
            # 	await ctx.send("Unable to send message.")

            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permission to do that.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            # await self.change_presence(activity=discord.Game(name="Break Adam's Monitor"))
            self.guild = self.get_guild(836317762657714217)
            self.stdout = self.get_channel(836317763139665975)
            self.scheduler.start()
            self.update_db()
            await self.stdout.send("Now online!")
            self.ready = True
            print("Bot Ready")

        else:
            print("Bot Reconnected")

    async def on_guild_join(self, guild):

        # if guild.id == 759091344617766933:
        #     Adam = self.get_user(536818739690340352)
        #     Jeremy = self.get_user(759097824502612029)
        #     Tom = self.get_user(610919121734991931)
        #     Ernest = self.get_user(534443891567362068)
        #     Anthony = self.get_user(495945320786690060)

        #     em = discord.Embed(
        #         description=f"Hello Everyone, I am the Bot Adam ({Adam.mention}) has been working on for the past month. Check out all of my commands on `a!help` and test them out. I would also like to thank Jeremy ({Jeremy.mention}), Tom ({Tom.mention}), Ernest ({Ernest.mention}) and Anthony ({Anthony.mention}) for helping me test the bot. Have a great day :))", color=discord.Color.red())
        #     await self.get_channel(797135125661089822).send(embed=em)

        with open("prefixes.json", "r") as f:
            prefixes = json.load(f)

        prefixes[str(guild.id)] = "a!"

        pre = prefixes[str(guild.id)]

        with open("prefixes.json", "w") as f:
            json.dump(prefixes, f)

        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        for guild in self.guilds:
            for member in guild.members:
                if not member.bot:
                    db.execute(
                        "INSERT OR IGNORE INTO bank (GuildID, UserID) VALUES (?, ?)", guild.id, member.id)

                    db.execute(
                        "INSERT OR IGNORE INTO exp (GuildID, UserID) VALUES (?, ?)", guild.id, member.id)

        # db.multiexec("INSERT OR IGNORE INTO members (UserID) VALUES (?)", ((
        #     member.id,) for member in self.guild.members if not member.bot))

        to_remove = []
        stored_members = db.column("SELECT UserID FROM exp")
        for id_ in stored_members:
            if not self.guild.get_member(id_):
                to_remove.append(id_)

        db.multiexec("DELETE FROM exp WHERE UserID = ?",
                     ((id_,) for id_ in to_remove))

        db.commit()

        # link = await self.guild.systemChannel.create_invite(max_age=300)
        Adam = self.get_user(536818739690340352)
        await Adam.send(f"I have joined **{guild.name}**")


bot = Bot()
