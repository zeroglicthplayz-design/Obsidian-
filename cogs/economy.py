import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta
import sqlite3
import config

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            daily_claimed TEXT,
            total_spent INTEGER DEFAULT 0,
            total_earned INTEGER DEFAULT 0
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            type TEXT,
            description TEXT,
            timestamp TEXT
        )""")

        conn.commit()
        conn.close()

    def get_balance(self, user_id):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def add_balance(self, user_id, amount, description=""):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
        c.execute("UPDATE users SET balance = balance + ?, total_earned = total_earned + ? WHERE user_id = ?",
                  (amount, amount, user_id))

        c.execute("INSERT INTO transactions (user_id, amount, type, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (user_id, amount, 'credit', description, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def remove_balance(self, user_id, amount, description=""):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)", (user_id,))
        c.execute("UPDATE users SET balance = balance - ?, total_spent = total_spent + ? WHERE user_id = ?",
                  (amount, amount, user_id))

        c.execute("INSERT INTO transactions (user_id, amount, type, description, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (user_id, amount, 'debit', description, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    @app_commands.command(name="balance", description="Check your G-Coin balance")
    async def balance(self, interaction: discord.Interaction):
        balance = self.get_balance(interaction.user.id)

        embed = discord.Embed(
            title="Your Balance",
            description=f"**{balance:,}** G-Coins",
            color=config.SHOP_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="Obsidian Marketplace Economy")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="daily", description="Claim your daily G-Coin reward")
    async def daily(self, interaction: discord.Interaction):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT daily_claimed FROM users WHERE user_id = ?", (interaction.user.id,))
        result = c.fetchone()
        conn.close()

        now = datetime.now()

        if result and result[0]:
            last_claimed = datetime.fromisoformat(result[0])
            if (now - last_claimed).days < 1:
                next_claim = last_claimed + timedelta(days=1)
                time_left = next_claim - now
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)

                await interaction.response.send_message(
                    f"You already claimed today! Come back in **{hours}h {minutes}m**.",
                    ephemeral=True
                )
                return

        reward = config.DAILY_REWARD

        if interaction.user.premium_since:
            reward += config.BOOSTER_BONUS
            bonus_text = f" (+{config.BOOSTER_BONUS} booster bonus!)"
        else:
            bonus_text = ""

        self.add_balance(interaction.user.id, reward, "Daily reward")

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE users SET daily_claimed = ? WHERE user_id = ?",
                  (now.isoformat(), interaction.user.id))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="Daily Reward Claimed!",
            description=f"You received **{reward:,}** G-Coins!{bonus_text}",
            color=config.SUCCESS_COLOR,
            timestamp=now
        )
        embed.set_footer(text="Come back tomorrow for more!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pay", description="Send G-Coins to another user")
    @app_commands.describe(user="User to send coins to", amount="Amount to send")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("Amount must be positive.", ephemeral=True)
            return

        sender_balance = self.get_balance(interaction.user.id)
        if sender_balance < amount:
            await interaction.response.send_message(
                f"You don't have enough G-Coins! Balance: **{sender_balance:,}**",
                ephemeral=True
            )
            return

        self.remove_balance(interaction.user.id, amount, f"Sent to {user}")
        self.add_balance(user.id, amount, f"Received from {interaction.user}")

        embed = discord.Embed(
            title="Transfer Complete",
            description=f"You sent **{amount:,}** G-Coins to {user.mention}!",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Your New Balance", value=f"**{self.get_balance(interaction.user.id):,}**", inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

        try:
            recv_embed = discord.Embed(
                title="You Received G-Coins!",
                description=f"**{amount:,}** G-Coins from {interaction.user.mention}",
                color=config.SUCCESS_COLOR
            )
            await user.send(embed=recv_embed)
        except:
            pass

    @app_commands.command(name="leaderboard", description="View top G-Coin balances")
    async def leaderboard(self, interaction: discord.Interaction):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT user_id, balance FROM users ORDER BY balance DESC LIMIT 10")
        results = c.fetchall()
        conn.close()

        if not results:
            await interaction.response.send_message("No data yet!", ephemeral=True)
            return

        embed = discord.Embed(
            title="G-Coin Leaderboard",
            color=config.SHOP_COLOR,
            timestamp=datetime.now()
        )

        medals = ["1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "10."]

        for i, (user_id, balance) in enumerate(results):
            user = self.bot.get_user(user_id)
            name = user.name if user else f"User {user_id}"
            embed.add_field(
                name=f"{medals[i]} {name}",
                value=f"**{balance:,}** G-Coins",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addcoins", description="Add G-Coins to a user (Admin only)")
    @app_commands.describe(user="User to add coins to", amount="Amount to add", reason="Reason")
    @app_commands.checks.has_permissions(administrator=True)
    async def addcoins(self, interaction: discord.Interaction, user: discord.Member, amount: int, reason: str = "Admin add"):
        self.add_balance(user.id, amount, reason)

        embed = discord.Embed(
            title="Coins Added",
            description=f"Added **{amount:,}** G-Coins to {user.mention}",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="New Balance", value=f"**{self.get_balance(user.id):,}**", inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removecoins", description="Remove G-Coins from a user (Admin only)")
    @app_commands.describe(user="User to remove coins from", amount="Amount to remove", reason="Reason")
    @app_commands.checks.has_permissions(administrator=True)
    async def removecoins(self, interaction: discord.Interaction, user: discord.Member, amount: int, reason: str = "Admin remove"):
        self.remove_balance(user.id, amount, reason)

        embed = discord.Embed(
            title="Coins Removed",
            description=f"Removed **{amount:,}** G-Coins from {user.mention}",
            color=config.ERROR_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Reason", value=reason, inline=True)
        embed.add_field(name="New Balance", value=f"**{self.get_balance(user.id):,}**", inline=True)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
