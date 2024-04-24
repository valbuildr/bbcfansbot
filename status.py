import random, discord, asyncio
from zoneinfo import ZoneInfo
from datetime import datetime
from simplejsondb import DatabaseFolder
from discord.ext import commands

run = True

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
            rand = random.choice(db["statuses"])

            typ = discord.ActivityType.playing

            match rand[1]:
                case 1:
                    typ = discord.ActivityType.streaming
                case 2:
                    typ = discord.ActivityType.listening
                case 3:
                    typ = discord.ActivityType.watching
                case 5:
                    typ = discord.ActivityType.competing
        
            await bot.change_presence(activity=discord.Activity(type=typ, name=rand[2]))
    else:
        rand = random.choice(db["statuses"])

        typ = discord.ActivityType.playing

        match rand[1]:
            case 1:
                typ = discord.ActivityType.streaming
            case 2:
                typ = discord.ActivityType.listening
            case 3:
                typ = discord.ActivityType.watching
            case 5:
                typ = discord.ActivityType.competing
    
        await bot.change_presence(activity=discord.Activity(type=typ, name=rand[2]))

        await asyncio.sleep(60) # run every minute

async def task(bot: commands.Bot, db: DatabaseFolder):
    while True:
        while run:
            await change_status(bot, db)