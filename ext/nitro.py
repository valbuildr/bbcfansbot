import config, aiohttp, re, math, messageutils
from datetime import datetime

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

 
async def resolve_sid(sid, db):
    for val in db['NitroSIDs']:
        if sid.lower() == val.lower(): # lower assures case-insensitive querying
            parsedsid = db['NitroSIDs'][val]
            return parsedsid
        else:
            continue

async def get_schedule(db, sid, date=None, page=0):
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
        parsedsid = await resolve_sid(sid, db)
        if not isinstance(parsedsid, str): raise Exception("ERROR - Incorrect Channel.") # raise error if sid given is incorrect
        # mixin titles is needed to get the proper related info about the scheduled broadcast's naming.
        params = { 
            'api_key': config.nitro_secret,
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

async def get_link(db, sid, date=None):
    if not isinstance(date, datetime):
        if not date:
            parsed_date = datetime.now()
        else:
            parsed_date = await verify_date(date)
        
    if isinstance(parsed_date, str):
        raise Exception(f"ERROR - {parsed_date}")
    else:
        sid = await resolve_sid(sid, db)

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
