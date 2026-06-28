# Deploy on Render

## Method 1: Web Service (Recommended for Free Tier)

A web service stays awake because Render pings it. We include a Flask health endpoint.

### Steps:

1. **In your repo, use `web_main.py` instead of `main.py`**

2. **Connect to Render:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click **New +** → **Web Service**
   - Connect your GitHub repo

3. **Configure:**
   - **Name:** `obsidian-marketplace-bot`
   - **Language:** Python 3
   - **Branch:** `main`
   - **Region:** Oregon (US West)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python web_main.py`

4. **Add Environment Variable:**
   - Click **Advanced** → **Add Environment Variable**
   - Key: `DISCORD_TOKEN`
   - Value: Your bot token

5. **Deploy!**

### Why this works on free tier:
- Render pings your web service every few minutes
- The Flask `/health` endpoint responds, keeping it alive
- The Discord bot runs in the same process

---

## Method 2: Background Worker (Requires Paid Plan)

Workers sleep after 15 minutes of inactivity on free tier. Use this only if you pay $7/month.

### Steps:

1. **Use `main.py` (original file)**

2. **Connect to Render:**
   - Click **New +** → **Background Worker**
   - Connect your GitHub repo

3. **Configure:**
   - **Name:** `obsidian-marketplace-bot`
   - **Language:** Python 3
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`

4. **Add Environment Variable:**
   - Key: `DISCORD_TOKEN`
   - Value: Your bot token

5. **Choose Plan:**
   - Select **Starter** ($7/month) or higher
   - Free tier will NOT work for Discord bots (they sleep)

---

## Troubleshooting

### Bot goes offline after 15 minutes?
**You're using Worker on free tier.** Switch to Web Service method above.

### "Build failed" error?
Check that `requirements.txt` has all dependencies:
```
discord.py>=2.3.0
python-dotenv>=1.0.0
flask>=3.0.0
```

### Bot not responding to commands?
- Check that `DISCORD_TOKEN` is set correctly
- Ensure the bot has `applications.commands` scope in Discord Developer Portal
- Check Render logs for errors

### Database errors?
The bot uses SQLite (`database.db`). On Render, this file is ephemeral (resets on redeploy).
For production, switch to PostgreSQL (Render offers free PostgreSQL).

---

## Quick Reference

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command (Web) | `python web_main.py` |
| Start Command (Worker) | `python main.py` |
| Required Env Var | `DISCORD_TOKEN` |
| Port (Web) | `10000` (Flask default) |
