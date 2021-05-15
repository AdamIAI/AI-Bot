from discord import Intents, message
from discord.embeds import Embed
from discord.ext import commands
from pathlib import Path
import discord
from discord.errors import HTTPException, Forbidden
from discord.ext import commands, ipc
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from youtube_dl import YoutubeDL
# from music_cog import music_cog
# from keep_alive import keep_alive
from typing import Optional
from discord.ext.commands import Bot as BotBase
from asyncio import sleep
from datetime import datetime
from glob import glob
import json
import os
import random
import math
import time
from decimal import Decimal
from lib.db import db
from lib.bot import Bot
from lib.bot import get_prefix
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import when_mentioned_or, command, has_permissions


def get_prefix(client, message):

    #    with open("prefixes.json", "r") as f:
    #        prefixes = json.load(f)

    #    return prefixes[str(message.guild.id)]

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)


client = Bot(command_prefix=get_prefix,
             intents=discord.Intents.all(), case_insensitive=True)

client.remove_command("help")


mainshop = [{"name": "Investor", "price": 500, "description": "Badge that shows you have started using the economy features"},
            {"name": "Banana", "price": 1000,
                "description": "Gives you Banana in your inventory and Gives you banana role"},
            {"name": "Entrepeneur", "price": 10000,
                "description": "Badge that shows You are a Professional Economy User"},
            {"name": "Capitalist", "price": 20000, "description": "Badge that shows you have Mastered the Economy"}]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)
filtered_words = ["daddy", "blyat", "rail me",
                  "nigg", "hitler", "fagg", "nazi", "autswitz"]
stfu = ["kam", "r slur"]
humour = ["I-"]
stop = ["msgdisable"]
start = ["msgenable"]
alpha = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q",
         "r", "s", "t", "u", "v", "w", "x", "y", "z", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
# Dashboard


# Events

async def on_ready():
    await client.change_presence(activity=discord.Game(name='Bonk!'))
    print("Bot is Online")


#    @client.event
#   async def on_guild_join(ctx, guild):

#       with open("prefixes.json", "r") as f:
#            prefixes = json.load(f)
#
#        prefixes[str(guild.id)] = "a!"
#
#        pre = prefixes[str(guild.id)]
#
#        with open("prefixes.json", "w") as f:
#            json.dump(prefixes, f)
#
#        db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?",
#                   pre, ctx.guild.id)
#
#        db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
#                     ((member.id,) for member in self.guild.members if not member.bot))
#
#        to_remove = []
#        stored_members = db.column("SELECT UserID FROM exp")
#        for id_ in stored_members:
#            if not self.guild.get_member(id_):
#                to_remove.append(id_)
#
#        db.multiexec("DELETE FROM exp WHERE UserID = ?",
#                     ((id_,) for id_ in to_remove))
#
#        db.commit()


# @client.event
# async def on_member_join(ctx, member):
    # await ctx.send(f"{member} has joined the server.")


# @client.event
# async def on_member_remove(ctx, member):
    # await ctx.send(f"{member} has left the server like the idiot they are!")


@client.event
async def on_message(msg):
    for word in filtered_words:
        if word in msg.content:
            await msg.delete()
            try:
                await msg.author.send("Please do not use language like that on our server")
            except:
                return

    for word in stfu:
        if word in msg.content:
            await msg.delete()
            await msg.channel.send(f"{msg.author.name}, do me a favour and actually shut the fuck up you set 8 dumbass")

    for word in humour:
        if word in msg.content:
            await msg.delete()
            await msg.channel.send(f"{msg.author.name}, come back when you have an actual sense of humour :)")

    try:
        if msg.mentions[0] == client.user:

            with open("prefixes.json", "r") as f:
                prefixes = json.load(f)

            pre = prefixes[str(msg.guild.id)]

            await msg.channel.send(f"My prefix for this server is {pre}")

    except:
        pass

    await client.process_commands(msg)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the permissions needed to perform this command")
    elif isinstance(error, MissingRequiredArgument):
        await ctx.send("Please input all the needed paramaters")
    elif isinstance(error, CommandNotFound):
        await ctx.send("That is not a command I have")
    elif isinstance(error, CommandOnCooldown):
        pass
    else:
        raise error

# Commands


