import discord
from discord.ext import commands
from discord import app_commands
from .database import DatabaseCog

class AdminCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a user from the guild.")
    @app_commands.describe(member="The member to ban", reason="Reason for banning")
    async def ban_user(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Ban a user from the guild."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return
        
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"User {member.mention} has been banned.")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to ban this user.")
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to ban the user.")

    @app_commands.command(name="hire", description="Assign a role to a user and set member role.")
    @app_commands.describe(role="Role to assign", member="The member to receive the role")
    async def hire_role(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member):
        """Assign a role to a user and set member role."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        if role not in interaction.guild.roles:
            await interaction.response.send_message("The specified role does not exist.")
            return

        try:
            await member.add_roles(role)
            member_role_id = role.id
            await DatabaseCog.upsert_guild_info(self.bot, interaction.guild.id, interaction.guild.name, await DatabaseCog.get_modmail_channel_id(self.bot, interaction.guild.id), member_role_id)
            await interaction.response.send_message(f"User {member.mention} has been given the role {role.name}.")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to assign this role.")
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to assign the role.")

    @app_commands.command(name="fire", description="Remove all roles from a user except for the member role.")
    @app_commands.describe(member="The member to remove roles from")
    async def fire_user(self, interaction: discord.Interaction, member: discord.Member):
        """Remove all roles from a user except for the member role."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        member_role_id = await DatabaseCog.get_member_role(self.bot, interaction.guild.id)
        if not member_role_id:
            await interaction.response.send_message("Member role is not set for this server.")
            return

        member_role = discord.utils.get(interaction.guild.roles, id=member_role_id)
        if not member_role:
            await interaction.response.send_message("Member role not found.")
            return

        roles_to_remove = [role for role in member.roles if role.id != member_role_id and role.id != interaction.guild.default_role.id]

        if not roles_to_remove:
            await interaction.response.send_message(f"User {member.mention} has no roles to remove except for the member role.")
            return

        try:
            await member.remove_roles(*roles_to_remove)
            await interaction.response.send_message(f"User {member.mention} has been stripped of all roles except the member role.")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to remove roles from this user.")
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to remove roles.")

    @app_commands.command(name="setup-modmail", description="Set up the modmail channel for this guild.")
    @app_commands.describe(channel="The channel to use for modmail")
    async def setup_modmail_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = interaction.guild_id
        guild_name = interaction.guild.name

        await DatabaseCog.upsert_guild_info(self.bot, guild_id, guild_name, channel.id, None)

        await interaction.response.send_message(f"Modmail channel set to {channel.mention} for guild {guild_name}.")

    @app_commands.command(name="announce")
    async def announce_message(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await interaction.response.send_message(f"Successfully sent **{message}** in the {channel.mention} channel.", ephemeral=True)

    @app_commands.command(name="set-member-role", description="Set the member role for this guild.")
    @app_commands.describe(role="The role to set as the member role")
    async def set_member_role(self, interaction: discord.Interaction, role: discord.Role):
        """Set the member role for this guild."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        if role not in interaction.guild.roles:
            await interaction.response.send_message("The specified role does not exist.")
            return

        try:
            await DatabaseCog.upsert_guild_info(self.bot, interaction.guild.id, interaction.guild.name, await DatabaseCog.get_modmail_channel_id(self.bot, interaction.guild.id), role.id)
            await interaction.response.send_message(f"Member role has been set to {role.name}.")
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to set this role.")
        except discord.HTTPException:
            await interaction.response.send_message("An error occurred while trying to set the member role.")

async def setup(bot):
    await bot.add_cog(AdminCommandsCog(bot))