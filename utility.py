import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import sqlite3
import config

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS vouches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receiver_id INTEGER,
            giver_id INTEGER,
            message TEXT,
            timestamp TEXT
        )""")

        conn.commit()
        conn.close()

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: **{latency}ms**",
            color=config.SUCCESS_COLOR if latency < 200 else config.WARNING_COLOR if latency < 500 else config.ERROR_COLOR
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="User to get info about")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        embed = discord.Embed(
            title=f"User Info - {user}",
            color=config.INFO_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(name="ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="Nickname", value=user.nick or "None", inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)

        embed.add_field(name="Account Created", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Joined Server", value=f"<t:{int(user.joined_at.timestamp())}:R>" if user.joined_at else "Unknown", inline=True)

        roles = [r.mention for r in user.roles if r.name != "@everyone"]
        embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles[:10]) or "None", inline=False)

        if user.premium_since:
            embed.add_field(name="Booster Since", value=f"<t:{int(user.premium_since.timestamp())}:R>", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Get information about the server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild

        embed = discord.Embed(
            title=f"{guild.name} Info",
            color=config.INFO_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)

        embed.add_field(name="ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)

        embed.add_field(name="Members", value=f"{guild.member_count}", inline=True)
        embed.add_field(name="Channels", value=f"{len(guild.channels)}", inline=True)
        embed.add_field(name="Roles", value=f"{len(guild.roles)}", inline=True)

        embed.add_field(name="Boost Level", value=f"Level {guild.premium_tier}", inline=True)
        embed.add_field(name="Boosts", value=f"{guild.premium_subscription_count}", inline=True)
        embed.add_field(name="Emojis", value=f"{len(guild.emojis)}", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="vouch", description="Leave a vouch/review for a user")
    @app_commands.describe(user="User to vouch for", message="Your review/message")
    async def vouch(self, interaction: discord.Interaction, user: discord.Member, message: str):
        if user.id == interaction.user.id:
            await interaction.response.send_message("You can't vouch for yourself!", ephemeral=True)
            return

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("INSERT INTO vouches (receiver_id, giver_id, message, timestamp) VALUES (?, ?, ?, ?)",
                  (user.id, interaction.user.id, message, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        # Send to vouch channel
        vouch_channel = interaction.guild.get_channel(config.VOUCH_CHANNEL)
        if vouch_channel:
            embed = discord.Embed(
                title="New Vouch!",
                description=f"{interaction.user.mention} vouched for {user.mention}",
                color=config.SUCCESS_COLOR,
                timestamp=datetime.now()
            )
            embed.add_field(name="Review", value=message, inline=False)
            await vouch_channel.send(embed=embed)

        await interaction.response.send_message(f"You vouched for {user.mention}!")

    @app_commands.command(name="vouches", description="View vouches for a user")
    @app_commands.describe(user="User to check vouches for")
    async def vouches(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT giver_id, message, timestamp FROM vouches WHERE receiver_id = ? ORDER BY timestamp DESC",
                  (user.id,))
        results = c.fetchall()
        conn.close()

        if not results:
            await interaction.response.send_message(f"{user.mention} has no vouches yet.", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"Vouches for {user}",
            description=f"Total: **{len(results)}** vouches",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        for giver_id, message, timestamp in results[:5]:
            giver = self.bot.get_user(giver_id)
            giver_name = giver.name if giver else f"User {giver_id}"
            date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')
            embed.add_field(
                name=f"From {giver_name} | {date}",
                value=message[:1024],
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="announce", description="Send an announcement (Admin only)")
    @app_commands.describe(channel="Channel to send announcement", title="Announcement title", message="Announcement content", ping="Ping @everyone?")
    @app_commands.checks.has_permissions(administrator=True)
    async def announce(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, message: str, ping: bool = False):
        embed = discord.Embed(
            title=title,
            description=message,
            color=config.EMBED_COLOR,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Announced by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        content = "@everyone" if ping else None
        await channel.send(content=content, embed=embed)

        await interaction.response.send_message(f"Announcement sent to {channel.mention}!")

    @app_commands.command(name="embed", description="Create a custom embed (Admin only)")
    @app_commands.describe(channel="Channel to send embed", title="Embed title", description="Embed description", color="Hex color (e.g., #5865F2)")
    @app_commands.checks.has_permissions(administrator=True)
    async def embed(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, description: str, color: str = "#5865F2"):
        try:
            color_int = int(color.lstrip('#'), 16)
        except:
            color_int = config.EMBED_COLOR

        embed = discord.Embed(
            title=title,
            description=description,
            color=color_int,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"By {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await channel.send(embed=embed)
        await interaction.response.send_message(f"Embed sent to {channel.mention}!")

    @app_commands.command(name="say", description="Make the bot say something (Admin only)")
    @app_commands.describe(channel="Channel to send message", message="Message content")
    @app_commands.checks.has_permissions(administrator=True)
    async def say(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await interaction.response.send_message(f"Message sent to {channel.mention}!")

    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(user="User to get avatar from")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        embed = discord.Embed(
            title=f"{user}'s Avatar",
            color=config.INFO_COLOR
        )
        embed.set_image(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="poll", description="Create a poll")
    @app_commands.describe(question="Poll question", option1="First option", option2="Second option", option3="Third option (optional)", option4="Fourth option (optional)")
    async def poll(self, interaction: discord.Interaction, question: str, option1: str, option2: str, option3: str = None, option4: str = None):
        options = [o for o in [option1, option2, option3, option4] if o]
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

        embed = discord.Embed(
            title="Poll",
            description=f"**{question}**",
            color=config.INFO_COLOR,
            timestamp=datetime.now()
        )

        for i, option in enumerate(options):
            embed.add_field(name=f"{emojis[i]} {option}", value="Vote below!", inline=False)

        embed.set_footer(text=f"Poll by {interaction.user}")

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        for i in range(len(options)):
            await message.add_reaction(emojis[i])


    @commands.command(name="sync")
    @commands.is_owner()
    async def sync_text(self, ctx):
        """Manual sync slash commands via text command"""
        import config
        guild = discord.Object(id=config.GUILD_ID)

        self.bot.tree.copy_global_to(guild=guild)
        synced = await self.bot.tree.sync(guild=guild)

        await ctx.send(f"Synced {len(synced)} slash commands! Type `/` to see them.")

async def setup(bot):
    await bot.add_cog(Utility(bot))
