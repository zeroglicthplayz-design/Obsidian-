# Obsidian Marketplace Bot

A complete, production-ready Discord bot for managing the **Obsidian Marketplace** server.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blue)](https://discordpy.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## Deploy on Render (Free Tier)

**Quick deploy:** Connect your GitHub repo to Render as a **Web Service**.

```
Build Command:  pip install -r requirements.txt
Start Command:  python web_main.py
```

Add `DISCORD_TOKEN` as an environment variable. Done!

**Why Web Service?** Render pings it to keep it alive. Background Workers sleep after 15 min on free tier.

**Full guide:** [DEPLOY.md](DEPLOY.md)

---

## Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Ticket System** | Button-based tickets with staff ping, transcripts | Ready |
| **AutoMod** | Anti-spam, anti-scam (instant ban), invite blocking | Ready |
| **Moderation** | Ban, kick, mute, warn (3-strike), purge | Ready |
| **Welcome & Verify** | Verification gate, welcome DM, auto-role | Ready |
| **Economy** | G-Coins currency, daily rewards, transfers | Ready |
| **Shop System** | Price tiers (1K-15K Robux), model categories | Ready |
| **Logging** | Message edits/deletes, member join/leave | Ready |
| **Utility** | Vouches, polls, announcements, info | Ready |

---

## Files

| File | Purpose |
|------|---------|
| `main.py` | Standard bot (use for local or paid hosting) |
| `web_main.py` | Bot + Flask health endpoint (use for Render free tier) |
| `config.py` | All your server IDs pre-configured |
| `render.yaml` | Render Blueprint config |
| `DEPLOY.md` | Detailed Render deployment guide |

---

## Post-Setup Commands

Run these in Discord after the bot is online:

```
/verifypanel    -> Send verification button
/ticketpanel     -> Send ticket button  
/rulespanel      -> Send rules embed
```

---

## License

[MIT](LICENSE)
