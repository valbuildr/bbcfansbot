import random, discord, asyncio
from zoneinfo import ZoneInfo
from datetime import datetime
from simplejsondb import DatabaseFolder
from discord.ext import commands

run = True

statuses = [
    discord.Activity(name="num make fire graphics 🔥", type=discord.ActivityType.watching),
    discord.Activity(name="Maryam bend a spoon", type=discord.ActivityType.watching),
    discord.Activity(name="The Shipping Forecast", type=discord.ActivityType.listening),
    discord.Activity(name="David Lowe's amazing music", type=discord.ActivityType.listening),
    discord.Activity(name="Talking Business with Aaron Heslehurst", type=discord.ActivityType.watching),
    discord.Activity(name="EF make a countdown", type=discord.ActivityType.watching),
    discord.Activity(name="Kat make BBCD2", type=discord.ActivityType.watching),
    # tv
    discord.Activity(name="BBC One", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Two", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Three", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Four", type=discord.ActivityType.watching),
    discord.Activity(name="CBBC", type=discord.ActivityType.watching),
    discord.Activity(name="CBeebies", type=discord.ActivityType.watching),
    discord.Activity(name="BBC News", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Parliament", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Alba", type=discord.ActivityType.watching),
    discord.Activity(name="S4C", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Scotland", type=discord.ActivityType.watching),
    # national radio
    discord.Activity(name="BBC Radio 1", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 1Xtra", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 2", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 3", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 4", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 4 Extra", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 5 Live", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 5 Sports Extra", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 6 Music", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Asian Network", type=discord.ActivityType.listening),
    discord.Activity(name="BBC World Service", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 1 Dance", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio 1 Relax", type=discord.ActivityType.listening),
    # regional radio
    discord.Activity(name="BBC Radio Scotland", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Orkney", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Shetland", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Scotland Extra", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Cymru 2", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio nan Gàidheal", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Ulster", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Foyle", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Wales", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Wales Extra", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Cymru", type=discord.ActivityType.listening),
    # local radio
    discord.Activity(name="BBC Radio Berkshire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Bristol", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Cambridgeshire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Cornwall", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Coventry & Warwickshire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Cumbria", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Derby", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Devon", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Essex", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Gloucestershire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Guernsey", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Hereford & Worcester", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Humberside", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Jersey", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Kent", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Lancashire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Leeds", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Leicester", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Lincolnshire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio London", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Manchester", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Merseyside", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Newcastle", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Norfolk", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Northampton", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Nottingham", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Oxford", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Sheffield", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Shropshire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Solent", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Dorset", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Somerset", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Stoke", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Suffolk", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Surrey", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Sussex", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Tees", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Three Counties Radio", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Wiltshire", type=discord.ActivityType.listening),
    discord.Activity(name="BBC WM 95.6", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio York", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Guernsey Extra", type=discord.ActivityType.listening),
    discord.Activity(name="BBC Radio Jersey Extra", type=discord.ActivityType.listening),
]

async def change_status(bot: commands.Bot, db: DatabaseFolder):
    now = datetime.now(ZoneInfo("Europe/London"))

    regions = ["Look North (NE&C)", "East Midlands Today", "BBC London", "North West Tonight", "Midlands Today", "South East Today", "Look North (Yorks)", "Look East", "South Today", "Look North (Yorks and Lincs)", "Points West", "Spotlight", "Reporting Scotland", "Wales Today", "Newsline"]

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    if now.strftime("%a") in weekdays:
        if now.hour == 6 or now.hour == 7 or now.hour == 8 or now.hour == 9:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="BBC Breakfast"))
        elif now.hour == 13 and now.minute >= 30:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the News at One"))
        elif now.hour == 13 and now.minute <= 31 and now.minute <= 45:
            random_region = random.choice(regions)
            if random_region == "North West Tonight":
                random_region = "North West Today"
            
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random_region))
        elif now.hour == 18 and now.minute >= 31:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the News at Six"))
        elif now.hour == 18 and now.minute <= 31 and now.minute <= 55:
            random_region = random.choice(regions)

            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random_region))
        elif now.hour == 22 and now.minute >= 30:
            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the News at Ten"))
        elif now.hour == 22 and now.minute <= 30 and now.minute <= 40:
            random_region = random.choice(regions)

            await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random_region))
        else:
            rand = random.choice(statuses)
            await bot.change_presence(activity=rand)
    else:
        rand = random.choice(statuses)
        await bot.change_presence(activity=rand)

    await asyncio.sleep(60) # run every minute

async def task(bot: commands.Bot, db: DatabaseFolder):
    while True:
        while run:
            await change_status(bot, db)