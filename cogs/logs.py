import discord
from discord.ext import commands
from datetime import datetime
import config

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        log_channel = message.guild.get_channel(config.MESSAGE_LOG_CHANNEL)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Message Deleted",
            description=f"**Author:** {message.author.mention} (`{message.author.id}`)",
            color=config.ERROR_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        if message.content:
            embed.add_field(name="Content", value=message.content[:1024], inline=False)
        if message.attachments:
            embed.add_field(name="Attachments", value=f"{len(message.attachments)} file(s)", inline=True)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content == after.content:
            return

        log_channel = before.guild.get_channel(config.MESSAGE_LOG_CHANNEL)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Message Edited",
            description=f"**Author:** {before.author.mention} (`{before.author.id}`)",
            color=config.WARNING_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Jump", value=f"[Go to message]({after.jump_url})", inline=True)
        embed.add_field(name="Before", value=before.content[:1024] or "*(empty)*", inline=False)
        embed.add_field(name="After", value=after.content[:1024] or "*(empty)*", inline=False)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        log_channel = member.guild.get_channel(config.MOD_LOG_CHANNEL)
        if not log_channel:
            return

        account_age = (datetime.now() - member.created_at).days

        embed = discord.Embed(
            title="Member Joined",
            description=f"{member.mention} (`{member.id}`)",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Account Age", value=f"{account_age} days", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Member Count", value=f"{member.guild.member_count}", inline=True)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        log_channel = member.guild.get_channel(config.MOD_LOG_CHANNEL)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Member Left",
            description=f"{member.mention} (`{member.id}`)",
            color=config.ERROR_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:R>" if member.joined_at else "Unknown", inline=True)
        embed.add_field(name="Member Count", value=f"{member.guild.member_count}", inline=True)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        log_channel = after.guild.get_channel(config.MOD_LOG_CHANNEL)
        if not log_channel:
            return

        # Check role changes
        if before.roles != after.roles:
            added = [r for r in after.roles if r not in before.roles and r.name != "@everyone"]
            removed = [r for r in before.roles if r not in after.roles and r.name != "@everyone"]

            if added or removed:
                embed = discord.Embed(
                    title="Role Update",
                    description=f"{after.mention} (`{after.id}`)",
                    color=config.INFO_COLOR,
                    timestamp=datetime.now()
                )
                if added:
                    embed.add_field(name="Added", value=", ".join([r.mention for r in added]), inline=False)
                if removed:
                    embed.add_field(name="Removed", value=", ".join([r.mention for r in removed]), inline=False)

                await log_channel.send(embed=embed)

        # Check nickname changes
        if before.nick != after.nick:
            embed = discord.Embed(
                title="Nickname Changed",
                description=f"{after.mention} (`{after.id}`)",
                color=config.INFO_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Before", value=before.nick or "None", inline=True)
            embed.add_field(name="After", value=after.nick or "None", inline=True)

            await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        log_channel = channel.guild.get_channel(config.MOD_LOG_CHANNEL)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Channel Created",
            description=f"{channel.mention} (`{channel.id}`)",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Type", value=str(channel.type), inline=True)
        if channel.category:
            embed.add_field(name="Category", value=channel.category.name, inline=True)

        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        log_channel = channel.guild.get_channel(config.MOD_LOG_CHANNEL)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Channel Deleted",
            description=f"#{channel.name} (`{channel.id}`)",
            color=config.ERROR_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Type", value=str(channel.type), inline=True)
        if channel.category:
            embed.add_field(name="Category", value=channel.category.name, inline=True)

        await log_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logs(bot))
