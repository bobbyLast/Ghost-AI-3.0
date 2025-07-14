# Ghost AI Odds Reverse Engineering Engine

A comprehensive system that analyzes player prop odds movement patterns and confidence trends, then integrates with Ghost AI to provide enhanced analysis without recalculating historical data.

## 🎯 Complete Workflow

### 1. **Reverse Engine Analyzes Tickets** 🔍
- Monitors `ghost_ai_core_memory/tickets/posted/` for new tickets
- Analyzes each ticket with odds reverse engineering
- Identifies hot picks, trap risks, and confidence trends
- Calculates enhanced confidence scores

### 2. **Posts Enhanced Analysis** 📢
- Posts enhanced tickets to Discord with detailed analysis
- Shows trend tags, ghost reads, and risk assessments
- Provides recommendations for each selection
- Updates confidence scores based on odds patterns

### 3. **Saves Data for AI** 💾
- Saves reverse engine analysis to `ghost_ai_core_memory/odds_analysis/`
- Stores odds memory for future reference
- Creates current analysis summary for quick access
- **Eliminates need for Ghost AI to recalculate 5 games back**

## 🚀 Quick Start

### Run Both Systems Together
```bash
# Start both Ghost AI and Auto Analyzer
start_ghost_ai_with_analyzer.bat
```

### Run Auto Analyzer Only
```bash
cd odds_reverse_engineering_test
python start_auto_analyzer.py
```

### Test the System
```bash
cd odds_reverse_engineering_test
python test_engine.py
```

## 📁 File Structure

```
odds_reverse_engineering_test/
├── odds_reverse_engine.py          # Main reverse engineering engine
├── auto_odds_analyzer.py           # 24/7 automated analyzer
├── ai_data_loader.py               # Data loader for Ghost AI
├── ghost_ai_integration.py         # Integration examples
├── start_auto_analyzer.py          # Auto analyzer runner
├── test_engine.py                  # Test suite
├── test_data_generator.py          # Mock data generator
├── data/
│   ├── prop_memory.json           # Odds memory storage
│   └── analysis_summary.json      # Current analysis summary
└── logs/
    └── auto_analyzer.log          # Analysis logs
```

## 🔄 How It Works

### Step 1: Ticket Analysis
```python
# Auto analyzer monitors posted tickets
analyzer = AutoOddsAnalyzer()
await analyzer.start_monitoring()

# When new tickets are found:
enhanced_tickets = await analyzer.analyze_tickets(tickets)
```

### Step 2: Enhanced Analysis
Each ticket gets enhanced with:
- **Confidence Drift Analysis**: Tracks odds movement patterns
- **Market Comparison**: Compares to current market odds
- **Trend Tags**: Identifies hot picks and trap risks
- **Ghost Reads**: Provides market sentiment analysis
- **Risk Assessment**: Overall ticket risk level

### Step 3: Data Storage
```python
# Saves analysis for Ghost AI to use
analyzer.save_ai_analysis_data(enhanced_tickets, filename)
analyzer.odds_engine.save_memory()
```

### Step 4: Ghost AI Integration
```python
# Ghost AI can now pull pre-calculated data
loader = AIDataLoader()
enhanced_confidence = loader.get_enhanced_confidence_score(
    player_name, prop_type, base_confidence
)
```

## 🧠 AI Data Integration

### For Ghost AI Developers
The system provides several ways to integrate:

#### 1. **Enhanced Confidence Scores**
```python
from ai_data_loader import AIDataLoader

loader = AIDataLoader()
enhanced_confidence = loader.get_enhanced_confidence_score(
    "Mike Trout", "hits", 0.75
)
# Returns: 0.85 (boosted due to hot pick status)
```

#### 2. **Hot Picks Detection**
```python
hot_picks = loader.get_hot_picks()
# Returns: [{"player": "Mike Trout", "prop": "hits", "trend_tag": "🔥 HOT"}]
```

#### 3. **Trap Risk Avoidance**
```python
if loader.is_trap_risk("Player Name", "prop_type"):
    # Skip this player in ticket generation
    pass
```

