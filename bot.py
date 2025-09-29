import discord
from discord.ext import commands, tasks
from logic import DatabaseManager
from config import TOKEN, DATABASE
import os
import random
import asyncio


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

manager = DatabaseManager(DATABASE)
manager.create_tables()


@bot.event
async def on_ready():
    print(f'{bot.user} olarak giriş yapıldı!')
@bot.command()
async def add(ctx):
    user_id = ctx.author.id
    if user_id in manager.get_users():
        await ctx.send("You are already added!")
    else:
        manager.add_user(user_id, ctx.author.name)
        await ctx.send("You have been added!")
@bot.command()
async def work(ctx):
    user_id = ctx.author.id
    income = 100
    manager.set_balance(user_id, income)
    await ctx.send(f"Woah, {ctx.author.mention}! For your efforts, you just got {income} bucks!")
@bot.command()
async def add_item(ctx, item_name, item_cost, sold, use):
    if ctx.author.id == 722496876351455293:
        manager.add_item(item_name, item_cost, int(sold), int(use))
        await ctx.send(f"Successfully added {item_name} to the shop for {item_cost}\n Item for sale: {bool(int(sold))}\nUsage Index: {int(use)}!")
    else:
        await ctx.send("Sorry, no perms!")
@bot.command()
async def add_use(ctx, use_name):
    if ctx.author.id == 722496876351455293:
        manager.add_use(use_name)
        await ctx.send(f"Successfully added {use_name} as a way of usage!")
    else:
        await ctx.send("Sorry, no perms!")
@bot.command()
async def add_loot_pool(ctx, pool_name, loots):
    if ctx.author.id == 722496876351455293:
        loot_list = loots.split(" ")
        manager.add_loot_pool(pool_name, loot_list)
        await ctx.send(f"Successfully added {loot_list} as loot '{pool_name}!'")
    else:
        await ctx.send("Sorry, no perms!")
@bot.command()
async def shop(ctx):
    output = "Item Name - Cost\n"
    shop_output = manager.get_shop()
    if shop_output:
        for i in shop_output: output += f"{i[0]} - {i[1]} Bucks\n"
    else:
        output += "Nothing in the shop"
    embed = discord.Embed(title = "Shop", description = output, color = 0xffff00)
    await ctx.send(embed = embed)
@bot.command()
async def uses(ctx):
    output = "Use ID - Use Name\n"
    uses_output = manager.get_uses()
    if uses_output:
        for i in uses_output: output += f"{i[0]} - {i[1]}\n"
    else:
        output += "No uses"
    embed = discord.Embed(title = "All Item Uses", description = output, color = 0x009fff)
    await ctx.send(embed = embed)
@bot.command()
async def buy(ctx, item_name, count):
    user_id = ctx.author.id
    delta = manager.get_cost(item_name)
    count_int = int(count)
    user_balance = manager.get_balance(user_id)
    if user_balance < delta*count_int:
        await ctx.send(f"Sorry, {ctx.author.mention}, insufficient balance!")
    else:
        manager.set_balance(user_id, -delta*count_int)
        manager.update_inv(user_id, item_name, count_int)
        if count_int == 1:
            await ctx.send(f"{ctx.author.mention} has successfully bought a(n) {item_name} for {delta} bucks!")
        else:
            await ctx.send(f"{ctx.author.mention} has successfully bought {count_int} {item_name}s for {delta*count_int} bucks!")
@bot.command()
async def use(ctx, item_name):
    user_id = ctx.author.id
    count = manager.check_inv(user_id, item_name)
    if count > 0:
        usage = manager.get_use(item_name)
        if usage == 0:
            await ctx.send("This item is not usable.")
        elif usage == 1:
            msg = await ctx.send(manager.get_random_loot("LootT1"))
            for i in range (5):
                await asyncio.sleep(0.5)
                await msg.edit(content=manager.get_random_loot("LootT1"))
            final_outcome = manager.get_random_loot("LootT1")
            if final_outcome.isdecimal():
                await msg.edit(content=f"{ctx.author.mention}, you just dropped {final_outcome} bucks!")
                manager.set_balance(user_id, int(final_outcome))
            else:
                await msg.edit(content=f"{ctx.author.mention}, you just dropped one {final_outcome}!")
                manager.update_inv(user_id, final_outcome, 1)
        elif usage == 11:
            gain = random.randint(1000, 3000)
            manager.set_balance(user_id, gain)
            await ctx.send(f"You just got {gain} bucks from the BoxOBucks!")
        manager.update_inv(user_id, item_name, -1)
    else:
        await ctx.send(f"Uh oh, {ctx.author.mention}, you don't have the item!")
@bot.command()
async def get_inv(ctx):
    user_id = ctx.author.id
    output = "Item Name - Count/Amount\n"
    user_inv = manager.get_inv(user_id)
    if user_inv:
        output += user_inv
    else:
        output += "Nothing in the inventory"
    embed = discord.Embed(title = f"Inventory of {ctx.author}", description = output, color = 0xffff00)
    await ctx.send(embed = embed)
bot.run(TOKEN)