@client.group(invoke_without_command=True)
async def help(ctx):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    em = discord.Embed(
        title="Help", description=f"Use {pre}help <command> for extended information on a command", color=ctx.author.color)

    em.add_field(name="Moderation", value=f"`{pre}help moderation`")
    em.add_field(
        name="Economy", value=f"`{pre}help economy`")
    em.add_field(name="Music", value=f"`{pre}help music`")
    em.add_field(name="Invite Me",
                 value=f"To invite this bot to you server [Click Here](https://discord.com/api/oauth2/authorize?client_id=805808053315436544&permissions=8&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcallback&scope=bot)!")
    em.set_footer(text="Powered By AI")
    await ctx.send(embed=em)


@help.command()
async def moderation(ctx):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    em = discord.Embed(title="Moderation",
                       description="Commands used for Moderation", color=ctx.author.color)

    em.add_field(
        name=f"`{pre}kick <member> [reason]`", value=f"Can only be used by members with 'Kick Member' permissions", inline=False)
    em.add_field(name=f"`{pre}ban <member> [reason]`",
                 value="Can only be used by members with 'Ban Member' permissions")
    em.add_field(name=f"`{pre}unban <member>`",
                 value="Can only be used by members with 'Administrator' permissions")
    em.add_field(name=f"`{pre}mute <member>`",
                 value="Can only be used by members with 'Kick Member' permissions")
    em.add_field(name="Invite Me",
                 value=f"To invite this bot to you server [Click Here](https://discord.com/api/oauth2/authorize?client_id=805808053315436544&permissions=8&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcallback&scope=bot)!", inline=False)
    em.set_footer(text="Powered By AI")
    await ctx.send(embed=em)


@help.command()
async def economy(ctx):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    em = discord.Embed(title="Economy",
                       description="Commands used for Economy", color=ctx.author.color)

    em.add_field(
        name=f"`{pre}balance [member]`", value=f"Shows member balance", inline=False)
    em.add_field(name=f"`{pre}daily`",
                 value="You can use this command once per day to get from 100 - 300 coins")
    em.add_field(name=f"`{pre}withdraw`",
                 value="Takes money from bank over to wallet")
    em.add_field(name=f"`{pre}deposit`",
                 value="Takes money from wallet over to bank")
    em.add_field(name=f"`{pre}send <member>`",
                 value="Sends money to chosen member's bank")
    em.add_field(name=f"`{pre}rob <member>`",
                 value="Steals from chosen member's wallet")
    em.add_field(name=f"`{pre}shop`",
                 value="Shows items that you can buy")
    em.add_field(name=f"`{pre}buy <item> [quantity]`",
                 value="Buys item from shop")
    em.add_field(name=f"`{pre}sell <item> <amount>`",
                 value="Sells item you own")
    em.add_field(name=f"`{pre}inventory`",
                 value="Shows your items")
    em.add_field(name=f"`{pre}rps <amount>`",
                 value="Bet money on rock paper scissors")
    em.add_field(name=f"`{pre}slots <amount>`",
                 value="Game of chance")
    em.add_field(name=f"`{pre}leaderboard`",
                 value="Shows top 10 richest members")
    em.add_field(name="Invite Me",
                 value=f"To invite this bot to you server [Click Here](https://discord.com/api/oauth2/authorize?client_id=805808053315436544&permissions=8&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcallback&scope=bot)!", inline=False)
    em.set_footer(text="Powered By AI")
    await ctx.send(embed=em)


@help.command()
async def music(ctx):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    pre = prefixes[str(ctx.guild.id)]
    em = discord.Embed(title="Music",
                       description="Commands used for Music", color=ctx.author.color)

    em.add_field(
        name=f"`{pre}play <song>`", value=f"Plays Song in your voice channel", inline=False)
    em.add_field(name=f"`{pre}skip`",
                 value="Skips current song")
    em.add_field(name=f"`{pre}pause`",
                 value="Will pause current song")
    em.add_field(name=f"`{pre}resume`",
                 value="Will resume paused song")
    em.add_field(name=f"`{pre}stop`",
                 value="Stops music")
    em.add_field(name=f"`{pre}join`",
                 value="Makes Bot join your voice channel")
    em.add_field(name=f"`{pre}leave`",
                 value="Makes Bot leave your voice channel")
    em.add_field(name=f"`{pre}queue`",
                 value="Shows upcoming songs in queue")
    em.add_field(name="Invite Me",
                 value=f"To invite this bot to you server [Click Here](https://discord.com/api/oauth2/authorize?client_id=805808053315436544&permissions=8&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcallback&scope=bot)!", inline=False)
    em.set_footer(text="Powered By AI")
    await ctx.send(embed=em)


