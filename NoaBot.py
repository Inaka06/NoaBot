import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="[", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author}!")

@bot.command()
async def say(ctx, *, text):
    await ctx.send(text)

@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(f'Sum of those numbers are: {a + b}')

@bot.command()
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f'Pong! {round(latency * 1000)}ms')

bot.run(token)