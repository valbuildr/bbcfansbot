import aiohttp, re, math, messageutils
from datetime import datetime
from dotenv import dotenv_values

config = dotenv_values(".env")

class Service:
    bbc_world_news_europe = "bbc_world_news_europe"
    bbc_world_news_middle_east = "bbc_world_news_middle_east"
    bbc_world_news_north_america = "bbc_world_news_north_america"
    bbc_world_news_asia_pacific = "bbc_world_news_asia_pacific"
    bbc_world_news_south_asia = "bbc_world_news_south_asia"
    bbc_world_news_latin_america = "bbc_world_news_latin_america"
    bbc_news24 = "bbc_news24"
    bbc_one_scotland = "bbc_one_scotland"
    bbc_one_north_east = "bbc_one_north_east"
    bbc_one_north_west = "bbc_one_north_west"
    bbc_one_east_midlands = "bbc_one_east_midlands"
    bbc_one_west_midlands = "bbc_one_west_midlands"
    bbc_one_east_yorkshire = "bbc_one_east_yorkshire"
    bbc_one_london = "bbc_one_london"
    bbc_one_south_east = "bbc_one_south_east"
    bbc_one_south_west = "bbc_one_south_west"
    bbc_one_northern_ireland = "bbc_one_northern_ireland"
    bbc_one_wales = "bbc_one_wales"
    bbc_one_west = "bbc_one_west"
    bbc_one_east = "bbc_one_east"
    bbc_one_south = "bbc_one_south"
    bbc_one_yorks = "bbc_one_yorks"
    bbc_one_hd = "bbc_one_hd"
    bbc_two_england = "bbc_two_england"
    bbc_two_scotland = "bbc_two_scotland"
    bbc_two_northern_ireland_digital = "bbc_two_northern_ireland_digital"
    bbc_two_wales_digital = "bbc_two_wales_digital"
    bbc_two_hd = "bbc_two_hd"
    bbc_three_hd = "bbc_three_hd"
    bbc_four_hd = "bbc_four_hd"
    cbeebies_hd = "cbeebies_hd"
    cbbc_hd = "cbbc_hd"
    bbc_parliament = "bbc_parliament"
    bbc_alba_hd = "bbc_alba_hd"
    bbc_scotland_hd = "bbc_scotland_hd"

nitroSIDs = {
    "region": [
        "Northern Ireland",
        "Scotland",
        "Wales",
        "South",
        "East Midlands",
        "West Midlands",
        "East Yorkshire",
        "North West",
        "North East",
        "London",
        "Sourth East",
        "South West",
        "West",
        "East",
        "South",
        "Yorks"
    ],
    "channels": [
        "BBC News [UK]",
        "BBC News [Europe]",
        "BBC News [Latin America]",
        "BBC News [North America]",
        "BBC News [South Asia]",
        "BBC News [Asia Pacific]",
        "BBC News [Middle East]",
        "BBC One",
        "BBC Two",
        "BBC Three",
        "BBC Four",
        "Cbeebies",
        "CBBC",
        "BBC Parliament",
        "BBC Alba",
        "BBC Scotland"
    ],
    "BBC News [Europe]": Service.bbc_world_news_europe,
    "BBC News [Middle East]": Service.bbc_world_news_middle_east,
    "BBC News [North America]": Service.bbc_world_news_north_america,
    "BBC News [Asia Pacific]": Service.bbc_world_news_asia_pacific,
    "BBC News [South Asia]": Service.bbc_world_news_south_asia,
    "BBC News [Latin America]": Service.bbc_world_news_latin_america,
    "BBC News [UK]": Service.bbc_news24,
    "BBC One Scotland": Service.bbc_one_scotland,
    "BBC One North East": Service.bbc_one_north_east,
    "BBC One North West": Service.bbc_one_north_west,
    "BBC One East Midlands": Service.bbc_one_east_midlands,
    "BBC One West Midlands": Service.bbc_one_west_midlands,
    "BBC One East Yorkshire": Service.bbc_one_east_yorkshire,
    "BBC One London": Service.bbc_one_london,
    "BBC One South East": Service.bbc_one_south_east,
    "BBC One South West": Service.bbc_one_south_west,
    "BBC One Northern Ireland": Service.bbc_one_northern_ireland,
    "BBC One Wales": Service.bbc_one_wales,
    "BBC One West": Service.bbc_one_west,
    "BBC One East": Service.bbc_one_east,
    "BBC One South": Service.bbc_one_south,
    "BBC One Yorks": Service.bbc_one_yorks,
    "BBC One": Service.bbc_one_hd,
    "BBC Two England": Service.bbc_two_england,
    "BBC Two Scotland": Service.bbc_two_scotland,
    "BBC Two Northern Ireland": Service.bbc_two_northern_ireland_digital,
    "BBC Two Wales": Service.bbc_two_wales_digital,
    "BBC Two": Service.bbc_two_hd,
    "BBC Three": Service.bbc_three_hd,
    "BBC Four": Service.bbc_four_hd,
    "CBeebies": Service.cbeebies_hd,
    "CBBC": Service.cbbc_hd,
    "BBC Parliament": Service.bbc_parliament,
    "BBC Alba": Service.bbc_alba_hd,
    "BBC Scotland": Service.bbc_scotland_hd
}

