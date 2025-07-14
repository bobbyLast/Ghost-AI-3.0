# Discord Integration Setup Guide

## 🤖 Discord Bot Setup

### Step 1: Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Name it "Ghost AI 3.0"
4. Go to "Bot" section
5. Click "Add Bot"
6. Copy the **Bot Token** (you'll need this)

### Step 2: Bot Permissions
Enable these permissions:
- ✅ Send Messages
- ✅ Embed Links
- ✅ Read Message History
- ✅ Use Slash Commands
- ✅ Add Reactions

### Step 3: Invite Bot to Server
1. Go to "OAuth2" → "URL Generator"
2. Select "bot" scope
3. Select the permissions above
4. Copy the generated URL
5. Open URL in browser to invite bot

### Step 4: Create Channels
Create these channels in your Discord server:
- `#picks` - For daily picks
- `#alerts` - For system alerts  
- `#system` - For system status

### Step 5: Configure Environment
Add to your `.env` file:
```env
DISCORD_TOKEN=your_bot_token_here
```

## 📢 What Gets Posted

### Daily Picks (9 AM)
- 🏆 **POTD** (Pick of the Day)
- 🔥 **RPOTD** (Risky Pick of the Day)
- 🎯 **TOTD** (Ticket of the Day)
- 💎 **RTOTD** (Risky Ticket of the Day)
- 🔥 **Streaks** (Dynamic streaks)

### System Alerts
- 🚨 **Startup/Shutdown** notifications
- ⚠️ **Health check** failures
- ❌ **API connectivity** issues
- ✅ **Successful operations**

### System Status
- 📊 **Performance metrics**
- 🏥 **Health status**
- 📈 **Success/error rates**

## 🎯 Example Discord Posts

### Pick of the Day
```
🏆 **PICK OF THE DAY**

**Player:** Ronald Acuna Jr. (Atlanta Braves)
**Prop:** Hits 1.5
**Confidence:** 45.5%
**Pick:** Over

🎯 **Confidence Score:** 45.5%
```

### Ticket of the Day
```
🎯 **TICKET OF THE DAY**

**8-Leg Ticket**

Leg 1: **Ronald Acuna Jr.** - Hits 1.5 (45.5%)
Leg 2: **Mike Trout** - Runs 0.5 (42.3%)
Leg 3: **Shohei Ohtani** - RBIs 0.5 (41.8%)
...
```

### System Alert
```
🚨 **System Alert**

Daily picks workflow failed: API timeout
Time: 2025-06-27 09:00:15
```

## 🔧 Testing Discord Integration

### Test Command
```bash
python test_discord_integration.py
```

### Manual Test
```python
import asyncio
from production_discord import ProductionDiscordBot

async def test():
    bot = ProductionDiscordBot()
    await bot.initialize("your_token_here")
    await bot.send_alert("Test message from Ghost AI 3.0")

asyncio.run(test())
```

## 🛠️ Troubleshooting

### "Discord not connected"
- Check bot token in `.env`
- Verify bot is invited to server
- Check bot permissions

### "Channel not found"
- Create required channels: `#picks`, `#alerts`, `#system`
- Check channel names match exactly

### "Permission denied"
- Give bot proper permissions
- Check bot role hierarchy

## 📊 Discord Features

### Rich Embeds
- **Color-coded** by pick type
- **Formatted stats** and confidence
- **Timestamps** and metadata

### Interactive Elements
- **Reactions** for tracking
- **Slash commands** (future)
- **Status indicators**

### Automated Posting
- **Scheduled** daily picks
- **Real-time** alerts
- **Performance** updates

## 🎯 Next Steps

1. **Set up Discord bot** (follow steps above)
2. **Test integration** with test script
3. **Configure channels** in your server
4. **Start production** with Discord enabled
5. **Monitor posts** for first few days

---

**🎉 Once configured, your Ghost AI 3.0 will automatically post daily picks to Discord!** 