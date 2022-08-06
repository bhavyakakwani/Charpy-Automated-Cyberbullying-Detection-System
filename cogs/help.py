import discord
from discord.ext import commands
import itertools

class MinimalHelpCommand(commands.MinimalHelpCommand):
    
    async def send_pages(self):
        ctx = self.context
        destination = self.get_destination()
        embed = discord.Embed(color = 0x000000, description = "")
        file = discord.File("./charpy.png", filename = "image.png")
        embed.set_author(name = f"{ctx.bot.user.name} Help", icon_url = "attachment://image.png")
        embed.set_footer(text = self.get_footer_note())
        for page in self.paginator.pages:
            embed.description += page
        await destination.send(file = file, embed = embed)
    
    def get_opening_note(self):
        command_name = self.invoked_with
        return f"You can get more information on a command using `{self.clean_prefix}{command_name} <name of command>`"
    
    async def send_bot_help(self, mapping):
        ctx = self.context
        bot = ctx.bot
        note = self.get_opening_note()
        if note:
            self.paginator.add_line(note, empty=True)

        no_category = '\u200b{0.no_category}'.format(self)
        
        def get_category(command, *, no_category = no_category):
            cog = command.cog
            return cog.qualified_name if cog is not None else no_category

        filtered = await self.filter_commands(bot.commands, sort = True, key = get_category)
        to_iterate = itertools.groupby(filtered, key = get_category)

        for category, commands in to_iterate:
            commands = sorted(commands, key = lambda c: c.name) if self.sort_commands else list(commands)
            self.add_bot_commands_formatting(commands, category)

        note = self.get_ending_note()
        if note:
            self.paginator.add_line()
            self.paginator.add_line(note)

        await self.send_pages()
    
    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = ' '.join(f"`{c.name}`"for c in commands)
            self.paginator.add_line('**%s**:' % heading)
            self.paginator.add_line(joined)

    async def send_command_help(self, command):
            ctx = self.context

            embed = discord.Embed(color = 0x000000, description = "")
            file = discord.File("./charpy.png", filename = "image.png")
            embed.set_author(name = f"Command help for {command.name}", icon_url = "attachment://image.png")
            embed.set_footer(text = f"Thanks for using {ctx.bot.user.name}! 😄")
            embed.description = command.help or "No description provided"
            embed.description += "\n\n**Don't include <> or [] on the command itself.**"
            if (command.hidden == True or command.enabled == False) and await ctx.bot.is_owner(ctx.author) == False:
                return await ctx.send(f'No command called "{command.qualified_name}" found.')
            if command.signature:
                embed.add_field(name = ":pencil: Usage", value=f"`{self.clean_prefix}{command.qualified_name} {command.signature} `\n",inline = False)
            else:
                embed.add_field(name = ":pencil: Usage", value=f"`{self.clean_prefix}{command.qualified_name}`\n", inline = False)

            if len(command.aliases) > 0:
                formatted = [f"`{self.clean_prefix}{x}`" for x in command.aliases]
                embed.add_field(name = ":pushpin: Aliases", value=", ".join(formatted), inline = False)
            await ctx.send(file = file, embed = embed)

    def get_footer_note(self):
        ctx = self.context
        return f"Thanks for using {ctx.bot.user.name}! 😄"

    async def send_cog_help(self, cog):
        pass

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.client._original_help_command = client.help_command
        client.help_command = MinimalHelpCommand()
        client.help_command.cog = self

    def cog_unload(self):
        self.client.help_command = self.client._original_help_command

def setup(client):
    client.add_cog(Help(client))