# Ghost AI 3.0 - Advanced Sports Betting Intelligence System

A sophisticated sports betting AI system with advanced odds intelligence, prop evaluation, confidence scoring, and automated ticket generation. Ghost AI combines real-time odds tracking, book behavior analysis, and machine learning to identify value opportunities across MLB and WNBA.

## 🚀 Core Features

### **Odds Intelligence Engine**
- **Real-time Odds Tracking**: Monitors odds movement across all major sportsbooks
- **CLV (Closing Line Value) Analysis**: Tracks posted vs closing odds to measure edge
- **Book Trap Detection**: Identifies juice traps, hidden demons, and book panic
- **Trend Analysis**: Tracks player prop trends and market movements
- **Historical Threading**: Per-player, per-stat memory with streak detection

### **Advanced Confidence Engine**
- **Multi-Factor Analysis**: Combines odds movement, historical performance, and market stability
- **Risk Assessment**: MEDIUM/HIGH/LOW risk ratings with detailed recommendations
- **Enhanced Scoring**: Sophisticated confidence algorithms beyond basic calculations
- **Market Stability Scoring**: Volatility analysis for prop types

### **Automated Ticket Generation**
- **Smart Prop Selection**: AI-driven prop evaluation and selection
- **Risk Management**: Built-in safeguards and confidence thresholds
- **Multi-Leg Optimization**: Intelligent parlay construction
- **Real-time Updates**: Continuous monitoring and adjustment

### **Reverse Engineering System**
- **W/L Result Tracking**: Automated processing of game outcomes
- **Streak Management**: Tracks winning/losing streaks with smart bankroll management
- **Learning Integration**: Uses results to improve future predictions
- **Memory Persistence**: Saves learning across sessions

### **Discord Integration**
- **Real-time Commands**: `/odds_history`, `/trend_analysis`, `/clv_dashboard`
- **Live Notifications**: Instant updates on odds movements and opportunities
- **Volatility Reports**: Shows most/least volatile props
- **Performance Tracking**: Real-time statistics and performance metrics

## 🏈 Supported Sports

| Sport | Description | Key Metrics | Odds Intelligence |
|-------|-------------|-------------|-------------------|
| **MLB** | Major League Baseball | Hits, Strikeouts, Home Runs, RBIs | ✅ Full Support |
| **WNBA** | Women's Basketball | Points, Rebounds, Assists, 3PT | ✅ Full Support |

## 📁 Directory Structure

```
Ghost AI 3.0/
├── ghost_ai.py                    # Main application entry point
├── ghost_odds_intelligence.py     # Odds intelligence system
├── mlb_props.py                   # MLB prop fetching
├── wnba_props.py                  # WNBA prop fetching
├── generate_tickets.py            # Ticket generation engine
├── run_ghost_with_odds_analyzer.bat  # Startup script with reverse engineering
│
├── ghost_core/                    # Core processing modules
│   ├── api/                       # API integrations
│   │   ├── oddsapi_handler.py     # OddsAPI integration
│   │   └── mysportsfeeds_handler.py # Stats API
│   ├── utils/                     # Utility functions
│   │   ├── odds_tracker.py        # Odds movement tracking
│   │   ├── line_movement.py       # Line movement analysis
│   │   └── cleanup.py            # System maintenance
│   ├── discord/                   # Discord integration
│   │   ├── odds_commands.py       # Odds intelligence commands
│   │   ├── betting_commands.py    # Betting commands
│   │   └── admin.py              # Admin commands
│   └── config/                    # Configuration
│       ├── mlb_prop_types.py      # MLB prop definitions
│       └── wnba_prop_types.py     # WNBA prop definitions
│
├── odds_reverse_engineering_test/ # Reverse engineering system
│   ├── auto_odds_analyzer.py      # Automated odds analysis
│   ├── odds_reverse_engine.py     # Reverse engineering engine
│   ├── start_auto_analyzer.py     # Startup script
│   ├── data/                      # Analysis data storage
│   └── logs/                      # System logs
│
├── ghost_ai_core_memory/          # Core memory and data
│   ├── tickets/                   # Ticket storage
│   │   ├── posted/                # Posted tickets
│   │   ├── analyzed/              # Enhanced analysis
│   │   ├── results/               # Game results
│   │   └── generated/             # Generated tickets
│   ├── odds_analysis/             # Odds intelligence data
│   ├── config/                    # Configuration files
│   ├── logs/                      # System logs
│   └── streaks/                   # Streak tracking
│
├── mlb_game_props/                # MLB prop data storage
├── wnba_game_props/               # WNBA prop data storage
├── odds_memory/                   # Odds tracking memory
├── logs/                          # Application logs
├── config.json                    # Main configuration
├── requirements.txt               # Python dependencies
├── VNC_SETUP.md                   # Remote access setup
└── README.md                      # This file
```

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.11 or higher
- Windows 10/11 (tested on Windows 10.0.26100)
- Discord Bot Token
- OddsAPI Key (for real-time odds data)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd "Ghost AI 3.0"

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
```

### Configuration
1. **Environment Variables** (`.env`)
   ```
   DISCORD_TOKEN=your_discord_bot_token
   ODDS_API_KEY=your_oddsapi_key
   MIN_CONFIDENCE=0.8
   MAX_DAILY_TICKETS=10
   DEBUG_MODE=true
   ```

2. **Main Configuration** (`config.json`)
   - Sports settings and prop types
   - Confidence thresholds
   - Discord channel IDs
   - Feature toggles

## 🚀 Usage

### Starting Ghost AI
```bash
# Start Ghost AI only
python ghost_ai.py

