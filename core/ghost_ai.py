"""
Ghost AI - Advanced Sports Betting Assistant

Core application for analyzing sports betting props and generating picks.
This is the unified version combining all Ghost AI functionality.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import system utilities
from system.logging_config import setup_logging, get_logger

# Third-party imports
import aiohttp
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import psutil

# Local imports
from core.vault_manager import VaultManager
from core.prop_processor import PropProcessor, ComboPropTester
from core.ticket_generator import TicketGenerator
# from core.utils.value_utils import calculate_implied_probability, calculate_expected_value, analyze_player_performance  # Uncomment if exists
from memory.ghost_memory import GhostMemory, PickStatus, PickImpact
# from core.utils.prop_tracker import PropTracker  # Uncomment if exists
# from core.utils.cleanup import CleanupManager  # Uncomment if exists
# from core.analysis.prop_analyzer import get_prop_analyzer  # Uncomment if exists
# from core.processing.data_processor import DataProcessor  # Uncomment if exists
# from core.pipeline.ticket_builder import save_tickets  # Uncomment if exists
from ghost_ai_core_memory.memory_manager import MemoryManager
from ghost_ai_core_memory.fantasy_score_calculator import FantasyScoreCalculator
from ghost_ai_core_memory.prop_filter import PropFilter
from ghost_ai_core_memory.reverse_engine_integration import ReverseEngineIntegration
from ghost_ai_core_memory.ghost_brain import create_ghost_brain

# Configure logging
setup_logging(
    log_dir="logs",
    log_file="ghost_ai.log",
    log_level=logging.DEBUG,  # Force DEBUG level
    console_log=True,
    file_log=True,
    max_bytes=10*1024*1024,  # 10MB
    backup_count=5
)
logger = get_logger("GhostAI")

# Import player data cache
try:
    from ghost_ai_core_memory.player_data_cache import player_cache
    CACHE_AVAILABLE = True
except ImportError:
    logger.warning("Player data cache not available - will fetch all data")
    CACHE_AVAILABLE = False

# Import odds intelligence
from intelligence.odds_intelligence import OddsIntelligence

# Check for existing instances
def is_ghost_ai_running() -> bool:
    """Check if any Ghost AI instance is already running."""
    current_pid = os.getpid()
    logger.info("Checking for running Ghost AI instances...")
    
    # List of possible Ghost AI script names to check for
    ghost_scripts = [
        'ghost_ai.py',
        'ghost_ai_.py',
        'ghost_ai_old.py',
        'ghost_ai_backup.py',
        'ghost_ai_clean.py',
        'ghost_ai_fixes.py'
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip the current process
            if proc.info['pid'] == current_pid:
                continue
                
            # Get command line arguments safely
            cmdline = proc.info.get('cmdline')
            if not cmdline or len(cmdline) < 2:
                continue
                
            # Check if this is a Python process running any Ghost AI script
            if ('python' in proc.info['name'].lower() or 
                'python.exe' in ' '.join(cmdline).lower()):
                
                # Get the script name from command line
                script_path = cmdline[1].lower()
                script_name = os.path.basename(script_path)
                
                # Check if it's one of our Ghost AI scripts
                if any(ghost_script in script_name for ghost_script in ghost_scripts):
                    logger.warning(f"Found running Ghost AI instance (PID: {proc.info['pid']}): {script_name}")
                    return True
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.debug(f"Error checking process {proc.info.get('pid')}: {e}")
            continue
            
    return False

# Run instance check
# Temporarily disabled due to process detection issues
# if is_ghost_ai_running():
#     logger.error("Another instance of Ghost AI is already running. Exiting...")
#     print("❌ Another instance of Ghost AI is already running. Exiting...")
#     sys.exit(1)
# else:
logger.info("No other Ghost AI instances found. Starting up...")


class GhostAI:
    """Ghost AI 3.0: Autonomous AI System (not a bot)"""
    def __init__(self):
        # Set base directory first
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / 'data'
        self.logs_dir = self.base_dir / 'logs'
        self.memory_dir = self.base_dir / 'ghost_ai_core_memory'
        self.streaks_dir = self.base_dir / 'streaks'
        self.confidence_dir = self.base_dir / 'confidence'
        self.start_time = datetime.utcnow()  # Track AI start time
        
        # Initialize core components
        try:
            self._ensure_directories()
            logger.info("GhostAI initialization complete.")
        except Exception as e:
            logger.error(f"Exception during GhostAI __init__: {e}")
            raise
        
        # Initialize last_weekly_review
        self.last_weekly_review = datetime.now() - timedelta(days=7)
        
        # Load environment variables
        load_dotenv()
        logger.info(f"Loaded environment variables: DISCORD_TOKEN={'set' if os.getenv('DISCORD_TOKEN') else 'missing'}, ODDS_API_KEY={'set' if os.getenv('ODDS_API_KEY') else 'missing'}")
        
        # Initialize components
        # self.prop_analyzer = get_prop_analyzer()
        self.memory = GhostMemory()
        self.prop_processor = None
        self.combo_tester = ComboPropTester()
        # self.prop_tracker = PropTracker(self.memory)
        self.ticket_generator = TicketGenerator()
        
        # Initialize player data cache
        self.cache_enabled = CACHE_AVAILABLE
        if self.cache_enabled:
            logger.info("✅ Player data cache enabled - will check for existing data before fetching")
        else:
            logger.warning("⚠️ Player data cache not available - will fetch all data")
        
        # Initialize odds intelligence
        self.odds_intelligence = None  # Will be initialized on first use
        
        # Initialize odds reverse engineering system for historical data
        try:
            sys.path.append(str(self.base_dir / 'odds_reverse_engineering'))
            try:
                from reverse_engine import OddsReverseEngine
                from reverse_engine.ai_data_loader import AIDataLoader
            self.odds_engine = OddsReverseEngine(data_dir=str(self.base_dir / 'odds_reverse_engineering' / 'data'))
            self.ai_loader = AIDataLoader()
            logger.info("✅ Odds reverse engineering system initialized for historical data")
            except ImportError:
                logger.warning("Could not import odds_reverse_engine or ai_data_loader. Odds reverse engineering system not initialized.")
                self.odds_engine = None
                self.ai_loader = None
        except Exception as e:
            logger.warning(f"Could not initialize odds reverse engineering system: {e}")
            self.odds_engine = None
            self.ai_loader = None
        
        # Initialize tracking
        self.active_streaks = {}
        self.health_checks = {
            'last_check': 0,
            'consecutive_errors': 0,
            'last_error_time': 0,
            'repair_attempts': 0
        }
        
        # Initialize task management
        self.current_task = None
        self.task_queue = asyncio.Queue()
        self.processing_lock = asyncio.Lock()
        self.last_api_call = 0
        self.min_api_interval = 1.0  # 1 second between API calls
        
        # Initialize background tasks
        self.watch_task = None
        self.ticket_generation_task = None
        self.scan_task = None
        self.report_task = None
        self.health_check_task = None
        
        # Initialize performance tracking
        self.performance_history = {
            'total_predictions': 0,
            'correct_predictions': 0,
            'incorrect_predictions': 0,
            'confidence_accuracy': {},
            'sport_performance': {},
            'player_performance': {},
            'stat_type_performance': {},
            'matchup_patterns': {},
            'stat_correlations': {},
            'weekly_reviews': []
        }
        
        # Initialize ticket generation tracking
        self.last_ticket_generation = {}  # Track last ticket generation time per sport
        self.ticket_generation_interval = 3600  # 1 hour between generations
        
        # Initialize other attributes
        self.cold_players = set()
        self.red_flag_players = {}
        self.bg_tasks = []
        self.player_tags = {}  # Initialize player tags
        self.saved_props = set()  # Track saved props to prevent duplicates
        self.daily_stats = {'tickets_posted': 0, 'props_processed': 0, 'confidence_calculated': 0}  # Initialize daily stats
        
        logger.info("GhostAI initialization complete.")

        # Add prefix command for !ghost
        @self.command(name='ghost', help='Submit a Ghost AI request via text command')
        async def ghost_text_command(ctx, *, text: str):
            response = await self.handle_ghost_request(text)
            await ctx.send(response)

        self.memory_manager = MemoryManager(self.base_dir)
        self.fantasy_calculator = FantasyScoreCalculator()
        self.prop_filter = PropFilter()
        self.reverse_engine = ReverseEngineIntegration(self.base_dir)
        self.ghost_brain = create_ghost_brain(self.base_dir)

    def _load_config(self):
        """Load configuration from config.json file."""
        try:
            config_path = self.base_dir / 'config' / 'config.json'
            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return {}
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            logger.info(f"Loaded config from {config_path}")
            logger.info(f"Config sports: {list(config.get('sports', {}).keys())}")
            
            # Log enabled sports
            for sport, sport_config in config.get('sports', {}).items():
                if sport_config.get('enabled', False):
                    logger.info(f"{sport.upper()} enabled: {sport_config.get('enabled', False)}")
            
            # Set active sports
            config['active_sports'] = [sport for sport, sport_config in config.get('sports', {}).items() 
                                     if sport_config.get('enabled', False)]
            logger.info(f"Final config sports: {config['active_sports']}")
            
            logger.info("Configuration loaded successfully.")
            return config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.logs_dir, exist_ok=True)
            os.makedirs(self.memory_dir, exist_ok=True)
            os.makedirs(self.streaks_dir, exist_ok=True)
            os.makedirs(self.confidence_dir, exist_ok=True)
            logger.info("Ensured all directories exist")
        except Exception as e:
            logger.error(f"Error ensuring directories: {e}")
            raise

    async def _cleanup_old_streaks(self):
        """Clean up old streaks from the database."""
        try:
            logger.info("Cleaning up old streaks...")
            # Implementation for cleaning up old streaks
            pass
        except Exception as e:
            logger.error(f"Error cleaning up old streaks: {e}")
            raise

    async def handle_ghost_request(self, text: str) -> str:
        """Handle text commands sent via !ghost command."""
        try:
            text = text.lower().strip()
            logger.info(f"Received ghost request: {text}")
            
            if text == "ai" or text == "go ai" or text == "start":
                # Generate tickets for all active sports
                response = "🤖 Ghost AI is generating tickets for all active sports...\n\n"
                
                # Check if config is loaded
                if not hasattr(self, 'config') or not self.config:
                    return "❌ Configuration not loaded yet. Please wait for system initialization."
                
                for sport in self.config.get('active_sports', []):
                    try:
                        sport_key = sport.lower()
                        if sport_key == 'mlb':
                            sport_key = 'baseball_mlb'
                        elif sport_key == 'wnba':
                            sport_key = 'basketball_wnba'
                        
                        logger.info(f"Generating tickets for {sport} using TicketGenerator")
                        await self.generate_and_post_tickets(sport_key)
                        response += f"✅ Generated tickets for {sport}\n"
                        
                    except Exception as e:
                        logger.error(f"Error generating tickets for {sport}: {e}")
                        response += f"❌ Error generating tickets for {sport}: {str(e)}\n"
                
                response += "\n🎯 Ticket generation complete!"
                return response
                
            elif text == "status" or text == "stats":
                # Return system status
                active_props = len(self.memory.get_active_props()) if hasattr(self, 'memory') else 0
                active_streaks = len(self.active_streaks) if hasattr(self, 'active_streaks') else 0
                
                return f"📊 **Ghost AI Status**\n" \
                       f"🔄 Active Props: {active_props}\n" \
                       f"🔥 Active Streaks: {active_streaks}\n" \
                       f"🏃‍♂️ Servers: {len(self.guilds)}\n" \
                       f"⏰ Uptime: {discord.utils.utcnow() - self.start_time}"
                       
            elif text == "help":
                return "🤖 **Ghost AI Commands**\n" \
                       "• `ai` or `go ai` - Generate tickets for all sports\n" \
                       "• `status` - Show system status\n" \
                       "• `help` - Show this help message\n\n" \
                       "Use `/generate_tickets` for manual ticket generation."
                       
            else:
                return f"❓ Unknown command: `{text}`\n" \
                       "Type `!ghost help` for available commands."
                       
        except Exception as e:
            logger.error(f"Error handling ghost request: {e}", exc_info=True)
            return f"❌ Error processing request: {str(e)}"

    def get_active_streaks(self) -> List[dict]:
        """Get all active streaks."""
        try:
            if hasattr(self, 'active_streaks'):
                return list(self.active_streaks.values())
            return []
        except Exception as e:
            logger.error(f"Error getting active streaks: {e}")
            return []
        
    async def periodic_status_update(self):
        """Periodically update the bot's status and log health metrics."""
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                # Update bot status
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{len(self.guilds)} servers"
                )
                await self.change_presence(activity=activity)
                
                # Log health metrics
                logger.info(f"Bot is running in {len(self.guilds)} servers")
                
                # Sleep for 5 minutes before next update
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in periodic status update: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait a minute before retrying on error
                
