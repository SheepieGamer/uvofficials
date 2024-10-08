import discord
from discord.ext import commands
import asyncio
from .database import DatabaseCog

class ModmailCog(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.user_message_count = {}
        self.user_guild_choice = {}

    async def get_member_by_username(self, guild: discord.Guild, username: str):
        for member in guild.members:
            if member.name.lower() == username.lower():
                return member
        return None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            user_id = message.author.id

            if user_id not in self.user_message_count:
                self.user_message_count[user_id] = 0
            if user_id not in self.user_guild_choice:
                self.user_guild_choice[user_id] = None

            self.user_message_count[user_id] += 1
            mutual_guilds = [guild for guild in self.bot.guilds if guild.get_member(user_id)]

            if len(mutual_guilds) > 1:
                if self.user_message_count[user_id] % 15 == 1 or not self.user_guild_choice[user_id]:
                    guild_names = [f"{i+1}. {guild.name}" for i, guild in enumerate(mutual_guilds)]
                    await message.channel.send(
                        "I found multiple servers we both belong to. Please reply with the number of the server you'd like to contact:\n" +
                        "\n".join(guild_names)
                    )

                    def check(m):
                        return m.author == message.author and m.channel == message.channel

                    try:
                        response = await self.bot.wait_for('message', check=check, timeout=60.0)
                        choice = int(response.content.strip()) - 1
                        if 0 <= choice < len(mutual_guilds):
                            chosen_guild = mutual_guilds[choice]
                            self.user_guild_choice[user_id] = chosen_guild
                        else:
                            await message.channel.send("Invalid choice. Please try again next time.")
                            return
                    except (ValueError, asyncio.TimeoutError):
                        await message.channel.send("No valid response received. Please try again next time.")
                        return

                chosen_guild = self.user_guild_choice[user_id]

            elif len(mutual_guilds) == 1:
                chosen_guild = mutual_guilds[0]
                self.user_guild_choice[user_id] = chosen_guild

            else:
                await message.channel.send("We don't share any servers. Please contact support.")
                return

            modmail_channel_id = await DatabaseCog.get_modmail_channel_id(self.bot, chosen_guild.id)
            if modmail_channel_id:
                modmail_channel = self.bot.get_channel(modmail_channel_id)
                if modmail_channel:
                    if message.attachments:
                        files = [await file.to_file() for file in message.attachments]
                        await modmail_channel.send(f"**{message.author}**: {message.content}", files=files)
                    else:
                        await modmail_channel.send(f"**{message.author}**: {message.content}")
                return

        elif isinstance(message.channel, discord.TextChannel):
            guild = message.guild
            if not guild:
                await message.channel.send("Guild not found.")
                return

            modmail_channel_id = await DatabaseCog.get_modmail_channel_id(self.bot, guild.id)
            if modmail_channel_id != message.channel.id:
                return

            if message.mentions:
                member = message.mentions[0]
            else:
                parts = message.content.split(' ', 1)
                if len(parts) > 1:
                    username = parts[0].strip('@')
                    member = await self.get_member_by_username(guild, username)
                else:
                    member = None

            if member:
                content = message.content
                if message.attachments:
                    files = [await file.to_file() for file in message.attachments]
                    index = content.find(" ")
                    mod_message = content[index:] if index != -1 else "."
                    await member.send(f"**{message.author}**: {mod_message}", files=files)
                else:
                    index = content.find(" ")
                    mod_message = content[index:] if index != -1 else "."
                    await member.send(f"**{message.author}**: {mod_message}")

            else:
                await message.channel.send("""## Please specify the user you want to reply to.
                ### Example:
    User Message: ``user123: I need help!!!``
    Your response: ``user123 what do you need help with?`` (do __NOT__ @mention them)

    :warning: **You must have a space between the ``user123`` and your message.** :warning:
                                           
    If you are upload an image, follow this: ``user123 .`` and then attach the image/file


    The specified user could not be found. Make sure you have typed their username correctly.""")


async def setup(bot: commands.Bot):
    await bot.add_cog(ModmailCog(bot))