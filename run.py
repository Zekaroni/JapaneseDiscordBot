import subprocess
import asyncio
import discord
from discord.ext import commands

from lib.initConfig import importConfig

def main() -> None:
    CONFIG = importConfig()
    TOKEN = CONFIG["DISCORD"]["BOT_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=">", intents=intents)
    bot.run(TOKEN)


if __name__ == "__main__":
    main()
