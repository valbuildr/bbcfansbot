import config
import aiohttp
import re
import datetime

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
        curdate = datetime.datetime.now()
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
        fetchdate = datetime.datetime(int(dsplit[0]), int(dsplit[1]), int(dsplit[2]))
        return fetchdate
    else:
        return "Incorrect Date"

 
async def resolve_sid(sid, db):
    for val in db['NitroSIDs']:
        if sid == val:
            parsedsid = db['NitroSIDs'][val]
        else:
            continue
    return parsedsid


async def get_schedule(db, sid, date=None, page=0):
    if not isinstance(date, datetime.datetime):
        # goes under a check to see if the inputted values are correct
        if not date: 
            parsed_date = datetime.datetime.now() # if date is none, give current day
        else:
            parsed_date = await verify_date(date) 
    # raises an exception if the function returns a string/error. 
    if isinstance(parsed_date, str):
        raise Exception(f"ERROR - {parsed_date}")
    else:
        parsedsid = await resolve_sid(sid, db)
        if not isinstance(parsedsid, str): raise Exception("ERROR - IncorrectSID") # raise error if sid given is incorrect
        # mixin titles is needed to get the proper related info about the scheduled broadcast's naming.
        params = { 
            'api_key': config.nitro, 'sid': parsedsid, 'mixin': 'titles', 
            'schedule_day': parsed_date.strftime("%Y-%m-%d"), 'page_size': 20, 'page': page
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
                            "items": [] 
                        }
                        # gets every item available in the first search query
                        try:
                            results = j['nitro']['results']['items']
                        # fails if there are total results, but there are no more items.
                        except:
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
                            starttime = int(datetime.datetime.fromisoformat(i['published_time']['start']).timestamp())
                            listing['items'].append({
                                "title": title['title'],
                                "pid": i['pid'],
                                "start": starttime
                            })
                        return listing
                        # fails if there are no results.
                    else:
                        raise Exception("ERROR - No Results")
                # raises a generic http status exception if it can't go any further.
                else:
                    raise Exception(f"ERROR - E{resp.status}")