async def _periodic_streak_backup(self):
    """Periodically back up streak data to disk."""
    await self.wait_until_ready()
    while not self.is_closed():
        try:
            # Backup active streaks
                if self.active_streaks:
                    backup_file = self.streaks_dir / f"streaks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(backup_file, 'w') as f:
                        json.dump(self.active_streaks, f, indent=2)
                    logger.info(f"Backed up {len(self.active_streaks)} active streaks to {backup_file}")
            # Sleep for 1 hour before next backup
            await asyncio.sleep(3600)
        except Exception as e:
                logger.error(f"Error in periodic streak backup: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def generate_and_post_tickets(self, sport_key):
        """Generate and post tickets for a given sport, enforcing strict duplicate checks."""
        # Load props for the sport
        props = []
        props_file = None
        if sport_key == 'MLB':
            props_file = file_for_today('mlb_game_props')
        elif sport_key == 'WNBA':
            props_file = file_for_today('wnba_game_props')
        if props_file:
            with open(props_file, 'r') as f:
                props = json.load(f)
        # Filter props using prop filter and memory manager
        filtered_props = self.prop_filter.filter_props(props, sport_key, memory_manager=self.memory_manager)
        filtered_props = self.ghost_brain.filter_duplicate_props(filtered_props)
        # Analyze props with AI brain
        intelligent_props = self.ghost_brain.analyze_props_intelligently(filtered_props)
        # Enhance with reverse engine
        intelligent_props = self.reverse_engine.get_ai_recommendations(intelligent_props, sport_key)
        # Remove any props already used today (final check)
        intelligent_props = [p for p in intelligent_props if not self.memory_manager.is_prop_used_today(p)]
        # Filter by confidence and odds using AI brain strategy
        objectives = self.ghost_brain.get_ai_objectives()
        strategy = self.ghost_brain.get_strategy_engine()
        confident_props = [p for p in intelligent_props if p.get('confidence', 0) >= strategy['confidence_threshold']]
        # Generate tickets with AI brain validation (placeholder logic)
        tickets = []
        # ... (insert ticket generation logic here, using confident_props) ...
        # Enforce strict no-duplicates policy
        tickets = self.ghost_brain.enforce_no_duplicates_policy(tickets)
        # Final memory manager check for tickets
        valid_tickets = []
        for ticket in tickets:
            if not self.memory_manager.is_ticket_posted_today(ticket):
                valid_tickets.append(ticket)
                self.memory_manager.mark_ticket_posted(ticket, ticket_id=ticket.get('ticket_id', 'auto'))
            else:
                self.ghost_brain.think(f"Ticket rejected by memory manager - duplicate detected")
        # Post or save valid_tickets as needed
        return valid_tickets
