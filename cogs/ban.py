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

class Ban(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(help = "Ban a member from the server.", aliases = ["b"])
    @commands.has_permissions(ban_members = True)
    async def ban(self, ctx, member : commands.MemberConverter, *, reason = None):
        if member.guild_permissions.manage_messages:
            return await ctx.send(f"{ctx.author.mention} you can't ban a moderator!")

        await member.ban(reason = reason)
        embed = discord.Embed(title = "Member Banned", color = discord.Color.dark_red())
        
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
    
    @commands.command(help = "Unban a member from the server.", aliases = ["ub"])
    @commands.has_permissions(ban_members = True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")
        for ban_entry in banned_users:
            user = ban_entry.user
            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                embed = discord.Embed(title = "Member Unbanned", color = discord.Color.green())
                if user.avatar == None:
                    url = user.default_avatar_url
                else:
                    url = user.avatar_url
                
                embed.set_thumbnail(url = url)
                embed.add_field(name = "Member", value = user.mention, inline = False)
                embed.add_field(name = "Moderator", value = ctx.message.author.mention, inline = False)
                await ctx.send(embed = embed)

                result = check(ctx.guild)
                if result and result[0][2] == 1:
                    channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
                    await channel.send(embed = embed)

                return
    
    @commands.command(help = "Temporarily ban a member from the server.", aliases = ["tb"])
    @commands.has_permissions(ban_members = True)
    async def tempban(self, ctx, member : commands.MemberConverter, duration: DurationConverter, *, reason = None):
        if member.guild_permissions.manage_messages:
            return await ctx.send(f"{ctx.author.mention} you can't ban a moderator!")
        
        multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        amount, unit = duration
        await ctx.guild.ban(member, reason = reason)
        
        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = PASSWORD,
            database = "charpy"
        )
        cursor = db.cursor()
        start_time = datetime.datetime.now()
        start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("insert into tempban values (%s, %s, %s, %s)", (member.id, ctx.guild.id, start_time, amount * multiplier[unit]))
        db.commit()
        db.close()
        
        embed = discord.Embed(title = "Member Banned", color = discord.Color.dark_red())

        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
            
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Duration", value = f"{amount}{unit}", inline = False)
        embed.add_field(name = "Reason", value = reason, inline = False)
        embed.add_field(name = "Moderator", value = ctx.message.author.mention, inline = False)
        await ctx.send(embed = embed)

        result = check(ctx.guild)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

        await asyncio.sleep(amount * multiplier[unit])

        db = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = PASSWORD,
            database = "charpy"
        )
        cursor = db.cursor()
        cursor.execute("delete from tempban where user_id = %s and server_id = %s", (member.id, ctx.guild.id))
        db.commit()
        db.close()

        await ctx.guild.unban(member)
        embed = discord.Embed(title = "Member Unbanned", color = discord.Color.green())
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Moderator", value = "<@931933313847939072>", inline = False)
        await ctx.send(embed = embed)
        if result and result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

def setup(client):
    client.add_cog(Ban(client))