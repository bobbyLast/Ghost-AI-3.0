#!/usr/bin/env python3
"""
Ghost AI 3.0 Enhanced Production Orchestrator

Advanced 24/7 autonomous operation with:
- Discord Integration
- Enhanced Intelligence
- Advanced Risk Management
- Performance Analytics
"""

import asyncio
import datetime
import logging
import os
import sys
import json
from pathlib import Path
from typing import Dict, List
import importlib

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.daily_pick_manager import DailyPickManager
from core.ghost_ai import GhostAI
from enhanced_intelligence import enhance_picks_with_intelligence
from production_discord import ProductionDiscordBot
from ghost_ai_core_memory.memory_manager import MemoryManager
from ghost_ai_core_memory.fantasy_score_calculator import FantasyScoreCalculator
from ghost_ai_core_memory.prop_filter import PropFilter
from ghost_ai_core_memory.reverse_engine_integration import ReverseEngineIntegration
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
        logging.FileHandler('logs/enhanced_production.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('enhanced.production')

def file_for_today(directory, tag=None):
    from datetime import datetime
    today_str = datetime.now().strftime('%Y-%m-%d')
    from pathlib import Path
    for f in Path(directory).glob(f'{today_str}*.json'):
        if not tag or tag in f.name:
            return f
    return None

class EnhancedProductionOrchestrator:
    """Enhanced production orchestrator with advanced features."""
    
    def __init__(self):
        self.base_dir = Path('.')
        self.ghost_ai = None
        self.daily_pick_manager = None
        self.discord_bot = None
        self.is_running = False
        self.health_status = {
            'last_daily_picks': None,
            'last_health_check': None,
            'errors_count': 0,
            'successful_runs': 0,
            'discord_status': 'disconnected',
            'intelligence_enabled': True
        }
        
        # Enhanced settings
        self.settings = {
            'daily_picks_time': '09:00',  # 9 AM daily
            'health_check_interval': 300,  # 5 minutes
            'max_retries': 3,
            'intelligence_enabled': True,
            'discord_enabled': True,
            'risk_management_enabled': True,
            'performance_tracking_enabled': True
        }
        
        # Ensure directories exist
        self._ensure_directories()
        
        self.memory_manager = MemoryManager(self.base_dir)
        self.fantasy_calculator = FantasyScoreCalculator()
        self.prop_filter = PropFilter()
        self.reverse_engine = ReverseEngineIntegration(self.base_dir)
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            'logs',
            'data/backups',
            'data/intelligence',
            'data/performance',
            'ghost_ai_core_memory/tickets/generated',
            'ghost_ai_core_memory/tickets/posted',
            'ghost_ai_core_memory/tickets/results'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize all components."""
        try:
            logger.info("Initializing Enhanced Production Orchestrator...")
            
            # Initialize Ghost AI
            self.ghost_ai = GhostAI()
            logger.info("Ghost AI initialized")
            
            # Initialize Daily Pick Manager
            self.daily_pick_manager = DailyPickManager(self.ghost_ai)
            logger.info("Daily Pick Manager initialized")
            
            # Initialize Discord Bot (if enabled)
            if self.settings['discord_enabled']:
                discord_token = os.getenv('DISCORD_TOKEN')
                if discord_token:
                    self.discord_bot = ProductionDiscordBot()
                    logger.info("Discord Bot initialized")
                    self.health_status['discord_status'] = 'initialized'
                else:
                    logger.warning("Discord token not found - Discord features disabled")
                    self.health_status['discord_status'] = 'no_token'
            
            logger.info("Enhanced Production Orchestrator initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False
    
    async def run_enhanced_daily_picks_workflow(self):
        """Run the enhanced daily picks workflow with intelligence and strict duplicate prevention."""
        try:
            logger.info("Starting enhanced daily picks workflow...")
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
            logger.info("Enhanced daily picks workflow complete")
            return all_picks
        except Exception as e:
            logger.error(f"Enhanced daily picks workflow failed: {e}")
            self.health_status['errors_count'] += 1
            return False
    
    async def _apply_enhanced_intelligence(self, picks: Dict) -> Dict:
        """Apply enhanced intelligence to picks."""
        try:
            enhanced_picks = {}
            
            for pick_type, pick_data in picks.items():
                if isinstance(pick_data, list):
                    # Process list of picks
                    enhanced_list = await enhance_picks_with_intelligence(pick_data)
                    enhanced_picks[pick_type] = enhanced_list
                elif isinstance(pick_data, dict):
                    # Process single pick
                    enhanced_list = await enhance_picks_with_intelligence([pick_data])
                    enhanced_picks[pick_type] = enhanced_list[0] if enhanced_list else None
            
            return enhanced_picks
            
        except Exception as e:
            logger.error(f"Error applying enhanced intelligence: {e}")
            return picks
    
    async def _apply_risk_management(self, picks: Dict) -> Dict:
        """Apply risk management to picks."""
        try:
            managed_picks = {}
            
            for pick_type, pick_data in picks.items():
                if isinstance(pick_data, list):
                    # Filter high-risk picks
                    managed_list = [p for p in pick_data if p.get('risk_score', 0) <= 0.7]
                    managed_picks[pick_type] = managed_list
                elif isinstance(pick_data, dict):
                    # Check single pick risk
                    if pick_data.get('risk_score', 0) <= 0.7:
                        managed_picks[pick_type] = pick_data
            
            return managed_picks
            
        except Exception as e:
            logger.error(f"Error applying risk management: {e}")
            return picks
    
    async def _post_enhanced_picks_to_discord(self, picks: Dict):
        """Post enhanced picks to Discord with intelligence data."""
        try:
            logger.info("Posting enhanced picks to Discord...")
            
            for pick_type, pick_data in picks.items():
                if not pick_data:
                    continue
                
                if pick_type == 'potd':
                    await self._post_enhanced_pick(pick_data, "PICK OF THE DAY")
                elif pick_type == 'rpotd':
                    await self._post_enhanced_pick(pick_data, "RISKY PICK OF THE DAY")
                elif pick_type == 'totd':
                    await self._post_enhanced_ticket(pick_data, "TICKET OF THE DAY")
                elif pick_type == 'rtotd':
                    await self._post_enhanced_ticket(pick_data, "RISKY TICKET OF THE DAY")
                elif pick_type == 'streaks':
                    await self._post_enhanced_streaks(pick_data, "STREAKS")
            
            logger.info("Enhanced picks posted to Discord")
            
        except Exception as e:
            logger.error(f"Failed to post enhanced picks to Discord: {e}")
    
    async def _post_enhanced_pick(self, pick: Dict, title: str):
        """Post enhanced single pick with intelligence data."""
        try:
            if not self.discord_bot:
                return
            
            # Format enhanced pick message
            player_name = pick.get('player_name', 'Unknown')
            stat = pick.get('stat', 'Unknown')
            line = pick.get('line', 'Unknown')
            enhanced_confidence = pick.get('enhanced_confidence', pick.get('confidence', 0))
            risk_score = pick.get('risk_score', 0)
            team = pick.get('team', 'Unknown')
            
            message = f"""
**{title}**

**Player:** {player_name} ({team})
**Prop:** {stat} {line}
**Enhanced Confidence:** {enhanced_confidence:.1%}
**Risk Score:** {risk_score:.1%}
**Pick:** {pick.get('side', 'Over')}

**Intelligence Factors:**
- Base Confidence: {pick.get('confidence_factors', {}).get('base_confidence', 0):.1%}
- Historical Boost: {pick.get('confidence_factors', {}).get('historical_boost', 0):.1%}
- Market Stability: {pick.get('confidence_factors', {}).get('market_stability', 0):.1%}
- Risk Adjustment: {pick.get('confidence_factors', {}).get('risk_adjustment', 0):.1%}
            """.strip()
            
            # Send to Discord (placeholder)
            logger.info(f"Would post enhanced pick to Discord: {title}")
            logger.info(message)
            
        except Exception as e:
            logger.error(f"Failed to post enhanced pick: {e}")
    
    async def _post_enhanced_ticket(self, picks: List[Dict], title: str):
        """Post enhanced ticket with intelligence data."""
        try:
            if not self.discord_bot:
                return
            
            message = f"**{title}**\n\n**{len(picks)}-Leg Ticket**\n\n"
            
            for i, pick in enumerate(picks, 1):
                player_name = pick.get('player_name', 'Unknown')
                stat = pick.get('stat', 'Unknown')
                line = pick.get('line', 'Unknown')
                enhanced_confidence = pick.get('enhanced_confidence', pick.get('confidence', 0))
                risk_score = pick.get('risk_score', 0)
                
                message += f"**Leg {i}:** {player_name}\n"
                message += f"{stat} {line} | Confidence: {enhanced_confidence:.1%} | Risk: {risk_score:.1%}\n\n"
            
            # Send to Discord (placeholder)
            logger.info(f"Would post enhanced ticket to Discord: {title}")
            logger.info(message)
            
        except Exception as e:
            logger.error(f"Failed to post enhanced ticket: {e}")
    
    async def _post_enhanced_streaks(self, picks: List[Dict], title: str):
        """Post enhanced streaks with intelligence data."""
        try:
            if not self.discord_bot:
                return
            
            message = f"**{title}**\n\n"
            
            for pick in picks:
                player_name = pick.get('player_name', 'Unknown')
                stat = pick.get('stat', 'Unknown')
                line = pick.get('line', 'Unknown')
                enhanced_confidence = pick.get('enhanced_confidence', pick.get('confidence', 0))
                streak_info = pick.get('streak_info', {})
                current_streak = streak_info.get('current_streak', 0)
                next_legs = streak_info.get('next_legs', 2)
                
                message += f"**{player_name}**\n"
                message += f"{stat} {line} | Confidence: {enhanced_confidence:.1%}\n"
                message += f"Streak: {current_streak} | Next: {next_legs}-leg\n\n"
            
            # Send to Discord (placeholder)
            logger.info(f"Would post enhanced streaks to Discord: {title}")
            logger.info(message)
            
        except Exception as e:
            logger.error(f"Failed to post enhanced streaks: {e}")
    
    async def _save_enhanced_picks(self, picks: Dict):
        """Save enhanced picks with intelligence data."""
        try:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            picks_file = Path(f'ghost_ai_core_memory/tickets/posted/enhanced_{today}.json')
            
            # Save enhanced picks with metadata
            picks_data = {
                'date': today,
                'timestamp': datetime.datetime.now().isoformat(),
                'picks': picks,
                'metadata': {
                    'total_picks': len(picks),
                    'intelligence_enabled': self.settings['intelligence_enabled'],
                    'risk_management_enabled': self.settings['risk_management_enabled'],
                    'enhanced_features': ['intelligence_analysis', 'risk_management', 'performance_tracking']
                }
            }
            
            with open(picks_file, 'w') as f:
                json.dump(picks_data, f, indent=2)
            
            logger.info(f"Saved enhanced picks to {picks_file}")
            
        except Exception as e:
            logger.error(f"Failed to save enhanced picks: {e}")
    
    async def _track_performance(self, picks: Dict):
        """Track performance metrics."""
        try:
            today = datetime.datetime.now().strftime('%Y-%m-%d')
            performance_file = Path(f'data/performance/{today}.json')
            
            # Calculate performance metrics
            total_picks = 0
            total_confidence = 0
            total_risk = 0
            
            for pick_type, pick_data in picks.items():
                if isinstance(pick_data, list):
                    for pick in pick_data:
                        total_picks += 1
                        total_confidence += pick.get('enhanced_confidence', pick.get('confidence', 0))
                        total_risk += pick.get('risk_score', 0)
                elif isinstance(pick_data, dict):
                    total_picks += 1
                    total_confidence += pick_data.get('enhanced_confidence', pick_data.get('confidence', 0))
                    total_risk += pick_data.get('risk_score', 0)
            
            performance_data = {
                'date': today,
                'total_picks': total_picks,
                'average_confidence': total_confidence / total_picks if total_picks > 0 else 0,
                'average_risk': total_risk / total_picks if total_picks > 0 else 0,
                'intelligence_enabled': self.settings['intelligence_enabled'],
                'risk_management_enabled': self.settings['risk_management_enabled']
            }
            
            with open(performance_file, 'w') as f:
                json.dump(performance_data, f, indent=2)
            
            logger.info(f"Performance tracked: {total_picks} picks, avg confidence: {performance_data['average_confidence']:.1%}")
            
        except Exception as e:
            logger.error(f"Failed to track performance: {e}")
    
    async def health_check(self):
        """Perform enhanced health check."""
        try:
            logger.info("Performing enhanced health check...")
            
            # Basic health checks
            fs_status = self._check_file_system()
            api_status = await self._check_api_status()
            intelligence_status = self._check_intelligence_status()
            
            # Update health status
            self.health_status['last_health_check'] = datetime.datetime.now()
            
            # Send alert if issues found
            if not all([fs_status, api_status, intelligence_status]):
                await self._send_alert("Health check failed - system issues detected")
            
            logger.info("Enhanced health check complete")
            return all([fs_status, api_status, intelligence_status])
            
        except Exception as e:
            logger.error(f"Enhanced health check failed: {e}")
            return False
    
    def _check_file_system(self) -> bool:
        """Check file system health."""
        try:
            critical_dirs = [
                'logs',
                'ghost_ai_core_memory',
                'mlb_game_props',
                'wnba_game_props',
                'data/intelligence',
                'data/performance'
            ]
            
            for directory in critical_dirs:
                if not Path(directory).exists():
                    logger.error(f"Critical directory missing: {directory}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"File system check failed: {e}")
            return False
    
    async def _check_api_status(self) -> bool:
        """Check API connectivity."""
        try:
            # Placeholder API check
            return True
        except Exception as e:
            logger.error(f"API status check failed: {e}")
            return False
    
    def _check_intelligence_status(self) -> bool:
        """Check intelligence system status."""
        try:
            return self.settings['intelligence_enabled']
        except Exception as e:
            logger.error(f"Intelligence status check failed: {e}")
            return False
    
    async def _send_alert(self, message: str):
        """Send alert to Discord."""
        try:
            if self.discord_bot and self.settings['discord_enabled']:
                # Send alert to Discord (placeholder)
                logger.info(f"ALERT: {message}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

def orchestrator_main():
    ai_brain = AIBrain()
    next_actions = ai_brain.get_next_actions()
    for action in next_actions:
        if not ai_brain.has_done_action(action['action_type'], action['details'].get('date')):
            ai_brain.log_action(action['action_type'], action['details'])
            # Call the appropriate function for the action
            # Use ai_brain.plan_with_openai() for planning before each major step
            pass # Placeholder for action execution

if __name__ == "__main__":
    try:
        orchestrator_main()
    except KeyboardInterrupt:
        logger.info("Enhanced production orchestrator stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}") 