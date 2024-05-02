import discord, config, random, traceback, datetime, logging, status, math, os
from datetime import datetime
from typing import List
from discord.ext import commands
from ext import nitro
from simplejsondb import DatabaseFolder
from messageutils import error_template

run_beta = False

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())
db = DatabaseFolder('db', default_factory=lambda _: dict())

if run_beta:
    bot.command_prefix = "."

fansbotlog = logging.getLogger('discord.fansbot')

nitroSIDs = { "region": [ "Northern Ireland", "Scotland", "Wales", "South", "East Midlands", "West Midlands", "East Yorkshire", "North West", "North East", "London", "Sourth East", "South West", "West", "East", "South", "Yorks" ], "channels": [ "BBC News [UK]", "BBC News [World]", "BBC One", "BBC Two", "BBC Three", "BBC Four", "Cbeebies", "CBBC", "BBC Parliament", "BBC Alba", "BBC Scotland" ], "BBC News [World]": "bbc_world_service", "BBC News [UK]": "bbc_news24", "BBC One Scotland": "bbc_one_scotland", "BBC One North East": "bbc_one_north_east", "BBC One North West": "bbc_one_north_west", "BBC One East Midlands": "bbc_one_east_midlands", "BBC One West Midlands": "bbc_one_west_midlands", "BBC One East Yorkshire": "bbc_one_east_yorkshire", "BBC One London": "bbc_one_london", "BBC One South East": "bbc_one_south_east", "BBC One South West": "bbc_one_south_west", "BBC One Northern Ireland": "bbc_one_northern_ireland", "BBC One Wales": "bbc_one_wales", "BBC One West": "bbc_one_west", "BBC One East": "bbc_one_east", "BBC One South": "bbc_one_south", "BBC One Yorks": "bbc_one_yorks", "BBC One": "bbc_one_hd", "BBC Two England": "bbc_two_england", "BBC Two Scotland": "bbc_two_scotland", "BBC Two Northern Ireland": "bbc_two_northern_ireland_digital", "BBC Two Wales": "bbc_two_wales_digital", "BBC Two": "bbc_two_hd", "BBC Three": "bbc_three_hd", "BBC Four": "bbc_four_hd", "CBeebies": "cbeebies_hd", "CBBC": "cbbc_hd", "BBC Parliament": "bbc_parliament", "BBC Alba": "bbc_alba_hd", "BBC Scotland": "bbc_scotland_hd" }
if db["NitroSIDs"] == []: db["NitroSIDs"] = nitroSIDs

# syntax: [status id, value of discord.StatusType enum, activity name]
basestatuses = [["bi01", 3, "num make fire graphics 🔥"], ["bi02", 3, "Maryam bend a spoon"], ["bi03", 2, "The Shipping Forecast"], ["bi04", 2, "David Lowe's amazing music"], ["bi05", 3, "the BBC News channel"], ["bi06", 3, "Talking Business with Aaron Heslehurst"], ["bi07", 4, "BBC World Service"]]
if db["statuses"] == []: db["statuses"] = basestatuses

if isinstance(db["croissants"], list): db["croissants"] = {}

@bot.event
async def on_ready():
    fansbotlog.info(f"Logged in as {bot.user.name}.")

    bot.loop.create_task(status.task(bot, db))

    # await bot.load_extension("ext.economy")

    return

# should only be used for debugging
# @bot.event
# async def on_app_command_completion(int: discord.Interaction, cmd: discord.app_commands.Command):
#     fansbotlog.info(f"Command {cmd.name} ran by {int.user.name}")
#     return

@bot.event
async def on_message(message: discord.Message):
    if bot.user.mentioned_in(message):
        await message.add_reaction("👋")
    
    if message.content == "(please do consider using vxtwitter please and thank you)" and message.author.id == 1091826653367386254:
        await message.delete()

    if ":pepeAngryPing:"in  message.content and message.author.id == 1091826653367386254:
        await message.delete()

    await bot.process_commands(message)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.timed_out_until == None and after.timed_out_until != None:
        to_until_a = nitro.dt_to_timestamp(after.timed_out_until, "R")
        to_until_b = nitro.dt_to_timestamp(after.timed_out_until, "f")

        embed = discord.Embed(title="Member timed out", colour=discord.Colour.brand_red())
        embed.add_field(name="Timed out until", value=f"{to_until_a} ({to_until_b})")
        embed.add_field(name="User", value=f"{after.mention}")
        embed.timestamp = datetime.now()

        await bot.get_guild(1016626731785928715).get_channel(1060597991347593297).send(embed=embed)

@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send(content=f"## Pong!\nMy ping is {round(bot.latency * 1000)}ms.")

@bot.command(name="nf-live-start", hidden=True)
async def nf_start(ctx: commands.Context):
    nf_role = bot.get_guild(1016626731785928715).get_role(1152621246748569650)
    if nf_role in ctx.author.roles:
        status.run = False
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="BBC News Fans"))
        await ctx.send(content="Set status!")
    else:
        await ctx.send(content="You can't run this command.")

@bot.command(name="nf-live-end", hidden=True)
async def nf_end(ctx: commands.Context):
    nf_role = bot.get_guild(1016626731785928715).get_role(1152621246748569650)
    if nf_role in ctx.author.roles:
        status.run = True
        await ctx.send(content="Changed status!")
    else:
        await ctx.send(content="You can't run this command.")

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

