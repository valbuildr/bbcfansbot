import discord
from discord.ext import commands
import config
import random

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")
    return

@bot.tree.command(name="sync")
async def sync(interaction: discord.interaction):
    if interaction.user.id == 1191850547138007132:
        await bot.tree.sync()
        await interaction.response.send_message(content="Synced!")

@bot.tree.command(name="aaron", description="Sends a random picture of Aaron Heslehurst!")
async def aaron(interaction: discord.Interaction):
    no = random.randint(0, 4)
    match no:
        case 2:
            fileformat = "webp"
        case _:
            fileformat = "jpg"
    image = discord.File(f"images/aaron/{no + 1}.{fileformat}")
    await interaction.response.send_message(file=image)

bot.run(config.token)