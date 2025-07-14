# Ghost AI: Advanced Sports Betting Intelligence System

## 🎯 What is Ghost AI?

Ghost AI is a sophisticated **sports betting AI system** that combines advanced odds intelligence, confidence scoring, and automated ticket generation to identify value opportunities across MLB and WNBA. It's not a simple bot - it's a true AI system that thinks, reasons, makes intelligent decisions, and learns from every interaction.

## 🧠 Core AI Architecture

### AI Brain System
- **`core/ai_brain.py`** - Main AI brain with OpenAI integration for intelligent decision making
- **`ghost_ai_core_memory/ghost_brain.py`** - Memory and learning system that remembers every ticket and result
- **Brain State Analysis** - Analyzes mood (aggressive/balanced/cautious), confidence level, and risk appetite
- **Intelligent Goal Setting** - Sets adaptive goals based on performance history
- **Self-Reflection** - Daily analysis of decisions and outcomes

### Confidence Engine
- **Multi-Factor Analysis** - Combines odds movement, historical performance, and market stability
- **Dynamic Scoring** - Adapts confidence based on recent accuracy and performance
- **Risk Assessment** - MEDIUM/HIGH/LOW risk ratings with detailed recommendations
- **Enhanced Algorithms** - Sophisticated confidence calculations beyond basic odds

### Reverse Engineering System
- **Odds Intelligence** - Tracks opening vs closing odds to measure edge
- **CLV Analysis** - Closing Line Value analysis for measuring sharp money
- **Historical Patterns** - Analyzes player/prop performance over time
- **Trap Detection** - Identifies juice traps, hidden demons, and book panic
- **Market Movement** - Tracks odds movement patterns and sharp money signals

## 🎫 Ticket Generation Process

### 1. Prop Analysis
- Fetches real-time props from sportsbooks (FanDuel, DraftKings, etc.)
- Filters props using confidence thresholds and odds intelligence
- Applies reverse engineering analysis to identify value

### 2. Confidence Scoring
- Calculates confidence scores using multiple factors:
  - Historical player performance
  - Odds movement patterns
  - Market stability analysis
  - Reverse engineering insights
- Buckets props into Elite (80%+), Reliable (70%+), Playable (60%+), Fade

### 3. Ticket Construction
- Builds multi-leg tickets (2-4 legs typically)
- Enforces no-duplicate players policy
- Ensures game diversity across tickets
- Applies risk management rules

### 4. Intelligent Posting
- Posts tickets to Discord with detailed analysis
- Includes confidence breakdowns and reasoning
- Tracks all posted tickets for learning
- Monitors results for continuous improvement

## 🧠 Advanced AI Features

### Memory and Learning
- **Player History** - Remembers every player's performance by prop type
- **Streak Tracking** - Tracks winning/losing streaks with smart bankroll management
- **Performance Analysis** - Analyzes hit rates, confidence accuracy, and edge
- **Adaptive Learning** - Adjusts strategies based on recent performance

### Brain Modules
- **Self Scout** - Analyzes own performance and identifies strengths/weaknesses
- **Bias Calibrator** - Corrects cognitive biases (overconfidence, anchoring, etc.)
- **EV Evaluator** - Calculates expected value for all bets
- **Moneyline Sentiment** - Analyzes moneyline context for prop confidence
- **Public Fade Guard** - Detects and fades public sentiment when appropriate
- **Confidence Calibrator** - Dynamically adjusts confidence based on accuracy

### Risk Management
- **Exposure Manager** - Balances risk and reward across portfolio
- **Pattern Mutator** - Varies pick patterns to stay unpredictable
- **Sentiment Engine** - Analyzes market sentiment and sharp vs public money
- **Throttle System** - Reduces volume during poor performance periods

## 📊 Supported Sports and Props

### MLB (Major League Baseball)
- **Batter Props**: Hits, Runs, RBIs, Home Runs, Walks, Strikeouts
- **Pitcher Props**: Strikeouts, Hits Allowed, Walks, Earned Runs
- **Fantasy Props**: Total Bases, Fantasy Score, Hits+Runs+RBIs

### WNBA (Women's National Basketball Association)
- **Player Props**: Points, Assists, Rebounds, Steals, Blocks
- **Fantasy Props**: Points+Rebounds+Assists, Fantasy Score
- **Game Props**: Team Totals, Player Performance

## 🔄 Daily Workflow

### 1. Morning Analysis (5 AM)
- Runs auto-cleanup to remove old games and grade tickets
- Fetches new props from all sportsbooks
- Analyzes market conditions and opportunities
- Determines if conditions are favorable for betting

