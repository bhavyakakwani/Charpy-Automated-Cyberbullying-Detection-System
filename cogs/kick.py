import discord
from discord.ext import commands
from database import check

class Kick(commands.Cog):

    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Sorry {ctx.message.author.mention}! You can't use that.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.message.author.mention} please pass in all the required arguments. Use ``.help <name of command>`` for more info.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{ctx.message.author.mention} please enter a valid command. Use ``.help`` to see all the valid commands.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{ctx.message.author.mention} please enter a valid member.")

    @commands.command(help = "Kick a member from the server.", aliases = ["k"])
    @commands.has_permissions(kick_members = True)
    async def kick(self, ctx, member : commands.MemberConverter, *, reason = None):
        if member.guild_permissions.manage_messages:
            return await ctx.send(f"{ctx.author.mention} you can't kick a moderator!")
        
        await member.kick(reason = reason)

        embed = discord.Embed(title = "Member Kicked", color = discord.Color.red())
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
        if result[0][2] == 1:
            channel = discord.utils.get(self.client.get_all_channels(), id = result[0][1])
            await channel.send(embed = embed)

def setup(client):
    client.add_cog(Kick(client))