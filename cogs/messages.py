import discord
from discord.ext import commands
from ml import predict
import mysql.connector
import os
import json
from database import check

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Password": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

PASSWORD = configData["Password"]    

def save_message(message, class_name):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("insert into message_classification values (%s, %s, %s)", (message.content, class_name, class_name))
    db.commit()
    db.close()

def add_warning(message, class_name):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("insert into warnings (author_id, server_id, message, type) values (%s, %s, %s, %s)", (message.author.id, message.guild.id, message.content, class_name))
    db.commit()
    db.close()

def get_warnings(message):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""select count(*) from warnings where author_id = %s and server_id = %s""", (message.author.id, message.guild.id))
    result = cursor.fetchall()
    db.close()
    return result[0][0]

async def take_action(client, message, warn_no):
    ctx = await client.get_context(message)
    if warn_no % 11 == 2:
        cmd = client.get_command("tempmute")
        await cmd(ctx, message.author, (1, "h"))
    elif warn_no % 11 == 3:
        cmd = client.get_command("tempmute")
        await cmd(ctx, message.author, (3, "h"))
    elif warn_no % 11 == 4:
        cmd = client.get_command("tempmute")
        await cmd(ctx, message.author, (6, "h"))
    elif warn_no % 11 == 5:
        cmd = client.get_command("tempmute")
        await cmd(ctx, message.author, (24, "h"))
    elif warn_no % 11 == 6:
        cmd = client.get_command("mute")
        await cmd(ctx, message.author)
    elif warn_no % 11 == 8:
        cmd = client.get_command("kick")
        await cmd(ctx, message.author)
    elif warn_no % 11 == 10:
        cmd = client.get_command("ban")
        await cmd(ctx, message.author)

class Messages(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(help = "Delete the specified number of messages from the channel.", aliases = ["c"])
    @commands.has_permissions(manage_messages = True)
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit = amount + 1)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        class_name = predict(message.content)
        save_message(message, class_name)

        if class_name != "not_cyberbullying":
            add_warning(message, class_name)

            warn_no = get_warnings(message)

            embed = discord.Embed(title = "Member Warned", color = discord.Color.dark_gold()) 
            if message.author.avatar == None:
                url = message.author.default_avatar_url
            else:
                url = message.author.avatar_url
            embed.set_thumbnail(url = url)
            embed.add_field(name = "Member", value = message.author.mention, inline = False)
            embed.add_field(name = "Message sent", value = message.content, inline = False)
            embed.add_field(name = "Classification", value = class_name, inline = False)
            embed.add_field(name = "Warning No.", value = warn_no, inline = False)
            await message.channel.send(embed = embed)

            ctx = await self.client.get_context(message)
            result = check(ctx.guild)
            if result[0][2] == 1:
                channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
                await channel.send(embed = embed)

            if message.author.guild_permissions.manage_messages:
                return
                
            await take_action(self.client, message, warn_no)

def setup(client):
    client.add_cog(Messages(client))