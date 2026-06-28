import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
class ObsidianBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )

    async def setup_hook(self):
        # Load all cogs
        cogs = [
            'cogs.tickets',
            'cogs.automod', 
            'cogs.moderation',
            'cogs.welcome',
            'cogs.economy',
            'cogs.shop',
            'cogs.logs',
            'cogs.utility'
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")

        # Sync slash commands
        await self.tree.sync()
        print("🔄 Slash commands synced")

    async def on_ready(self):
        print(f"🤖 {self.user} is online!")
        print(f"📊 In {len(self.guilds)} guilds")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Obsidian Marketplace"
            )
        )

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing argument: `{error.param.name}`", delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(f"Error: {error}")

# Run the bot
bot = ObsidianBot()
bot.run(os.getenv('DISCORD_TOKEN'))
