import discord
import os

from discord.ext import commands
from random import randint
from re import split, IGNORECASE
from utilities import settings

settings = settings.config("settings.json")

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        #ready globals
        self.embed = None
        self.message = None
        self.waiting = {}

    ##################### Utility Commands
    @commands.command(help="no arg: WARNING reloads all cogs")
    @commands.is_owner()
    async def reload(self, ctx):
        for file in os.listdir(settings.COG_PATH):
            if file.endswith(".py"):
                name = file[:-3]
                self.bot.reload_extension(f"cogs.{name}")

        await ctx.send(content="cogs reloaded") 


    @commands.command(help="latency test")
    async def ping(self, ctx):
        await ctx.send(content=f"Discord websocket latency: **{round(self.bot.latency, 3)} seconds**")


    #################### User Commands
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ready(self, ctx):
        if self.embed:
            #Edit ready check as closed and then clean up vars
            self.embed = None
            self.message = None
            self.waiting = {}
        self.embed = discord.Embed(title="Ready Check", description="React to this post with ✅ whenever you're ready!\nYou can un-ready by reacting with the ❌.", color=0x64b4ff)
        self.embed.set_thumbnail(url="https://i.imgur.com/Uk87ls4.png")

        body = ""
        i = 0
        for member in ctx.author.voice.channel.members:
            name = member.nick
            if not name:
                name = member.name

            self.waiting[member.id] = {
                "name": name,
                "ready_icon": "❌",
                "ready": False,
                "position": i,
            }
            body = f'{body}-__{name}__: ❌\n'
            i += 1
        
        self.embed.add_field(name='Ready?', value=body[:-1])
        self.message = await ctx.send(embed=self.embed)

        await self.message.add_reaction("✅")
        await self.message.add_reaction("❌")


    @commands.command(help="(num of dice)d(faces on die) +/- (num modifier)")
    async def roll(self, ctx, *, roll):
        t = split(r"(d)", roll, flags=IGNORECASE)
        quantity, faces = min(100, int(t[0])), t[2] #["5" , "20 - 3"]
        mod_op = ''

        try:
            t = split(r"(\+|\-)", faces) #["20", "-" "3"]
            faces, mod_op, mod_val = int(t[0]), t[1], int(t[2])
        except Exception:
            faces = int(faces)
        
        roll_results = []
        message = ""
        
        while quantity > 0:
            roll = randint(1, faces)
            roll_results.append(roll)
            message = f"{message}[ **{roll}** ] + "
            quantity -= 1
        message = message [:-3]

        results = 0
        for roll in roll_results:
            results += roll

        if mod_op:
            if mod_op == "+":
                results += mod_val
            else:
                results -= mod_val
            message = f'{message} {mod_op} {mod_val}'

        message = message + f"\n\n__Total__ = {results}"
        await ctx.send(content=message)


    ##################### Events
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message == self.message and not user.bot:
            if reaction.emoji == "✅":
                self.waiting[user.id]["ready"] = True
                self.waiting[user.id]["ready_icon"] = "✅"
                inverse = "❌"
            elif reaction.emoji == "❌":
                self.waiting[user.id]["ready"] = False
                self.waiting[user.id]["ready_icon"] = "❌"
                inverse = "✅"
            
            out = self.embed.fields[0].value.replace(
                "{name}__: {inverse}".format(name=self.waiting[user.id]["name"], inverse=inverse),
                "{name}__: {icon}".format(name=self.waiting[user.id]["name"], icon=self.waiting[user.id]["ready_icon"]),
                1
            )

            self.embed.set_field_at(index=0, name="Ready?", value=out)
            await self.message.edit(embed=self.embed)
            await reaction.message.channel.send(f'```{t}```')

    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected succesfully!')
        game = discord.Game(name="Dungeons and Dragons")
        await self.bot.change_presence(activity=game)

def setup(bot):
    bot.add_cog(Commands(bot))