@client.command(aliases=['cp'])
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):

    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f)

    await ctx.send(f"My Prefix was changed to {prefix}")

    db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?",
               prefix, ctx.guild.id)


@client.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"I have cleared `{amount} messages`!")
    time.sleep(2)
    await ctx.channel.purge(limit=1)

# Kick/Ban


@client.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    try:
        await member.send(f"You have been kicked from **{(member.guild.name)}** because {reason}")
    except:
        await ctx.author.send("The member has their dms closed")
    await member.kick(reason=reason)


@client.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await ctx.channel.purge(limit=1)
    if reason != None:
        try:
            await member.send(f"You have been banned from **{(member.guild.name)}** because {reason}")
        except:
            return
    await member.ban(reason=reason)


@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_disc = member.split('#')

    for banned_entry in banned_users:
        user = banned_entry.user

        if(user.name, user.discriminator) == (member_name, member_disc):
            await ctx.guild.unban(user)
            await ctx.send(member_name + " has been unbanned")
            return

    await ctx.send(member + " was not found")


@client.command(aliases=['m'])
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member):
    await ctx.channel.purge(limit=1)
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mutedRole:
        mutedRole = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)

    await member.add_roles(mutedRole)
    await ctx.send(f"{member.mention} has been muted")


@client.command(aliases=['um'])
@commands.has_permissions(kick_members=True)
async def unmute(ctx, member: discord.Member):
    mutedRole = discord.utils.get(ctx.guild.roles, name="Muted")
    try:
        await member.remove_roles(mutedRole)
        await ctx.send(f"{member.mention} was unmuted")
    except:
        await ctx.send(f"{member.display_name} is not muted")
        if not mutedRole:
            mutedRole = await ctx.guild.create_role(name="Muted")

            for channel in ctx.guild.channels:
                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)

# Economy System
Working = False
workMon = 0
mins = 0
secs = 0


@client.group(invoke_without_command=True)
@cooldown(1, 120, BucketType.guild)
async def work(ctx):
    await open_account(ctx.author)
    global workMon
    workMon = random.randrange(100, 300)
    Working = True
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

        pre = prefixes[str(ctx.guild.id)]
    em = discord.Embed(
        description=f"You have started working, come back in **1 hour** and use the `{pre}work claim` command to claim your **{workMon}** :coin: paycheck", color=ctx.author.color)
    await ctx.send(embed=em)


@work.error
async def work_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        ab = error.retry_after/60
        abc = int(ab)
        global mins
        mins = round(abc, 0)
        global secs
        secs = int(round(error.retry_after, 0))

        if mins == 0:
            em = discord.Embed(
                description=f"You are still working, come back in **{secs} seconds** to claim your paycheck of {workMon} :coin:", color=discord.Color.red())
            await ctx.send(embed=em)
        else:
            em = discord.Embed(
                description=f"You are still working, come back in **{mins} minutes** to claim your paycheck of {workMon} :coin:", color=discord.Color.red())
            await ctx.send(embed=em)


