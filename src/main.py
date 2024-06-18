import discord, random, traceback, datetime, logging, math, os, messageutils, database, argparse, peewee
import ext.status as status
from datetime import datetime
from typing import List
from discord.ext import commands
from discord import app_commands as appcmds
from discord import ui
from ext import nitro
from simplejsondb import DatabaseFolder
from messageutils import error_template
from dotenv import dotenv_values
from models.croissants import CroissantsModel
from models.livepages import LivePage
from models.moderation import ModerationNotes
from database import db as database
from zoneinfo import ZoneInfo

# TODO: Refactor to new database stuff.

config = dotenv_values("src/.env")

parser = argparse.ArgumentParser(prog='BBCFansBot',
                                 description='a silly lil bot :3',
                                 epilog='stay silly :3 :3 :3 :3')
parser.add_argument('-d', '--debug',
                    action="store_true")
args = parser.parse_args()

bot = commands.Bot(command_prefix=",", intents=discord.Intents.all())
db = DatabaseFolder('db', default_factory=lambda _: dict())

if args.debug:
    bot.command_prefix = "."

server: discord.Guild
mod_role: discord.Role

fansbotlog = logging.getLogger('discord.fansbot')

@bot.command()
@commands.dm_only()
async def sync_tables(ctx: commands.Context):
    ids = [1191850547138007132, 152501641436856321]
    if ctx.author.id in ids:
        r = await ctx.send(content="Syncing...")
        
        database.create_tables([
            CroissantsModel,
            LivePage,
        ])

        await r.edit(content="Synced!")
    else:
        await ctx.send(content="You don't have the permissions to do this!")
        return

@bot.event
async def on_ready():
    fansbotlog.info(f"Logged in as {bot.user.name}.")

    server = bot.get_guild(1199367542901325854)
    mod_role = server.get_role(1249855596094820382)

    bot.loop.create_task(status.task(bot))

    return

# should only be used for debugging
# @bot.event
# async def on_app_command_completion(int: discord.Interaction, cmd: discord.app_commands.Command):
#     fansbotlog.info(f"Command {cmd.name} ran by {int.user.name}")
#     return

@bot.event
async def on_message(message: discord.Message):
    if bot.user.mentioned_in(message): await message.add_reaction("👋")
    
    # censoring bot bot 🥰🥰
    if message.content == "(please do consider using vxtwitter please and thank you)" and message.author.id == 1091826653367386254: await message.delete()
    if message.content == ":pepeAngryPing:" and message.author.id == 1091826653367386254: await message.delete()
    if message.content == "Sent to https://bloopertrack.club" and message.author.id == 1091826653367386254: await message.delete()

    await bot.process_commands(message)

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.timed_out_until == None and after.timed_out_until != None:
        to_until_a = messageutils.dt_to_timestamp(after.timed_out_until, "R")
        to_until_b = messageutils.dt_to_timestamp(after.timed_out_until, "f")

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
    ids = [1191850547138007132, 152501641436856321]
    if interaction.author.id in ids:
        m = await interaction.send("Syncing....")
        await bot.tree.sync()
        await m.edit(content="Synced!")
        return
    else:
        m = await interaction.send(content="You don't have the permissions to do this!")
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
async def give_croissant(interaction: commands.Context, user: discord.User):
    if user.id == interaction.author.id:
        await interaction.reply(content=f"Silly {interaction.author.mention}, you can't give a croissant to yourself!")
        return
    elif user.bot:
        await interaction.reply(content=f"Silly {interaction.author.mention}, you can't give a croissant to a bot!")
    else:
        await interaction.reply(content=f"{interaction.author.mention}, gave a croissant to {user.mention}! Enjoy it!")

        CroissantsModel.add_croissant(user.id)

