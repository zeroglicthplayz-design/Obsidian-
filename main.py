import discord
from discord.ext import commands
import asyncio
import os

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to import Flask for Render web service (optional)
try:
    from flask import Flask
    from threading import Thread
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Flask app for Render health checks (keeps free tier alive)
if FLASK_AVAILABLE:
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Obsidian Marketplace Bot is running!", 200

    @app.route('/health')
    def health():
        return {"status": "ok", "bot": bot.user.name if bot.user else "offline"}, 200

    def run_flask():
        app.run(host='0.0.0.0', port=10000)

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
                print(f"Loaded {cog}")
            except Exception as e:
                print(f"Failed to load {cog}: {e}")

        # Sync slash commands to guild
        import config
        guild = discord.Object(id=config.GUILD_ID)
        try:
            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} slash commands to guild {config.GUILD_ID}")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def on_ready(self):
        print(f"{self.user} is online!")
        print(f"In {len(self.guilds)} guilds")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Obsidian Marketplace"
            )
        )

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: `{error.param.name}`", delete_after=5)
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            print(f"Error: {error}")

# Run the bot
bot = ObsidianBot()

# Start Flask in background thread for Render
if FLASK_AVAILABLE:
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask health server started on port 10000")


    @commands.command()
    @commands.is_owner()
    async def sync(ctx):
        """Sync slash commands manually"""
        import config
        guild = discord.Object(id=config.GUILD_ID)
        ctx.bot.tree.copy_global_to(guild=guild)
        synced = await ctx.bot.tree.sync(guild=guild)
        await ctx.send(f"Synced {len(synced)} slash commands! Type `/` to see them.")

bot.run(os.getenv('DISCORD_TOKEN'))