# Start Ghost AI with reverse engineering system
run_ghost_with_odds_analyzer.bat
```

### Discord Commands

#### **Odds Intelligence Commands**
- `/odds_history [player] [stat] [sport]` - View odds history for a player
- `/trend_analysis [player] [stat] [sport]` - Get trend analysis and trap detection
- `/clv_dashboard [days] [sport]` - View CLV (Closing Line Value) dashboard
- `/volatility_report [days] [sport]` - View volatility report for all props
- `/odds_summary` - Get summary of odds intelligence data

#### **Betting Commands**
- `/pick [sport]` - Get best pick for a sport
- `/streak [sport]` - Start a new streak
- `/stats` - View system statistics
- `/status` - Check system status

### Prop Data Management
```bash
# Fetch MLB props
python mlb_props.py

# Fetch WNBA props  
python wnba_props.py

# Generate tickets
python generate_tickets.py
```

## 🧠 How Ghost AI Works

### **1. Data Collection**
- **Real-time Props**: Fetches player props from FanDuel via OddsAPI
- **Historical Data**: Stores odds history per player/stat combination
- **Game Context**: Includes team matchups, game times, and venue data

### **2. Odds Intelligence Analysis**
- **Trend Tracking**: Monitors odds movement (rising/falling/stable)
- **Trap Detection**: Identifies juice traps, sharp movements, and book behavior
- **CLV Calculation**: Compares posted odds to closing odds
- **Market Stability**: Scores volatility and stability for prop types

### **3. Confidence Scoring**
- **Multi-Factor Model**: Combines odds movement, historical performance, and market analysis
- **Risk Assessment**: Provides MEDIUM/HIGH/LOW risk ratings
- **Enhanced Scoring**: Sophisticated algorithms beyond basic calculations
- **Recommendations**: Detailed guidance on prop selection

### **4. Ticket Generation**
- **Smart Selection**: AI-driven prop evaluation and selection
- **Risk Management**: Built-in safeguards and confidence thresholds
- **Multi-Leg Optimization**: Intelligent parlay construction
- **Real-time Updates**: Continuous monitoring and adjustment

### **5. Reverse Engineering & Learning**
- **W/L Tracking**: Automated processing of game outcomes
- **Memory Updates**: Updates odds engine with actual results
- **Streak Management**: Tracks winning/losing streaks
- **Learning Integration**: Uses results to improve future predictions

## 📊 Advanced Features

### **Odds Intelligence Engine**
- **Per-Player Memory**: Stores odds history per player/stat combination
- **Book Behavior Analysis**: Detects patterns in book adjustments
- **Juice Analysis**: Identifies sharp juice imbalances and traps
- **Market Movement Tracking**: Monitors line movements and trends

### **Reverse Engineering System**
- **24/7 Monitoring**: Automatically processes new tickets and results
- **Enhanced Analysis**: Adds confidence scores, risk assessments, and recommendations
- **Results Processing**: Automatically updates tracking when results files are added
- **Learning Persistence**: Saves learning across sessions

### **Discord Integration**
- **Real-time Commands**: Live odds intelligence and analysis
- **Volatility Reports**: Shows most/least volatile props
- **Performance Tracking**: Real-time statistics and performance metrics
- **Automated Notifications**: Instant updates on opportunities

## 🔧 Development

### Running Tests
```bash
# Test odds intelligence
python test_oddsapi_odds_tracking.py

