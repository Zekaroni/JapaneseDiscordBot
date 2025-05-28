import discord
from discord.ext import commands, tasks
from time import time
from datetime import timedelta
from os import path
import datetime
import asyncio
import subprocess

from lib.myLogging import log
from lib.initConfig import importConfig
from lib.translation import CustomTranslator
from lib.userdata import UserDataHandler
from lib.customEmbeds import *
from lib.botdata import BotData
from lib.japanesedata import JapaneseData
from lib.botutil import updateBot

BOOT_TIME = time()
translator = CustomTranslator()
userdataHandler = UserDataHandler()
botData = BotData()
japaneseData = JapaneseData()

# Config reading
CONFIG = importConfig()
TOKEN = CONFIG["DISCORD"]["BOT_TOKEN"]
GUILD_ID = CONFIG["DISCORD"]["GUILD_ID"]

# Disdcord bot initialization
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=">", intents=intents)


@bot.event
async def on_ready():
    try:
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        log(f"~~~ Logged in as {bot.user}. ~~~")
        try:
            asyncio.create_task(initializeTimedEvents());
            log(f"Created hook for looping tasks.")
        except Exception as e:
            log(f"Failed to create hook for looping tasks.")
    except Exception as e:
        log(f"Failed to sync commands: {e}")

@bot.tree.command(name="translate", description="Auto-detects and translates sentences.", guild=discord.Object(id=GUILD_ID))
async def botTranslate(interaction: discord.Interaction, passage: str):
    await interaction.response.send_message("Processing your request...", ephemeral=True, delete_after=3)

    result = translator.translate(passage)
    if result == None:
        await interaction.channel.send(f"Prompt: {passage}\nNeither English or Japanese deteced.")
        return
    
    nickname = interaction.user.nick
    
    languageEmbed = generateTranslationEmbed(result, passage, nickname, interaction)

    userdataHandler.incrementTranslationCount(interaction.user)

    log(
        (nickname if nickname else interaction.user.name) + " used /translate : " + passage + "  -->  " + result[0]
    )

    await interaction.channel.send(embed=languageEmbed)

@bot.command(name="debug")
async def debug(ctx: commands.context):
    log(f"User {ctx.author.name} used debug.")
    if userdataHandler.getUser(ctx.author)["admin"]:
        latency = round(bot.latency * 1000)
        uptime = timedelta(seconds=int(time() - BOOT_TIME))
        debugEmbed = generateDebugEmbed(latency, uptime)
        log(f"{ctx.author.name} debugged. Latency:{latency}; Uptime: {uptime}")
        await ctx.author.send(embed=debugEmbed)
        try:
            await ctx.message.delete()
        except Exception:
            pass
    else:
        await ctx.channel.send("You do not have permission to debug.", delete_after=5)
        try:
            await ctx.message.delete()
        except Exception:
            pass
        log(f"User {ctx.author.name} does not have admin permissions.")

@bot.command(name = "getData")
async def getData(ctx: commands.Context):
    log(f"User {ctx.author.name} used getData.")
    if userdataHandler.getUser(ctx.author)["admin"]:
        if path.exists("./data/userdata.json"):
            userdataFile = discord.File("./data/userdata.json", filename=f"user{int(time())}.json")
            await ctx.author.send(file = userdataFile)
            log(f"User data sent to {ctx.author.name}.")
        if path.exists("./data/botdata.json"):
            botdataFile = discord.File("./data/botdata.json", filename=f"bot{int(time())}.json")
            await ctx.author.send(file = botdataFile)
            log(f"Bot data sent to {ctx.author.name}.")
    else:
        await ctx.send("You do not have permission access user data.", delete_after = 5)
    await ctx.message.delete()

@bot.command(name = "getLog")
async def getLog(ctx: commands.Context):
    log(f"User {ctx.author.name} used getLog.")
    if userdataHandler.getUser(ctx.author)["admin"]:
        if path.exists("./log.txt"):
            logFile = discord.File("./log.txt", filename=f"{int(time())}.txt")
            await ctx.author.send(file = logFile)
            log(f"Log data sent to {ctx.author.name}.")
    else:
        log(f"User {ctx.author.name} does not have permission.")
        await ctx.send("You do not have permission access the log.", delete_after = 5)
    await ctx.message.delete()

@bot.command(name = "update")
async def update(ctx: commands.Context):
    log(f"User {ctx.author.name} used update.")
    if userdataHandler.getUser(ctx.author)["admin"]:
        if updateBot():
            log(f"Bot has been updated.")
            log(f"Restarting the bot.")
            await ctx.channel.send("Restarting the bot.")
            await ctx.bot.close()
            subprocess.Popen([".venv\Scripts\python.exe","bot.py"])
            exit(0)
    else:
        log(f"User {ctx.author.name} does not have permission.")
        await ctx.send("You do not have permission update the bot.", delete_after = 5)
    await ctx.message.delete()


# @bot.tree.command(name="reload", description="Reloads various parts of the bot.", guild=discord.Object(id=GUILD_ID))
# async def reload(interaction: discord.Interaction):
#     # TODO: Add stuff that should be reloaded here
#     if not userdataHandler.getUser(interaction.author)["admin"]:
#         await interaction.response.send_message("You do not have permission to debug.", delete_after=5)
#     else:
#         pass


# Looping Tasks
@tasks.loop(seconds=86400)
async def japaneseDailies():
    try:
        grammarChannel = bot.get_channel(botData.dailyGrammarChannelID)
        grammarEmbed = generateDailyGrammarEmbed(botData.dailyGrammarIndex, japaneseData.grammar[botData.dailyGrammarIndex])
        botData.incrementGrammarIndex()
        await grammarChannel.send(embed=grammarEmbed)
        log(f"Grammar daily number {botData.dailyGrammarIndex} was sent successfully.")
    except Exception as e:
        log(f"CRITICAL ERROR IN GRAMMAR DAILY: {e}")
    try:
        wordChannel = bot.get_channel(botData.dailyWordChannelID)
        wordEmbed = generateDailyWordEmbed(botData.dailyWordIndex, japaneseData.words[botData.dailyWordIndex])
        botData.incrementWordIndex()
        await wordChannel.send(embed=wordEmbed)
        log(f"Word daily number {botData.dailyWordIndex} was sent successfully.")
    except Exception as e:
        log(f"CRITICAL ERROR IN WORD DAILY: {e}")


async def initializeTimedEvents():
    now = datetime.datetime.now()
    targetTime = now.replace(hour=botData.taskHour, minute=0, second=0, microsecond=0)
    if targetTime < now:
        targetTime += datetime.timedelta(days=1)
    # delay = (targetTime - now).total_seconds()
    delay = 0
    log(f"Dailies initalized and will start in {delay} seconds.")
    await asyncio.sleep(delay)
    japaneseDailies.start()


bot.run(TOKEN)