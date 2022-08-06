import discord
from discord.ext import commands

class Roles(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.command(help = "Give a specified role to the mentioned user.", aliases = ["a"])
    @commands.has_permissions(manage_roles = True)
    async def add(self, ctx, member : commands.MemberConverter, *, role):
        requiredRole = discord.utils.get(ctx.guild.roles, name = role)
        if not requiredRole:
            await ctx.send(f"`{role}` role doesn't exist!")
            return
        await member.add_roles(requiredRole)
        embed = discord.Embed(title = "Added Role", color = discord.Color.random())
        
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Role", value = requiredRole.mention, inline = False)
        await ctx.send(embed = embed)
    
    @commands.command(help = "Remove a specified role from the mentioned user.", aliases = ["r"])
    @commands.has_permissions(manage_roles = True)
    async def remove(self, ctx, member : commands.MemberConverter, *, role):
        requiredRole = discord.utils.get(ctx.guild.roles, name = role)
        if not requiredRole:
            await ctx.send(f"`{role}` role doesn't exist!")
            return
        await member.remove_roles(requiredRole)
        embed = discord.Embed(title = "Removed Role", color = discord.Color.random())
        
        if member.avatar == None:
            url = member.default_avatar_url
        else:
            url = member.avatar_url
        
        embed.set_thumbnail(url = url)
        embed.add_field(name = "Member", value = member.mention, inline = False)
        embed.add_field(name = "Role", value = requiredRole.mention, inline = False)
        await ctx.send(embed = embed)

def setup(client):
    client.add_cog(Roles(client))