import subprocess
import asyncio
import discord
from discord.ext import commands

from lib.initConfig import importConfig

def runBot() -> None:
    subprocess(".venv\Scripts\python.exe .\\bot.py")

def updateBot() -> None:
    result = subprocess.run("git pull", capture_output=True, shell=True, text=True)
    if result.returncode == 0:
        output = result.stdout
        if output == "Already up to date.":
            return False
        else:
            return True

def main() -> None:
    CONFIG = importConfig()
    TOKEN = CONFIG["DISCORD"]["BOT_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=">", intents=intents)
    botTask = asyncio.create_task(runBot())
    bot.run(TOKEN)


if __name__ == "__main__":
    main()