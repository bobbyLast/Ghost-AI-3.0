#!/usr/bin/env python3
"""
start_ghost_ai.py - Ghost AI 4.0 Startup Script
Ensures all directories exist and starts Ghost AI in autonomous AI mode.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def setup_directories():
    """Create all necessary directories."""
    base_dir = Path(__file__).parent
    
    directories = [
        'logs',
        'data',
        'data/performance',
        'data/feedback',
        'config',
        'auto_fixes',
        'auto_features',
        'ghost_ai_core_memory/tickets/generated',
        'ghost_ai_core_memory/tickets/posted',
        'ghost_ai_core_memory/tickets/graded',
        'ghost_ai_core_memory/confidence/mlb',
        'ghost_ai_core_memory/player_tags',
        'ghost_ai_core_memory/odds_analysis',
        'ghost_ai_core_memory/used_props',
        'ghost_ai_core_memory/streaks',
        'ghost_ai_core_memory/prop_outcomes',
        'ghost_ai_core_memory/tracked_picks',
        'ghost_ai_core_memory/player_cache',
        'ghost_ai_core_memory/ghost_ai_core_memory/tickets',
        'ghost_ai_core_memory/ghost_ai_core_memory/player_tags',
        'data/historical_odds',
        'data/historical_odds/baseball_mlb',
        'data/historical_odds/basketball_wnba',
        'data/historical/odds',
        'data/historical/players',
        'data/historical/teams',
        'data/historical/props',
        'data/mlb/rosters',
        'data/wnba/rosters',
        'data/player_props',
        'data/props_archive',
        'data/streaks',
        'data/backups',
        'data/cache',
        'data/games',
        'data/ghost_confidence',
        'data/historical',
        'data/memory',
        'data/mlb',
        'data/nba',
        'data/performance',
        'data/player_props',
        'data/props_archive',
        'data/streaks',
        'data/wnba',
        'mlb_game_props/fresh_games',
        'wnba_game_props/fresh_games',
        'props_archive/mlb',
        'props_archive/wnba',
        'odds_reverse_engineering/data',
        'odds_reverse_engineering/data/ai_analysis',
        'odds_reverse_engineering/data/enhanced_tickets_mock',
        'odds_reverse_engineering/data/ghost_confidence',
        'odds_reverse_engineering/data/performance',
        'odds_reverse_engineering/logs',
        'odds_reverse_engineering/models',
        'odds_reverse_engineering/test_data',
        'odds_reverse_engineering/tests',
        'odds_reverse_engineering/utils',
        'odds_reverse_engineering/odds_reverse_engineering_test/data',
        'production',
        'sportsbook_prop_audit',
        'system',
        'intelligence',
        'memory',
        'odds_memory',
        'odds_reverse_engine',
        'reverse_engine',
        'sports',
        'sports/mlb',
        'sports/wnba',
        'sports/shared',
        'core',
        'core/confidence',
        'core/data',
        'core/ghost_ai_core_memory',
        'core/logs',
        'core/streaks',
        'discord_integration',
        'docs',
        'ghost_ai_core_memory',
        'ghost_ai_core_memory/confidence',
        'ghost_ai_core_memory/confidence/mlb',
        'ghost_ai_core_memory/config',
        'ghost_ai_core_memory/ghost_ai_core_memory',
        'ghost_ai_core_memory/ghost_ai_core_memory/player_tags',
        'ghost_ai_core_memory/ghost_ai_core_memory/tickets',
        'ghost_ai_core_memory/logs',
        'ghost_ai_core_memory/mlb',
        'ghost_ai_core_memory/mlb/player_data',
        'ghost_ai_core_memory/odds_analysis',
        'ghost_ai_core_memory/player_cache',
        'ghost_ai_core_memory/player_tags',
        'ghost_ai_core_memory/prop_outcomes',
        'ghost_ai_core_memory/streaks',
        'ghost_ai_core_memory/tickets',
        'ghost_ai_core_memory/tickets/analyzed',
        'ghost_ai_core_memory/tickets/archive',
        'ghost_ai_core_memory/tickets/generated',
        'ghost_ai_core_memory/tickets/graded',
        'ghost_ai_core_memory/tickets/historical',
        'ghost_ai_core_memory/tickets/posted',
        'ghost_ai_core_memory/tickets/results',
        'ghost_ai_core_memory/tickets/unified',
        'ghost_ai_core_memory/tracked_picks',
        'ghost_ai_core_memory/used_props',
        'intelligence',
        'logs',
        'memory',
        'mlb_game_props',
        'mlb_game_props/fresh_games',
        'odds_memory',
        'odds_reverse_engine',
        'odds_reverse_engineering',
        'odds_reverse_engineering/ai_data_loader',
        'odds_reverse_engineering/auto_integration',
        'odds_reverse_engineering/auto_odds_analyzer',
        'odds_reverse_engineering/config',
        'odds_reverse_engineering/data',
        'odds_reverse_engineering/data/ai_analysis',
        'odds_reverse_engineering/data/enhanced_tickets_mock',
        'odds_reverse_engineering/data/ghost_confidence',
        'odds_reverse_engineering/data/performance',
        'odds_reverse_engineering/logs',
        'odds_reverse_engineering/models',
        'odds_reverse_engineering/test_data',
        'odds_reverse_engineering/tests',
        'odds_reverse_engineering/utils',
        'odds_reverse_engineering/odds_reverse_engineering_test',
        'odds_reverse_engineering/odds_reverse_engineering_test/data',
        'production',
        'props_archive',
        'props_archive/mlb',
        'props_archive/wnba',
        'reverse_engine',
        'sports',
        'sports/mlb',
        'sports/wnba',
        'sports/shared',
        'sportsbook_prop_audit',
        'system',
        'venv',
        'venv/Include',
        'venv/Lib',
        'venv/Lib/site-packages',
        'venv/Scripts',
        'wnba_game_props',
        'wnba_game_props/fresh_games',
        'ai_brain',
        'ai_brain/brain_modules'
    ]
    
    print("📁 Creating directories...")
    for directory in directories:
        dir_path = base_dir / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✅ {directory}")
    
    print("✅ All directories created successfully!")

def check_environment():
    """Check if environment variables are set."""
    print("🔍 Checking environment...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'DISCORD_BOT_TOKEN',
        'DISCORD_WEBHOOK_URL'
    ]
    
    optional_vars = [
        'TICKET_WEBHOOK',
        'MONEYLINE_WEBHOOK', 
        'UPDATE_WEBHOOK'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ All required environment variables are set!")
    
    # Check optional variables
    for var in optional_vars:
        if os.getenv(var):
            print(f"   ✅ {var} is set")
        else:
            print(f"   ⚠️ {var} is not set (optional)")
    
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    print("📦 Checking dependencies...")
    
    required_packages = [
        'requests',
        'python-dotenv',
        'discord.py',
        'schedule',
        'openai',
        'pandas',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease install with:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def create_default_configs():
    """Create default configuration files if they don't exist."""
    print("⚙️ Setting up default configurations...")
    
    base_dir = Path(__file__).parent
    
    # Default schedule config
    schedule_config = {
        'enabled': True,
        'wake_up_time': '05:00',
        'run_interval_hours': 6,
        'max_cycles_per_day': 4,
        'auto_cleanup_time': '02:00',
        'auto_learning_time': '23:00',
        'error_retry_delay_minutes': 30,
        'max_retries': 3
    }
    
    schedule_file = base_dir / 'config' / 'schedule.json'
    if not schedule_file.exists():
        schedule_file.parent.mkdir(exist_ok=True)
        import json
        with open(schedule_file, 'w') as f:
            json.dump(schedule_config, f, indent=2)
        print("   ✅ schedule.json created")
    
    # Default strategy config
    strategy_config = {
        'confidence_threshold': 0.7,
        'max_tickets_per_day': 10,
        'risk_management': {
            'max_bet_size': 100,
            'max_daily_loss': 500,
            'stop_loss_percentage': 0.1
        },
        'sports': {
            'mlb': {
                'enabled': True,
                'confidence_threshold': 0.75
            },
            'wnba': {
                'enabled': True,
                'confidence_threshold': 0.7
            }
        }
    }
    
    strategy_file = base_dir / 'config' / 'strategy.json'
    if not strategy_file.exists():
        strategy_file.parent.mkdir(exist_ok=True)
        with open(strategy_file, 'w') as f:
            json.dump(strategy_config, f, indent=2)
        print("   ✅ strategy.json created")
    
    # Default confidence config
    confidence_config = {
        'mlb': {
            'hitting_props': {
                'min_confidence': 0.7,
                'max_confidence': 0.95
            },
            'pitching_props': {
                'min_confidence': 0.75,
                'max_confidence': 0.9
            }
        },
        'wnba': {
            'scoring_props': {
                'min_confidence': 0.65,
                'max_confidence': 0.9
            },
            'rebounding_props': {
                'min_confidence': 0.6,
                'max_confidence': 0.85
            }
        }
    }
    
    confidence_file = base_dir / 'config' / 'confidence.json'
    if not confidence_file.exists():
        confidence_file.parent.mkdir(exist_ok=True)
        with open(confidence_file, 'w') as f:
            json.dump(confidence_config, f, indent=2)
        print("   ✅ confidence.json created")
    
    print("✅ Default configurations created!")

def main():
    """Main startup function."""
    print("🧠 Ghost AI 4.0 Startup")
    print("=" * 50)
    
    # Setup directories
    setup_directories()
    print()
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment not configured properly!")
        return False
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Dependencies not installed!")
        return False
    print()
    
    # Create default configs
    create_default_configs()
    print()
    
    print("🚀 Starting Ghost AI 4.0 in autonomous AI mode...")
    print("🧠 The AI will think, learn, and make intelligent decisions!")
    print("📊 Check logs/ghost_ai_main.log for detailed logs")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    # Start Ghost AI in continuous mode
    try:
        from main import run_continuous_ai
        run_continuous_ai()
    except KeyboardInterrupt:
        print("\n🛑 Ghost AI stopped by user")
    except Exception as e:
        print(f"\n❌ Ghost AI failed to start: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 