@work.command()
async def claim(ctx):
    if work_error == None:
        await update_bank(ctx.author, workMon)
        em = discord.Embed(
            description=f"{ctx.author.name}, here is your paycheck for your last work. You gained **{workMon}** :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
    else:
        await work_error(ctx, CommandOnCooldown)


@client.command()
async def Bank(ctx, member: discord.Member = None):
    if member == None:
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()

        bank_amt = users[str(user.id)]["bank"]

        em = discord.Embed(
            title=f"{ctx.author.name}'s balance", color=ctx.author.color)
        em.add_field(name="Bank Balance", value=bank_amt)
        await ctx.send(embed=em)
    else:
        await open_account(member)
        user = member
        users = await get_bank_data()

        bank_amt = users[str(user.id)]["bank"]

        em = discord.Embed(
            title=f"{member.name}'s balance", color=member.color)
        em.add_field(name="Bank Balance", value=int(bank_amt))
        await ctx.send(embed=em)


@client.command()
async def Wallet(ctx, member: discord.Member = None):
    if member == None:
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()

        wallet_amt = users[str(user.id)]["wallet"]

        em = discord.Embed(
            title=f"{ctx.author.name}'s balance", color=ctx.author.color)
        em.add_field(name="Wallet Balance", value=wallet_amt)
        await ctx.send(embed=em)
    else:
        await open_account(member)
        user = member
        users = await get_bank_data()

        wallet_amt = users[str(user.id)]["wallet"]

        em = discord.Embed(
            title=f"{member.name}'s balance", color=member.color)
        em.add_field(name="Wallet Balance", value=int(wallet_amt))
        await ctx.send(embed=em)


@client.command()
async def balance(ctx, member: discord.Member = None):
    if member == None:
        await open_account(ctx.author)
        user = ctx.author
        users = await get_bank_data()

        wallet_amt = users[str(user.id)]["wallet"]
        bank_amt = users[str(user.id)]["bank"]

        em = discord.Embed(
            title=f"{ctx.author.name}'s balance", color=ctx.author.color)
        em.add_field(name="Wallet Balance", value=wallet_amt)
        em.add_field(name="Bank Balance", value=bank_amt)
        await ctx.send(embed=em)
    else:
        await open_account(member)
        user = member
        users = await get_bank_data()

        wallet_amt = users[str(user.id)]["wallet"]
        bank_amt = users[str(user.id)]["bank"]

        em = discord.Embed(
            title=f"{member.name}'s balance", color=member.color)
        em.add_field(name="Wallet Balance", value=int(wallet_amt))
        em.add_field(name="Bank Balance", value=int(bank_amt))
        await ctx.send(embed=em)


@client.command()
@cooldown(1, 86400, BucketType.user)
async def daily(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    users[str(user.id)]["wallet"]

    earnings = random.randrange(101)

    await ctx.send(f"I gave you {earnings} :coin:!")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@daily.error
async def daily_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        fractional, whole = math.modf(error.retry_after/3600)
        ab = fractional*60
        abc = int(ab)
        mins = round(abc, 0)
        cool = int(error.retry_after//3600)
        await ctx.send(f"That command is on **Cooldown**. Try again in {int(cool)} hours and {mins} minutes")


@ client.command(aliases=['w'])
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            ctx.command.reset_cooldown(ctx)
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}withdraw <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}withdraw <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")

    await ctx.send(f"You withdrew {amount} :coin:!")


@ client.command(aliases=['d'])
async def deposit(ctx, amount=None):
    await open_account(ctx.author)
    bal = await update_bank(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        amount = 0
        if bal[0] == 0:
            await ctx.send(f"{ctx.author.name}, You have no money in your wallet to deposit to you bank")
        else:
            await update_bank(ctx.author, -1*bal[0])
            await update_bank(ctx.author, bal[0], "bank")

            await ctx.send(f"You Deposited {bal[0]} :coin:!")
        return

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}deposit <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author, amount, "bank")

    await ctx.send(f"You Deposited {amount} :coin:!")


@ client.command()
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}dice <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}dice <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        return

    if amount > 1000:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you can't gamble more than 1000 :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
        return

    await update_bank(ctx.author, -1*amount, "bank")
    await update_bank(member, amount, "bank")

    await ctx.send(f"You sent {member.display_name} {amount} :coin:!")


@ client.command()
@cooldown(1, 3600, BucketType.guild)
async def slots(ctx, amount=None):
    await open_account(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            ctx.command.reset_cooldown(ctx)
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}slots <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}slots <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    if amount > 1000:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you can't gamble more than 1000 :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    final = []
    for i in range(3):
        a = random.choice(
            [":game_die:", ":coin:", ":diamond_shape_with_a_dot_inside:"])

        final.append(a)

    await ctx.send(f"{str(final)}")

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
        await update_bank(ctx.author, amount)
        await ctx.send(f"You won {amount} :coin:")
    else:
        await update_bank(ctx.author, -1*amount)
        await ctx.send(f"You lost {-1*amount} :coin:")


@slots.error
async def slots_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        em = discord.Embed(
            description=f"This game is on **Cooldown**, try playing this again in {int(error.retry_after//60)} minutes", color=discord.Color.red())
        await ctx.send(embed=em)


@ client.command()
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0] < 100:
        em = discord.Embed(
            description=f"You can't rob {member.mention}? They have under 100 :coin:!", color=discord.Color.red())
        await ctx.send(embed=em)
    else:
        if ctx.author.id == 764185204830765076:
            earnings = random.randrange(0, bal[0])
            await update_bank(member, earnings)
            await update_bank(ctx.author, -1*earnings)

            await ctx.send(f"Plan Backfired {member.name} robbed you of {earnings}")
        else:
            earnings = random.randrange(0, bal[0])
            await update_bank(ctx.author, earnings)
            await update_bank(member, -1*earnings)

            await ctx.send(f"You robbed {member} of {earnings} coins!")


