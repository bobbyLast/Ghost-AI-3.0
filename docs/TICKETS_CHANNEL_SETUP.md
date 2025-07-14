# Tickets Channel Setup Guide

## 🎯 **Current Discord Channel Setup**

Your Discord bot is currently looking for these channels:

### **Required Channels:**
- `#picks` - For single picks (POTD, RPOTD)
- `#tickets` - For multi-leg tickets (TOTD, RTOTD) ⭐ **NEW!**
- `#alerts` - For system alerts and notifications
- `#system` - For system status and health updates

## 🔧 **How to Set Up Tickets Channel**

### **Step 1: Create the Tickets Channel**
1. In your Discord server, right-click in the channel list
2. Select "Create Channel"
3. Name it `tickets` (or `#tickets`)
4. Set it as a Text Channel
5. Click "Create Channel"

### **Step 2: Set Bot Permissions**
Make sure your Ghost AI bot has these permissions in the `#tickets` channel:
- ✅ Send Messages
- ✅ Embed Links
- ✅ Read Message History

### **Step 3: Verify Channel Setup**
Your Discord server should now have:
```
📁 Your Server
├── #picks          (single picks)
├── #tickets        (multi-leg tickets) ⭐
├── #alerts         (system alerts)
└── #system         (system status)
```

## 📢 **What Gets Posted Where**

### **#picks Channel:**
- 🏆 **Pick of the Day** (single player prop)
- 🔥 **Risky Pick of the Day** (single player prop)
- 🔥 **Streaks** (dynamic streaks)

### **#tickets Channel:**
- 🎯 **Ticket of the Day** (multi-leg ticket)
- 💎 **Risky Ticket of the Day** (multi-leg ticket)

### **#alerts Channel:**
- 🚨 System alerts
- ⚠️ Health check failures
- ❌ API connectivity issues

### **#system Channel:**
- 📊 Performance metrics
- 🏥 Health status
- 📈 Success/error rates

## 🎯 **Example Tickets Channel Posts**

### **Ticket of the Day:**
```
🎯 **TICKET OF THE DAY**

**4-Leg Ticket**

Leg 1: **Paige Bueckers** - Player Threes 1.5 (68.8%)
Leg 2: **Marina Mabrey** - Player Threes 1.5 (66.7%)
Leg 3: **Jewell Loyd** - Player Threes 1.5 (65.8%)
Leg 4: **Caitlin Clark** - Player Threes 3.5 (65.8%)

**Overall Confidence:** 66.8%
```

### **Risky Ticket of the Day:**
```
💎 **RISKY TICKET OF THE DAY**

**5-Leg Ticket**

Leg 1: **Jackie Young** - Player Rebounds 4.5 (64.0%)
Leg 2: **Kayla Thornton** - Player Threes 1.5 (64.0%)
Leg 3: **Arike Ogunbowale** - Player Assists 3.5 (60.8%)
Leg 4: **Arike Ogunbowale** - Player Points 16.5 (55.0%)
Leg 5: **Arike Ogunbowale** - Player Points 16.5 (56.8%)

**Overall Confidence:** 60.1%
```

## 🔍 **Check Your Current Setup**

Run this command to see what channels your bot can find:
```bash
python check_discord_channels.py
```

## ✅ **Verification Steps**

1. **Create the #tickets channel** in your Discord server
2. **Check bot permissions** in the new channel
3. **Restart your production system** to pick up the new channel
4. **Wait for 9 AM** for the next daily picks to be posted
5. **Check both #picks and #tickets** channels for posts

## 🚀 **After Setup**

Once you have the `#tickets` channel set up:
- **Single picks** will go to `#picks`
- **Multi-leg tickets** will go to `#tickets`
- **System alerts** will go to `#alerts`
- **System status** will go to `#system`

This gives you a clean separation between different types of picks and makes it easier to track tickets separately from single picks!

---

**🎉 Your Discord integration will be even better organized with the dedicated tickets channel!** 