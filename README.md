# Obsidian Marketplace Bot

A complete, production-ready Discord bot for managing the **Obsidian Marketplace** server — a premium Roblox model marketplace with automated moderation, ticketing, economy, and shop systems.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blue)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Ticket System** | Button-based tickets with staff ping, transcripts, user add | Ready |
| **AutoMod** | Anti-spam, anti-scam (instant ban), invite blocking, mass mention protection | Ready |
| **Moderation** | Ban, kick, mute, warn (3-strike system), purge | Ready |
| **Welcome & Verify** | Verification gate, welcome DM, auto-role | Ready |
| **Economy** | G-Coins currency, daily rewards, transfers, leaderboard | Ready |
| **Shop System** | Price tiers (1K-15K Robux), model categories, purchase flow | Ready |
| **Logging** | Message edits/deletes, member join/leave, role changes, channel events | Ready |
| **Utility** | Vouches, polls, announcements, user/server info | Ready |

---

## Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/obsidian-marketplace-bot.git
cd obsidian-marketplace-bot
pip install -r requirements.txt
```

### 2. Configure
Create a `.env` file:
```env
DISCORD_TOKEN=your_bot_token_here
```

Or edit `config.py` directly with your IDs.

### 3. Run
```bash
python main.py
```

---

## Post-Setup Commands

Run these in your Discord server after inviting the bot:

```
/verifypanel    → Send verification button in verify channel
/ticketpanel     → Send ticket button in support channel
/rulespanel      → Send rules embed in rules channel
/welcomepanel    → Send welcome info (optional)
```

---

## Hosting Options (2026)

### Free Tier
| Platform | Pros | Cons |
|----------|------|------|
| **Fly.io** | 3 free VMs, no sleep, production-ready | CLI-only, 256MB RAM limit |
| **Oracle Cloud** | Truly free forever, 4 ARM cores, 24GB RAM | Complex setup, account verification |
| **Render** | 750hrs/month, easy GitHub deploy | Sleeps after 15min inactivity |

### Paid (Recommended for Production)
| Platform | Price | Best For |
|----------|-------|----------|
| **Railway** | $5/mo | Git push deploy, auto-scaling, great DX |
| **DigitalOcean** | $4-7/mo | Full control, predictable pricing |
| **Kuberns** | $7/mo | Persistent processes, auto-restart, CI/CD |

### Hosting Guide: Railway (Recommended)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/obsidian-marketplace-bot.git
git push -u origin main
```

2. **Deploy on Railway**
- Go to [railway.app](https://railway.app)
- New Project → Deploy from GitHub repo
- Select your repo
- Add environment variable: `DISCORD_TOKEN=your_token`
- Deploy

3. **Done!** Your bot is online 24/7.

### Hosting Guide: Fly.io (Free)

1. **Install Fly CLI**
```bash
curl -L https://fly.io/install.sh | sh
```

2. **Launch**
```bash
fly launch
fly deploy
```

3. **Set secrets**
```bash
fly secrets set DISCORD_TOKEN=your_token
```

### Hosting Guide: Render (Free)

1. **Push to GitHub** (see above)
2. Go to [render.com](https://render.com)
3. New → Background Worker
4. Connect GitHub repo
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python main.py`
7. Add environment variable: `DISCORD_TOKEN`

---

## Project Structure

```
obsidian-bot/
├── .env                    # Environment variables
├── config.py               # Bot configuration (your IDs)
├── main.py                 # Bot entry point
├── requirements.txt        # Dependencies
├── LICENSE                 # MIT License
├── README.md               # This file
└── cogs/
    ├── automod.py          # Anti-spam, anti-scam, invite block
    ├── moderation.py       # Ban, kick, mute, warn, purge
    ├── tickets.py          # Ticket system with buttons
    ├── welcome.py          # Welcome, verify, rules panels
    ├── economy.py          # G-Coins, daily, pay, leaderboard
    ├── shop.py             # Shop browse, buy, inventory
    ├── logs.py             # Message/member/channel logging
    └── utility.py          # Vouches, polls, announcements
```

---

## Slash Commands

### Tickets
| Command | Description | Permission |
|---------|-------------|------------|
| `/ticket [reason]` | Create a support ticket | Everyone |
| `/ticketpanel` | Send ticket panel embed | Manage Channels |
| `/close` | Close current ticket (text cmd) | Manage Channels |

### Moderation
| Command | Description | Permission |
|---------|-------------|------------|
| `/ban @user [reason] [days]` | Ban a user | Ban Members |
| `/kick @user [reason]` | Kick a user | Kick Members |
| `/mute @user [duration] [reason]` | Timeout/mute | Moderate Members |
| `/unmute @user` | Remove timeout | Moderate Members |
| `/warn @user [reason]` | Warn user (3-strike auto-kick) | Kick Members |
| `/warnings @user` | View user warnings | Kick Members |
| `/clearwarns @user` | Clear all warnings | Administrator |
| `/purge [amount] [@user]` | Delete messages | Manage Messages |

### Economy
| Command | Description | Permission |
|---------|-------------|------------|
| `/balance` | Check G-Coins | Everyone |
| `/daily` | Claim daily reward | Everyone |
| `/pay @user [amount]` | Send G-Coins | Everyone |
| `/leaderboard` | Top balances | Everyone |
| `/addcoins @user [amount] [reason]` | Admin add coins | Administrator |
| `/removecoins @user [amount] [reason]` | Admin remove coins | Administrator |

### Shop
| Command | Description | Permission |
|---------|-------------|------------|
| `/shop [tier] [category]` | Browse items | Everyone |
| `/buy [item_id]` | Purchase item | Everyone |
| `/inventory` | View purchases | Everyone |
| `/additem ...` | Add item to shop | Administrator |
| `/removeitem [item_id]` | Remove item | Administrator |

### Utility
| Command | Description | Permission |
|---------|-------------|------------|
| `/ping` | Check bot latency | Everyone |
| `/userinfo [@user]` | User information | Everyone |
| `/serverinfo` | Server information | Everyone |
| `/vouch @user [message]` | Leave a review | Everyone |
| `/vouches [@user]` | View reviews | Everyone |
| `/announce [channel] [title] [message] [ping]` | Send announcement | Administrator |
| `/embed [channel] [title] [description] [color]` | Custom embed | Administrator |
| `/say [channel] [message]` | Bot says message | Administrator |
| `/avatar [@user]` | Get avatar | Everyone |
| `/poll [question] [opt1] [opt2] ...` | Create poll | Everyone |

---

## Important Notes

1. **Muted Role**: Create a "Muted" role manually in Discord, deny `Send Messages` in all channels, and update `MUTED_ROLE` in `config.py`.

2. **Privileged Intents**: Enable in [Discord Developer Portal](https://discord.com/developers/applications):
   - Presence Intent
   - Server Members Intent
   - Message Content Intent

3. **Permissions**: The bot needs these permissions:
   - Manage Channels
   - Manage Roles
   - Manage Messages
   - Kick Members
   - Ban Members
   - Moderate Members
   - Read Message History
   - Send Messages
   - Embed Links
   - Attach Files
   - Add Reactions
   - Use Slash Commands

---

## License

[MIT](LICENSE) - Free to use, modify, and distribute.

---

## Support

For issues or feature requests, open an [Issue](https://github.com/YOUR_USERNAME/obsidian-marketplace-bot/issues) or contact the Obsidian Marketplace staff.

---

Built with Python and discord.py for the Obsidian Marketplace community.