#### 4. **Trend Analysis**
```python
trend = loader.get_player_confidence_trend("Player Name", "prop_type")
# Returns: "🔥 Rising" or "🔻 Falling"
```

## 📊 Analysis Features

### Confidence Drift Analysis
- Tracks odds movement over time
- Identifies rising vs falling confidence
- Calculates risk ratings
- Provides recommendations

### Market Comparison
- Compares current odds to historical patterns
- Identifies market inefficiencies
- Detects line movement significance

### Trend Identification
- **Hot Picks**: Players with rising confidence and positive trends
- **Trap Risks**: Players with falling confidence and negative patterns
- **Ghost Reads**: Market sentiment analysis

### Enhanced Scoring
- Base confidence from Ghost AI
- Hot pick bonuses (+0.15)
- Trap risk penalties (-0.20)
- Trend adjustments (±0.10)
- Risk rating adjustments (±0.15)

## 🔧 Configuration

### Auto Analyzer Settings
```python
# Check interval (seconds)
check_interval = 300  # 5 minutes

# Analysis freshness threshold
max_age_hours = 24   # Consider data fresh for 24 hours

# Discord integration
discord_enabled = True
```

### Data Storage Locations
```python
# Posted tickets
posted_tickets_dir = "ghost_ai_core_memory/tickets/posted"

# Enhanced tickets
analyzed_tickets_dir = "ghost_ai_core_memory/tickets/analyzed"

# AI analysis data
ai_data_dir = "ghost_ai_core_memory/odds_analysis"

# Results tracking
results_dir = "ghost_ai_core_memory/tickets/results"
```

## 📈 Performance Benefits

### Before (Ghost AI Only)
- ❌ Recalculates 5 games back every time
- ❌ No odds pattern recognition
- ❌ No confidence drift analysis
- ❌ No market comparison

### After (With Reverse Engine)
- ✅ Pre-calculated analysis data
- ✅ Odds pattern recognition
- ✅ Confidence drift tracking
- ✅ Market comparison
- ✅ Hot pick identification
- ✅ Trap risk avoidance

## 🎯 Use Cases

### 1. **Ticket Generation Enhancement**
```python
# Ghost AI generates base ticket
base_ticket = generate_ticket()

# Enhance with reverse engine analysis
integration = GhostAIIntegration()
enhanced_ticket = integration.enhance_ticket_with_reverse_analysis(base_ticket)
```

### 2. **Player Selection Filtering**
```python
# Check if player should be included
should_include = integration.should_include_player_in_ticket(
    player_name, prop_type, base_confidence
)
```

### 3. **Confidence Score Enhancement**
```python
# Get enhanced confidence score
enhanced_confidence = loader.get_enhanced_confidence_score(
    player_name, prop_type, base_confidence
)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **No Analysis Data Found**
```bash
# Check if auto analyzer is running
python start_auto_analyzer.py

# Check if tickets exist
ls ghost_ai_core_memory/tickets/posted/
```

#### 2. **Stale Analysis Data**
```bash
# Analysis data is older than 24 hours
# Auto analyzer should update automatically
# Or restart the analyzer
```

#### 3. **Integration Errors**
```python
# Check if data loader can access files
loader = AIDataLoader()
status = loader.get_analysis_status()
print(status)
```

### Log Files
- `odds_reverse_engineering_test/logs/auto_analyzer.log` - Auto analyzer logs
- `ghost_ai_core_memory/logs/` - Ghost AI logs

## 🔄 Continuous Operation

The system is designed to run 24/7:

1. **Ghost AI** generates and posts tickets
2. **Auto Analyzer** detects new tickets and analyzes them
3. **Enhanced Analysis** is posted to Discord
4. **Analysis Data** is saved for Ghost AI to use
5. **Ghost AI** uses pre-calculated data instead of recalculating

This creates a continuous feedback loop where:
- Reverse engine learns from posted tickets
- Ghost AI benefits from enhanced analysis
- No need to recalculate historical patterns
- System becomes more accurate over time

## 📞 Support

For issues or questions:
1. Check the log files for error messages
2. Verify file paths and permissions
3. Ensure both systems are running
4. Check if analysis data is fresh

The system is designed to be self-maintaining and will automatically handle most issues. 