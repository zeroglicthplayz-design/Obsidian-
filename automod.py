import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import re
import config

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = {}  # {user_id: [(timestamp, channel_id)]}
        self.mention_cache = {}  # {user_id: [(timestamp, mention_count)]}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return

        content_lower = message.content.lower()
        user_id = message.author.id
        now = datetime.now()

        # Check account age
        account_age = (now - message.author.created_at).days
        if account_age < config.MIN_ACCOUNT_AGE:
            await message.delete()
            try:
                await message.author.send(
                    f"Your account must be at least {config.MIN_ACCOUNT_AGE} days old to chat in Obsidian Marketplace."
                )
            except:
                pass

            # Log
            log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
            if log_channel:
                embed = discord.Embed(
                    title="🚫 Account Age Kick",
                    description=f"{message.author.mention} was kicked - Account is {account_age} days old",
                    color=config.ERROR_COLOR,
                    timestamp=now
                )
                await log_channel.send(embed=embed)

            await message.author.kick(reason=f"Account too new ({account_age} days)")
            return

        # Check scam keywords (instant ban)
        for keyword in config.SCAM_KEYWORDS:
            if keyword in content_lower:
                await message.delete()

                # Try to ban
                try:
                    await message.author.ban(reason=f"AutoMod: Scam keyword detected - '{keyword}'")
                except:
                    pass

                # Log
                log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
                if log_channel:
                    embed = discord.Embed(
                        title="🔨 Auto Ban - Scam Detected",
                        description=f"**User:** {message.author.mention} (`{message.author.id}`)",
                        color=config.ERROR_COLOR,
                        timestamp=now
                    )
                    embed.add_field(name="Keyword", value=f"`{keyword}`", inline=True)
                    embed.add_field(name="Message", value=f"```{message.content[:500]}```", inline=False)
                    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                    await log_channel.send(embed=embed)

                # Send alert to channel
                alert = discord.Embed(
                    title="🔨 User Banned",
                    description=f"{message.author.mention} was automatically banned for scam content.",
                    color=config.ERROR_COLOR
                )
                await message.channel.send(embed=alert, delete_after=10)
                return

        # Check suspicious keywords (warn + delete)
        for keyword in config.SUSPICIOUS_KEYWORDS:
            if keyword in content_lower:
                await message.delete()

                # Warn user
                try:
                    await message.author.send(
                        f"Your message was deleted in **{message.guild.name}** for containing suspicious content."
                    )
                except:
                    pass

                # Log
                log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
                if log_channel:
                    embed = discord.Embed(
                        title="⚠️ Suspicious Content Deleted",
                        description=f"**User:** {message.author.mention}",
                        color=config.WARNING_COLOR,
                        timestamp=now
                    )
                    embed.add_field(name="Keyword", value=f"`{keyword}`", inline=True)
                    embed.add_field(name="Message", value=f"```{message.content[:500]}```", inline=False)
                    await log_channel.send(embed=embed)
                return

        # Check invite links
        invite_pattern = r'discord\.gg/[a-zA-Z0-9]+|discord\.com/invite/[a-zA-Z0-9]+'
        if re.search(invite_pattern, content_lower):
            # Check if user has manage_channels permission (staff)
            if not message.author.guild_permissions.manage_channels:
                await message.delete()

                # Warn
                try:
                    await message.author.send(
                        f"Invite links are not allowed in **{message.guild.name}**."
                    )
                except:
                    pass

                # Log
                log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
                if log_channel:
                    embed = discord.Embed(
                        title="🔗 Invite Link Deleted",
                        description=f"**User:** {message.author.mention}",
                        color=config.WARNING_COLOR,
                        timestamp=now
                    )
                    embed.add_field(name="Message", value=f"```{message.content[:500]}```", inline=False)
                    await log_channel.send(embed=embed)
                return

        # Check @everyone/@here by non-staff
        if '@everyone' in message.content or '@here' in message.content:
            if not message.author.guild_permissions.mention_everyone:
                await message.delete()

                # Log
                log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
                if log_channel:
                    embed = discord.Embed(
                        title="📢 Mass Mention Blocked",
                        description=f"**User:** {message.author.mention}",
                        color=config.WARNING_COLOR,
                        timestamp=now
                    )
                    await log_channel.send(embed=embed)
                return

        # Check mass mentions
        mention_count = len(message.mentions) + len(message.role_mentions)
        if mention_count >= config.MENTION_LIMIT:
            if not message.author.guild_permissions.mention_everyone:
                await message.delete()

                # Add to mention cache for potential mute
                if user_id not in self.mention_cache:
                    self.mention_cache[user_id] = []
                self.mention_cache[user_id].append((now, mention_count))

                # Clean old entries
                self.mention_cache[user_id] = [
                    (t, c) for t, c in self.mention_cache[user_id]
                    if (now - t).seconds < 60
                ]

                # If 3+ violations in 1 minute, mute
                if len(self.mention_cache[user_id]) >= 3:
                    muted_role = message.guild.get_role(config.MUTED_ROLE)
                    if muted_role:
                        await message.author.add_roles(muted_role, reason="AutoMod: Mass mention spam")
                        await asyncio.sleep(600)  # 10 min mute
                        await message.author.remove_roles(muted_role)

                # Log
                log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
                if log_channel:
                    embed = discord.Embed(
                        title="📢 Mass Mention Deleted",
                        description=f"**User:** {message.author.mention} mentioned {mention_count} users/roles",
                        color=config.WARNING_COLOR,
                        timestamp=now
                    )
                    await log_channel.send(embed=embed)
                return

        # Anti-spam check
        if user_id not in self.message_cache:
            self.message_cache[user_id] = []

        self.message_cache[user_id].append((now, message.channel.id))

        # Clean old messages
        self.message_cache[user_id] = [
            (t, c) for t, c in self.message_cache[user_id]
            if (now - t).seconds < config.SPAM_INTERVAL
        ]

        # Check spam threshold
        if len(self.message_cache[user_id]) >= config.SPAM_THRESHOLD:
            # Delete recent messages from this user
            deleted = 0
            async for msg in message.channel.history(limit=50):
                if msg.author.id == user_id and (now - msg.created_at).seconds < 10:
                    await msg.delete()
                    deleted += 1

            # Mute user
            muted_role = message.guild.get_role(config.MUTED_ROLE)
            if muted_role:
                await message.author.add_roles(muted_role, reason="AutoMod: Spam detected")
                await asyncio.sleep(600)  # 10 min mute
                await message.author.remove_roles(muted_role)

            # Log
            log_channel = message.guild.get_channel(config.MOD_LOG_CHANNEL)
            if log_channel:
                embed = discord.Embed(
                    title="🚫 Spam Detected",
                    description=f"**User:** {message.author.mention}",
                    color=config.ERROR_COLOR,
                    timestamp=now
                )
                embed.add_field(name="Messages Deleted", value=str(deleted), inline=True)
                embed.add_field(name="Action", value="10 minute mute", inline=True)
                await log_channel.send(embed=embed)

            # Clear cache
            self.message_cache[user_id] = []

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Check edited messages too"""
        await self.on_message(after)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
