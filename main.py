from typing import List
import discord
from discord.ext import commands
import config
import random
import time
import traceback
from modules import nitro
from simplejsondb import DatabaseFolder

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())
db = DatabaseFolder('db', default_factory=lambda _: list())

async def error_template(e):
    embed = discord.Embed(title=f"An error occurred!", colour=discord.Colour.red())
    embed.add_field(name="Error", value=f"{e}")
    return embed

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

async def programme_sid_autocomplete(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
    options = list(db['NitroSIDs'])
    return [
        discord.app_commands.Choice(name=option, value=option)
        for option in options if current.lower() in option.lower()
    ]

# programme works best as a slash-only command. 
# primarily because it's more practical to get the arguments from the user.
@bot.tree.command(name="programme", description="Gets the latest schedules from the BBC services!")
@discord.app_commands.describe(sid="The channel (service ID) by it's short-name", 
                                date="The date of the schedule to get. Uses YYYY-MM-DD formatting.", 
                                page="The page of the schedule to get.")
@discord.app_commands.autocomplete(sid=programme_sid_autocomplete)
@discord.app_commands.rename(sid='channel')
async def programme(interaction: discord.InteractionResponse, 
                    sid: str="BBC News [UK]", date: str=None, page: int=1):
    try:
        listing = await nitro.get_schedule(db, sid, date, page)
        items = ""
        # makes the embed base
        e = discord.Embed(title=f"Schedule for {listing['passedSid']}, {listing['date']}", 
            colour=discord.Colour.red())
        # sorts out every item with it's formatted date
        for i in listing['items']:
            items += f"<t:{i['start']}:t> - **{i['title']}**\n"
        # adds the items field after being parsed as a single-str
        e.add_field(name=f"Page {page} (times are based on your system clock):", value=items)
        await interaction.response.send_message(embed=e, ephemeral=True)
    except Exception as e:
        msg = await error_template(f"```\n{e}\n```")
        m = await interaction.response.send_message(embed=msg, ephemeral=True)
        return
    except:
        print(traceback.format_exc())
        msg = await error_template(f"<:idk:1100473028485324801> Check bot logs.")
        m = await interaction.response.send_message(embed=msg, ephemeral=True)
        return

@bot.hybrid_command(name="credits", description="Thanks everyone who helped work on this bot!")
async def credits(interaction: commands.Context):
    e = discord.Embed(title="Credits", colour=discord.Colour.blurple())
    e.add_field(name="Programming", value="[valbuildr](https://github.com/valbuildr)\n[slipinthedove](https://github.com/slipinthedove) (soapu64)", inline=False)

    await interaction.send(embed=e, ephemeral=True)

bot.run(config.discord_token)
