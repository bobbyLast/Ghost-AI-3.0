#!/usr/bin/env python3
"""
Ghost AI 3.0 Production Orchestrator (Simple Version)

24/7 Autonomous Operation System - Windows Compatible
"""

import asyncio
import datetime
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict
import importlib

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.daily_pick_manager import DailyPickManager
from core.ghost_ai import GhostAI
from ghost_ai_core_memory.memory_manager import MemoryManager
from ghost_ai_core_memory.fantasy_score_calculator import FantasyScoreCalculator
from ghost_ai_core_memory.prop_filter import PropFilter
from ghost_ai_core_memory.reverse_engine_integration import ReverseEngineIntegration
from ghost_ai_core_memory.ghost_brain import create_ghost_brain
from ghost_ai_core_memory.prop_intake import PropIntake
from ghost_ai_core_memory.confidence_scoring import ConfidenceScorer
from ghost_ai_core_memory.fade_detector import FadeDetector
from ghost_ai_core_memory.ticket_builder import TicketBuilder
from ghost_ai_core_memory.poster import Poster
from ghost_ai_core_memory.self_audit import SelfAudit
from core.ai_brain import AIBrain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_orchestrator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('production.orchestrator')

class ProductionOrchestrator:
    """Production orchestrator for 24/7 Ghost AI operation."""
    
    def __init__(self):
        self.ghost_ai = None
        self.daily_pick_manager = None
        self.is_running = False
        self.health_status = {
            'last_daily_picks': None,
            'last_health_check': None,
            'errors_count': 0,
            'successful_runs': 0
        }
        
        # Production settings
        self.settings = {
            'daily_picks_time': '09:00',  # 9 AM daily
            'health_check_interval': 300,  # 5 minutes
            'max_retries': 3
        }
        
        # Ensure directories exist
        self._ensure_directories()
        
        self.base_dir = Path('.')
        self.memory_manager = MemoryManager(self.base_dir)
        self.fantasy_calculator = FantasyScoreCalculator()
        self.prop_filter = PropFilter()
        self.reverse_engine = ReverseEngineIntegration(self.base_dir)
        self.ghost_brain = create_ghost_brain(self.base_dir)
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            'logs',
            'data/backups',
            'ghost_ai_core_memory/tickets/generated',
            'ghost_ai_core_memory/tickets/posted',
            'ghost_ai_core_memory/tickets/results'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize all components."""
        try:
            logger.info("Initializing Production Orchestrator...")
            
            # Initialize Ghost AI
            self.ghost_ai = GhostAI()
            logger.info("Ghost AI initialized")
            
            # Initialize Daily Pick Manager
            self.daily_pick_manager = DailyPickManager(self.ghost_ai)
            logger.info("Daily Pick Manager initialized")
            
            logger.info("Production Orchestrator initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def run_daily_picks_workflow(self):
        """Run the complete daily picks workflow."""
        try:
            logger.info("Starting daily picks workflow...")
            
            # Generate daily picks
            picks = await self.daily_pick_manager.generate_daily_picks()
            
            if not picks:
                logger.warning("No daily picks generated")
                return False
            
            logger.info(f"Generated {len(picks)} pick types")
            
            # Save picks to memory
            await self.save_daily_picks(picks)
            
            # Update health status
            self.health_status['last_daily_picks'] = datetime.datetime.now()
            self.health_status['successful_runs'] += 1
            
            logger.info("Daily picks workflow complete")
            return True
            
        except Exception as e:
            logger.error(f"Daily picks workflow failed: {e}")
            self.health_status['errors_count'] += 1
            return False
    
    async def save_daily_picks(self, picks: Dict):
        """Save daily picks to memory for tracking."""
        try:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            picks_file = Path(f'ghost_ai_core_memory/tickets/posted/{today}.json')
            
            # Save picks with metadata
            picks_data = {
                'date': today,
                'timestamp': datetime.datetime.now().isoformat(),
                'picks': picks,
                'metadata': {
                    'total_picks': len(picks),
                    'sports': ['mlb', 'wnba']
                }
            }
            
            with open(picks_file, 'w') as f:
                json.dump(picks_data, f, indent=2)
            
            logger.info(f"Saved daily picks to {picks_file}")
            
        except Exception as e:
            logger.error(f"Failed to save daily picks: {e}")
    
    async def health_check(self):
        """Perform health check of the system."""
        try:
            logger.info("Performing health check...")
            
            # Check file system
            fs_status = self.check_file_system()
            
            # Update health status
            self.health_status['last_health_check'] = datetime.datetime.now()
            
            logger.info("Health check complete")
            return fs_status
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def check_file_system(self) -> bool:
        """Check file system health."""
        try:
            # Check critical directories
            critical_dirs = [
                'logs',
                'ghost_ai_core_memory',
                'mlb_game_props',
                'wnba_game_props'
            ]
            
            for directory in critical_dirs:
                if not Path(directory).exists():
                    logger.error(f"Critical directory missing: {directory}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"File system check failed: {e}")
            return False
    
    async def main_loop(self):
        """Main production loop."""
        logger.info("Starting production main loop...")
        self.is_running = True

        # --- Run auto-cleanup before anything else ---
        try:
            enhanced_cleanup = importlib.import_module('system.enhanced_auto_cleanup')
            cleanup_system = enhanced_cleanup.EnhancedAutoCleanupSystem()
            import asyncio
            asyncio.run(cleanup_system.cleanup_completed_games())
            logger.info("✅ Enhanced auto-cleanup with AI brain monitoring completed before main loop")
        except Exception as e:
            logger.error(f"Enhanced auto-cleanup failed at startup: {e}")

        # Initialize components
        if not await self.initialize():
            logger.error("Failed to initialize - exiting")
            return
        
        # Main production loop
        while self.is_running:
            try:
                current_time = datetime.datetime.now()
                
                # Check if it's time for daily picks (9 AM)
                if current_time.hour == 9 and current_time.minute == 0:
                    await self.run_daily_picks_workflow()
                
                # Health check every 5 minutes
                if current_time.minute % 5 == 0 and current_time.second == 0:
                    await self.health_check()
                
                # Sleep for 1 second
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
        
        # Cleanup
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")
        self.is_running = False
        logger.info("Cleanup complete")

    async def run_simple_picks_workflow(self):
        prop_intake = PropIntake(self.memory_manager)
        confidence_scorer = ConfidenceScorer(self.memory_manager)
        fade_detector = FadeDetector(self.memory_manager, self.fantasy_calculator)
        ticket_builder = TicketBuilder(self.memory_manager)
        poster = Poster(self.memory_manager, self.discord_bot)
        self_audit = SelfAudit(self.memory_manager)
        all_picks = {}
        for sport_key in ['MLB', 'WNBA']:
            props = []
            props_file = None
            if sport_key == 'MLB':
                props_file = file_for_today('mlb_game_props')
            elif sport_key == 'WNBA':
                props_file = file_for_today('wnba_game_props')
            if props_file:
                with open(props_file, 'r') as f:
                    raw_props = json.load(f)
                normalized_props = prop_intake.normalize_props(raw_props, source=sport_key)
                scored_props = confidence_scorer.score_props(normalized_props)
                fades = fade_detector.detect_fades(scored_props, sport_key)
                main_props = [p for p in scored_props if p not in fades]
                tickets = ticket_builder.build_tickets(main_props, max_tickets=10, max_legs=3)
                fade_tickets = ticket_builder.build_tickets(fades, max_tickets=3, max_legs=1)
                all_tickets = tickets + fade_tickets
                tickets_to_post = poster.should_post(all_tickets, min_confidence=0.6)
                poster.post_tickets(tickets_to_post)
                self_audit.run_end_of_day_audit(tickets_to_post, normalized_props)
                all_picks[sport_key] = tickets_to_post
        return all_picks

def file_for_today(directory, tag=None):
    from datetime import datetime
    today_str = datetime.now().strftime('%Y-%m-%d')
    from pathlib import Path
    for f in Path(directory).glob(f'{today_str}*.json'):
        if not tag or tag in f.name:
            return f
    return None

async def main():
    """Main entry point."""
    orchestrator = ProductionOrchestrator()
    await orchestrator.main_loop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Production orchestrator stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}") 