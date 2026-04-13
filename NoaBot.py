import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(
    command_prefix="[",
    intents=discord.Intents.all(),
    help_command=None
)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Cooldown: try again in {round(error.retry_after, 2)}s")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid arguments")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments")
    else:
        raise error


@bot.command(
    help="Greets the user",
    brief=""
)
@commands.cooldown(1, 5, commands.BucketType.user)
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author}!")

@bot.command(
    help="Repeats what you say",
    brief="<text>"
)
async def say(ctx, *, text):
    await ctx.send(text)

@bot.command(
    help="Adds two numbers",
    brief="<a> <b>"
)
async def add(ctx, a: int, b: int):
    await ctx.send(f"Sum: {a + b}")

@bot.command(
    help="Shows bot latency",
    brief=""
)
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(
    help="Choose randomly from options",
    brief="<option1> <option2> ..."
)
async def choose(ctx, *, options):
    choices = options.split()
    if len(choices) <= 1:
        await ctx.send("Give me at least 2 options bruv")
    else:
        await ctx.send(f"I'd choose: {random.choice(choices)}")

@bot.command(
    help="Shows bot information",
    brief=""
)
async def info(ctx):
    embed = discord.Embed(
        title="NoaBot Info",
        description="NoaBot is still under development. Stay tuned!",
        color=discord.Color.blue()
    )

    embed.add_field(name="Author", value="inakaishere", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)} ms", inline=True)
    embed.add_field(name="Commands", value="Use `[help` to see all commands", inline=False)

    await ctx.send(embed=embed)


#====================help command, PLS DON'T TOUCH====================================

@bot.command(
    help="Shows all commands or info about a specific command",
    brief="[command_name]"
)
async def help(ctx, command_name=None):

    #SHOW ALL COMMANDS
    if command_name is None:
        embed = discord.Embed(
            title="NoaBot Commands",
            description="Here are all available commands",
            color=discord.Color.green()
        )

        for command in bot.commands:
            if command.hidden:
                continue

            usage = f"[{command.name}"
            if command.brief:
                usage += f" {command.brief}"

            embed.add_field(
                name=f"`{usage}`",
                value=command.help or "No description",
                inline=False
            )

        await ctx.send(embed=embed)

    #   SHOW SPECIFIC COMMAND
    else:
        command = bot.get_command(command_name)

        if command is None:
            await ctx.send("Command not found")
            return

        usage = f"[{command.name}"
        if command.brief:
            usage += f" {command.brief}"

        embed = discord.Embed(
            title=f"Command: {command.name}",
            color=discord.Color.orange()
        )

        embed.add_field(
            name="Description",
            value=command.help or "No description",
            inline=False
        )

        embed.add_field(
            name="Usage",
            value=f"`{usage}`",
            inline=False
        )

        await ctx.send(embed=embed)


bot.run(token)