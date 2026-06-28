"""
Keep-alive script for Render free tier.
On free tier, services sleep after 15 minutes of inactivity.
For Discord bots, this means the bot will go offline.

Solutions:
1. Upgrade to paid ($7/month) - recommended for production
2. Use a web service with a health check endpoint instead of worker
3. Use UptimeRobot to ping a health endpoint every 5 minutes

For now, this bot uses discord.py which keeps a websocket connection open.
If you need 24/7 uptime on free tier, consider switching to a web service
with a small Flask/FastAPI health endpoint.
