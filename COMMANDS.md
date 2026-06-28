
# OBSIDIAN MARKETPLACE BOT - ALL COMMANDS

## TICKETS (cogs/tickets.py)
/ticket [reason]          - Create a support ticket
/ticketpanel              - Send ticket panel embed (Staff only)
/close                    - Close current ticket (text command)

## MODERATION (cogs/moderation.py)
/ban @user [reason] [days]     - Ban a user
/kick @user [reason]           - Kick a user
/mute @user [duration] [reason] - Timeout/mute user
/unmute @user                  - Remove timeout
/warn @user [reason]           - Warn user (3-strike auto-kick)
/warnings @user                - View user warnings
/clearwarns @user              - Clear all warnings (Admin)
/purge [amount] [@user]        - Delete messages

## WELCOME (cogs/welcome.py)
/verifypanel              - Send verification button panel
/welcomepanel             - Send welcome info panel
/rulespanel               - Send rules embed panel

## ECONOMY (cogs/economy.py)
/balance                  - Check G-Coin balance
/daily                    - Claim daily reward
/pay @user [amount]       - Send G-Coins to user
/leaderboard              - View top balances
/addcoins @user [amount]  - Add coins (Admin only)
/removecoins @user [amount] - Remove coins (Admin only)

## SHOP (cogs/shop.py)
/shop [tier] [category]   - Browse shop items
/buy [item_id]            - Purchase an item
/inventory                - View purchased items
/additem ...              - Add item to shop (Admin)
/removeitem [item_id]     - Remove item (Admin)

## UTILITY (cogs/utility.py)
/ping                     - Check bot latency
/userinfo [@user]         - User information
/serverinfo               - Server information
/vouch @user [message]    - Leave a review
/vouches [@user]          - View reviews
/announce [channel] [title] [message] [ping] - Send announcement (Admin)
/embed [channel] [title] [description] [color] - Custom embed (Admin)
/say [channel] [message]  - Bot says message (Admin)
/avatar [@user]           - Get user avatar
/poll [question] [opt1] [opt2] ... - Create poll

## LOGGING (cogs/logs.py) - Automatic, no commands
- Message delete logs
- Message edit logs  
- Member join/leave logs
- Role change logs
- Nickname change logs
- Channel create/delete logs

## AUTOMOD (cogs/automod.py) - Automatic, no commands
- Anti-spam (5 msgs in 5s)
- Anti-scam (instant ban keywords)
- Invite link blocking
- Mass mention protection
- Account age check (7+ days)
