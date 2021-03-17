import discord
import os

from discord.ext import commands
from utilities import settings

settings = settings.config("settings.json")

intents = discord.Intents.none()
permissions = ["guilds", "guild_messages", "guild_reactions", "guild_typing", "members", "voice_states",]
for perm in permissions:
    setattr(intents, perm, True)

bot = commands.Bot(command_prefix='.', intents=intents)
    
for file in os.listdir(settings.COG_PATH):
    if file.endswith('.py'):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        
bot.run(settings.DISCORD_TOKEN)