@ client.command()
async def shop(ctx):
    em = discord.Embed(title="Shop", color=ctx.author.color)

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name=name, value=f"£{price} | {desc}")

    await ctx.send(embed=em)


@ client.command()
async def buy(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        em = discord.Embed(
            description=f"That item doesn't exist!", color=discord.Color.red())
        await ctx.send(embed=em)
        return
    if res[1] == 2:
        em = discord.Embed(
            description=f"You don't have enough :coin: in your wallet to buy {amount} {item}", color=discord.Color.red())
        await ctx.send(embed=em)
        return

    await ctx.send(f"You just bought {amount} {item}")


@ client.command(aliases=['i'])
async def inventory(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    em = discord.Embed(title="Inventory", color=ctx.author.color)
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name=name, value=amount)

    await ctx.send(embed=em)


async def buy_this(user, item_name, amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    if bal[0] < cost:
        return [False, 2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item": item_name, "amount": amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item": item_name, "amount": amount}
        users[str(user.id)]["bag"] = [obj]

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, int(cost*-1), "wallet")

    return [True, "Worked"]


@ client.command()
async def sell(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have {amount} {item} in your bag")
            return
        if res[1] == 3:
            await ctx.send(f"You don't have {item} in your bag")
            return

    await ctx.send(f"You just sold {amount} {item}")


async def sell_this(user, item_name, amount, price=None):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            if price == None:
                price = 0.9 * item["price"]
            break

    if name_ == None:
        return [False, 1]

    cost = price*amount

    users = await get_bank_data()

    bal = await update_bank(user)

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                if new_amt < 0:
                    return [False, 2]
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            return [False, 3]
    except:
        return [False, 3]

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    await update_bank(user, int(cost), "wallet")

    return [True, "Worked"]


@ client.command(aliases=["lb"])
async def leaderboard(ctx):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"{ctx.author.guild.name} Richest People",
                       description="This is decided on the basis of :coin: in the bank and wallet", color=ctx.author.color)

    x = 10
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await client.fetch_user(id_)
        name = member.name
        em.add_field(name=f"**{index}**. {name}",
                     value=f"{amt}",  inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)

    # Mastermind


@ client.command(aliases=["mm"])
@cooldown(1, 3600, BucketType.guild)
async def mastermind(ctx, amount=None):
    await open_account(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            ctx.command.reset_cooldown(ctx)
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}mastermind <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}mastermind <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    if amount > 1000:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you can't gamble more than 1000 :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return
    # Game Code

    code_digits = 4  # Number of digits in the code
    min_num = 0  # Largest possible number in the code
    max_num = 9  # Smallest possible number in the code
    max_turns = 10  # Number of turns
    await ctx.send(str(code_digits)+" Digit Code - Numbers "+str(min_num)+" to "+str(max_num)+" - "+str(max_turns)+" Turns")
    code = ""
    for x in range(0, code_digits):
        code += str(random.randint(min_num, max_num))

    mmGame = [1, 10]

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in mmGame

    async def black_check():
        current_value = 0
        black_num = 0
        while current_value < code_digits:
            if code[current_value] == guess[current_value]:
                black_num += 1
            current_value += 1
        return black_num

    async def white_check():
        current_value = min_num
        white_num = 0
        while current_value <= max_num:
            white_num += min(code.count(str(current_value)),
                             guess.count(str(current_value)))
            current_value += 1
        white_num -= black_check()
        return white_num
    turn = 1
    while turn <= max_turns:
        input_check = False
        while input_check == False:
            guess = input("Turn "+str(turn)+". Guess: ")
            if guess.isdigit() == True and len(guess) == code_digits:
                input_check = True
            else:
                await ctx.send("Please enter a "+str(code_digits)+" digit number.")
        plural = ""
        if black_check() != 1:
            plural += "s"
        await ctx.send(str(black_check())+" black pin"+plural+".")
        plural = ""
        if white_check() != 1:
            plural = plural+"s"
        await ctx.send(str(white_check())+" white pin"+plural+".")
        if black_check() == code_digits:
            turn = max_turns+1
        await ctx.send("---------------")
        turn += 1
    if black_check() == code_digits:
        await ctx.send("You win")
    else:
        await ctx.send("You lose. The code was "+code+".")
        await update_bank(ctx.author, -1*amount)
        await ctx.send(f"You lost {amount} coins")


