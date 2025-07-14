# Tennis Local Data System Guide

## 🎾 Overview

This system downloads and stores comprehensive tennis data locally, eliminating API dependency issues and providing reliable data for making picks.

## 🚀 Quick Start

### 1. Download Tennis Data
```bash
python download_tennis_data.py
```

This will:
- Download 30 days of tennis fixtures
- Store player statistics locally
- Cache H2H (head-to-head) data
- Save odds and tournament information
- Test the local engine

### 2. Use Local Engine
```bash
python tennis_local_engine.py
```

This will:
- Generate tennis picks using local data
- No API calls required
- Fast and reliable

## 📁 Data Structure

```
data/tennis_local/
├── players/           # Player statistics
├── matches/           # Daily fixtures
├── h2h/              # Head-to-head records
├── odds/             # Match odds data
├── tournaments/      # Tournament information
└── stats/           # Additional statistics
```

## 🎯 What Gets Downloaded

### Player Data
- **ATP Top 50** players
- **WTA Top 50** players
- Player statistics and rankings
- Performance history

### Match Data
- **Fixtures** for next 30 days
- **Match details** and schedules
- **Tournament information**
- **Surface types** and conditions

### Historical Data
- **H2H records** between players
- **Match outcomes** and scores
- **Performance patterns**
- **Surface-specific stats**

### Odds Data
- **Live odds** for matches
- **Market information**
- **Betting lines**

## 🧠 Local Engine Features

### Pick Generation
- **Total Games** (Higher/Lower)
- **Aces** for individual players
- **Double Faults** for individual players
- **1st Set Total Games**
- **Surface-specific analysis**

### Data Analysis
- **H2H pattern analysis**
- **Player performance trends**
- **Tournament-specific insights**
- **Surface performance correlation**

### Confidence Scoring
- Based on **data quality**
- **Historical accuracy**
- **Sample size** of matches
- **Recent performance** trends

## 🔧 Configuration

### Environment Variables
```env
TENNIS_API_KEY=your_tennis_api_key_here
```

### Star Players (Auto-configured)
- **ATP Top 50** players
- **WTA Top 50** players
- **Major tournament** focus
- **Grand Slam** priority

## 📊 Data Management

### Automatic Updates
- **Daily fixture** updates
- **Player stats** refresh
- **H2H data** maintenance
- **Odds data** updates

### Data Retention
- **Player stats**: 7 days
- **H2H data**: 30 days
- **Odds data**: 6 hours
- **Fixtures**: 30 days

### Storage Optimization
- **Compressed JSON** storage
- **Efficient indexing**
- **Automatic cleanup**
- **Size monitoring**

## 🎯 Integration with Ghost AI

### Replace API Calls
```python
# Old way (API dependent)
from core.tennis_api_client import get_fixtures
fixtures = get_fixtures('2025-01-15')

# New way (local data)
from tennis_local_engine import TennisLocalEngine
engine = TennisLocalEngine()
picks = engine.generate_daily_tennis_picks('2025-01-15')
```

### Enhanced Reliability
- ✅ **No API rate limits**
- ✅ **No server downtime**
- ✅ **Faster response times**
- ✅ **Consistent data quality**

## 📈 Performance Benefits

### Speed
- **Instant data access**
- **No network delays**
- **Parallel processing**
- **Cached results**

### Reliability
- **No API failures**
- **Consistent availability**
- **Data integrity**
- **Backup capability**

### Cost Savings
- **Reduced API calls**
- **Lower bandwidth usage**
- **No rate limit costs**
- **Predictable expenses**

## 🔍 Monitoring & Maintenance

### Data Health Check
```bash
python tennis_local_engine.py
```

This will show:
- **Data summary**
- **Storage size**
- **Pick generation test**
- **Engine status**

### Regular Updates
```bash
# Update data weekly
python download_tennis_data.py
```

### Data Backup
```bash
# Backup local data
cp -r data/tennis_local/ backup/tennis_data_$(date +%Y%m%d)/
```

## 🎾 Example Output

### Data Summary
```
📊 Local Data Summary:
   Players: 1,247
   Matches: 892
   H2H Records: 3,456
   Odds Data: 1,234
   Tournaments: 45
   Total Size: 156.7 MB
```

### Generated Picks
```
🎯 Generated 15 picks for 2025-01-15:
1. N. Djokovic vs C. Alcaraz - Total Games 20.5 Higher (65%)
2. I. Swiatek - Aces 4.5 Higher (70%)
3. C. Gauff - Double Faults 2.5 Lower (65%)
4. D. Medvedev vs A. Zverev - 1st Set Total Games 9.5 Higher (60%)
5. E. Rybakina - Aces 5.5 Higher (75%)
```

## 🚨 Troubleshooting

### No API Key
```
❌ No tennis API key found!
Please set TENNIS_API_KEY environment variable
```

### Download Failed
```
❌ Download failed: [Error details]
```
- Check internet connection
- Verify API key validity
- Check API rate limits

### Engine Test Failed
```
❌ Engine test failed: [Error details]
```
- Ensure data was downloaded successfully
- Check file permissions
- Verify data integrity

## 🎯 Next Steps

1. **Run the download script** to get initial data
2. **Test the local engine** to verify functionality
3. **Integrate with Ghost AI** to replace API calls
4. **Set up regular updates** for fresh data
5. **Monitor performance** and data quality

## 📞 Support

- **Data issues**: Check API key and connectivity
- **Engine problems**: Verify data download completed
- **Integration issues**: Review code examples above
- **Performance**: Monitor storage and update frequency

Your tennis data is now stored locally and ready for reliable pick generation! 🎾 