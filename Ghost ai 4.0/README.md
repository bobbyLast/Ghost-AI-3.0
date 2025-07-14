# Ghost AI 4.0 - Autonomous Sports Betting AI

🤖 **Ghost AI 4.0** is a fully autonomous sports betting AI that makes intelligent decisions, learns from results, and adapts its strategy continuously. The AI has its own mind and decides when to sleep and wake based on market conditions, performance, and opportunities.

## 🧠 AI Features

### Autonomous Decision Making
- **Self-Directed**: AI decides what actions to take without human intervention
- **Intelligent Sleep/Wake**: AI analyzes time, performance, and market conditions to decide when to work or rest
- **Adaptive Strategy**: AI learns from results and modifies its approach based on what's working
- **Market Analysis**: AI continuously analyzes market conditions and opportunities

### Sports Coverage
- **MLB**: Player props, game analysis, intelligent ticket generation
- **WNBA**: Player props, performance tracking, adaptive strategies
- **Tennis**: Star player detection, H2H analysis, prop generation
- **Multi-Sport**: Intelligent mixing of sports for optimal ticket combinations

### AI Brain Architecture
- **Memory System**: Persistent learning and performance tracking
- **Confidence Scoring**: AI evaluates its own confidence in predictions
- **Risk Management**: Intelligent risk assessment and ticket sizing
- **Performance Analytics**: Continuous self-evaluation and improvement

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone <repository-url>
cd "Ghost ai 4.0"

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and webhooks
```

### 2. Environment Variables
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_WEBHOOK_URL=your_main_webhook_url
TICKET_WEBHOOK=your_ticket_webhook_url
MONEYLINE_WEBHOOK=your_moneyline_webhook_url
UPDATE_WEBHOOK=your_update_webhook_url
TENNIS_API_KEY=your_tennis_api_key
```

### 3. Start Ghost AI 4.0
```bash
# Initialize the system
python start_ghost_ai.py

# Run the AI forever (recommended)
python run_ai_forever.py

# Or use the scheduler
python scheduler.py

# Or run main directly
python main.py
```

## 📁 Project Structure

```
Ghost ai 4.0/
├── ai_brain/                 # AI Brain and decision making
│   ├── ai_brain.py          # Main AI brain class
│   ├── ghost_brain.py       # Core memory and learning
│   ├── tennis_ai_fixtures_test.py  # Tennis AI analysis
│   └── brain_modules/       # Specialized AI modules
├── sports/                   # Sports-specific modules
│   ├── mlb/                 # MLB analysis and props
│   ├── wnba/                # WNBA analysis and props
│   └── shared/              # Shared sports utilities
├── system/                   # System management
│   └── enhanced_auto_cleanup.py  # Intelligent cleanup
├── config/                   # Configuration files
├── data/                     # Data storage
├── logs/                     # Log files
├── main.py                   # Main AI runner
├── scheduler.py              # AI scheduler
├── run_ai_forever.py         # Forever runner
└── start_ghost_ai.py         # Startup script
```

## 🎯 AI Capabilities

### Intelligent Decision Making
- **Market Analysis**: AI analyzes current market conditions and opportunities
- **Performance Tracking**: Continuous monitoring of win rates and ticket performance
- **Adaptive Strategy**: AI modifies its approach based on results
- **Risk Assessment**: Intelligent evaluation of ticket risk and confidence

### Autonomous Operations
- **Self-Directed Workflow**: AI decides what actions to take
- **Intelligent Sleep/Wake**: AI analyzes conditions to decide when to work or rest
- **Continuous Learning**: AI learns from every decision and result
- **Performance Optimization**: AI optimizes its strategy based on outcomes

### Sports Intelligence
- **Multi-Sport Analysis**: AI analyzes MLB, WNBA, and Tennis simultaneously
- **Player Performance**: AI tracks individual player performance and trends
- **Market Movement**: AI detects market shifts and opportunities
- **Prop Generation**: AI generates intelligent prop combinations

## 🔧 Configuration

### Discord Setup
The AI posts to multiple Discord webhooks:
- **Main Webhook**: General updates and summaries
- **Ticket Webhook**: Individual ticket posts
- **Moneyline Webhook**: Moneyline-specific tickets
- **Update Webhook**: Status updates and notifications

### AI Behavior Configuration
- **Sleep/Wake Logic**: AI considers time, performance, and market conditions
- **Ticket Generation**: AI decides how many tickets to generate based on opportunities
- **Risk Management**: AI evaluates confidence and adjusts ticket sizes
- **Learning Rate**: AI adapts its strategy based on recent performance

## 📊 AI Performance Tracking

The AI tracks its own performance:
- **Win Rate**: Overall success rate of predictions
- **Ticket Performance**: Individual ticket success tracking
- **Market Analysis**: Success rates by sport and prop type
- **Learning Progress**: How the AI improves over time

## 🤖 AI Commands

### Manual AI Control
```bash
# Run AI analysis only
python run_analysis.py

# Generate tickets only
python generate_tickets.py

# Run cleanup only
python run_cleanup.py

# Test tennis AI
python ai_brain/tennis_ai_fixtures_test.py
```

### AI Sports Fetch
```bash
# Fetch MLB props with AI analysis
python run_mlb_fetch.py

# Fetch WNBA props with AI analysis
python run_wnba_fetch.py

# Fetch Tennis props with AI analysis
python run_tennis_fetch.py
```

## 🔍 Monitoring

### Logs
- **AI Brain Logs**: Decision making and learning logs
- **Performance Logs**: Ticket and prediction performance
- **System Logs**: Technical operations and errors
- **Market Logs**: Market analysis and opportunities

### AI State
The AI maintains its state in:
- `ghost_ai_core_memory/ai_brain_state.json`
- `ghost_ai_core_memory/active_streaks.json`
- `ghost_ai_core_memory/daily_learning.json`

## 🚨 Troubleshooting

### Common Issues
1. **Missing Environment Variables**: Ensure all required API keys are set
2. **Discord Webhook Issues**: Check webhook URLs and permissions
3. **AI Brain Errors**: Check logs in `logs/` directory
4. **Performance Issues**: Monitor AI brain state and memory usage

### Debug Mode
```bash
# Run with verbose logging
python main.py --debug

# Check AI brain state
python -c "from ai_brain.ai_brain import AIBrain; print(AIBrain().state)"
```

## 🔄 AI Evolution

The AI continuously evolves:
- **Self-Improvement**: AI analyzes its own performance and makes improvements
- **Strategy Adaptation**: AI modifies its approach based on market conditions
- **Learning Integration**: AI incorporates new data and patterns
- **Risk Optimization**: AI adjusts risk tolerance based on performance

## 📈 Performance Metrics

The AI tracks:
- **Overall Win Rate**: Percentage of successful predictions
- **Sport-Specific Performance**: Success rates by sport
- **Ticket Success Rate**: Individual ticket performance
- **Market Opportunity Detection**: Success in identifying value
- **Risk-Adjusted Returns**: Performance considering risk levels

## 🤝 Contributing

Ghost AI 4.0 is designed to be self-evolving. The AI can:
- **Self-Modify**: AI can update its own code based on performance
- **Learn New Patterns**: AI discovers and adapts to new market patterns
- **Optimize Strategy**: AI continuously optimizes its betting strategy
- **Expand Coverage**: AI can add new sports and markets

## 📝 License

This project is for educational and research purposes. Please ensure compliance with local gambling laws and regulations.

---

**Ghost AI 4.0** - The future of autonomous sports betting intelligence. 🤖⚡ 