@mastermind.error
async def mastermind_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        em = discord.Embed(
            description=f"This game is on **Cooldown**, try playing this again in {int(error.retry_after//60)} minutes", color=discord.Color.red())
        await ctx.send(embed=em)


@client.command()
@cooldown(1, 3600, BucketType.guild)
async def dice(ctx, amount=None):
    await open_account(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            ctx.command.reset_cooldown(ctx)
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}dice <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}dice <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    if amount > 1000:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you can't gamble more than 1000 :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    user_roll1 = random.randrange(1, 6)
    user_roll2 = random.randrange(1, 6)
    comp_roll1 = random.randrange(1, 6)
    comp_roll2 = random.randrange(1, 6)

    userT = user_roll1 + user_roll2
    compT = comp_roll1 + comp_roll2

    await ctx.send(f":game_die: {ctx.author.name} bets {amount} :coin: and throws their dice...")
    time.sleep(2)
    if userT == 12:
        time.sleep(1)
        await ctx.send(f":game_die: :astonished: {ctx.author.name} rolls two 6s! Their opponent is afraid and gives up. {ctx.author.name} won {3*amount} :coin:!")
        await update_bank(ctx.author, 3*amount)
    else:
        await ctx.send(f":game_die: {ctx.author.name} rolls a **{user_roll1}** and a **{user_roll2}**...")
        time.sleep(2)
        await ctx.send(f":game_die: your opponent has rolled their dice... and get a **{comp_roll1}** and a **{comp_roll2}**...")
        if userT > compT:
            if user_roll1 == user_roll2:
                time.sleep(1)
                await ctx.send(f":game_die: {ctx.author.name}, you rolled a double and won twice your bet: {2*amount} :coin:")
                await update_bank(ctx.author, 2*amount)
            time.sleep(1)
            await ctx.send(f":game_die: {ctx.author.name}, you **won {amount} :coin:**")
            await update_bank(ctx.author, amount)
        elif userT == compT:
            time.sleep(1)
            await ctx.send(f":game_die: {ctx.author.name}, its's a draw, you get your {amount} :coin:")
        else:
            time.sleep(1)
            await ctx.send(f":game_die: {ctx.author.name}, you lost your bet of {amount} :coin:")
            await ctx.send("https://tenor.com/view/rick-astley-rick-roll-dancing-dance-moves-gif-14097983")


@dice.error
async def dice_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        em = discord.Embed(
            description=f"This game is on **Cooldown**, try playing this again in {int(error.retry_after//60)} minutes", color=discord.Color.red())
        await ctx.send(embed=em)


@ client.command()
@cooldown(1, 3600, BucketType.guild)
async def rps(ctx, amount=None):
    await open_account(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            return

    if ctx.author.id == 688834818603089925 or 772184962815361096:
        bad = random.randint(1, 10)
        if bad == 2:
            await ctx.send("smh ur a burnt popadom m8")
            return
        else:
            pass

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}rps <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}rps <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    if amount > 1000:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you can't gamble more than 1000 :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    rpsGame = ["rock", "paper", "scissors"]

    await ctx.send("Rock, Paper or Scissors?")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in rpsGame

    user_choice = (await client.wait_for('message', check=check)).content

    comp_choice = random.choice(rpsGame)
    if user_choice == 'rock':
        if comp_choice == 'rock':
            await ctx.send("You played Rock :rock: Your Opponent also played Rock :rock:")
            await ctx.send("Its a draw. You get your bet back")
        elif comp_choice == 'paper':
            await ctx.send("You played Rock :rock: Your Opponent played Paper :newspaper:")
            await update_bank(ctx.author, -1*amount)
            await ctx.send(f"You lost {amount} coins")
            await ctx.send("https://tenor.com/view/rick-astley-rick-roll-dancing-dance-moves-gif-14097983")
        elif comp_choice == 'scissors':
            await ctx.send("You played Rock :rock: Your Oppornent played Scissors :scissors:")
            await update_bank(ctx.author, amount)
            await ctx.send(f"You won {amount} Coins")

    elif user_choice == 'paper':
        if comp_choice == 'rock':
            await ctx.send("You played Paper :newspaper: Your Opponent played Rock :rock:")
            await update_bank(ctx.author, amount)
            await ctx.send(f"You won {amount} Coins")
        elif comp_choice == 'paper':
            await ctx.send("You played Paper :newspaper: Your Opponent played Paper :newspaper:")
            await ctx.send("It's a draw. You get your bet back")
        elif comp_choice == 'scissors':
            await ctx.send("You played Paper :newspaper: Your Oppornent played Scissors :scissors:")
            await update_bank(ctx.author, -1*amount)
            await ctx.send(f"You lost {amount} coins")
            await ctx.send("https://tenor.com/view/rick-astley-rick-roll-dancing-dance-moves-gif-14097983")

    elif user_choice == 'scissors':
        if comp_choice == 'rock':
            await ctx.send("You played Scissors :scissors: Your Opponent played Rock :rock:")
            await update_bank(ctx.author, -1*amount)
            await ctx.send(f"You lost {amount} coins")
            await ctx.send("https://tenor.com/view/rick-astley-rick-roll-dancing-dance-moves-gif-14097983")
        elif comp_choice == 'paper':
            await ctx.send("You played Scissors :scissors: Your Opponent played Paper :newspaper:")
            await update_bank(ctx.author, amount)
            await ctx.send(f"You won {amount} Coins")
        elif comp_choice == 'scissors':
            await ctx.send("You played Rock :rock: Your Oppornent played Scissors :scissors:")
            await ctx.send("It's a draw. You get your bet back")


