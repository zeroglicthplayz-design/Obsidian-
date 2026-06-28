import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import sqlite3
import config

class ShopItem:
    def __init__(self, id, name, description, price, category, tier, image_url=None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.tier = tier
        self.image_url = image_url

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price INTEGER,
            category TEXT,
            tier TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT -1,
            created_at TEXT
        )""")

        c.execute("""CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_id INTEGER,
            price_paid INTEGER,
            timestamp TEXT
        )""")

        conn.commit()
        conn.close()

    def get_items(self, tier=None, category=None):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        if tier and category:
            c.execute("SELECT * FROM shop_items WHERE tier = ? AND category = ? ORDER BY price", (tier, category))
        elif tier:
            c.execute("SELECT * FROM shop_items WHERE tier = ? ORDER BY price", (tier,))
        elif category:
            c.execute("SELECT * FROM shop_items WHERE category = ? ORDER BY price", (category,))
        else:
            c.execute("SELECT * FROM shop_items ORDER BY tier, price")

        items = c.fetchall()
        conn.close()
        return items

    @app_commands.command(name="shop", description="Browse the Obsidian Marketplace")
    @app_commands.describe(tier="Filter by price tier", category="Filter by model category")
    @app_commands.choices(tier=[
        app_commands.Choice(name="1K-4K Robux", value="1k-4k"),
        app_commands.Choice(name="5K-10K Robux", value="5k-10k"),
        app_commands.Choice(name="11K-15K Robux", value="11k-15k")
    ])
    @app_commands.choices(category=[
        app_commands.Choice(name="Vegetation Models", value="vegetation-models"),
        app_commands.Choice(name="Chinese Theme Models", value="chinese-theme-models"),
        app_commands.Choice(name="Car Models", value="car-models"),
        app_commands.Choice(name="Rocket Models", value="rocket-models")
    ])
    async def shop(self, interaction: discord.Interaction, tier: app_commands.Choice[str] = None, category: app_commands.Choice[str] = None):
        tier_value = tier.value if tier else None
        category_value = category.value if category else None

        items = self.get_items(tier_value, category_value)

        if not items:
            await interaction.response.send_message("No items found in this category.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Obsidian Marketplace",
            description="Browse our premium Roblox models and assets.",
            color=config.SHOP_COLOR,
            timestamp=datetime.now()
        )

        if tier_value:
            tier_info = config.PRICE_TIERS.get(tier_value, {})
            embed.title += f" | {tier_info.get('emoji', '')} {tier_value.upper()}"

        if category_value:
            embed.title += f" | {category_value.replace('-', ' ').title()}"

        for item in items[:10]:  # Show max 10
            item_id, name, desc, price, cat, t, img, stock, created = item
            stock_text = f" | Stock: {stock}" if stock >= 0 else ""
            embed.add_field(
                name=f"#{item_id} {name} - {price:,} G-Coins",
                value=f"{desc}{stock_text}\nCategory: {cat.replace('-', ' ').title()}",
                inline=False
            )

        embed.set_footer(text=f"Use /buy [item-id] to purchase | {len(items)} items total")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Purchase an item from the shop")
    @app_commands.describe(item_id="The ID of the item you want to buy")
    async def buy(self, interaction: discord.Interaction, item_id: int):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM shop_items WHERE id = ?", (item_id,))
        item = c.fetchone()

        if not item:
            await interaction.response.send_message("Item not found.", ephemeral=True)
            conn.close()
            return

        item_id, name, desc, price, category, tier, image_url, stock, created = item

        # Check stock
        if stock == 0:
            await interaction.response.send_message("This item is out of stock!", ephemeral=True)
            conn.close()
            return

        # Check balance
        c.execute("SELECT balance FROM users WHERE user_id = ?", (interaction.user.id,))
        result = c.fetchone()
        balance = result[0] if result else 0

        if balance < price:
            await interaction.response.send_message(
                f"You don't have enough G-Coins! Price: **{price:,}** | Your balance: **{balance:,}**",
                ephemeral=True
            )
            conn.close()
            return

        # Process purchase
        c.execute("UPDATE users SET balance = balance - ?, total_spent = total_spent + ? WHERE user_id = ?",
                  (price, price, interaction.user.id))

        c.execute("INSERT INTO purchases (user_id, item_id, price_paid, timestamp) VALUES (?, ?, ?, ?)",
                  (interaction.user.id, item_id, price, datetime.now().isoformat()))

        if stock > 0:
            c.execute("UPDATE shop_items SET stock = stock - 1 WHERE id = ?", (item_id,))

        conn.commit()
        conn.close()

        # Send purchase confirmation
        embed = discord.Embed(
            title="Purchase Complete!",
            description=f"You bought **{name}** for **{price:,}** G-Coins!",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Item ID", value=str(item_id), inline=True)
        embed.add_field(name="Category", value=category.replace('-', ' ').title(), inline=True)
        embed.add_field(name="Tier", value=tier, inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

        # DM delivery info
        try:
            dm_embed = discord.Embed(
                title="Your Purchase Receipt",
                description=f"**Item:** {name}\n**Price:** {price:,} G-Coins\n**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                color=config.SUCCESS_COLOR
            )
            dm_embed.add_field(
                name="Next Steps",
                value="A staff member will contact you shortly with your asset delivery.\\nIf you don't hear back within 24 hours, open a ticket.",
                inline=False
            )
            await interaction.user.send(embed=dm_embed)
        except:
            pass

        # Log purchase
        log_channel = interaction.guild.get_channel(config.MOD_LOG_CHANNEL)
        if log_channel:
            log_embed = discord.Embed(
                title="Purchase Log",
                description=f"{interaction.user.mention} bought **{name}**",
                color=config.INFO_COLOR,
                timestamp=datetime.now()
            )
            log_embed.add_field(name="Price", value=f"{price:,} G-Coins", inline=True)
            log_embed.add_field(name="Item ID", value=str(item_id), inline=True)
            await log_channel.send(embed=log_embed)

    @app_commands.command(name="additem", description="Add an item to the shop (Admin only)")
    @app_commands.describe(
        name="Item name",
        description="Item description",
        price="Price in G-Coins",
        tier="Price tier",
        category="Model category",
        stock="Stock amount (-1 for unlimited)",
        image_url="Optional image URL"
    )
    @app_commands.choices(tier=[
        app_commands.Choice(name="1K-4K Robux", value="1k-4k"),
        app_commands.Choice(name="5K-10K Robux", value="5k-10k"),
        app_commands.Choice(name="11K-15K Robux", value="11k-15k")
    ])
    @app_commands.choices(category=[
        app_commands.Choice(name="Vegetation Models", value="vegetation-models"),
        app_commands.Choice(name="Chinese Theme Models", value="chinese-theme-models"),
        app_commands.Choice(name="Car Models", value="car-models"),
        app_commands.Choice(name="Rocket Models", value="rocket-models")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def additem(self, interaction: discord.Interaction, name: str, description: str, price: int, 
                      tier: app_commands.Choice[str], category: app_commands.Choice[str], 
                      stock: int = -1, image_url: str = None):

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""INSERT INTO shop_items (name, description, price, category, tier, image_url, stock, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (name, description, price, category.value, tier.value, image_url, stock, datetime.now().isoformat()))

        item_id = c.lastrowid
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="Item Added to Shop",
            description=f"**{name}** has been added to the shop!",
            color=config.SUCCESS_COLOR,
            timestamp=datetime.now()
        )
        embed.add_field(name="Item ID", value=str(item_id), inline=True)
        embed.add_field(name="Price", value=f"{price:,} G-Coins", inline=True)
        embed.add_field(name="Tier", value=tier.value, inline=True)
        embed.add_field(name="Category", value=category.value.replace('-', ' ').title(), inline=True)
        embed.add_field(name="Stock", value="Unlimited" if stock == -1 else str(stock), inline=True)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removeitem", description="Remove an item from the shop (Admin only)")
    @app_commands.describe(item_id="ID of the item to remove")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeitem(self, interaction: discord.Interaction, item_id: int):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT name FROM shop_items WHERE id = ?", (item_id,))
        result = c.fetchone()

        if not result:
            await interaction.response.send_message("Item not found.", ephemeral=True)
            conn.close()
            return

        name = result[0]
        c.execute("DELETE FROM shop_items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

        await interaction.response.send_message(f"Removed **{name}** (ID: {item_id}) from the shop.")

    @app_commands.command(name="inventory", description="View your purchased items")
    async def inventory(self, interaction: discord.Interaction):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""SELECT p.item_id, s.name, s.category, s.tier, p.price_paid, p.timestamp 
                     FROM purchases p 
                     JOIN shop_items s ON p.item_id = s.id 
                     WHERE p.user_id = ? 
                     ORDER BY p.timestamp DESC""", (interaction.user.id,))

        purchases = c.fetchall()
        conn.close()

        if not purchases:
            await interaction.response.send_message("You haven't purchased anything yet!", ephemeral=True)
            return

        embed = discord.Embed(
            title="Your Inventory",
            description=f"You have **{len(purchases)}** purchased items.",
            color=config.SHOP_COLOR,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        for item_id, name, category, tier, price, timestamp in purchases[:10]:
            date = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d')
            embed.add_field(
                name=f"#{item_id} {name}",
                value=f"Tier: {tier} | {price:,} G-Coins | Purchased: {date}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Shop(bot))
