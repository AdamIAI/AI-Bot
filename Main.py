import discord
from discord.ext import commands
from discord.ext.commands import Cog, BucketType
from discord.ext.commands import command, cooldown
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,
                                  CommandOnCooldown)
from youtube_dl import YoutubeDL
from music_cog import music_cog
import json
import os
import random


os.chdir("D:\\Adam\\Projects\\Discord Bot")

client = commands.Bot(command_prefix="a!")

mainshop = [{"name": "Watch", "price": 100, "description": "Time"},
            {"name": "Laptop", "price": 1000, "description": "Work"},
            {"name": "PC", "price": 10000, "description": "Gaming"}]

# Events


@client.event
async def on_ready():
    print("Bot is Online")


@client.event
async def on_member_join(member):
    await ctx.send(f"{member} has joined the server.")


@client.event
async def on_member_remove(member):
    await ctx.send(f"{member} has left the server like the idiot they are!")

# Commands


@client.command()
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=amount)

# Kick/Ban


@client.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)


@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)

# Music

client.add_cog(music_cog(client))

# Economy System


@client.command()
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(
        title=f"{ctx.author.name}'s balance", color=discord.Color.red())
    em.add_field(name="Wallet Balance", value=wallet_amt)
    em.add_field(name="Bank Balance", value=bank_amt)
    await ctx.send(embed=em)


@client.command()
@cooldown(1, 86400, BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)

    users = await get_bank_data()

    user = ctx.author

    users[str(user.id)]["wallet"]

    earnings = random.randrange(101)

    await ctx.send(f"I gave you {earnings} coins!")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)


@client.command()
async def withdraw(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount you would like to withdraw.")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("Insuffficient amount of money to complete transaction!")
        return
    if amount < 0:
        await ctx.send("Quantity of money must be Positive!")
        return

    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")

    await ctx.send(f"You withdrew {amount} coins!")


@client.command()
async def deposit(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount you would like to withdraw.")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("Insuffficient amount of money to complete transaction!")
        return
    if amount < 0:
        await ctx.send("Quantity of money must be Positive!")
        return

    await update_bank(ctx.author, -1*amount)
    await update_bank(ctx.author, amount, "bank")

    await ctx.send(f"You Deposited {amount} coins!")


@client.command()
async def send(ctx, member: discord.Member, amount=None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please enter the amount you would like to withdraw.")
        return

    bal = await update_bank(ctx.author)
    if amount == "all":
        amount = bal[0]

    amount = int(amount)
    if amount > bal[1]:
        await ctx.send("Insuffficient amount of money to complete transaction!")
        return
    if amount < 0:
        await ctx.send("Quantity of money must be Positive!")
        return

    await update_bank(ctx.author, -1*amount, "bank")
    await update_bank(member, amount, "bank")

    await ctx.send(f"You sent {member.display_name} {amount} coins!")


@client.command()
async def slots(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount you would like to withdraw.")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("Insuffficient amount of money to complete transaction!")
        return
    if amount < 0:
        await ctx.send("Quantity of money must be Positive!")
        return

    final = []
    for i in range(3):
        a = random.choice(["X", "O", "Q"])

        final.append(a)

    await ctx.send(str(final))

    if final[0] == final[1] or final[0] == final[2] or final[2] == final[1]:
        await update_bank(ctx.author, 2*amount)
        await ctx.send(f"You won {2*amount} coins")
    else:
        await update_bank(ctx.author, -1*amount)
        await ctx.send(f"You lost {-1*amount} coins")


@client.command()
async def rob(ctx, member: discord.Member):
    await open_account(ctx.author)
    await open_account(member)

    bal = await update_bank(member)

    if bal[0] < 100:
        await ctx.send(f"Are you sure you want to rob {member}? They have under 100 coins!")

    earnings = random.randrange(0, bal[0])

    await update_bank(ctx.author, earnings)
    await update_bank(member, -1*earnings)

    await ctx.send(f"You robbed {member} of {earnings} coins!")


@client.command()
async def shop(ctx):
    em = discord.Embed(title="Shop")

    for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        em.add_field(name=name, value=f"£{price} | {desc}")

    await ctx.send(embed=em)


@client.command()
async def buy(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return

    await ctx.send(f"You just bought {amount} {item}")


@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    em = discord.Embed(title="Bag")
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

    await update_bank(user, cost*-1, "wallet")

    return [True, "Worked"]


@client.command()
async def sell(ctx, item, amount=1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1] == 1:
            await ctx.send("That Object isn't there!")
            return
        if res[1] == 2:
            await ctx.send(f"You don't have {amount} {item} in your bag.")
            return
        if res[1] == 3:
            await ctx.send(f"You don't have {item} in your bag.")
            return

    await ctx.send(f"You just sold {amount} {item}.")


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

    await update_bank(user, cost, "wallet")

    return [True, "Worked"]


@client.command(aliases=["lb"])
async def leaderboard(ctx, x=1):
    users = await get_bank_data()
    leader_board = {}
    total = []
    for user in users:
        name = int(user)
        total_amount = users[user]["wallet"] + users[user]["bank"]
        leader_board[total_amount] = name
        total.append(total_amount)

    total = sorted(total, reverse=True)

    em = discord.Embed(title=f"Top {x} Richest People",
                       description="This is decided on the basis of raw money in the bank and wallet", color=discord.Color(red))
    index = 1
    for amt in total:
        id_ = leader_board[amt]
        member = await client.fetch_user(id_)
        name = member.name
        em.add_field(name=f"{index}. {name}", value=f"{amt}",  inline=False)
        if index == x:
            break
        else:
            index += 1

    await ctx.send(embed=em)

# Mastermind


@client.command(aliases=["mm"])
async def mastermind(ctx, amount=None):
    # Betting System
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount you would like to Bet")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("Insuffficient amount of money to complete transaction!")
        return

    if amount < 0:
        await ctx.send("Quantity of money must be Positive!")
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

mastermind()


@client.command()
async def rps(ctx, amount=None):
    await open_account(ctx.author)

    if amount == None:
        await ctx.send("Please enter the amount you would like to Bet")
        return

    bal = await update_bank(ctx.author)

    amount = int(amount)
    if amount > bal[0]:
        await ctx.send("Insuffficient amount of money to complete transaction!")
        return

    if amount < 0:
        await ctx.send("Quantity of money must be Positive!")
        return

    rpsGame = ["rock", "paper", "scissors"]

    await ctx.send("Rock, Paper or Scissors? If you win you take home twice your bet")

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
            await update_bank(ctx.author, 2*amount)
            await ctx.send(f"You won {2*amount} Coins")

    elif user_choice == 'paper':
        if comp_choice == 'rock':
            await ctx.send("You played Paper :newspaper: Your Opponent played Rock :rock:")
            await update_bank(ctx.author, 2*amount)
            await ctx.send(f"You won {2*amount} Coins")
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
            await update_bank(ctx.author, 2*amount)
            await ctx.send(f"You won {2*amount} Coins")
        elif comp_choice == 'scissors':
            await ctx.send("You played Rock :rock: Your Oppornent played Scissors :scissors:")
            await ctx.send("It's a draw. You get your bet back")


@client.command()
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


client.run("ODA1ODA4MDUzMzE1NDM2NTQ0.YBgROw.CvbQja1nEKoVFbYIYWHzfL42StY")
