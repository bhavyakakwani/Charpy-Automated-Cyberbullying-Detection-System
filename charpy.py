import discord
from discord.ext import commands
import os
import json
from database import create_database

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = ".", intents = intents)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Password": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

TOKEN = configData["Token"]
create_database()

client.run(TOKEN)   