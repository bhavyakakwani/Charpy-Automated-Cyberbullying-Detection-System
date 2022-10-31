from email import message
import discord
from discord.ext import commands
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

def get_warnings(ctx, member):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""select count(*) from warnings where author_id = %s and server_id = %s""", (member.id, ctx.guild.id))
    result = cursor.fetchall()
    db.close()
    return result[0][0]

async def take_action(ctx, client, member, warn_no):
    if warn_no % 11 == 2:
        cmd = client.get_command("tempmute")
        await cmd(ctx, member, (1, "h"))
    elif warn_no % 11 == 3:
        cmd = client.get_command("tempmute")
        await cmd(ctx, member, (3, "h"))
    elif warn_no % 11 == 4:
        cmd = client.get_command("tempmute")
        await cmd(ctx, member, (6, "h"))
    elif warn_no % 11 == 5:
        cmd = client.get_command("tempmute")
        await cmd(ctx, member, (24, "h"))
    elif warn_no % 11 == 6:
        cmd = client.get_command("mute")
        await cmd(ctx, member)
    elif warn_no % 11 == 8:
        cmd = client.get_command("kick")
        await cmd(ctx, member)
    elif warn_no % 11 == 10:
        cmd = client.get_command("ban")
        await cmd(ctx, member)

class Warnings(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(help = "Gives a warning to the specified user.", aliases = ["w"])
    @commands.has_permissions(administrator = True)
    async def warn(self, ctx, member: commands.MemberConverter, *, reason: str = None):
        if member.guild_permissions.manage_messages:
            return await ctx.send(f"{ctx.author.mention} you can't warn a moderator!")
        
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = PASSWORD,
            database = "charpy"
        )
        cursor = db.cursor()
        message = f"Warning by {ctx.message.author}"
        cursor.execute("insert into warnings (author_id, server_id, message, type) values (%s, %s, %s, %s)", (member.id, ctx.guild.id, message, reason))
        db.commit()
        db.close()

        warn_no = get_warnings(ctx, member)

        embed = discord.Embed(title = "Member Warned", color = discord.Color.dark_gold()) 
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Reason", value = reason, inline = False)
        embed.add_field(name = "Moderator", value = ctx.message.author.mention, inline = False)
        embed.add_field(name = "Warning No.", value = warn_no, inline = False)
        await ctx.send(embed = embed)
        
        result = check(ctx.guild)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

        await take_action(ctx, self.client, member, warn_no)

    @commands.command(help = "Lists the warnings for the specified user.")
    async def shw(self, ctx, member: commands.MemberConverter):
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = PASSWORD,
            database = "charpy"
        )
        cursor = db.cursor()
        cursor.execute("""select * from warnings where author_id = %s and server_id = %s""", (member.id, ctx.guild.id))
        results = cursor.fetchall()
        db.close()

        ids = []
        messages = []
        classification = []

        for i in results:
            ids.append(i[0])
            messages.append('"' + i[3] + '"')
            classification.append(i[4])

        str_ids = []
        for i in ids:
            str_ids.append(str(i))

        embed = discord.Embed(title = f"Warnings for {member}", color = discord.Color.dark_gold()) 
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        embed.set_thumbnail(url = url)
        if len(str_ids) == 0:
            str_ids.append("-")
            messages.append("-")
            classification.append("-")
        embed.add_field(name = "Warning ID", value = "\n".join(str_ids), inline = True)
        embed.add_field(name = "Message", value = "\n".join(messages), inline = True)
        embed.add_field(name = "Reason", value = "\n".join(classification), inline = True)
        await ctx.send(embed = embed)

    @commands.command(help = "Remove a specific warning from the user based on the id provided.")
    @commands.has_permissions(administrator = True)
    async def rmw(self, ctx, warn_id: int):
        db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
        )
        cursor = db.cursor()
        cursor.execute("""select * from warnings where warn_id = %s and server_id = %s""", (warn_id, ctx.guild.id))
        results = cursor.fetchall()
        cursor.execute("""delete from warnings where warn_id = %s and server_id = %s""", (warn_id, ctx.guild.id))
        db.commit()
        db.close()

        if len(results) != 0:
            member = ctx.guild.get_member(results[0][1])
            embed = discord.Embed(title = f"Warning Removed", color = discord.Color.dark_green()) 
            if member.avatar == None:
                url = member.default_avatar_url
            else:
                url = member.avatar_url
            embed.set_thumbnail(url = url)
            embed.add_field(name = "Warning ID", value = results[0][0], inline = False)
            embed.add_field(name = "Member", value = member.mention, inline = False)
            embed.add_field(name = "Message", value = results[0][3], inline = False)
            embed.add_field(name = "Classification", value = results[0][4], inline = False)
            await ctx.send(embed = embed)

            result = check(ctx.guild)
            if result and result[0][2] == 1:
                channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
                await channel.send(embed = embed)

def setup(client):
    client.add_cog(Warnings(client))