def random_file(path: str):
    files = os.listdir(path)
    return random.choice(files)

@bot.hybrid_command(name="aaron", description="Sends a random picture of Aaron Heslehurst!")
async def aaron(interaction: commands.Context):
    imgpath = random_file("images/aaron")
    image = discord.File(f"images/aaron/{imgpath}")
    await interaction.send(file=image)

@bot.hybrid_command(name="give-croissant", description="Gives a croissant to a user.")
async def give_croissant(interaction: commands.Context, user: discord.Member):
    if user.id == interaction.author.id:
        await interaction.reply(content=f"Sily {interaction.author.mention}, you can't give a croissant to yourself!")
        return
    elif user.bot:
        await interaction.reply(content=f"Sily {interaction.author.mention}, you can't give a croissant to a bot!")
    else:
        await interaction.reply(content=f"{interaction.author.mention}, gave a croissant to {user.mention}! Enjoy it!")

        if str(user.id) not in db["croissants"].keys():
            db["croissants"][str(user.id)] = 1
        else:
            db["croissants"][str(user.id)] += 1

@bot.hybrid_command(name="croissant-inventory", description="Tells you how many croissants you have.")
async def no_croissants(interaction: commands.Context):
    if str(interaction.author.id) not in db["croissants"].keys():
        db["croissants"][str(interaction.author.id)] = 0
    
    no = db["croissants"][str(interaction.author.id)]

    await interaction.reply(content=f"You have **{no} croissants**!")

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
    await interaction.response.defer(ephemeral=False)
    try:
        if region: sid = f"{sid} {region}"
        listing = await nitro.get_schedule(db, sid, date, page)
        items = ""
        # makes the embed base
        e = discord.Embed(title=f"Schedule for {listing['passedSid']}, {listing['date']}", 
            colour=discord.Colour.blurple())
        # checks which program is live, if it's a schedule from today:
        todaylive = None
        if listing['isToday']: 
            for off, i in enumerate(listing['items']):
                epochnow = int(datetime.now().timestamp())
                starttime, endtime = i['time'][0], i['time'][1]
                # if the time right now is higher than the start time 
                # *and* the endtime is higher than the start... it's live.
                if epochnow > i['time'][0] and i['time'][1] > epochnow:
                   todaylive = off 
        # sorts out every item with it's formatted date
        for off, i in enumerate(listing['items']):
            starttime = i['time'][0]
            if todaylive and off == todaylive: # live
                if i['title'] == "World Business Report" or i['title'] == "Asia Business Report": # wbr/abr emoji, to be replaced with business today
                    items += f"<:business:1229821037860880515> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "BBC News": # news emoji
                    items += f"<:news:1229821049986875474> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "BBC News Now": # news now emoji
                    items += f"<:newsnow:1229891488662425721> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "BBC News at One": # nao emoji
                    items += f"<:one:1229821045393981460> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "": # regions emoji
                    # TODO: get a list of region programme names
                    items += f"<:regions:1229438785737986068> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "BBC News at Six": # nas emoji
                    items += f"<:six:1229821042432671825> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "Sportsday": # sport emoji
                    items += f"<:sport:1229829293094469774> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "BBC News at Ten": # nat emoji
                    items += f"<:ten:1229821040637513799> <t:{starttime}:t> - **{i['title']}**\n"
                elif i['title'] == "Pointless": # pointless emoji
                    items += f"<:pointless:1233447132619608237> <t:{starttime}:t> - **{i['title']}**\n"
                else:
                    items += f"<a:LivePulseRed:1233447000574398557> <t:{starttime}:t> - **{i['title']}**\n"
            else: # not live
                if i['title'] == "World Business Report" or i['title'] == "Asia Business Report": # wbr/abr emoji, to be replaced with business today
                    items += f"<:business:1229821037860880515> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "BBC News": # news emoji
                    items += f"<:news:1229821049986875474> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "BBC News Now": # news now emoji
                    items += f"<:newsnow:1229891488662425721> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "BBC News at One": # nao emoji
                    items += f"<:one:1229821045393981460> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "": # regions emoji
                    # TODO: get a list of region programme names
                    items += f"<:regions:1229438785737986068> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "BBC News at Six": # nas emoji
                    items += f"<:six:1229821042432671825> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "Sportsday": # sport emoji
                    items += f"<:sport:1229829293094469774> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "BBC News at Ten": # nat emoji
                    items += f"<:ten:1229821040637513799> <t:{starttime}:t> - {i['title']}\n"
                elif i['title'] == "Pointless": # pointless emoji
                    items += f"<:pointless:1233447132619608237> <t:{starttime}:t> - {i['title']}\n"
                else:
                    items += f"⬛ <t:{starttime}:t> - {i['title']}\n"
        # adds the items field after being parsed as a single-str
        e.add_field(name=f"Page {page}/{math.ceil(listing['total_items'] / 10)}:", value=items)
        e.set_footer(text="Times are based on your system clock.")
        e.url = await nitro.get_link(db, sid)
        await interaction.followup.send(embed=e)
    except Exception as e:
        fansbotlog.error(traceback.format_exc())
        msg = error_template(f"```\n{e}\n```")
        m = await interaction.followup.send(embed=msg)
        return
    except:
        fansbotlog.error(traceback.format_exc())
        msg = error_template(f"<:idk:1100473028485324801> Check bot logs.")
        m = await interaction.followup.send(embed=msg)
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

bot.run(config.main_discord_token)
