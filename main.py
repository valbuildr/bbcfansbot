import discord
from discord.ext import commands
import config
import random
import time

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}.")
    return

@bot.command(name="sync")
async def sync(interaction: commands.Context):
    owner = await bot.is_owner(interaction.author)
    if owner:
        m = await interaction.send("Syncing....")
        await bot.tree.sync()
        await m.edit(content="Synced!")
        return
    else:
        m = await interaction.send(content="You don't have the permissions to do this!")
        await interaction.message.delete(10)
        await m.delete(10)
        return

@bot.hybrid_command(name="aaron", description="Sends a random picture of Aaron Heslehurst!")
async def aaron(interaction: commands.Context):
    no = random.randint(0, 4)
    match no:
        case 2:
            fileformat = "webp"
        case _:
            fileformat = "jpg"
    image = discord.File(f"images/aaron/{no + 1}.{fileformat}")
    await interaction.send(file=image)

@bot.hybrid_command(name="credits", description="Thanks everyone who helped work on this bot!")
async def credits(interaction: commands.Context):
    e = discord.Embed(title="Credits", colour=discord.Colour.blurple())
    e.add_field(name="Programming", value="[valbuildr](https://github.com/valbuildr)\n[slipinthedove](https://github.com/slipinthedove) (also known as <@1132298238628724837>)", inline=False)

    await interaction.send(embed=e, ephemeral=True)

bot.run(config.discord_token)