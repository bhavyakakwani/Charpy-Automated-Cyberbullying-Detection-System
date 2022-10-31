import discord
from discord.ext import commands
import mysql.connector
import os
import json
from database import create_database, check, tempcheck

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Password": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

PASSWORD = configData["Password"]

async def create_channel(ctx):
    everyone = ctx.guild.default_role
    overwrites = {everyone: discord.PermissionOverwrite.from_pair(deny=discord.Permissions.all(), allow=[])}
    channel = await ctx.guild.create_text_channel("charpy logs", overwrites = overwrites)
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""insert into logs values (%s, %s, %s)""", (ctx.guild.id, channel.id, 1))
    db.commit()
    db.close()
    await channel.send(f"{ctx.author.mention} Logging enabled here.")

class Logs(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        create_database()
        await tempcheck(self.client)
        print("Bot is ready!")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        ctx = await self.client.get_context(message)
        result = check(ctx.guild)
        if result and result[0][2] == 1:
            embed = discord.Embed(title = "Message Deleted", color = discord.Color.random()) 
            if message.author.avatar == None:
                    url = message.author.default_avatar_url
            else:
                url = message.author.avatar_url
            embed.set_thumbnail(url = url)
            embed.add_field(name = "Member", value = message.author.mention, inline = False)
            embed.add_field(name = "Message content", value = message.content, inline = False)
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        ctx = await self.client.get_context(messages[0])
        result = check(ctx.guild)
        if result and result[0][2] == 1:
            author = []
            content = []
            for message in messages:
                author.append(message.author.mention)
                content.append('"' + message.content + '"')

            embed = discord.Embed(color = discord.Color.random())
            if message.author.avatar == None:
                url = message.author.default_avatar_url
            else:
                url = message.author.avatar_url
            embed.set_thumbnail(url = url) 
            embed.description = f"**Bulk deletion in {message.channel.mention} by {message.author.mention} \n\nRecovered Messages: **"
            embed.add_field(name = "Author", value = "\n".join(author), inline = True)
            embed.add_field(name = "Message", value = "\n".join(content), inline = True)
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        ctx = await self.client.get_context(before)
        result = check(ctx.guild)
        if result and result[0][2] == 1:
            embed = discord.Embed(color = discord.Color.random()) 
            if before.author.avatar == None:
                url = before.author.default_avatar_url
            else:
                url = before.author.avatar_url
            embed.set_thumbnail(url = url)
            b = before.content or "N/A"
            a = after.content or "N/A"
            embed.description = f"**Message edited in {before.channel.mention} by {before.author.mention}**"
            embed.add_field(name = "Before", value = b, inline = False)
            embed.add_field(name = "After", value = a, inline = False)
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        result = check(member.guild)
        if result and result[0][2] == 1:
            embed = discord.Embed(title = "Member Joined", color = discord.Color.green()) 
            if member.avatar == None:
                url = member.default_avatar_url
            else:
                url = member.avatar_url
            embed.set_thumbnail(url = url)
            embed.description = f"{member.mention} has joined the server."
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        result = check(member.guild)
        if result and result[0][2] == 1:
            embed = discord.Embed(title = "Member Left", color = discord.Color.red()) 
            if member.avatar == None:
                url = member.default_avatar_url
            else:
                url = member.avatar_url
            embed.set_thumbnail(url = url)
            embed.description = f"{member.mention} has left the server."
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)
    
    @commands.command(help = "Enables logging.")
    @commands.has_permissions(administrator = True)
    async def logstart(self, ctx):
        result = check(ctx.guild)

        if len(result) == 0:
            await create_channel(ctx)
        
        else:
            flag = 0
            for channels in ctx.guild.text_channels:
                if result[0][1] == channels.id:
                    if result[0][2] == 0:
                        db = mysql.connector.connect(
                            host = "localhost",
                            user = "root",
                            password = PASSWORD,
                            database = "charpy"
                        )
                        cursor = db.cursor()
                        cursor.execute("""update logs set logging = %s where server_id = %s""", (1, ctx.guild.id))
                        db.commit()
                        db.close()
                        await channels.send(f"{ctx.author.mention} Logging is re-enabled here.")
                    else:
                        await channels.send(f"{ctx.author.mention} Logging is already enabled here.")
                    return

            db = mysql.connector.connect(
                host = "localhost",
                user = "root",
                password = PASSWORD,
                database = "charpy"
            )
            cursor = db.cursor()
            cursor.execute("""delete from logs where server_id = (%s)""", (ctx.guild.id,))
            db.commit()
            db.close()

            await create_channel(ctx)

    @commands.command(help = "Disables logging.")
    @commands.has_permissions(administrator = True)
    async def logstop(self, ctx):
        result = check(ctx.guild)

        if len(result) == 0:
            await ctx.send(f"{ctx.author.mention} logging is already disabled.")
        else:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            if result[0][2] == 0:
                await channel.send(f"{ctx.author.mention} logging is already disabled.")
            else:
                db = mysql.connector.connect(
                    host = "localhost",
                    user = "root",
                    password = PASSWORD,
                    database = "charpy"
                )
                cursor = db.cursor()
                cursor.execute("""update logs set logging = %s where server_id = %s""", (0, ctx.guild.id))
                db.commit()
                db.close()
                await channel.send(f"{ctx.author.mention} Logging disabled here.")

def setup(client):
    client.add_cog(Logs(client))