@bot.hybrid_command(name="croissant-inventory", description="Tells you how many croissants you have.")
async def croissant_inv(interaction: commands.Context, user: discord.User = None):
    if user == None: user = interaction.author

    u = CroissantsModel.check_user(user.id)

    cc = ""

    if u['croissant_count'] == 1:
        cc = "**1 croissant**!"
    elif u["croissant_count"] == 0:
        cc = "**no croissants**."
    else:
        cc = f"**{u['croissant_count']} croissants**!"

    await interaction.reply(content=f"{user.mention} has {cc}", allowed_mentions=discord.AllowedMentions.none())

# @bot.hybrid_command(name="croissant-lb", description="The croisant leaderboard! Shows the top 3 users with the most croissants.")
# async def croissant_leader(interaction: commands.Context):
#     ...

async def programme_sid_autocomplete(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
    options = nitro.nitroSIDs["channels"]
    return [
        discord.app_commands.Choice(name=option, value=option)
        for option in options if current.lower() in option.lower()
    ]

async def programme_region_autocomplete(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
    options = nitro.nitroSIDs["region"]
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
        listing = await nitro.get_schedule(sid, date, page)
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
                items += f"> **<a:LivePulseRed:1233447000574398557> <t:{starttime}:t> - {i['title']}**\n"
            else: # not live
                # TODO: Change all of this to simply fetch the emojis from Discord instead of having to change the emojis in the strings.
                regions_emoji = "<:regions:1239609035624288367>"
                match i['title']:
                    case "Breakfast": items += f"<:breakfast:1239516524893437995> <t:{starttime}:t> - {i['title']}\n"
                    case "BBC News": items += f"<:news:1239516535790506025> <t:{starttime}:t> - {i['title']}\n"
                    case "Business Today - NYSE Opening Bell" | "Business Today": items += f"<:business:1239516530417340498> <t:{starttime}:t> - {i['title']}\n"
                    case "BBC News Now": items += f"<:newsnow:1239517505341362266> <t:{starttime}:t> - {i['title']}\n"
                    case "BBC News at One": items += f"<:one:1239607750913294356> <t:{starttime}:t> - {i['title']}\n"
                    case "Look East": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Channel Islands News": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Look East": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "East Midlands Today": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "BBC London": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Look North (North East and Cumbria)": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "North West Today" | "North West Tonight": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "BBC Newsline": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "South Today": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Reporting Scotland": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "South East Today": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Spotlight": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "BBC Wales Today": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Points West": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Midlands Today": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Look North (East Yorkshire and Lincolnshire)": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Look North (Yorkshire)": items += f"{regions_emoji} <t:{starttime}:t> - {i['title']}\n"
                    case "Verified Live": items += f"<:verifiedlive:1239516563229638696> <t:{starttime}:t> - {i['title']}\n"
                    case "BBC News at Six": items += f"<:six:1239607743539576862> <t:{starttime}:t> - {i['title']}\n"
                    case "Sportsday": items += f"<:sport:1239516554304028673> <t:{starttime}:t> - {i['title']}\n"
                    case "The World Today with Maryam Moshiri": items += f"<:worldtoday:1239516571555201024> <t:{starttime}:t> - {i['title']}\n"
                    case "BBC World News America": items += f"<:worldnewsamerica:1239516567444656140> <t:{starttime}:t> - {i['title']}\n"
                    case "BBC News at Ten": items += f"<:ten:1239607736631562291> <t:{starttime}:t> - {i['title']}\n"
                    case "Newswatch": items += f"<:newswatch:1239516541167468654> <t:{starttime}:t> - {i['title']}\n"
                    case _: items += f"⚫ <t:{starttime}:t> - {i['title']}\n"
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

async def rule_autocomplete(interaction: discord.Interaction, current: str) -> List[discord.app_commands.Choice[str]]:
    options = {
        "Be respectful": 1,
        "Drama": 2,
        "Use the correct channels": 3,
        "Doxxing": 4,
        "Hate speech": 5,
        "Spam": 6,
        "Pings": 7,
        "NSFW content": 8,
        "Maturity": 9,
    }
    return [
        appcmds.Choice(name=key, value=string)
        for key, string in options if current.lower() in key.lower()
    ]

async def length_autocomplete(interaction: discord.Interaction, current: str) -> List[appcmds.Choice[str]]:
    options = {
        "1 hour": 3600,
        "6 hours": 21600,
        "1 day": 86400,
        "1 week": 604800,
        "2 weeks": 1209600,
    }
    return [
        appcmds.Choice(name=key, value=string)
        for key, string in options if current.lower() in key.lower()
    ]

@bot.tree.command(name="add-note", description="Adds a note to a users profile.")
async def add_note(interaction: discord.Interaction, user: discord.Member, note: str, image: discord.Attachment = None, dm_user: bool = False):
    if mod_role in interaction.user.roles:
        ...
    else:
        await interaction.response.send_message(content="You don't have the permissions to do this.", ephemeral=True)

@bot.tree.command(name="warn", description="Warns a user.")
@appcmds.autocomplete(rule=rule_autocomplete)
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str, image: discord.Attachment = None, rule: int = 0, dm_user: bool = False):
    if mod_role in interaction.user.roles:
        ...
    else:
        await interaction.response.send_message(content="You don't have the permissions to do this.", ephemeral=True)

@bot.tree.command(name="mute", description="Mutes a user.")
@appcmds.autocomplete(length=length_autocomplete,
                      rule=rule_autocomplete)
async def mute(interaction: discord.Interaction, user: discord.Member, reason: str, length: int = 3600, image: discord.Attachment = None, rule: int = 0, dm_user: bool = False):
    if mod_role in interaction.user.roles:
        ...
    else:
        await interaction.response.send_message(content="You don't have the permissions to do this.", ephemeral=True)

image_types = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
]

