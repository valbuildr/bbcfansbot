import discord, logging
from discord.ext import commands
import config

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

newsfansbotlog = logging.getLogger('discord.newsfansbot')

@bot.event
async def on_ready():
    newsfansbotlog.info(f'Logged in as {bot.user.name}.')

@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send(content=f"My ping is {round(bot.latency * 1000)}ms!")

@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)

bot.run(config.helper_discord_token)