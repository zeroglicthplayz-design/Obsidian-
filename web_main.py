import discord
from discord.ext import commands
import asyncio
import os

# Try to import Flask, if not available use fallback
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from flask import Flask
    from threading import Thread
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("WARNING: Flask not installed. Running without web server.")

# Flask app for health checks (keeps Render web service alive)
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

        await self.tree.sync()
        print("Slash commands synced")

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

bot = ObsidianBot()

# Start Flask in a thread
if FLASK_AVAILABLE:
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask server started on port 10000")

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
