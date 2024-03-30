import discord
from discord.ext import commands
import config
import random
import time
from modules import nitro

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())

async def error_template(e):
    embed = discord.Embed(title=f"oops lol", colour=discord.Colour.red())
    embed.add_field(name="error while running command", value=f"`{e}`")
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

# programme works best as a slash-only command. 
# primarily because it's more practical to get the arguments from the user.
@bot.tree.command(name="programme", description="Gets the latest schedules from the BBC services!")
@discord.app_commands.describe(sid="The service ID by it's short-name", 
                                date="The date of the schedule to get. Uses YYYY-MM-DD formatting.", 
                                page="The page of the schedule to get.")
async def programme(interaction: discord.InteractionResponse, sid: str="one", date: str=None, page: int=1):
    try:
        listing = await nitro.get_schedule(date, sid, page)
        items = ""
        # makes the embed base
        e = discord.Embed(title=f"Schedule for {listing['sid']} (`{listing['passedSid']}`), {listing['date']}", 
            colour=discord.Colour.red())
        # sorts out every item with it's formatted date
        for i in listing['items']:
            items += f"<t:{i['start']}:t> - **{i['title']}**\n"
        # adds the items field after being parsed as a single-str
        e.add_field(name=f"Page {page} (times are based on your clock):", value=items)
        await interaction.response.send_message(embed=e, ephemeral=True)
    except Exception as e:
        msg = await error_template(f"{e}")
        m = await interaction.response.send_message(embed=msg, ephemeral=True)
        return
    except:
        msg = await error_template(f"Check bot logs, i guess.")
        m = await interaction.response.send_message(embed=msg, ephemeral=True)
        return

@bot.hybrid_command(name="credits", description="Thanks everyone who helped work on this bot!")
async def credits(interaction: commands.Context):
    e = discord.Embed(title="Credits", colour=discord.Colour.blurple())
    e.add_field(name="Programming", value="[valbuildr](https://github.com/valbuildr)\n[slipinthedove](https://github.com/slipinthedove) (soapu64)", inline=False)

    await interaction.send(embed=e, ephemeral=True)

bot.run(config.discord_token)
