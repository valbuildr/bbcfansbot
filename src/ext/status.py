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
    # discord.Activity(name="CBBC", type=discord.ActivityType.watching),
    # discord.Activity(name="CBeebies", type=discord.ActivityType.watching),
    discord.Activity(name="BBC News", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Parliament", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Alba", type=discord.ActivityType.watching),
    discord.Activity(name="S4C", type=discord.ActivityType.watching),
    discord.Activity(name="BBC Scotland", type=discord.ActivityType.watching),
]

async def change_status(bot: commands.Bot) -> None:
    """Change the bot's status.

    Args:
        bot (commands.Bot): The bot to change status.
    """    
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

async def task(bot: commands.Bot) -> None:
    """The status task.

    Args:
        bot (commands.Bot): The bot that should change status.
    """    
    while True:
        while run:
            await change_status(bot)
            await asyncio.sleep(60) # run every minute