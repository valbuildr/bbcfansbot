import discord
from discord.ext import commands
import config
import random

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")
    return

@bot.command()
async def sync(ctx: commands.Context):
    if ctx.author.id == 1191850547138007132:
        r = await ctx.reply(content="Syncing...", mention_author=False)
        await bot.tree.sync()

        await r.edit(content="Synced!")

@bot.tree.command(name="aaron", description="Sends a random picture of Aaron Heslehurst!")
async def aaron_slash(interaction: discord.Interaction):
    no = random.randint(0, 4)

    match no:
        case 0:
            image = discord.File("images/aaron/1.jpg")
        case 1:
            image = discord.File("images/aaron/2.jpg")
        case 2:
            image = discord.File("images/aaron/3.webp")
        case 3:
            image = discord.File("images/aaron/4.jpg")
        case 4:
            image = discord.File("images/aaron/5.jpg")

    await interaction.response.send_message(file=image)

@bot.command()
async def aaron(ctx: commands.Context):
    no = random.randint(0, 4)

    match no:
        case 0:
            image = discord.File("images/aaron/1.jpg")
        case 1:
            image = discord.File("images/aaron/2.jpg")
        case 2:
            image = discord.File("images/aaron/3.webp")
        case 3:
            image = discord.File("images/aaron/4.jpg")
        case 4:
            image = discord.File("images/aaron/5.jpg")

    await ctx.reply(file=image, mention_author=False)

bot.run(config.token)