import discord, config, random, time, traceback, datetime, logging
from logging import handlers
from datetime import datetime
from typing import List, Optional
from discord.ext import commands
from modules import nitro
from simplejsondb import DatabaseFolder

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())
db = DatabaseFolder('db', default_factory=lambda _: list())

fansbotlog = logging.getLogger('discord.fansbot')

def error_template(e):
    embed = discord.Embed(title=f"An error occurred!", colour=discord.Colour.red())
    embed.add_field(name="Error", value=f"{e}")
    return embed

def dt_to_timestamp(dt: datetime, f):
    formats = ["d", "D", "t", "T", "f", "F", "R"]
    if f not in formats:
        return str(round(time.mktime(dt.timetuple())))
    else:
        return f"<t:{round(time.mktime(dt.timetuple()))}:{f}>"

@bot.event
async def on_ready():
    fansbotlog.info(f"Logged in as {bot.user.name}.")
    return

@bot.event
async def on_app_command_completion(int: discord.Interaction, cmd: discord.app_commands.Command):
    fansbotlog.info(f"Command {cmd.name} ran by {int.user.name}")
    return

@bot.event
async def on_message(message: discord.Message):
    if "bbc fans bot" in message.content.lower() or bot.user.mentioned_in(message):
        await message.channel.send("hellow!")

    await bot.process_commands(message)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.timed_out_until == None and after.timed_out_until != None:
        to_until_a = dt_to_timestamp(after.timed_out_until, "R")
        to_until_b = dt_to_timestamp(after.timed_out_until, "f")

        embed = discord.Embed(title="Member timed out", colour=discord.Colour.brand_red())
        embed.add_field(name="Timed out until", value=f"{to_until_a} ({to_until_b})")
        embed.add_field(name="User", value=f"{after.mention}")
        embed.timestamp = datetime.now()

        await bot.get_guild(1016626731785928715).get_channel(1060597991347593297).send(embed=embed)

@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send(content=f"## Pong!\nMy ping is {round(bot.latency * 1000)}ms.")

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
        case 2: fileformat = "webp"
        case _: fileformat = "jpg"
    image = discord.File(f"images/aaron/{no + 1}.{fileformat}")
    await interaction.send(file=image)

async def programme_sid_autocomplete(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
    options = db['NitroSIDs']['channels']
    return [
        discord.app_commands.Choice(name=option, value=option)
        for option in options if current.lower() in option.lower()
    ]

async def programme_region_autocomplete(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
    options = db['NitroSIDs']['region']
    return [
        discord.app_commands.Choice(name=option, value=option)
        for option in options if current.lower() in option.lower()
    ]

# schedule works best as a slash-only command. 
# primarily because it's more practical to get the arguments from the user.
@bot.tree.command(name="schedule", description="Gets the latest schedules from the BBC services!")
@discord.app_commands.describe(sid="The channel (service ID) by it's short-name", 
                                date="The date of the schedule to get. Uses YYYY-MM-DD formatting.", 
                                page="The page of the schedule to get.",
                                region="The region of the channel.")
@discord.app_commands.autocomplete(sid=programme_sid_autocomplete,
                                    region=programme_region_autocomplete)
@discord.app_commands.rename(sid='channel')
async def programme(interaction: discord.Interaction, 
                    sid: str="BBC News [UK]", date: str=None, page: int=1, region: str=None):
    try:
        if region: sid = f"{sid} {region}"
        listing = await nitro.get_schedule(db, sid, date, page)
        items = ""
        # makes the embed base
        e = discord.Embed(title=f"Schedule for {listing['passedSid']}, {listing['date']}", 
            colour=discord.Colour.red())
        # checks which program is live, if it's a schedule from today:
        todaylive = None
        if listing['isToday']: 
            for off, i in enumerate(listing['items']):
                epochnow = int(datetime.now().timestamp())
                # if the time right now is higher than the start time 
                # *and* the endtime is higher than the start... it's live.
                if epochnow > i['time'][0] and i['time'][1] > epochnow:
                   todaylive = off 
        # sorts out every item with it's formatted date
        for off, i in enumerate(listing['items']):
            if todaylive and off == todaylive:
                items += f"<t:{i['time'][0]}:t> - **{i['title']} (LIVE)**\n"
            else:
                items += f"<t:{i['time'][0]}:t> - {i['title']}\n"
        # adds the items field after being parsed as a single-str
        e.add_field(name=f"Page {page} (times are based on your system clock):", value=items)
        await interaction.response.send_message(embed=e, ephemeral=False)
    except Exception as e:
        fansbotlog.error(traceback.format_exc())
        msg = error_template(f"```\n{e}\n```")
        m = await interaction.response.send_message(embed=msg, ephemeral=True)
        return
    except:
        fansbotlog.error(traceback.format_exc())
        msg = error_template(f"<:idk:1100473028485324801> Check bot logs.")
        m = await interaction.response.send_message(embed=msg, ephemeral=True)
        return

@bot.hybrid_command(name="credits", description="Thanks everyone who helped work on this bot!")
async def credits(interaction: commands.Context):
    e = discord.Embed(title="Credits", colour=discord.Colour.blurple())
    e.add_field(name="Programming", 
    value="[valbuildr](https://github.com/valbuildr)\n[slipinthedove](https://github.com/slipinthedove) (soapu64)", 
    inline=False)

    await interaction.send(embed=e, ephemeral=True)

@bot.hybrid_command(name="issue", description="Having an issue with the bot? Learn how to report it here.")
async def issue(interaction: commands.Context):
    e = discord.Embed(title="Having an issue?", 
    description="Report it on the [Github repository](https://github.com/valbuildr/bbcfansbot/issues).", 
    colour=discord.Colour.blurple())
    await interaction.send(embed=e, ephemeral=True)

@bot.command(name="threads")
async def direct_to_threads(ctx: commands.Context, mention_member: Optional[discord.Member]):
    if bot.get_guild(1016626731785928715).get_role(1060342499111092244) or bot.get_guild(1016626731785928715).get_role(1193959337136242768) in ctx.author.roles:
        thread_channels = [1048544405977579631, 1058384048386490368]
        if ctx.channel.id in thread_channels:
            c = ""
            if mention_member:
                c += f"{mention_member.mention} "
            
            c += "Please keep discussion in threads!"
            
            await ctx.send(content=c)

bot.run(config.discord_token)
