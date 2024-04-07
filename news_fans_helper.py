import discord, logging, traceback
from discord.ext import commands
from messageutils import autothread_from_message
import config

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

newsfansbotlog = logging.getLogger('discord.newsfansbot')

@bot.event
async def on_ready():
    newsfansbotlog.info(f'Logged in as {bot.user.name}.')

@bot.command()
async def ping(ctx: commands.Context):
    await ctx.send(content=f"My ping is {round(bot.latency * 1000)}ms!")

async def publish_to_announcement_channel(message: discord.Message):
    if message.channel.id == 1226649237899444284: # log
        send_to = discord.Webhook.from_url(url=config.nf_announcement_webhook_url, client=bot)

        files = []
        for attachment in message.attachments:
            await attachment.to_file()

        await send_to.send(content=message.content, files=files)

@bot.event
async def on_message(message: discord.Message):
    await autothread_from_message(message, newsfansbotlog)
    await publish_to_announcement_channel(message)
    await bot.process_commands(message)

bot.run(config.helper_discord_token)