async def verify_date(date):
    try:
        dsplit = re.split('-', date)
    except:
        return "Split Failure"
    if len(dsplit) > 3 or len(dsplit) < 3:
        return "Not Enough Values (input must be of format YYYY-MM-DD)"
    year, month, day = int(dsplit[0]), int(dsplit[1]), int(dsplit[2])
    # chaotic. but it's basically all the checks for 
    # year, month and day to ensure they are with the correct length 
    # and do not contain strings or any special contents.
    if isinstance(dsplit[0], str) and len(dsplit[0]) == 4 and isinstance(dsplit[1], str) and len(dsplit[1]) == 2 and isinstance(dsplit[2], str) and len(dsplit[2]) == 2:
        curdate = datetime.now()
        # check if it's not higher than current year and if date is not not older than two years.
        if year > curdate.year or year < curdate.year - 2:
            return "Year higher, or older than accepted"
        # check if it's not newer than current month if it's in the same year, but only if the current day gap is lower than 26 
        if year == curdate.year and curdate.day < 26 and month > curdate.month:
            return "Month newer than current"
        if month > 12:
            return "Incorrect Month"
        # check if it's not newer than 5 days ahead if it's in the same month and year. 
        if year == curdate.year and month == curdate.month and day > curdate.day + 5: 
            fetchdate = "Day newer than accepted"
            return fetchdate
        if day > 31 or month == 2 and day > 28:
            return "incorrectDay"
        # else, return the correct datetime.
        fetchdate = datetime(int(dsplit[0]), int(dsplit[1]), int(dsplit[2]))
        return fetchdate
    else:
        return "Incorrect Date"

 
async def resolve_sid(sid):
    for val in nitroSIDs:
        if sid.lower() == val.lower(): # lower assures case-insensitive querying
            parsedsid = nitroSIDs[val]
            return parsedsid
        else:
            continue

async def get_schedule(sid, date=None, page=0):
    if not isinstance(date, datetime):
        # goes under a check to see if the inputted values are correct
        if not date: 
            parsed_date = datetime.now() # if date is none, give current day
        else:
            parsed_date = await verify_date(date) 
    # raises an exception if the function returns a string/error. 
    if isinstance(parsed_date, str):
        raise Exception(f"ERROR - {parsed_date}")
    else:
        parsedsid = await resolve_sid(sid)
        if not isinstance(parsedsid, str): raise Exception("ERROR - Incorrect Channel.") # raise error if sid given is incorrect
        # mixin titles is needed to get the proper related info about the scheduled broadcast's naming.
        params = { 
            'api_key': config["NITRO_SECRET"],
            'sid': parsedsid,
            'mixin': 'titles', 
            'schedule_day': parsed_date.strftime("%Y-%m-%d"),
            'page_size': 10,
            'page': page
        }
        # nitro uses xml by default, so we need to specify that it must only accept json for it to return into such syntax.
        async with aiohttp.ClientSession() as sesh:
            async with sesh.get("https://programmes.api.bbc.com/nitro/api/broadcasts", params=params,
            headers={'Accept': 'application/json'}) as resp:
                if resp.status >= 200 and not resp.status > 299:
                    try: 
                        j = await resp.json()
                    except: 
                        raise Exception("ERROR - JSONDeserError")

                    if j['nitro']['results']['total'] > 0:
                        # gives the parsed sid information, and the date, alongside with the items.
                        listing = { 
                            "passedSid": sid,
                            "date": parsed_date.strftime("%Y-%m-%d"),
                            "isToday": False,
                            "items": [],
                            "total_items": j['nitro']['results']['total']
                        }
                        # checks if schedule is from today
                        if listing['date'] == datetime.now().strftime("%Y-%m-%d"):
                            listing['isToday'] = True
                        # gets every item available in the first search query
                        try:
                            results = j['nitro']['results']['items']
                        # fails if there are total results, but there are no more items.
                        except:
                            if math.ceil(j['nitro']['results']['total'] / 10) < page:
                                raise Exception("ERROR - Page doesnt exist.")
                            else:
                                raise Exception("ERROR - No Items")
                        for i in results:
                            # not always a program will return it's title by the brand 
                            # (nor by the series) value, so we add a failsafe to ensure it'll get it from the one available.
                            try:
                                title = i['ancestors_titles']['brand']
                            except:
                                try:
                                    title = i['ancestors_titles']['series']
                                except:
                                    title = i['ancestors_titles']['episode']
                            # converts to unix
                            starttime = messageutils.dt_to_timestamp(datetime.fromisoformat(i['published_time']['start']), "z")
                            endtime = messageutils.dt_to_timestamp(datetime.fromisoformat(i['published_time']['end']), "z")
                            listing['items'].append({
                                "title": title['title'],
                                "pid": i['pid'],
                                "time": [starttime, endtime]
                            })
                        return listing
                        # fails if there are no results.
                    else:
                        raise Exception("ERROR - No Results")
                # raises a generic http status exception if it can't go any further.
                else:
                    raise Exception(f"ERROR - E{resp.status}")

