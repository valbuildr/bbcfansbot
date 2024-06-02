from datetime import datetime
import discord, logging, traceback

def dt_to_timestamp(dt: datetime, f: str) -> str:
    """Converts a datetime object to a Discord timestamp.

    Args:
        dt (datetime): The datetime object to convert.
        format (str): The format that the timestamp should be in. See the Discord Developer Documentation for more info: https://discord.com/developers/docs/reference#message-formatting-timestamp-styles

    Returns:
        str: The timestamp.
    """    
    formats = ["d", "D", "t", "T", "f", "F", "R"]
    if f not in formats:
        return str(int(dt.timestamp()))
    else:
        return f"<t:{int(dt.timestamp())}:{f}>"

def error_template(e: str) -> discord.Embed:
    """The error template.

    Args:
        e (str): The error to put in the embed.

    Returns:
        discord.Embed: The embed to add to a message.
    """    
    embed = discord.Embed(title=f"An error occurred!", colour=discord.Colour.red())
    embed.add_field(name="Error", value=f"```\n{e}\n```")
    return embed