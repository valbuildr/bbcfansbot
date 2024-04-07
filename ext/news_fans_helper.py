import discord
from discord.ext import commands
import config

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@client.command()
async def ping(ctx: commands.Context):
    await ctx.send(content=f"My ping is {client.latency}!")

client.run(config.helper_discord_token)