async def get_link(sid, date=None):
    if not isinstance(date, datetime):
        if not date:
            parsed_date = datetime.now()
        else:
            parsed_date = await verify_date(date)
        
    if isinstance(parsed_date, str):
        raise Exception(f"ERROR - {parsed_date}")
    else:
        sid = await resolve_sid(sid)

        links = {
            "bbc_world_news_europe": "https://www.bbc.co.uk/schedules/p00fzl9j", # news, europe
            "bbc_world_news_north_america": "https://www.bbc.co.uk/schedules/p00fzl9m", # news, na
            "bbc_world_news_latin_america": "https://www.bbc.co.uk/schedules/p00fzl9k", # news, latam
            "bbc_world_news_middle_east": "https://www.bbc.co.uk/schedules/p00fzl9l", # news, m-east
            "bbc_world_news_asia_pacific": "https://www.bbc.co.uk/schedules/p00fzl9h", # news, asia pacific
            "bbc_world_news_south_asia": "https://www.bbc.co.uk/schedules/p00fzl9n", # news, south asia
            "bbc_news24": "https://www.bbc.co.uk/schedules/p01kv924", # news, uk hd
            "bbc_one_scotland": "https://www.bbc.co.uk/schedules/p013blmc", # one, scotland hd
            "bbc_one_north_east": "https://www.bbc.co.uk/schedules/p00fzl6r", # one, north east & cumbria hd
            "bbc_one_north_west": "https://www.bbc.co.uk/schedules/p09v556j", # one, north west hd
            "bbc_one_east_midlands": "https://www.bbc.co.uk/schedules/p09v5563", # one, east midlands hd
            "bbc_one_west_midlands": "https://www.bbc.co.uk/schedules/p09v557h", # one, west midlands hd
            "bbc_one_east_yorkshire": "https://www.bbc.co.uk/schedules/p09v5567", # one, yorks & lincs hd
            "bbc_one_london": "https://www.bbc.co.uk/schedules/p09v556b", # one, london hd
            "bbc_one_south_east": "https://www.bbc.co.uk/schedules/p09v5570", # one, south east hd
            "bbc_one_south_west": "https://www.bbc.co.uk/schedules/p09v5575", # one, south west hd
            "bbc_one_northern_ireland": "https://www.bbc.co.uk/schedules/p00zskxc", # one, northern ireland hd
            "bbc_one_wales": "https://www.bbc.co.uk/schedules/p013bkc7", # one, wales hd
            "bbc_one_west": "https://www.bbc.co.uk/schedules/p09v557b", # one, west hd
            "bbc_one_east": "https://www.bbc.co.uk/schedules/p09v5561", # one, east hd
            "bbc_one_south": "https://www.bbc.co.uk/schedules/p09v556t", # one, south hd
            "bbc_one_yorks": "https://www.bbc.co.uk/schedules/p09v557j", # one, yorkshire hd
            "bbc_one_hd": "https://www.bbc.co.uk/schedules/p00fzl6n", # one, hd
            "bbc_two_england": "https://www.bbc.co.uk/schedules/p00fzl97", # two, england
            "bbc_two_scotland": "https://www.bbc.co.uk/schedules/p015pksy", # two, hd (cant find scotland)
            "bbc_two_northern_ireland_digital": "https://www.bbc.co.uk/schedules/p06ngcbm", # two, northern ireland hd
            "bbc_two_wales_digital": "https://www.bbc.co.uk/schedules/p06ngc52", # two, wales hd
            "bbc_two_hd": "https://www.bbc.co.uk/schedules/p015pksy", # two, hd
            "bbc_three_hd": "https://www.bbc.co.uk/schedules/p01kv7xf", # three, hd
            "bbc_four_hd": "https://www.bbc.co.uk/schedules/p01kv81d", # four, hd
            "cbeebies_hd": "https://www.bbc.co.uk/schedules/p01kv8yz", # cbeebies, hd
            "cbbc_hd": "https://www.bbc.co.uk/schedules/p01kv86b", # cbbc, hd
            "bbc_parliament": "https://www.bbc.co.uk/schedules/p09vztlr", # parliament, hd
            "bbc_alba_hd": "https://www.bbc.co.uk/schedules/p09vztlq", # alba, hd
            "bbc_scotland_hd": "https://www.bbc.co.uk/schedules/p06p396y" # scotland, hd
        }

        return links[sid]
