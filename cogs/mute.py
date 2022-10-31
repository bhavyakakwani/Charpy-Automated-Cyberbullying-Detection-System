from multiprocessing import get_context
import discord
from discord.ext import commands
import asyncio
from duration_converter import DurationConverter
from database import check
import mysql.connector
import datetime
import os
import json

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Password": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

PASSWORD = configData["Password"]  

class Mute(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(help = "Mute a member from the server.", aliases = ["m"])
    @commands.has_permissions(manage_messages = True)
    async def mute(self, ctx, member : commands.MemberConverter, *, reason = None):
        if member.guild_permissions.manage_messages:
            return await ctx.send(f"{ctx.author.mention} you can't mute a moderator!")
        
        guild = ctx.guild
        mutedRole = discord.utils.get(guild.roles, name = "Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name = "Muted")
            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak = False, send_messages = False, read_message_history = True, read_messages = False)
        
        embed = discord.Embed(title = "Member Muted", color = discord.Color.gold())
        
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        
        moderator = ctx.message.author.mention
        if member.mention == moderator:
            moderator = "<@931933313847939072>"
            reason = "Cyberbullying"

        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Reason", value = reason, inline = False)
        embed.add_field(name = "Moderator", value = moderator, inline = False)
        await ctx.send(embed = embed)

        result = check(ctx.guild)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

        await member.send(f"You are now muted in the server: {guild.name} \nReason: {reason}")
        await member.add_roles(mutedRole, reason = reason)
    
    @commands.command(help = "Unmute a member from the server.", aliases = ["um"])
    @commands.has_permissions(manage_messages = True)
    async def unmute(self, ctx, member : commands.MemberConverter):
        mutedRole = discord.utils.get(ctx.guild.roles, name = "Muted")
        await member.remove_roles(mutedRole)
        embed = discord.Embed(title = "Member Unmuted", color = discord.Color.green())
        
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Moderator", value = ctx.message.author.mention, inline = False)
        await ctx.send(embed = embed)

        result = check(ctx.guild)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

        await member.send(f"You are now unmuted in the server: {ctx.guild.name}")

    @commands.command(help = "Temporarily mute a member from the server.", aliases = ["tm"])
    @commands.has_permissions(manage_messages = True)
    async def tempmute(self, ctx, member : commands.MemberConverter, duration: DurationConverter, *, reason = None):
        if member.guild_permissions.manage_messages:
            return await ctx.send(f"{ctx.author.mention} you can't mute a moderator!")
        
        guild = ctx.guild
        multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        amount, unit = duration
        mutedRole = discord.utils.get(guild.roles, name = "Muted")

        if not mutedRole:
            mutedRole = await guild.create_role(name = "Muted")
            for channel in guild.channels:
                await channel.set_permissions(mutedRole, speak = False, send_messages = False, read_message_history = True, read_messages = False)
        
        embed = discord.Embed(title = "Member Muted", color = discord.Color.gold())
        
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        
        moderator = ctx.message.author.mention
        if member.mention == moderator:
            moderator = "<@931933313847939072>"
            reason = "Cyberbullying"

        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Duration", value = f"{amount}{unit}", inline = False)
        embed.add_field(name = "Reason", value = reason, inline = False)
        embed.add_field(name = "Moderator", value = moderator, inline = False)
        await ctx.send(embed = embed)

        result = check(ctx.guild)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

        await member.send(f"You are now muted in the server: {guild.name} \nReason: {reason}")
        await member.add_roles(mutedRole, reason = reason)

        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = PASSWORD,
            database = "charpy"
        )
        cursor = db.cursor()
        start_time = datetime.datetime.now()
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("insert into tempmute values (%s, %s, %s, %s)", (member.id, ctx.guild.id, start_time, amount * multiplier[unit]))
        db.commit()
        db.close()

        await asyncio.sleep(amount * multiplier[unit])

        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = PASSWORD,
            database = "charpy"
        )
        cursor = db.cursor()
        cursor.execute("delete from tempmute where user_id = %s and server_id = %s", (member.id, ctx.guild.id))
        db.commit()
        db.close()

        await member.remove_roles(mutedRole)
        embed = discord.Embed(title = "Member Unmuted", color = discord.Color.green())
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Moderator", value = "<@931933313847939072>", inline = False)
        await ctx.send(embed = embed)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

def setup(client):
    client.add_cog(Mute(client))