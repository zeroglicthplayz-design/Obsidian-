import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import config

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = {}  # {guild_id: {user_id: [warnings]}}

    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(user="User to ban", reason="Reason for ban", delete_days="Days of messages to delete (0-7)")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided", delete_days: int = 0):
        if user.top_role >= interaction.user.top_role and interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message("❌ You cannot ban someone with a higher or equal role.", ephemeral=True)
            return

        try:
            # DM user
            embed = discord.Embed(
                title=f"🔨 Banned from {interaction.guild.name}",
                description=f"**Reason:** {reason}",
                color=config.ERROR_COLOR,
                timestamp=datetime.now()
            )
            await user.send(embed=embed)
        except:
            pass

        await user.ban(reason=reason, delete_message_days=delete_days)

        # Log
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🔨 User Banned",
                description=f"**User:** {user.mention} (`{user.id}`)",
                color=config.ERROR_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.add_field(name="Messages Deleted", value=f"{delete_days} days", inline=True)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"✅ {user.mention} has been banned. Reason: {reason}")

    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(user="User to kick", reason="Reason for kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        if user.top_role >= interaction.user.top_role and interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message("❌ You cannot kick someone with a higher or equal role.", ephemeral=True)
            return

        try:
            embed = discord.Embed(
                title=f"👢 Kicked from {interaction.guild.name}",
                description=f"**Reason:** {reason}",
                color=config.WARNING_COLOR,
                timestamp=datetime.now()
            )
            await user.send(embed=embed)
        except:
            pass

        await user.kick(reason=reason)

        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="👢 User Kicked",
                description=f"**User:** {user.mention} (`{user.id}`)",
                color=config.WARNING_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"✅ {user.mention} has been kicked. Reason: {reason}")

    @app_commands.command(name="mute", description="Timeout/mute a user")
    @app_commands.describe(user="User to mute", duration="Duration (e.g., 10m, 1h, 1d)", reason="Reason for mute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        if user.top_role >= interaction.user.top_role and interaction.user.id != config.OWNER_ID:
            await interaction.response.send_message("❌ You cannot mute someone with a higher or equal role.", ephemeral=True)
            return

        # Parse duration
        time_units = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
        unit = duration[-1].lower()
        if unit not in time_units:
            await interaction.response.send_message("❌ Invalid duration format. Use: `10m`, `1h`, `1d`, `1w`", ephemeral=True)
            return

        try:
            amount = int(duration[:-1])
        except ValueError:
            await interaction.response.send_message("❌ Invalid duration number.", ephemeral=True)
            return

        seconds = amount * time_units[unit]
        if seconds > 2419200:  # Max 4 weeks
            seconds = 2419200

        timeout_until = datetime.now() + timedelta(seconds=seconds)
        await user.timeout(timeout_until, reason=reason)

        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🔇 User Muted",
                description=f"**User:** {user.mention} (`{user.id}`)",
                color=config.WARNING_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=False)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"🔇 {user.mention} has been muted for {duration}. Reason: {reason}")

    @app_commands.command(name="unmute", description="Remove timeout from a user")
    @app_commands.describe(user="User to unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        await user.timeout(None)

        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🔊 User Unmuted",
                description=f"**User:** {user.mention} (`{user.id}`)",
                color=config.SUCCESS_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"🔊 {user.mention} has been unmuted.")

    @app_commands.command(name="warn", description="Warn a user")
    @app_commands.describe(user="User to warn", reason="Reason for warning")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        guild_id = interaction.guild.id
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user.id not in self.warnings[guild_id]:
            self.warnings[guild_id][user.id] = []

        warning = {
            'moderator': interaction.user.id,
            'reason': reason,
            'timestamp': datetime.now()
        }
        self.warnings[guild_id][user.id].append(warning)
        warn_count = len(self.warnings[guild_id][user.id])

        # DM user
        try:
            embed = discord.Embed(
                title=f"⚠️ Warning in {interaction.guild.name}",
                description=f"**Reason:** {reason}",
                color=config.WARNING_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Warning Count", value=f"{warn_count}/3")
            await user.send(embed=embed)
        except:
            pass

        # Auto-actions
        if warn_count >= 3:
            await user.kick(reason=f"Auto-kick: Reached {warn_count} warnings")
            action = f"Auto-kicked (reached {warn_count} warnings)"
        elif warn_count == 2:
            await user.timeout(datetime.now() + timedelta(hours=1), reason=f"Auto-mute: {warn_count} warnings")
            action = f"Auto-muted 1h (warning {warn_count}/3)"
        else:
            action = f"Warning {warn_count}/3"

        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="⚠️ User Warned",
                description=f"**User:** {user.mention} (`{user.id}`)",
                color=config.WARNING_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            embed.add_field(name="Action", value=action, inline=True)
            embed.add_field(name="Total Warnings", value=str(warn_count), inline=True)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"⚠️ {user.mention} has been warned. {action}")

    @app_commands.command(name="warnings", description="View a user's warnings")
    @app_commands.describe(user="User to check")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warnings_cmd(self, interaction: discord.Interaction, user: discord.Member):
        guild_id = interaction.guild.id
        user_warnings = self.warnings.get(guild_id, {}).get(user.id, [])

        if not user_warnings:
            await interaction.response.send_message(f"✅ {user.mention} has no warnings.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"⚠️ Warnings for {user}",
            description=f"Total: {len(user_warnings)}",
            color=config.WARNING_COLOR,
            timestamp=datetime.now()
        )

        for i, warn in enumerate(user_warnings[-5:], 1):  # Show last 5
            mod = self.bot.get_user(warn['moderator'])
            embed.add_field(
                name=f"Warning #{i}",
                value=f"**Reason:** {warn['reason']}\n**By:** {mod.mention if mod else 'Unknown'}\n**Date:** {warn['timestamp'].strftime('%Y-%m-%d')}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="clearwarns", description="Clear all warnings for a user")
    @app_commands.describe(user="User to clear warnings for")
    @app_commands.checks.has_permissions(administrator=True)
    async def clearwarns(self, interaction: discord.Interaction, user: discord.Member):
        guild_id = interaction.guild.id
        if guild_id in self.warnings and user.id in self.warnings[guild_id]:
            self.warnings[guild_id][user.id] = []

        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Warnings Cleared",
                description=f"**User:** {user.mention}",
                color=config.SUCCESS_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            await log_channel.send(embed=embed)

        await interaction.response.send_message(f"🗑️ All warnings cleared for {user.mention}.")

    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(amount="Number of messages to delete (1-100)", user="Optional: only delete from this user")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int, user: discord.Member = None):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        if user:
            deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.author.id == user.id)
        else:
            deleted = await interaction.channel.purge(limit=amount)

        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Messages Purged",
                description=f"**Channel:** {interaction.channel.mention}",
                color=config.WARNING_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Amount", value=str(len(deleted)), inline=True)
            if user:
                embed.add_field(name="Target User", value=user.mention, inline=True)
            await log_channel.send(embed=embed)

        await interaction.followup.send(f"🗑️ Deleted {len(deleted)} messages.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
