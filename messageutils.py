import discord, logging, traceback

def error_template(e):
    embed = discord.Embed(title=f"An error occurred!", colour=discord.Colour.red())
    embed.add_field(name="Error", value=f"{e}")
    return embed

async def autothread_from_message(message: discord.Message, log: logging.Logger):
    if message.channel.type != discord.ChannelType.news_thread and message.channel.type != discord.ChannelType.public_thread and message.channel.type != discord.ChannelType.private_thread:
        if message.channel.topic != None:
            if "autothread" in message.channel.topic:
                try:
                    t = await message.create_thread(name=f"{message.author.name}'s autothread")
                except discord.Forbidden as e:
                    log.error(traceback.format_exception(e))
                    msg = error_template(f"```\n{e}\n```")
                    await message.channel.send(embed=msg)
                except discord.HTTPException as e:
                    log.error(traceback.format_exception(e))
                    msg = error_template(f"```\n{e}\n```")
                    await message.channel.send(embed=msg)
                except discord.ValueError as e:
                    log.error(traceback.format_exception(e))
                    msg = error_template(f"```\n{e}\n```")
                    await message.channel.send(embed=msg)
                except:
                    log.error(traceback.format_exception(e))
                    msg = error_template(f"<:idk:1100473028485324801> Check bot logs.")
                    await message.channel.send(embed=msg)