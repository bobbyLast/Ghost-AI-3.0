# Ghost AI 4.0 Discord Setup - Complete Guide

## 🎯 Your Discord Configuration

### Bot Token
- **Token**: `summaries`
- **Status**: ✅ Configured

### Webhook URLs
- **Ticket Webhook**: `https://discord.com/api/webhooks/1386168741938597989/Ib-d9TDtSnd4gZ-C2JkKQ866p6fxAF3Ps4fLUhkGJYI_dZQCe8hCRBTODv1-vZV_U7Sy`
- **Update Webhook**: `https://discord.com/api/webhooks/1375912085762080868/qRsmIH92iKpMwrtt2TYWsRY1OkFerN61zFVGooCFZvae-liF5l_4ovbwpgv0b7nSOKJg`
- **Moneyline Webhook**: `https://discord.com/api/webhooks/1390410910392385756/w9-96vnCSQQjfu_hzesnaSt6MP3EEbC_5WuTGuQnvsKnxoxkS4cj8Nl3Z0KYqWnaV36z`

## 🚀 Quick Start

### 1. Run Environment Setup
```bash
python setup_discord_env.py
```

### 2. Start Ghost AI 4.0
```bash
python start_ghost_ai.py
```

## 📢 What Gets Posted Where

### Ticket Webhook
- 🎯 **Player Props** (MLB, WNBA, etc.)
- 🏆 **Pick of the Day (POTD)**
- 🔥 **Risky Pick of the Day (RPOTD)**
- 🎯 **Ticket of the Day (TOTD)**
- 💎 **Risky Ticket of the Day (RTOTD)**
- 🔥 **Dynamic Streaks**

### Moneyline Webhook
- ⚾ **Moneyline bets**
- 🏀 **Game winners**
- 🎯 **Head-to-head matchups**

### Update Webhook
- 📊 **Daily summaries**
- 🚨 **System alerts**
- ⚠️ **Health check failures**
- ✅ **Successful operations**
- 📈 **Performance metrics**

## 🤖 Discord Bot Commands

The Ghost AI bot supports these slash commands:

- `/status` - Show AI system status
- `/performance` - Show recent performance metrics
- `/help` - Show available commands

## 🔧 Environment Variables

Your system is configured with these environment variables:

```env
DISCORD_BOT_TOKEN=summaries
TICKET_WEBHOOK=https://discord.com/api/webhooks/1386168741938597989/Ib-d9TDtSnd4gZ-C2JkKQ866p6fxAF3Ps4fLUhkGJYI_dZQCe8hCRBTODv1-vZV_U7Sy
UPDATE_WEBHOOK=https://discord.com/api/webhooks/1375912085762080868/qRsmIH92iKpMwrtt2TYWsRY1OkFerN61zFVGooCFZvae-liF5l_4ovbwpgv0b7nSOKJg
MONEYLINE_WEBHOOK=https://discord.com/api/webhooks/1390410910392385756/w9-96vnCSQQjfu_hzesnaSt6MP3EEbC_5WuTGuQnvsKnxoxkS4cj8Nl3Z0KYqWnaV36z
```

## 🎯 Example Discord Posts

### Player Prop Ticket
```
🧠 AI-POWERED SELECTION

AI Analysis: AI analysis indicates strong value opportunity

AI Selections:
1. Ronald Acuna Jr. Hits 1.5 OVER (AI Confidence: 45%)
2. Mike Trout Runs 0.5 OVER (AI Confidence: 42%)
3. Shohei Ohtani RBIs 0.5 OVER (AI Confidence: 41%)

Ticket Info: AI Confidence: 43% | Legs: 3 | Ticket ID: TKT-001
```

### Moneyline Bet
```
🧠 MONEYLINE SELECTION

AI Analysis: Strong team performance indicators

AI Selections:
1. Atlanta Braves ML -150 (AI Confidence: 65%)
2. Los Angeles Dodgers ML -120 (AI Confidence: 58%)

Ticket Info: AI Confidence: 62% | Legs: 2 | Ticket ID: ML-001
```

### System Update
```
📊 Ghost AI 4.0 Daily Summary

✅ Generated 15 tickets today
🎯 8 tickets posted to Discord
📈 73% confidence average
🚀 System running optimally
```

## 🔍 Testing Your Setup

### Test Webhooks
```bash
python setup_discord_env.py
```

### Test Bot Commands
1. Invite the bot to your Discord server
2. Use `/status` to check system status
3. Use `/performance` to see recent metrics

## 🚨 Troubleshooting

### Webhook Not Working
- Check webhook URL is correct
- Ensure Discord server has proper permissions
- Verify bot token is valid

### Bot Not Responding
- Check bot token is correct
- Ensure bot has proper permissions
- Verify bot is online in Discord

### No Posts Appearing
- Check webhook URLs are correct
- Verify AI is generating tickets
- Check system logs for errors

## 🎉 Success!

Your Ghost AI 4.0 Discord integration is now fully configured and ready to:

- ✅ Post tickets to ticket webhook
- ✅ Post moneyline bets to moneyline webhook  
- ✅ Post updates and summaries to update webhook
- ✅ Respond to bot commands
- ✅ Provide system status and performance metrics

The AI will automatically post to the appropriate webhooks based on the type of content being generated. 