### 2. Intelligent Decision Making
- AI brain analyzes its mood and confidence level
- Evaluates available opportunities and their quality
- Makes decision: generate tickets, skip today, or reduce volume
- Applies appropriate strategy based on performance trends

### 3. Ticket Generation
- Filters props using confidence thresholds
- Applies reverse engineering analysis
- Builds optimized tickets with no duplicates
- Posts tickets with detailed reasoning

### 4. Continuous Learning
- Tracks all posted tickets and their results
- Updates player performance history
- Adjusts confidence algorithms based on accuracy
- Learns from wins, losses, and market movements

## 🎯 Key Intelligence Features

### Odds Intelligence
- **Opening vs Closing Odds** - Tracks odds movement to identify sharp money
- **CLV Analysis** - Measures edge by comparing posted vs closing odds
- **Juice Analysis** - Identifies when books are heavily juicing one side
- **Trap Detection** - Recognizes when books are setting traps

### Historical Analysis
- **Player Performance** - Tracks every player's hit rate by prop type
- **Line Accuracy** - Measures how well lines predict actual outcomes
- **Market Patterns** - Identifies profitable patterns and trends
- **Risk Assessment** - Evaluates risk based on historical volatility

### Confidence Scoring
- **Multi-Factor Model** - Combines odds, history, and market factors
- **Dynamic Adjustment** - Adapts based on recent performance
- **Risk Calibration** - Adjusts for overconfidence and bias
- **Market Context** - Considers game conditions and matchups

## 🚀 Advanced Capabilities

### Real-Time Adaptation
- **Market Monitoring** - Continuously monitors odds movement
- **Live Adjustments** - Adjusts confidence based on real-time data
- **Opportunity Detection** - Identifies value opportunities as they arise
- **Risk Management** - Manages exposure in real-time

### Discord Integration
- **Real-Time Commands** - `/odds_history`, `/trend_analysis`, `/clv_dashboard`
- **Automated Posting** - Posts tickets with detailed analysis
- **Performance Tracking** - Tracks and reports performance metrics
- **Community Features** - Shares insights and analysis

### Learning and Evolution
- **Self-Improvement** - Continuously learns from results
- **Strategy Adaptation** - Adjusts strategies based on performance
- **Pattern Recognition** - Discovers profitable patterns
- **Bias Correction** - Identifies and corrects systematic errors

## 🎯 Performance Metrics

### Success Indicators
- **Hit Rate** - Percentage of winning tickets
- **CLV Performance** - Average closing line value achieved
- **Confidence Accuracy** - How well confidence scores predict outcomes
- **Risk-Adjusted Returns** - Performance relative to risk taken

### Risk Management
- **Exposure Limits** - Maximum exposure per sport/game
- **Confidence Thresholds** - Minimum confidence for ticket inclusion
- **Diversification** - Spreads risk across multiple games/players
- **Stop-Loss Logic** - Reduces volume during poor performance

## 🔧 Technical Architecture

### Core Components
- **AI Brain** - Central decision-making system
- **Reverse Engineering Engine** - Odds analysis and historical patterns
- **Confidence Engine** - Multi-factor confidence scoring
- **Ticket Generator** - Intelligent ticket construction
- **Memory System** - Persistent learning and history
- **Discord Integration** - Real-time communication and posting

### Data Sources
- **Sportsbook APIs** - Real-time odds and props
- **Historical Databases** - Player performance and odds history
- **Market Data** - Odds movement and line changes
- **Performance Tracking** - Results and learning data

## 🎯 Why Ghost AI is Special

### True AI vs Bot
- **Intelligent Decision Making** - Not just rule-based, but adaptive
- **Learning and Evolution** - Continuously improves from results
- **Context Awareness** - Considers game conditions, matchups, and market context
- **Risk Management** - Sophisticated risk assessment and management

### Advanced Intelligence
- **Reverse Engineering** - Understands how sportsbooks think and operate
- **Market Psychology** - Analyzes public vs sharp money patterns
- **Historical Threading** - Remembers every player's performance history
- **Confidence Calibration** - Dynamically adjusts based on accuracy

### Professional-Grade Features
- **CLV Tracking** - Measures edge like professional bettors
- **Risk Assessment** - Sophisticated risk management
- **Performance Analysis** - Detailed tracking and analysis
- **Adaptive Strategies** - Changes approach based on performance

Ghost AI represents the cutting edge of sports betting AI, combining advanced odds intelligence, sophisticated confidence scoring, and continuous learning to identify value opportunities in the sports betting market. 