class LivePageCommand(appcmds.Group):
    @appcmds.command(name="new", description="Creates a live page.")
    @appcmds.describe(title="The title of the live page.",
                      image="The image to add onto the welcome embed.")
    async def new(self, interaction: discord.Interaction, title: str, image: discord.Attachment = None):
        if mod_role in interaction.user.roles:
            class Modal(ui.Modal, title="Create a first post!"):
                t = ui.TextInput(label="Post Title",
                                 style=discord.TextStyle.short,
                                 placeholder="Our live coverage starts now!",
                                 default="Our live coverage starts now!",
                                 required=False,
                                 max_length=1000)
                d = ui.TextInput(label="Post Description",
                                 style=discord.TextStyle.long,
                                 placeholder=f"Read along as we learn more about \"{title}\", as it happens.",
                                 default=f"Read along as we learn more about \"{title}\", as it happens.",
                                 required=False,
                                 max_length=3000)
            
                async def on_submit(self, interaction: discord.Interaction):
                    embed = discord.Embed(title=self.t, description=self.d, colour=discord.Colour.from_rgb(20, 0, 71))
                    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                    embed.timestamp = datetime.now(ZoneInfo("Europe/London"))
                    if image != None and image.content_type in image_types: embed.set_image(url=image.proxy_url)
                    channel = bot.get_guild(1016626731785928715).get_channel(1249931775845863555)
                    post = await channel.create_thread(name=title, embed=embed)
                    try:
                        LivePage.create(thread_id=post.thread.id,
                                        title=post.thread.name,
                                        started_by=interaction.user.id,
                                        participating_members=str([interaction.user.id]))
                    except:
                        await post.thread.delete()
                        return await interaction.response.send_message(content="An issue occurred.", ephemeral=True)
                    
                    await post.thread.send(content="<@&1098348259870777465>")
                    return await interaction.response.send_message(content=f"Page created! {post.thread.mention}", ephemeral=True)
            await interaction.response.send_modal(Modal())
        else:
            await interaction.response.send_message(content="You don't have the permissions to do this.", ephemeral=True)
            return

    # TODO: Posting in live page
    @appcmds.command(name="post", description="Posts to a live page.")
    @appcmds.describe(thread="The live page's thread.",
                      image="The image to add onto the welcome embed.")
    async def post(self, interaction: discord.Interaction, thread: discord.Thread, image: discord.Attachment = None):
        if mod_role in interaction.user.roles:
            try:
                page = LivePage.get(LivePage.thread_id == thread.id)
            except peewee.DoesNotExist:
                return await interaction.response.send_message(content="That thread is not a live page.", ephemeral=True)
            
            if page.active:
                class Modal(ui.Modal, title="Creating a new post"):
                    t = ui.TextInput(label="Post Title",
                                     style=discord.TextStyle.short,
                                     required=True,
                                     max_length=1000)
                    d = ui.TextInput(label="Post Description",
                                     style=discord.TextStyle.long,
                                     required=True,
                                     max_length=3000)
                    
                    async def on_submit(self, interaction: discord.Interaction):
                        embed = discord.Embed(title=self.t, description=self.d, colour=discord.Colour.from_rgb(20, 0, 71))
                        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                        embed.timestamp = datetime.now(ZoneInfo("Europe/London"))
                        if image != None and image.content_type in image_types: embed.set_image(url=image.proxy_url)

                        partusers = list(page.participating_members)
                        if interaction.user.id not in partusers:
                            partusers.append(interaction.user.id)
                            page.participating_members = str(partusers)
                            page.save()

                        msg = await thread.send(embed=embed)
                        return await interaction.response.send_message(content=f"Sent! {msg.jump_url}", ephemeral=True)
                await interaction.response.send_modal(Modal())
            else:
                return await interaction.response.send_message(content="That live page is not active.", ephemeral=True)
        else:
            await interaction.response.send_message(content="You don't have the permissions to do this.", ephemeral=True)
            return

    @appcmds.command(name="end", description="Closes a live page.")
    @appcmds.describe(thread="The live page's thread.",
                      image="The image to add onto the welcome embed.")
    async def end(self, interaction: discord.Interaction, thread: discord.Thread, image: discord.Attachment = None):
        if mod_role in interaction.user.roles:
            try:
                page = LivePage.get(LivePage.thread_id == thread.id)
            except peewee.DoesNotExist:
                return await interaction.response.send_message(content="That thread is not a live page.", ephemeral=True)
            
            if page.active:
                class Modal(ui.Modal, title="Creating a last post"):
                    t = ui.TextInput(label="Post Title",
                                     style=discord.TextStyle.short,
                                     placeholder="That's is from us!",
                                     default="That's is from us!",
                                     required=True,
                                     max_length=1000)
                    d = ui.TextInput(label="Post Description",
                                     style=discord.TextStyle.long,
                                     placeholder="The journey ends here. Thank you for reading our live coverage.",
                                     default="The journey ends here. Thank you for reading our live coverage.",
                                     required=True,
                                     max_length=3000)
                    
                    async def on_submit(self, interaction: discord.Interaction):
                        embed = discord.Embed(title=self.t, description=self.d, colour=discord.Colour.from_rgb(20, 0, 71))
                        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                        embed.timestamp = datetime.now(ZoneInfo("Europe/London"))
                        if image != None and image.content_type in image_types: embed.set_image(url=image.proxy_url)

                        msg = await thread.send(embed=embed)

                        await thread.edit(locked=True, archived=True)

                        page.active = False
                        page.save()

                        return await interaction.response.send_message(content=f"The live page is now archived! {msg.jump_url}", ephemeral=True)
                await interaction.response.send_modal(Modal())
            else:
                return await interaction.response.send_message(content="That live page is not active.", ephemeral=True)
        else:
            await interaction.response.send_message(content="You don't have the permissions to do this.", ephemeral=True)
            return

bot.tree.add_command(LivePageCommand(name="livepage", description="Live page commands"))

bot.run(config["DISCORD_TOKEN"])