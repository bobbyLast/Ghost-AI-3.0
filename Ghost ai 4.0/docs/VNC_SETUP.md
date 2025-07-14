# Ghost AI VNC Server Setup Guide

## 🚀 Quick Start

### Option 1: One-Click Startup (Recommended)
1. **Double-click** `start_ghost_ai_vnc.bat`
2. **Wait** for the deployment to complete
3. **Check** `logs/vnc_deployment.log` for status

### Option 2: Manual Startup
```bash
python vnc_deployment.py
```

## 📋 Prerequisites

### Environment Variables Required:
- `DISCORD_TOKEN` - Your Discord bot token
- `ODDS_API_KEY` - Your OddsAPI key

### Python Dependencies:
- All requirements in `requirements.txt` installed
- Virtual environment recommended (but not required)

## 🔧 VNC Server Configuration

### Recommended VNC Settings:
- **Resolution:** 1920x1080 or higher
- **Color Depth:** 24-bit
- **Auto-start:** Enable for automatic startup
- **Session Persistence:** Keep sessions alive

### Windows VNC Server Setup:
1. **Install VNC Server** (TightVNC, RealVNC, etc.)
2. **Set Display:** Configure for headless operation
3. **Auto-start:** Add to Windows startup programs
4. **Firewall:** Allow VNC connections on port 5900

## 📁 File Structure for VNC

```
Ghost AI 3.0/
├── vnc_deployment.py          # Main deployment script
├── start_ghost_ai_vnc.bat     # One-click startup
├── auto_cleanup_system.py     # Auto-cleanup system
├── ghost_ai.py               # Main Ghost AI
├── mlb_props.py              # MLB props fetcher
├── wnba_props.py             # WNBA props fetcher
├── generate_tickets.py       # Ticket generation
├── logs/                     # Log files
│   ├── vnc_deployment.log
│   ├── ghost_ai.log
│   └── auto_cleanup.log
├── mlb_props/               # MLB raw props
├── wnba_props/              # WNBA raw props
├── mlb_game_props/          # MLB game props
├── wnba_game_props/         # WNBA game props
└── ghost_ai_core_memory/    # AI memory and tracking
```

## 🔄 Deployment Sequence

The VNC deployment script runs this sequence:

1. **Environment Check** ✅
   - Verify environment variables
   - Create required directories
   - Check Python dependencies

2. **Auto-Cleanup** 🧹
   - Archive completed games
   - Trigger reverse engineering analysis
   - Clean up old data

3. **Props Fetching** 📊
   - Check if `mlb_props/` is empty → run `mlb_props.py`
   - Check if `wnba_props/` is empty → run `wnba_props.py`

4. **Ghost AI Startup** 🤖
   - Start main Ghost AI system
   - Begin ticket generation and posting

## 🏆 Unified Moneyline Ticket Generator Integration

As of Ghost AI 3.0, the system now includes a unified moneyline ticket generator that:
- Selects and posts only the single best bet per team vs team matchup (ML, run line, or total)
- Runs automatically as part of the main pipeline after all props and player tickets are processed
- Posts tickets directly to your configured Discord channel
- Uses the same environment variables and requirements as the main system

**No extra steps are needed**—the moneyline ticket generator is fully integrated. Just ensure:
- `moneyline_ticket_generator.py` is present in your project root
- Your `config/requirements.txt` is installed (`pip install -r config/requirements.txt`)
- Your Discord webhook and OddsAPI keys are set in your environment or config

**How it works:**
- After the main pipeline completes, the best bet ticket generator runs automatically
- Only one bet per matchup is posted, with sharp filtering and confidence thresholds
- Tickets appear in your Discord channel and are saved to the local archive

**Troubleshooting:**
- Check `logs/ghost_ai.log` for any errors related to moneyline ticketing
- Ensure your Discord webhook is valid and enabled in your config

## 📊 Monitoring

### Log Files to Monitor:
- `logs/vnc_deployment.log` - Deployment status
- `logs/ghost_ai.log` - Main AI operations
- `logs/auto_cleanup.log` - Cleanup operations

### Key Status Indicators:
- ✅ **Deployment Complete** - System ready
- 🔄 **Processing** - AI actively working
- ⚠️ **Warnings** - Non-critical issues
- ❌ **Errors** - Critical problems

## 🛠️ Troubleshooting

### Common Issues:

**1. Environment Variables Missing**
```
Error: Missing environment variables: ['DISCORD_TOKEN', 'ODDS_API_KEY']
```
**Solution:** Set environment variables in VNC server

**2. Python Dependencies Missing**
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:** Install requirements: `pip install -r requirements.txt`

**3. Directory Permissions**
```
PermissionError: [Errno 13] Permission denied
```
**Solution:** Run as administrator or check folder permissions

**4. Network Connectivity**
```
ConnectionError: Failed to connect to Discord/API
```
**Solution:** Check internet connection and firewall settings

### Emergency Restart:
```bash
# Stop all processes
taskkill /f /im python.exe

# Restart deployment
python vnc_deployment.py
```

## 🔒 Security Considerations

### VNC Security:
- **Use strong passwords** for VNC access
- **Enable encryption** if available
- **Restrict access** to trusted IPs
- **Regular updates** for VNC server

### Ghost AI Security:
- **Secure environment variables** (don't hardcode)
- **Regular log rotation** to prevent disk space issues
- **Monitor API usage** to avoid rate limits

## 📈 Performance Optimization

### VNC Server:
- **Dedicated resources** for Ghost AI
- **Regular restarts** (weekly recommended)
- **Monitor CPU/memory** usage

### Ghost AI:
- **Auto-cleanup** runs every hour
- **Log rotation** prevents disk bloat
- **Memory management** for long-running sessions

## 🎯 Success Indicators

Your Ghost AI is working correctly when you see:

1. **Discord Posts** - Tickets appearing in your channel
2. **Log Activity** - Regular processing in logs
3. **File Updates** - New props and game files
4. **W/L Tracking** - Results being recorded
5. **Streak Management** - Active streaks being tracked

## 📞 Support

If you encounter issues:
1. **Check logs** first for error details
2. **Restart deployment** using the batch file
3. **Verify environment** variables are set
4. **Check network** connectivity

---

**Ghost AI VNC Server is ready for deployment! 🚀** 