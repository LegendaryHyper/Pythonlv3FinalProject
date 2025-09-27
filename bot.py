import discord
from discord.ext import commands, tasks
from logic import DatabaseManager
from config import TOKEN, DATABASE
import os

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
async def add_item(ctx, item_name, item_cost):
    if ctx.author.id == 722496876351455293:
        manager.add_to_shop(item_name, item_cost)
        await ctx.send(f"Successfully added {item_name} to the shop for {item_cost}!")
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
            await ctx.send(f"{ctx.author.mention} has successfully bought a(n) {item_name}!")
        else:
            await ctx.send(f"{ctx.author.mention} has successfully bought {count_int} {item_name}s!")
    
bot.run(TOKEN)