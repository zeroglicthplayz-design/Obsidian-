import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import asyncio
import config

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Check if user already has an open ticket
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing:
            await interaction.response.send_message(
                f"❌ You already have an open ticket: {existing.mention}", 
                ephemeral=True
            )
            return

        # Create ticket channel
        category = guild.get_channel(config.TICKET_CATEGORY)
        staff_role = guild.get_role(config.TICKET_STAFF_ROLE)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites,
            topic=f"Ticket opened by {user} | {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )

        # Send ticket embed
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description=f"Hello {user.mention}, a staff member will be with you shortly.",
            color=config.TICKET_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="User", value=f"{user.mention} (`{user.id}`)", inline=True)
        embed.add_field(name="Opened", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)
        embed.set_footer(text=f"Ticket ID: {ticket_channel.id}")

        view = TicketControlView()
        await ticket_channel.send(content=staff_role.mention, embed=embed, view=view)

        await interaction.response.send_message(
            f"✅ Ticket created: {ticket_channel.mention}", 
            ephemeral=True
        )

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Only staff can close tickets.", ephemeral=True)
            return

        await interaction.response.send_message("🔒 Closing ticket in 5 seconds...", ephemeral=False)

        # Generate transcript (simplified - saves messages)
        channel = interaction.channel
        messages = []
        async for msg in channel.history(limit=500, oldest_first=True):
            messages.append(f"[{msg.created_at.strftime('%H:%M')}] {msg.author}: {msg.content}")

        transcript = "\n".join(messages)

        # Send transcript to log channel
        log_channel = interaction.guild.get_channel(config.TICKET_LOG_CHANNEL)
        if log_channel:
            transcript_embed = discord.Embed(
                title=f"📋 Ticket Transcript - {channel.name}",
                description=f"Closed by {interaction.user.mention}",
                color=config.INFO_COLOR,
                timestamp=datetime.now()
            )
            transcript_embed.add_field(name="Messages", value=str(len(messages)))

            # Send as file if too long
            if len(transcript) > 4000:
                from io import StringIO
                file = discord.File(StringIO(transcript), filename=f"{channel.name}-transcript.txt")
                await log_channel.send(embed=transcript_embed, file=file)
            else:
                transcript_embed.add_field(name="Transcript", value=f"```\n{transcript[:1000]}...\n```", inline=False)
                await log_channel.send(embed=transcript_embed)

        await asyncio.sleep(5)
        await channel.delete()

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.blurple, emoji="👤", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Only staff can claim tickets.", ephemeral=True)
            return

        embed = discord.Embed(
            title="👤 Ticket Claimed",
            description=f"This ticket is now being handled by {interaction.user.mention}",
            color=config.SUCCESS_COLOR
        )
        await interaction.response.send_message(embed=embed)
        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Add User", style=discord.ButtonStyle.gray, emoji="➕", custom_id="add_user_ticket")
    async def add_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ Only staff can add users.", ephemeral=True)
            return

        await interaction.response.send_message(
            "Please mention the user you want to add:", 
            ephemeral=True
        )

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await interaction.client.wait_for('message', check=check, timeout=30)
            user = msg.mentions[0] if msg.mentions else None
            if user:
                await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
                await interaction.channel.send(f"✅ Added {user.mention} to the ticket.")
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Timed out.", ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketControlView())

    @app_commands.command(name="ticket", description="Create a support ticket")
    @app_commands.describe(reason="Reason for opening the ticket")
    async def ticket_cmd(self, interaction: discord.Interaction, reason: str = None):
        """Slash command to create a ticket"""
        guild = interaction.guild
        user = interaction.user

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
        if existing:
            await interaction.response.send_message(
                f"❌ You already have an open ticket: {existing.mention}", 
                ephemeral=True
            )
            return

        category = guild.get_channel(config.TICKET_CATEGORY)
        staff_role = guild.get_role(config.TICKET_STAFF_ROLE)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Support Ticket",
            description=f"Hello {user.mention}, a staff member will be with you shortly.",
            color=config.TICKET_COLOR,
            timestamp=datetime.now()
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="User", value=f"{user.mention} (`{user.id}`)", inline=True)
        embed.add_field(name="Opened", value=f"<t:{int(datetime.now().timestamp())}:R>", inline=True)

        view = TicketControlView()
        await ticket_channel.send(content=staff_role.mention, embed=embed, view=view)

        await interaction.response.send_message(
            f"✅ Ticket created: {ticket_channel.mention}", 
            ephemeral=True
        )

    @app_commands.command(name="ticketpanel", description="Send the ticket panel embed (Staff only)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ticket_panel(self, interaction: discord.Interaction):
        """Send ticket panel with button"""
        embed = discord.Embed(
            title="🎫 Support Center",
            description="Need help? Click the button below to open a ticket!",
            color=config.TICKET_COLOR
        )
        embed.add_field(name="Response Time", value="Usually within 1-2 hours", inline=True)
        embed.add_field(name="Available For", value="Purchases, refunds, reports, general support", inline=True)
        embed.set_footer(text="Obsidian Marketplace Support")

        view = TicketView()
        await interaction.response.send_message(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def close(self, ctx):
        """Close the current ticket channel"""
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("❌ This is not a ticket channel.")
            return

        await ctx.send("🔒 Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(Tickets(bot))
