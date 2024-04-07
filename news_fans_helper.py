import discord
from discord.ext import commands
import config

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send(content=f"My ping is {bot.latency}!")

bot.run(config.helper_discord_token)
