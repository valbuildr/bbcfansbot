import config
import aiohttp
import re
import datetime

async def verify_date(date):
    try:
        dsplit = re.split('-', date)
    except:
        return "splitFailure"
    if dsplit.len() > 3 or dsplit.len() < 3:
        return "notEnoughValues"

    # chaotic. but it's basically all the checks for 
    # year, month and day to ensure they are with the correct length 
    # and do not contain strings or any special contents.
    if isinstance(dsplit[0], int) and dsplit[0].len() == 4 and isinstance(dsplit[1], int) and dsplit[1].len() == 2 and isinstance(dsplit[2], int) and dsplit[2].len() == 2:
        curdate = datetime.datetime.now()
        # check if it's not higher than current year and if date is not not older than a year.
        if not dsplit[0] > curdate.year() and not dsplit[0] < curdate.year() - 1:
            fetchdate = "incorrectYear"
        # check if it's not newer than current month if it's in the same year. 
        if dsplit[0] == curdate.year() and dsplit[1] > curdate.month():
            fetchdate = "newerMonth"
        if dsplit[1] > 12:
            fetchdate = "incorrectMonth"
        # check if it's not newer than current day if it's in the same month and year. 
        if dsplit[0] == curdate.year() and dsplit[1] == curdate.month() and dsplit[2] > curdate.day(): 
            fetchdate = "newerDay"
        if dsplit[2] > 31:
            fetchdate = "incorrectDay"
        # else, return the correct datetime.
        fetchdate = datetime.datetime(dsplit[0], dsplit[1], dsplit[2])
        return fetchdate

 
async def resolve_sid(sid):
    match sid:
        case "wnews": parsedsid = "bbc_world_service"
        case "news": parsedsid = "bbc_news24"
        case "onesc": parsedsid = "bbc_one_scotland"
        case "onene": parsedsid = "bbc_one_north_east"
        case "onenw": parsedsid = "bbc_one_north_west"
        case "oneem": parsedsid = "bbc_one_east_midlands"
        case "onewm": parsedsid = "bbc_one_west_midlands"
        case "oneey": parsedsid = "bbc_one_east_yorkshire"
        case "oneld": parsedsid = "bbc_one_london"
        case "onese": parsedsid = "bbc_one_south_east"
        case "onesw": parsedsid = "bbc_one_south_west"
        case "oneni": parsedsid = "bbc_one_northern_ireland"
        case "onewa": parsedsid = "bbc_one_wales"
        case "onewe": parsedsid = "bbc_one_west"
        case "oneea": parsedsid = "bbc_one_east"
        case "oneso": parsedsid = "bbc_one_south"
        case "oneyo": parsedsid = "bbc_one_yorks"
        case "onewa": parsedsid = "bbc_one_wales"
        case "one": parsedsid = "bbc_one_hd"
        case "twoen": parsedsid = "bbc_two_england"
        case "twosc": parsedsid = "bbc_two_scotland"
        case "twoni": parsedsid = "bbc_two_northern_ireland_digital"
        case "twowa": parsedsid = "bbc_two_wales_digital"
        case "two": parsedsid = "bbc_two_hd"
        case "three": parsedsid = "bbc_three_hd"
        case "four": parsedsid = "bbc_four_hd"
        case "cbeebies": parsedsid = "cbeebies_hd"
        case "cbbc": parsedsid = "cbbc_hd"
        case "parliament": parsedsid = "bbc_parliament"
        case "alba": parsedsid = "bbc_alba_hd"
        case "scotland": parsedsid = "bbc_scotland_hd"
    return parsedsid


async def get_schedule(date=None, sid="one", page=1):
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
        parsedsid = await resolve_sid(sid)
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
                        if j['nitro']['results']['total'] > 0:
                            # gives the parsed sid information, and the date, alongside with the items.
                            listing = { 
                                "sid": parsedsid, 
                                "passedSid": sid,
                                "date": parsed_date.strftime("%Y-%m-%d"),
                                "items": [] 
                            }
                            # gets every item available in the first search query
                            for i in j['nitro']['results']['items']:
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
                            raise Exception("ERROR - NoResults")
                    # fails if the json can't be properly deserialized for some reason.
                    except Exception as err:
                        raise Exception(f"{err}")
                    except: 
                        raise Exception("ERROR - JSONDeserError")
                # raises a generic http status exception if it can't go any further.
                else:
                    raise Exception(f"ERROR - E{resp.status}")

