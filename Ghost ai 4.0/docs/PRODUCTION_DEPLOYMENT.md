# Ghost AI 3.0 Production Deployment Guide

## 🚀 Overview

This guide will help you deploy Ghost AI 3.0 for 24/7 autonomous operation with Discord integration, health monitoring, and automated grading.

## 📋 Prerequisites

### Required Environment Variables
Create a `.env` file in your project root:

```env
# Required
ODDS_API_KEY=your_oddsapi_key_here

# Optional (for Discord integration)
DISCORD_TOKEN=your_discord_bot_token_here
```

### Discord Setup (Optional but Recommended)
1. Create a Discord bot at https://discord.com/developers/applications
2. Get your bot token
3. Create these channels in your Discord server:
   - `#picks` - For daily picks
   - `#alerts` - For system alerts
   - `#system` - For system status

## 🎯 Production Components

### 1. Production Orchestrator (`production_orchestrator.py`)
- **24/7 Autonomous Operation**
- **Automated Daily Picks** (9 AM daily)
- **Health Monitoring** (every 5 minutes)
- **Performance Tracking**
- **Error Recovery**

### 2. Discord Integration (`production_discord.py`)
- **Automated Pick Posting**
- **System Alerts**
- **Status Updates**
- **Rich Embeds**

### 3. Startup Scripts
- `start_production.py` - Python startup script
- `start_production.bat` - Windows batch file

## 🚀 Quick Start

### Option 1: Windows (Recommended)
```bash
# Double-click or run:
start_production.bat
```

### Option 2: Command Line
```bash
# Activate virtual environment
venv\Scripts\activate

# Start production system
python start_production.py
```

## 📊 System Features

### Daily Picks Workflow
1. **9:00 AM** - Generate daily picks
2. **Auto-post** to Discord (if configured)
3. **Save** picks to memory for tracking
4. **Health check** every 5 minutes

### Pick Types Generated
- 🏆 **POTD** (Pick of the Day)
- 🔥 **RPOTD** (Risky Pick of the Day)
- 🎯 **TOTD** (Ticket of the Day)
- 💎 **RTOTD** (Risky Ticket of the Day)
- 🔥 **Streaks** (Dynamic streak system)

### Health Monitoring
- **API Connectivity** checks
- **File System** health
- **Error Tracking**
- **Performance Metrics**

## 🔧 Configuration

### Production Settings
Edit `production_orchestrator.py` to customize:

```python
self.settings = {
    'daily_picks_time': '09:00',  # Change pick generation time
    'health_check_interval': 300,  # Health check frequency (seconds)
    'max_retries': 3,             # Error retry attempts
    'discord_channels': {          # Discord channel names
        'picks': 'picks',
        'alerts': 'alerts',
        'system': 'system'
    }
}
```

### Confidence Thresholds
Edit `ghost_core/daily_pick_manager.py`:

```python
# Current: 40% for testing
high_confidence_picks = [p for p in processed_props if p.get('confidence', 0) >= 0.4]

# Production: 60% recommended
high_confidence_picks = [p for p in processed_props if p.get('confidence', 0) >= 0.6]
```

## 📈 Monitoring & Logs

### Log Files
- `logs/production_orchestrator.log` - Main production logs
- `logs/production_startup.log` - Startup logs
- `logs/ghost_ai.log` - Ghost AI core logs
- `logs/DailyPickManager.log` - Daily picks logs

### Key Log Messages
```
✅ Daily picks workflow complete
✅ Generated 5 pick types
📢 Posted daily picks to Discord
🏥 Health check complete
```

### Performance Tracking
- **Successful runs** counter
- **Error count** tracking
- **Last daily picks** timestamp
- **System uptime** monitoring

## 🛠️ Troubleshooting

### Common Issues

#### 1. "No cached props found"
**Solution**: Copy recent prop files from archive:
```bash
copy "mlb_game_props\archive\props_mlb_*.json" "mlb_game_props\"
```

#### 2. "Discord not connected"
**Solution**: Check Discord token in `.env` file

#### 3. "API key not working"
**Solution**: Verify ODDS_API_KEY in `.env` file

#### 4. "No picks generated"
**Solution**: Lower confidence threshold temporarily for testing

### Health Check Commands
```bash
# Check system status
python -c "from production_orchestrator import ProductionOrchestrator; import asyncio; asyncio.run(ProductionOrchestrator().health_check())"

# Test daily picks
python test_daily_picks_simple.py

# Debug confidence scoring
python debug_confidence.py
```

## 🔄 Maintenance

### Daily Tasks
- **Monitor logs** for errors
- **Check Discord** for posted picks
- **Verify API** connectivity

### Weekly Tasks
- **Review performance** metrics
- **Clean old logs** (auto-cleanup handles this)
- **Update confidence** thresholds if needed

### Monthly Tasks
- **Backup system** data
- **Review pick accuracy**
- **Update player rosters**

## 🚨 Alerts & Notifications

### Discord Alerts
- **System startup/shutdown**
- **Daily picks generated**
- **Health check failures**
- **API connectivity issues**

### Alert Levels
- **Info** (Blue) - Normal operations
- **Warning** (Orange) - Minor issues
- **Error** (Red) - Critical problems
- **Success** (Green) - Successful operations

## 📊 Performance Metrics

### Tracked Metrics
- **Daily picks generated** per day
- **Confidence scores** distribution
- **API request count** and remaining
- **System uptime** percentage
- **Error rate** and types

### Optimization Tips
1. **Adjust confidence thresholds** based on performance
2. **Monitor API usage** to avoid rate limits
3. **Review pick accuracy** weekly
4. **Fine-tune risk tiers** based on results

## 🔐 Security Considerations

### Environment Variables
- **Never commit** `.env` files to version control
- **Use strong tokens** for Discord and API keys
- **Rotate keys** periodically

### File Permissions
- **Restrict access** to log files
- **Secure backup** directories
- **Monitor file** access patterns

## 🎯 Next Steps

After successful production deployment:

1. **Monitor** system for 1 week
2. **Adjust** confidence thresholds
3. **Fine-tune** Discord channels
4. **Implement** advanced features:
   - Automated grading
   - Risk management
   - Performance analytics
   - Multi-sport expansion

## 📞 Support

For issues or questions:
1. Check the logs first
2. Review this deployment guide
3. Test individual components
4. Check environment variables

---

**🎉 Congratulations!** Your Ghost AI 3.0 system is now running in production mode with 24/7 autonomous operation! 