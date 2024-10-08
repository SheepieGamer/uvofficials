import discord
from discord.ext import commands
import settings
import pretty_help
import settings.utils as utils
from keep_alive import keep_alive
keep_alive()

class MyBot(commands.Bot):
    async def setup_hook(self):
        await utils.setup_database()
        print("Database setup complete.")
        await self.load_extension("cogs.database")
        await self.load_extension("cogs.modmail")
        await self.load_extension("cogs.admin_commands")
        await self.load_extension("cogs.owner")
        print("All cogs loaded.")
        print("------")
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")
        

bot = MyBot(
    command_prefix=settings.CMD_PREF, 
    intents=settings.INTENTS, 
    help_command=pretty_help.PrettyHelp(),
    status=settings.STATUS, 
    activity=discord.CustomActivity(name='DM me for support!' ,emoji='👑')
)


if __name__ == "__main__":
    bot.run(settings.BOT_TOKEN)