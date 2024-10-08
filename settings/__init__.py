import discord
import os
from dotenv import load_dotenv
load_dotenv()

CMD_PREF = "r!"
INTENTS = discord.Intents.all()
BOT_TOKEN = os.getenv("TOKEN")

STATUS = discord.Status.idle
ACTIVITY = discord.Activity(type=discord.ActivityType.playing, name="DM me for support!")