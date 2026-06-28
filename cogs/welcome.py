import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import config

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅", custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        verified_role = interaction.guild.get_role(config.VERIFIED_ROLE)

        if not verified_role:
            await interaction.response.send_message("❌ Verification role not configured.", ephemeral=True)
            return

        if verified_role in interaction.user.roles:
            await interaction.response.send_message("✅ You are already verified!", ephemeral=True)
            return

        await interaction.user.add_roles(verified_role, reason="User verified")

        # Send welcome message in welcome channel
        welcome_channel = interaction.guild.get_channel(config.WELCOME_CHANNEL)
        if welcome_channel:
            embed = discord.Embed(
                title="👋 New Member!",
                description=f"Welcome {interaction.user.mention} to **Obsidian Marketplace**!",
                color=config.SUCCESS_COLOR,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            embed.add_field(name="Member Count", value=f"{interaction.guild.member_count}", inline=True)
            embed.add_field(name="Account Created", value=f"<t:{int(interaction.user.created_at.timestamp())}:R>", inline=True)
            embed.set_footer(text=f"User ID: {interaction.user.id}")
            await welcome_channel.send(embed=embed)

        # DM welcome
        try:
            dm_embed = discord.Embed(
                title="🖤 Welcome to Obsidian Marketplace!",
                description=config.WELCOME_MESSAGE.format(
                    user=interaction.user.mention,
                    rules=config.RULES_CHANNEL
                ),
                color=config.EMBED_COLOR
            )
            dm_embed.add_field(
                name="Quick Links",
                value=f"<#{config.RULES_CHANNEL}> | <#{config.WELCOME_CHANNEL}> | <#ticket-support>",
                inline=False
            )
            await interaction.user.send(embed=dm_embed)
        except:
            pass

        await interaction.response.send_message("✅ You have been verified! Welcome to Obsidian Marketplace.", ephemeral=True)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(WelcomeView())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send DM on join before verification"""
        try:
            embed = discord.Embed(
                title="🖤 Welcome to Obsidian Marketplace!",
                description=f"Hey {member.mention}, thanks for joining!",
                color=config.EMBED_COLOR
            )
            embed.add_field(
                name="Next Steps",
                value="1. Go to the verification channel\n2. Click the **Verify** button\n3. Read the rules\n4. Start browsing!",
                inline=False
            )
            embed.add_field(
                name="Need Help?",
                value="Open a ticket anytime for support.",
                inline=False
            )
            await member.send(embed=embed)
        except:
            pass

    @app_commands.command(name="verifypanel", description="Send the verification panel (Staff only)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def verify_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="✅ Verification",
            description="Click the button below to verify yourself and gain access to the server!",
            color=config.SUCCESS_COLOR
        )
        embed.add_field(name="Requirements", value="- Discord account must be 7+ days old\n- No prior bans from our network", inline=False)
        embed.set_footer(text="Obsidian Marketplace Verification")

        view = WelcomeView()
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="welcomepanel", description="Send welcome info panel (Staff only)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def welcome_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🖤 Welcome to Obsidian Marketplace",
            description="Your one-stop shop for premium Roblox models and assets.",
            color=config.EMBED_COLOR
        )
        embed.add_field(
            name="📋 Getting Started",
            value="1. Verify in <#verify-channel>\n2. Read <#rules>\n3. Browse categories by price tier\n4. Open a ticket to purchase",
            inline=False
        )
        embed.add_field(
            name="💰 Price Tiers",
            value="🥉 1K-4K Robux | 🥈 5K-10K Robux | 🥇 11K-15K Robux",
            inline=False
        )
        embed.add_field(
            name="🛡️ Safety",
            value="All transactions are monitored. Scammers are banned instantly.",
            inline=False
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/placeholder/banner.png")
        embed.set_footer(text="Obsidian Marketplace | Est. 2024")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rulespanel", description="Send the rules panel (Staff only)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def rules_panel(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📜 Server Rules",
            description="Breaking any rule may result in warnings, mutes, kicks, or bans.",
            color=config.WARNING_COLOR
        )
        rules = [
            ("1. Respect Everyone", "No harassment, hate speech, racism, sexism, or discrimination."),
            ("2. No Scamming", "Scamming = instant permanent ban + report to Roblox."),
            ("3. No Spam", "No repeated messages, excessive emoji, or character spam."),
            ("4. No NSFW", "Keep it clean. No gore, explicit content, or shock links."),
            ("5. No Advertising", "No promoting other servers without staff approval."),
            ("6. Use Channels Correctly", "Post assets in correct tiers and categories."),
            ("7. No Alts", "Alt accounts to bypass bans will be detected and banned."),
            ("8. Follow Roblox ToS", "All assets must comply with Roblox Terms of Use."),
            ("9. Staff Have Final Say", "Don't argue with mod decisions. Appeal via ticket."),
            ("10. English Only", "Keep public communication in English for moderation."),
        ]

        for title, desc in rules:
            embed.add_field(name=title, value=desc, inline=False)

        embed.add_field(
            name="⚠️ Disclaimer",
            value="Obsidian Marketplace is not affiliated with Roblox Corporation. We are not responsible for peer-to-peer transaction losses. Always verify sellers before payment.",
            inline=False
        )
        embed.set_footer(text="Last Updated: June 2026")

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