# Test reverse engineering
cd odds_reverse_engineering_test
python test_results_processing.py
```

### Logs and Monitoring
- **Application Logs**: `logs/ghost_ai.log`
- **Odds Intelligence Logs**: `odds_reverse_engineering_test/logs/`
- **Performance Data**: `ghost_ai_core_memory/odds_analysis/`

## 📈 Performance Metrics

The system tracks comprehensive performance metrics including:
- **Success Rates**: By sport, player, and prop type
- **Confidence Accuracy**: How well confidence scores predict outcomes
- **Value Generation**: Expected value and actual returns
- **Streak Performance**: Win/loss streak analysis
- **Market Efficiency**: Odds movement and closing line value

## 🔒 Security & Best Practices

- **API Key Management**: Store sensitive keys in environment variables
- **Rate Limiting**: Built-in protection against API rate limits
- **Error Handling**: Comprehensive error handling and recovery
- **Logging**: Detailed logging for debugging and monitoring
- **Backup Systems**: Automatic backup of critical data

## 🤝 Contributing

This is a private AI system designed for advanced sports betting analysis. The system is continuously improved based on performance data and market analysis.

## 📄 License

Private system - All rights reserved.

---

**Ghost AI 3.0** - Advanced sports betting intelligence powered by machine learning and real-time odds analysis. 

## 🌐 API & ChatGPT Integration (Ghost AI 3.0+)

### New API Endpoints (FastAPI)

| Endpoint              | Method | Description                                              |
|----------------------|--------|----------------------------------------------------------|
| /generate-tickets    | POST   | Generate tickets for any sport (MLB, WNBA, tennis, golf) |
| /performance         | GET    | Get performance tracking from GhostBrain                 |
| /self-awareness      | GET    | Get self-awareness/feature status from GhostBrain        |
| /config              | GET    | Get config (features, etc)                               |
| /chatgpt-data        | POST   | Custom ChatGPT data pulls (news, context, stats, etc)    |

**Example:**
```bash
curl -X POST http://localhost:8000/generate-tickets -H "Content-Type: application/json" -d '{"sport": "tennis", "date": "2024-07-10"}'
```

### ChatGPT Integration
- **Tennis/Golf:** Uses ChatGPT to pull daily matchups, tag favorites/underdogs, detect trap matches, and estimate win probabilities.
- **All Sports:** ChatGPT can be used for news/context pulls, sentiment analysis, ticket explanations, and grading for unsupported sports.
- **Caching & Cost Control:** All ChatGPT responses are cached by date/sport/query to minimize API calls and cost.

### Robustness & Monitoring
- **Circuit Breaker:** If too many errors occur with ChatGPT/OpenAI, further calls are blocked for 5 minutes and fallback/cached data is used.
- **Rate Limiting:** Max 20 ChatGPT calls per minute; excess calls use fallback/cached data.
- **Logging:** All ChatGPT errors, rate limits, and circuit breaker events are logged to `data/cache/chatgpt_fetcher.log`.
- **Historical Archiving:**
  - All tickets: `data/historical/props/tickets_history.json`
  - All ChatGPT pulls: `data/cache/chatgpt_fetches.json`

### How to Use
- Use the `/generate-tickets` endpoint to generate tickets for any supported sport, including tennis/golf (no OddsAPI required).
- Use `/chatgpt-data` for custom context/news/stat pulls or explanations.
- Monitor logs and archives for all ChatGPT activity and ticket history.

--- 