@rps.error
async def rps_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        em = discord.Embed(
            description=f"This game is on **Cooldown**, try playing this again in {int(error.retry_after//60)} minutes", color=discord.Color.red())
        await ctx.send(embed=em)


@client.command()
# @cooldown(1, 3600, BucketType.guild)
async def roulette(ctx, amount=None):
    await open_account(ctx.author)

    if ctx.author.id == 764185204830765076:
        bad = random.randint(1, 3)
        if bad == 2:
            await ctx.send("no ur bad")
            ctx.command.reset_cooldown(ctx)
            return

    prefix = db.field(
        "SELECT Prefix FROM guilds WHERE GuildID = ?", ctx.guild.id)

    if amount == None:
        em = discord.Embed(
            description=f"`Invalid command usage, try this instead: {prefix}roulette <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you dont have enough :coin: to make this transaction", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return
    if amount < 0:
        em = discord.Embed(
            description=f"`amount Argument given negative must be positive, try this instead: {prefix}roulette <amount>`", color=discord.Color.red())
        em = em.add_field(name="Arguments",
                          value="`amount` : *Positive Integer*")
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    if amount > 1000:
        em = discord.Embed(
            description=f"{ctx.author.mention}, you can't gamble more than 1000 :coin:", color=discord.Color.red())
        await ctx.send(embed=em)
        ctx.command.reset_cooldown(ctx)
        return

    round1 = random.randint(1, 6)
    await ctx.send(f":persevere::gun: {ctx.author.name} bets {amount} :coin: and pulls the trigger...")
    time.sleep(3)
    if round1 == 6:
        await update_bank(ctx.author, -1*amount)
        await ctx.send(f":skull_crossbones: {ctx.author.name} lost {amount}")
        return
    else:
        win1 = int(1.1*amount)
        await update_bank(ctx.author, win1 - amount)
        await ctx.send(f":hot_face: {ctx.author.name} wins back {win1} :coin:")
        win2 = int(1.3*amount)
        time.sleep(0.5)
        await ctx.send(f"{ctx.author.name}, type **continue** to bet your gains and try to win {win2} :coin:")
        roulet = ["continue"]

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in roulet

        cont = (await client.wait_for('message', check=check)).content
        if cont == "continue":
            round2 = random.randint(1, 5)
            await ctx.send(f":persevere::gun: {ctx.author.name} bets {win1} :coin: and pulls the trigger...")
            time.sleep(3)
            if round2 == 5:
                await update_bank(ctx.author, -1*win1)
                await ctx.send(f":skull_crossbones: {ctx.author.name} lost {win1}")
                return
            else:
                await update_bank(ctx.author, win2-amount)
                await ctx.send(f":hot_face: {ctx.author.name} wins back {win2} :coin:")
                win3 = int(1.8*amount)
                time.sleep(0.5)
                await ctx.send(f"{ctx.author.name}, type **continue** to bet your gains and try to win {win3} :coin:")

                cont = (await client.wait_for('message', check=check)).content
                if cont == "continue":
                    round3 = random.randint(1, 4)
                    await ctx.send(f":persevere::gun: {ctx.author.name} bets {win2} :coin: and pulls the trigger...")
                    time.sleep(3)
                    if round3 == 4:
                        await update_bank(ctx.author, -1*win2)
                        await ctx.send(f":skull_crossbones: {ctx.author.name} lost {win2}")
                        return
                    else:
                        await update_bank(ctx.author, win3-amount)
                        await ctx.send(f":hot_face: {ctx.author.name} wins back {win3} :coin:")
                        win4 = int(2.5*amount)
                        time.sleep(0.5)
                        await ctx.send(f"{ctx.author.name}, type **continue** to bet your gains and try to win {win4} :coin:")

                    cont = (await client.wait_for('message', check=check)).content
                    if cont == "continue":
                        round4 = random.randint(1, 3)
                        await ctx.send(f":persevere::gun: {ctx.author.name} bets {win3} :coin: and pulls the trigger...")
                        time.sleep(3)
                        if round4 == 3:
                            await update_bank(ctx.author, -1*win3)
                            await ctx.send(f":skull_crossbones: {ctx.author.name} lost {win3}")
                            return
                        else:
                            await update_bank(ctx.author, win4-amount)
                            await ctx.send(f":hot_face: {ctx.author.name} wins back {win4} :coin:")
                            win5 = int(4*amount)
                            time.sleep(0.5)
                            await ctx.send(f"{ctx.author.name}, type **continue** to bet your gains and try to win {win5} :coin:")

                            cont = (await client.wait_for('message', check=check)).content
                            if cont == "continue":
                                round5 = random.randint(1, 2)
                                await ctx.send(f":persevere::gun: {ctx.author.name} bets {win4} :coin: and pulls the trigger...")
                                time.sleep(3)
                                if round5 == 2:
                                    await update_bank(ctx.author, -1*win4)
                                    await ctx.send(f":skull_crossbones: {ctx.author.name} lost {win4}")
                                    return
                                else:
                                    await update_bank(ctx.author, win5-amount)
                                    await ctx.send(f":four_leaf_clover: Amazing {ctx.author.name}, you won all rounds and gained {win5} :coin:!")
                                    return
        else:
            return


@ client.command(name="slap", aliases=["hit"])
async def slap(ctx, member: discord.Member, *, reason: Optional[str] = "for no reason"):
    await ctx.channel.purge(limit=1)
    if ctx.author.id == 764185204830765076:
        await ctx.send(f"I slapped {ctx.author.name} because yes!")
        return
    elif ctx.author.id == 763478341679972401:
        rand = random.randint(1, 5)
        if random.randint == 5:
            await ctx.send(f"I slapped Carlyn FOR SZYMON BOIIIIII")
            return
    else:
        await ctx.send(f"{ctx.author.display_name} slapped {member.mention} {reason}")


@ slap.error
async def slap_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.send("I can't find that member")


@ client.command()
async def test(ctx):
    await ctx.send("Hello there")


async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 0
        users[str(user.id)]["bank"] = 0

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    return True


async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)

    return users


async def update_bank(user, change=0, mode="wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

    bal = [users[str(user.id)]["wallet"], users[str(user.id)]["bank"]]
    return bal

client.load_extension('lib.cogs.music_cog')
client.load_extension('lib.cogs.welcome')
client.load_extension('lib.cogs.exp')
client.load_extension('lib.cogs.help')
client.load_extension('lib.cogs.meta')
client.load_extension('lib.cogs.misc')

bot = Bot()


@client.command(name="restart")
async def restart(ctx):
    if ctx.author.id == 536818739690340352:
        await ctx.send("Restarting...")

        with open("./data/banlist.txt", "w", encoding="utf-8") as f:
            f.writelines([f"{item}\n" for item in client.banlist])

        db.commit()
        await client.logout()
        time.sleep(3)
        await client.login("ODA1ODA4MDUzMzE1NDM2NTQ0.YBgROw.bDqNogddX_pbvEoq03Kr012oFDk", bot=True)

    else:
        await ctx.send("You are not the right person to shutdown the bot")

# client.ipc.start()
# keep_alive()
client.run("ODA1ODA4MDUzMzE1NDM2NTQ0.YBgROw.bDqNogddX_pbvEoq03Kr012oFDk")
