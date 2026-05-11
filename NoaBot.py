import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import random
import json
import asyncio
import yt_dlp

def load_data():
    with open("storage.json", "r") as f:
        return json.load(f)

def save_data(data):
    with open("storage.json", "w") as f:
        json.dump(data, f, indent=4)

load_dotenv()
token = os.getenv("DISCORD_TOKEN")


#COMMANDS


bot = commands.Bot(
    command_prefix="[",
    intents=discord.Intents.all(),
    help_command=None
)

@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    await bot.change_presence(
        activity=discord.Game(name="use [info")
    )

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
    help="Joins author's voice channel(if any)",
    brief=""
)
async def join(ctx):
    if ctx.author.voice:
        await ctx.message.author.voice.channel.connect()
    else:
        await ctx.send("Uh.. where are you?")

@bot.command(
    help="Leave the voice channel",
    brief=""
)
async def leave(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send('Bye~')
    else:
        await ctx.send("I'm not in a voice channel, use the join command to make me join")

@bot.command(
    help="Adding things to a list",
    brief="<text>"
)
async def list(ctx, *, arg):
    data = load_data()
    data["items"].append(arg)
    save_data(data)

    await ctx.send(data["items"])

@bot.command(
    help="Remove an element from the list",
    brief="<int>"
)
async def pop(ctx, index: int):
    data = load_data()

    if index < 0 or index >= len(data["items"]):
        await ctx.send("Invalid index")
        return

    removed = data["items"].pop(index)
    save_data(data)

    await ctx.send(f"Removed: {removed}\n{data['items']}")

@bot.command(
    help="pls don't.",
    brief=""
)
async def rickroll(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel

        if not ctx.voice_client:
            await channel.connect()

        voice = ctx.voice_client

        def after_playing(error):
            if error:
                print(error)

            fut = asyncio.run_coroutine_threadsafe(
                voice.disconnect(),
                bot.loop
            )
            try:
                fut.result()
            except:
                pass

        source = discord.FFmpegPCMAudio("rickroll.mp3")
        voice.play(source, after=after_playing)

        await ctx.send("You did it yourself, not me")

    else:
        await ctx.send("Uh.. where are you?")



#=========Music player=========
def play_next(ctx):
    data = load_data()

    if len(data["queue"]) == 0:
        if ctx.voice_client:
            asyncio.run_coroutine_threadsafe(
                ctx.voice_client.disconnect(),
                bot.loop
            )
        return

    song = data["queue"][0]
    url = song["url"]
    title = song["title"]

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    source = discord.FFmpegPCMAudio(
        audio_url,
        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        options="-vn"
    )

    def after_playing(error):
        if error:
            print(error)
        fresh = load_data()
        fresh["queue"].pop(0)
        save_data(fresh)
        play_next(ctx)

    ctx.voice_client.play(source, after=after_playing)

    asyncio.run_coroutine_threadsafe(
        ctx.send(f"🎶 Now playing: **{title}**"),
        bot.loop
    )

@bot.command(
    help="Plays music"
)
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("Join a VC first 😭")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    guild_id = str(ctx.guild.id)
    data = load_data()

    if guild_id not in data["queues"]:
        data["queues"][guild_id] = []

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        title = info.get("title", "Unknown")

    data["queues"][guild_id].append({
        "url": url,
        "title": title
    })
    save_data(data)

    await ctx.send(f"Added to queue 🎶\n**{title}**")

    if not ctx.voice_client.is_playing():
        play_next(ctx)

# SHOW QUEUE
@bot.command()
async def queue(ctx):
    guild_id = str(ctx.guild.id)
    data = load_data()
    guild_queue = data.get("queues", {}).get(guild_id, [])

    if not guild_queue:
        await ctx.send("Queue is empty :/")
        return

    msg = ""
    for i, song in enumerate(guild_queue, start=1):
        msg += f"{i}. {song['title']}\n"

    await ctx.send(msg)

# REMOVE FROM QUEUE
@bot.command()
async def remove(ctx, index: int):
    guild_id = str(ctx.guild.id)
    data = load_data()
    guild_queue = data.get("queues", {}).get(guild_id, [])

    if index < 1 or index > len(guild_queue):
        await ctx.send("Invalid index")
        return


    if index == 1:
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(f"Skipped and removed: **{guild_queue[0]['title']}**")
        return

    removed = guild_queue.pop(index - 1)
    data["queues"][guild_id] = guild_queue
    save_data(data)

    await ctx.send(f"Removed: **{removed['title']}**")

# SKIP SONG
@bot.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped ⏭️")
    else:
        await ctx.send("Nothing is playing :/")

@bot.command()
async def clear(ctx):
    guild_id = str(ctx.guild.id)
    data = load_data()
    if "queues" in data and guild_id in data["queues"]:
        data["queues"][guild_id] = []
    save_data(data)
    await ctx.send("Queue cleared")


#====================help command, PLS DON'T TOUCH====================================

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