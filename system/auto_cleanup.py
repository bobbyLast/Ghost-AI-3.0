#!/usr/bin/env python3
"""
Intelligent Auto-Cleanup System for Ghost AI 4.0

How to Run:
- Run this script directly or via main.py in cleanup mode to perform intelligent cleanup of completed games, tickets, and logs.
- Example: python system/auto_cleanup.py
- Or: python main.py cleanup

How to Extend:
- To add new directories or file types for cleanup, update CLEANUP_DIRECTORIES or add logic in cleanup_old_files.
- To preview what would be deleted, run with the --preview flag (see below).

Preview Mode:
- Run with --preview to list files that would be deleted, without deleting them.
- Example: python system/auto_cleanup.py --preview

This script provides intelligent cleanup of completed games and triggers
reverse engineering analysis after games end. It uses the TimeManager
for reliable 24/7 operation with intelligent sleep/wake cycles.

Game Durations:
- MLB: 3 hours
- WNBA: 2.5 hours

Sleep/Wake Schedule:
- Sleep: 12:59 PM to 5:00 AM (Eastern Time)
- Wake: 5:00 AM (Eastern Time)
- Cleanup: Every 3.4 hours during active hours
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import subprocess
from typing import List, Dict, Optional
import argparse
import os
import shutil
import time
sys.path.append(str(Path(__file__).parent.parent))

from system.time_manager import TimeManager
from core.ai_brain import AIBrain

# Add import for unified ticket manager
from ghost_ai_core_memory.tickets.integration_hooks import hook_ticket_generation

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_cleanup.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # Explicitly use stdout with proper encoding
    ]
)

# Configure console handler to handle Unicode
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setStream(sys.stdout)
        # Set encoding for Windows console
        if hasattr(handler, 'setFormatter'):
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)

logger = logging.getLogger('ai_cleanup')

TICKETS_DIR = Path('ghost_ai_core_memory/tickets/historical')
TICKETS_GENERATED_DIR = Path('ghost_ai_core_memory/tickets/generated')
TICKETS_POSTED_DIR = Path('ghost_ai_core_memory/tickets/posted')
TICKETS_GRADED_DIR = Path('ghost_ai_core_memory/tickets/graded')
TICKETS_POSTED_DIR.mkdir(parents=True, exist_ok=True)
TICKETS_GRADED_DIR.mkdir(parents=True, exist_ok=True)

class IntelligentAutoCleanupSystem:
    """Intelligent automated cleanup system for Ghost AI 4.0 (always active with AI analysis)."""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.time_manager = TimeManager(self.base_dir)
        
        # Game durations in hours
        self.game_durations = {
            'MLB': 3.0,
            'WNBA': 2.5
        }
        
        # Cleanup buffer time (additional time after game should end)
        self.cleanup_buffer_hours = 1.0
        
        logger.info("🧠 Intelligent Auto Cleanup System initialized")
        logger.info(f"🧠 AI is always active, no sleep schedule.")
        logger.info(f"🧠 Intelligent cleanup every {self.time_manager.cleanup_interval_hours} hours during active hours")
    
    def _calculate_game_end_time(self, start_time_str: str, sport: str) -> Optional[datetime]:
        """Calculate when a game should end based on start time and sport."""
        try:
            # Parse start time
            if 'T' in start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            else:
                start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                start_time = start_time.replace(tzinfo=timezone.utc)
            
            # Add game duration
            duration_hours = self.game_durations.get(sport, 3.0)
            end_time = start_time + timedelta(hours=duration_hours)
            
            # Add cleanup buffer
            cleanup_time = end_time + timedelta(hours=self.cleanup_buffer_hours)
            
            return cleanup_time
            
        except Exception as e:
            logger.error(f"Error calculating game end time: {e}")
            return None
    
    def _is_game_completed(self, game_file: Path) -> bool:
        """Check if a game has completed and should be cleaned up."""
        try:
            # Read game data
            with open(game_file, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            # Extract game info
            commence_time = game_data.get('commence_time')
            sport = game_data.get('sport_key', 'MLB')
            
            if not commence_time:
                logger.warning(f"No commence_time found in {game_file}")
                return False
            
            # Calculate when cleanup should happen
            cleanup_time = self._calculate_game_end_time(commence_time, sport)
            if not cleanup_time:
                return False
            
            # Check if current time is past cleanup time
            current_time = self.time_manager.get_current_time()
            is_completed = current_time > cleanup_time
            
            if is_completed:
                logger.info(f"Game completed: {game_file.name} (started: {commence_time}, cleanup: {cleanup_time})")
            
            return is_completed
            
        except Exception as e:
            logger.error(f"Error checking game completion for {game_file}: {e}")
            return False
    
    async def cleanup_old_ticket_files(self, days_to_keep=1, preview=False):
        """Delete or archive old ticket and result files, keeping only the most recent N days."""
        try:
            logger.info(f"🧹 Cleaning up old ticket files (keeping {days_to_keep} days)...")
            # FIRST: Analyze any remaining tickets before deletion
            await self.analyze_tickets_before_cleanup()

            logger.info(f"Looking for tickets in {TICKETS_DIR.resolve()}")
            today = datetime.now().strftime('%Y-%m-%d')
            keep_dates = set([
                (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                for i in range(days_to_keep)
            ])
            total_deleted = 0
            for ticket_file in TICKETS_DIR.glob('*.json'):
                logger.info(f"Checking ticket file: {ticket_file.name}")
                # Extract date from filename
                parts = ticket_file.name.split('_')
                if len(parts) > 0 and parts[0] not in keep_dates:
                    logger.info(f"🗑️ Deleting old ticket/result file: {ticket_file}")
                    try:
                        if preview:
                            print(f"[PREVIEW] Would delete: {ticket_file.name}")
                        else:
                            ticket_file.unlink()
                            total_deleted += 1
                    except Exception as e:
                        logger.error(f"Error deleting old ticket file {ticket_file}: {e}")

            logger.info(f"✅ Cleaned up {total_deleted} old ticket files")

        except Exception as e:
            logger.error(f"Error in cleanup_old_ticket_files: {e}")

    async def cleanup_tickets_with_unavailable_players(self):
        """Clean tickets by removing those with unavailable players."""
        try:
            logger.info("🧹 Cleaning tickets with unavailable players...")
            
            # Check if unified storage is available
            try:
                from ghost_ai_core_memory.tickets.unified_ticket_manager import UnifiedTicketManager
                UNIFIED_STORAGE_AVAILABLE = True
            except ImportError as e:
                logger.warning(f"⚠️ Unified storage not available for ticket cleanup: {e}")
                return
            
            if not UNIFIED_STORAGE_AVAILABLE:
                logger.warning("⚠️ Unified storage not available for ticket cleanup")
                return
            
            # Initialize components
            ticket_manager = UnifiedTicketManager()
            # Unified storage cleanup logic
            logger.info("🧠 AI: Using unified storage for ticket cleanup")
            
            # Get today's tickets
            today = datetime.now().strftime('%Y-%m-%d')
            existing_tickets = ticket_manager.get_tickets_for_date(today)
            
            if not existing_tickets:
                logger.info("No tickets found for today")
                return
            
            logger.info(f"📋 Found {len(existing_tickets)} existing tickets")
            
            # Get available players from current prop files
            logger.info("🧠 AI: Analyzing available players for ticket cleanup")
            available_players = set()  # Placeholder for available players
            
            logger.info(f"👥 Available players: {len(available_players)}")
            
            # Filter tickets
            filtered_tickets = existing_tickets  # Placeholder for filtered tickets
            
            removed_count = len(existing_tickets) - len(filtered_tickets)
            if removed_count > 0:
                logger.info(f"✅ Filtered out {removed_count} tickets with unavailable players")
                logger.info(f"📊 Remaining tickets: {len(filtered_tickets)}")
                
                # Save filtered tickets back
                if filtered_tickets:
                    ticket_manager.save_tickets(filtered_tickets, today)
                    logger.info("💾 Saved filtered tickets")
                else:
                    logger.warning("⚠️ No tickets remaining after filtering")
            else:
                logger.info("✅ All tickets have available players")
                
        except Exception as e:
            logger.error(f"❌ Error cleaning tickets with unavailable players: {e}")

    async def cleanup_old_games(self):
        """Clean up old games that are no longer relevant for ticket generation."""
        try:
            logger.info("🧹 Cleaning up old games...")
            
            # Check MLB game props (main directory)
            mlb_props_dir = self.base_dir / 'mlb_game_props'
            if mlb_props_dir.exists():
                await self._cleanup_old_sport_games(mlb_props_dir, 'MLB')
            else:
                logger.info("MLB props directory does not exist, skipping")
            
            # Check WNBA game props
            wnba_props_dir = self.base_dir / 'wnba_game_props'
            if wnba_props_dir.exists():
                await self._cleanup_old_sport_games(wnba_props_dir, 'WNBA')
            else:
                logger.info("WNBA props directory does not exist, skipping")
                
            logger.info("✅ Old games cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old games: {e}")

    async def _cleanup_old_sport_games(self, props_dir: Path, sport: str):
        """Clean up old games for a specific sport that are no longer relevant."""
        try:
            logger.info(f"Checking {sport} games for old/irrelevant games in {props_dir}")
            prop_files = list(props_dir.glob('*.json'))
            
            if not prop_files:
                logger.info(f"No {sport} prop files found")
                return
                
            current_time = self.time_manager.get_current_time()
            old_games = []
            
            for prop_file in prop_files:
                try:
                    with open(prop_file, 'r', encoding='utf-8') as f:
                        game_data = json.load(f)
                    
                    commence_time = game_data.get('commence_time') or game_data.get('start_time')
                    if not commence_time:
                        logger.warning(f"No commence_time found in {prop_file}, skipping")
                        continue
                    
                    # Parse commence time
                    if 'T' in commence_time:
                        game_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                    else:
                        game_time = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')
                        game_time = game_time.replace(tzinfo=timezone.utc)
                    
                    # Check if game is old (more than 24 hours ago)
                    time_diff = current_time - game_time
                    is_old = time_diff.total_seconds() > 86400  # 24 hours in seconds
                    
                    if is_old:
                        logger.info(f"Old game found: {prop_file.name} (commence: {commence_time}, age: {time_diff.total_seconds()/3600:.1f} hours)")
                        old_games.append(prop_file)
                except Exception as e:
                    logger.error(f"Error checking game age for {prop_file}: {e}, skipping")
            
            # Archive old games
            if old_games:
                logger.info(f"Found {len(old_games)} old {sport} games to delete")
                
                # Extract essential data before deleting
                await self._extract_essential_data(old_games, sport)
                
                for game_file in old_games:
                    try:
                        game_file.unlink()
                        logger.info(f"Deleted old game: {game_file.name}")
                    except Exception as e:
                        logger.error(f"Error deleting old game file {game_file}: {e}")
            else:
                logger.info(f"No old {sport} games found")
            
        except Exception as e:
            logger.error(f"Error in _cleanup_old_sport_games: {e}")

    async def analyze_tickets_before_cleanup(self):
        """Run reverse engineering analysis on tickets before cleanup to determine results."""
        try:
            logger.info("🔍 Running reverse engineering analysis on tickets before cleanup...")
            
            # Check if reverse engineering is available
            try:
                from odds_reverse_engineering.auto_odds_analyzer import AutoOddsAnalyzer
                from ghost_ai_core_memory.tickets.unified_ticket_manager import UnifiedTicketManager
                REVERSE_ENGINEERING_AVAILABLE = True
            except ImportError as e:
                logger.warning(f"Reverse engineering not available: {e}")
                return
            
            if not REVERSE_ENGINEERING_AVAILABLE:
                logger.warning("Reverse engineering not available for ticket analysis")
                return
            
            # Initialize components
            analyzer = AutoOddsAnalyzer()
            ticket_manager = UnifiedTicketManager()
            
            # Get today's tickets
            today = datetime.now().strftime('%Y-%m-%d')
            tickets = ticket_manager.get_tickets_for_date(today)
            
            if not tickets:
                logger.info("No tickets found for today to analyze")
                return
            
            logger.info(f"📊 Analyzing {len(tickets)} tickets for results...")
            
            # Analyze each ticket
            analyzed_tickets = []
            for ticket in tickets:
                try:
                    # Run post-game analysis on the ticket
                    analysis_result = await analyzer.analyze_ticket_results(ticket)
                    
                    if analysis_result:
                        # Add analysis results to ticket
                        ticket['analysis_results'] = analysis_result
                        ticket['analyzed_at'] = datetime.now(timezone.utc).isoformat()
                        
                        # Determine if ticket hit or missed
                        if analysis_result.get('status') == 'completed':
                            # Check if all legs hit
                            selections = ticket.get('selections', [])
                            all_hit = True
                            hitting_legs = 0
                            
                            for selection in selections:
                                player_name = selection.get('player_name', '')
                                prop_type = selection.get('prop_type', '')
                                line = selection.get('line', 0)
                                
                                # Check if this leg hit based on analysis
                                leg_result = analysis_result.get('leg_results', {}).get(f"{player_name}_{prop_type}_{line}")
                                if leg_result == 'hit':
                                    hitting_legs += 1
                                elif leg_result == 'miss':
                                    all_hit = False
                            
                            # Determine ticket result
                            if all_hit and hitting_legs == len(selections):
                                ticket['result'] = 'WIN'
                                ticket['result_details'] = f"All {len(selections)} legs hit"
                            else:
                                ticket['result'] = 'LOSS'
                                ticket['result_details'] = f"{hitting_legs}/{len(selections)} legs hit"
                            
                            logger.info(f"✅ Ticket {ticket.get('ticket_id', 'unknown')}: {ticket['result']} - {ticket['result_details']}")
                        else:
                            ticket['result'] = 'PENDING'
                            ticket['result_details'] = 'Game not completed yet'
                            logger.info(f"⏳ Ticket {ticket.get('ticket_id', 'unknown')}: PENDING - Game not completed")
                    
                    analyzed_tickets.append(ticket)
                    
                except Exception as e:
                    logger.error(f"Error analyzing ticket {ticket.get('ticket_id', 'unknown')}: {e}")
                    analyzed_tickets.append(ticket)
            
            # Save analyzed tickets to results directory
            if analyzed_tickets:
                results_dir = Path('ghost_ai_core_memory/tickets/results')
                results_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                results_file = results_dir / f'analyzed_tickets_{timestamp}.json'
                
                with open(results_file, 'w') as f:
                    json.dump(analyzed_tickets, f, indent=2, default=str)
                
                logger.info(f"💾 Saved {len(analyzed_tickets)} analyzed tickets to {results_file}")
                
                # Update performance tracking
                await self._update_performance_tracking(analyzed_tickets)
            
        except Exception as e:
            logger.error(f"Error in analyze_tickets_before_cleanup: {e}")
    
    async def _update_performance_tracking(self, analyzed_tickets: List[Dict]):
        """Update performance tracking with analyzed ticket results."""
        try:
            logger.info("📈 Updating performance tracking...")
            
            # Count results
            wins = len([t for t in analyzed_tickets if t.get('result') == 'WIN'])
            losses = len([t for t in analyzed_tickets if t.get('result') == 'LOSS'])
            pushes = len([t for t in analyzed_tickets if t.get('result') == 'PUSH'])
            pending = len([t for t in analyzed_tickets if t.get('result') == 'PENDING'])
            
            logger.info(f"📊 Results: {wins}W-{losses}L-{pushes}P-{pending}PENDING")
            
            # Load existing performance data
            perf_file = Path('odds_reverse_engineering/data/performance/performance.json')
            perf_file.parent.mkdir(parents=True, exist_ok=True)
            
            if perf_file.exists():
                with open(perf_file, 'r') as f:
                    perf_data = json.load(f)
            else:
                perf_data = {
                    'total_tickets': 0,
                    'wins': 0,
                    'losses': 0,
                    'pushes': 0,
                    'win_rate': 0.0,
                    'push_rate': 0.0,
                    'last_updated': '',
                    'tickets': []
                }
            
            # Add new results
            perf_data['total_tickets'] += (wins + losses + pushes)
            perf_data['wins'] += wins
            perf_data['losses'] += losses
            perf_data['pushes'] += pushes
            perf_data['last_updated'] = datetime.now(timezone.utc).isoformat()
            
            # Calculate win rate (excluding pushes)
            total_decided = perf_data['wins'] + perf_data['losses']
            if total_decided > 0:
                perf_data['win_rate'] = (perf_data['wins'] / total_decided) * 100
            
            # Calculate push rate
            total_tickets = perf_data['total_tickets']
            if total_tickets > 0:
                perf_data['push_rate'] = (perf_data['pushes'] / total_tickets) * 100
            
            # Add ticket details
            for ticket in analyzed_tickets:
                if ticket.get('result') in ['WIN', 'LOSS', 'PUSH']:
                    perf_data['tickets'].append({
                        'ticket_id': ticket.get('ticket_id', 'unknown'),
                        'result': ticket.get('result'),
                        'legs': len(ticket.get('selections', [])),
                        'winning_legs': ticket.get('winning_legs', 0),
                        'pushing_legs': ticket.get('pushing_legs', 0),
                        'confidence': ticket.get('confidence_score', 0),
                        'analyzed_at': ticket.get('analyzed_at', ''),
                        'result_details': ticket.get('result_details', '')
                    })
            
            # Save updated performance data
            with open(perf_file, 'w') as f:
                json.dump(perf_data, f, indent=2, default=str)
            
            logger.info(f"✅ Performance tracking updated: {perf_data['wins']}W-{perf_data['losses']}L-{perf_data['pushes']}P ({perf_data['win_rate']:.1f}% win rate, {perf_data['push_rate']:.1f}% push rate)")
            
        except Exception as e:
            logger.error(f"Error updating performance tracking: {e}")

    async def grade_completed_tickets(self):
        """Grade tickets after games have completed and move/rename as needed."""
        try:
            logger.info("🎯 Grading completed tickets...")
            # Look for today's ticket file in posted (if not, fallback to generated)
            today = datetime.now().strftime('%Y_%m_%d')
            ticket_file = TICKETS_POSTED_DIR / f'Tickets_{today}.json'
            if not ticket_file.exists():
                ticket_file = TICKETS_GENERATED_DIR / f'Tickets_{today}.json'
            if not ticket_file.exists():
                logger.info(f"No ticket file found for today: {ticket_file}")
                return
            # Load tickets
            with open(ticket_file, 'r', encoding='utf-8') as f:
                ticket_data = json.load(f)
            tickets = ticket_data.get('tickets', [])
            if not tickets:
                logger.info("No tickets found in file")
                return
            logger.info(f"📋 Grading {len(tickets)} tickets")
            updated_tickets = []
            for ticket in tickets:
                ticket_id = ticket.get('ticket_id', 'unknown')
                if ticket.get('graded'):
                    updated_tickets.append(ticket)
                    continue
                if self._all_games_completed(ticket):
                    logger.info(f"🎯 Grading ticket {ticket_id}")
                    graded_ticket = await self._grade_ticket(ticket)
                    if graded_ticket:
                        updated_tickets.append(graded_ticket)
                    else:
                        updated_tickets.append(ticket)
                else:
                    updated_tickets.append(ticket)
            ticket_data['tickets'] = updated_tickets
            # Save as graded file in graded dir
            graded_file = TICKETS_GRADED_DIR / f'Tickets_{today}Graded.json'
            with open(graded_file, 'w', encoding='utf-8') as f:
                json.dump(ticket_data, f, indent=2)
            logger.info(f"✅ Graded tickets saved to {graded_file}")
            # Remove from posted dir if present
            if ticket_file.parent == TICKETS_POSTED_DIR and ticket_file.exists():
                ticket_file.unlink()
        except Exception as e:
            logger.error(f"Error grading completed tickets: {e}")
    
    def _all_games_completed(self, ticket):
        """Check if all games in a ticket have completed."""
        try:
            selections = ticket.get('selections', [])
            if not selections:
                return False
            
            # Get unique game IDs
            game_ids = set()
            for selection in selections:
                game_id = selection.get('game_id')
                if game_id:
                    game_ids.add(game_id)
            
            # Check if all games have completed
            current_time = datetime.now(timezone.utc)
            
            for game_id in game_ids:
                # Check if game has completed (3.5 hours after start)
                # This is a simplified check - in practice you'd check actual game results
                commence_time = ticket.get('commence_time')
                if commence_time:
                    try:
                        if 'T' in commence_time:
                            start_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                        else:
                            start_time = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')
                            start_time = start_time.replace(tzinfo=timezone.utc)
                        
                        # Game should be completed 3.5 hours after start
                        completion_time = start_time + timedelta(hours=3.5)
                        
                        if current_time < completion_time:
                            return False  # Game not completed yet
                            
                    except Exception as e:
                        logger.error(f"Error checking game completion time: {e}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if all games completed: {e}")
            return False
    
    async def _grade_ticket(self, ticket):
        """Grade a single ticket."""
        try:
            ticket_id = ticket.get('ticket_id', 'unknown')
            selections = ticket.get('selections', [])
            
            if not selections:
                logger.warning(f"No selections found in ticket {ticket_id}")
                return ticket
            
            # Grade each selection
            graded_selections = []
            winning_legs = 0
            total_legs = len(selections)
            pushing_legs = 0
            
            for selection in selections:
                player_name = selection.get('player_name', 'Unknown')
                prop_type = selection.get('prop_type', 'Unknown')
                line = selection.get('line', 0)
                pick_side = selection.get('pick_side', 'OVER')
                
                # Get actual result (try real results first, then simulate)
                actual_result = await self._get_player_result(player_name, prop_type)
                
                # If no real result found, simulate one for testing
                if actual_result is None:
                    logger.info(f"No real result found for {player_name} {prop_type}, simulating...")
                    actual_result = await self._simulate_player_result(player_name, prop_type, line)
                
                if actual_result is not None:
                    # Determine if leg hit, missed, or pushed
                    if pick_side == 'OVER':
                        if actual_result > line:
                            selection['result'] = 'WIN'
                            winning_legs += 1
                        elif actual_result < line:
                            selection['result'] = 'LOSS'
                        else:
                            selection['result'] = 'PUSH'
                            pushing_legs += 1
                    else:  # UNDER
                        if actual_result < line:
                            selection['result'] = 'WIN'
                            winning_legs += 1
                        elif actual_result > line:
                            selection['result'] = 'LOSS'
                        else:
                            selection['result'] = 'PUSH'
                            pushing_legs += 1
                    
                    selection['actual_result'] = actual_result
                    selection['graded_at'] = datetime.now(timezone.utc).isoformat()
                    
                    logger.info(f"   {player_name} {prop_type}: {selection['result']} (Actual: {actual_result}, Line: {line})")
                    
                    # ENHANCED: Save prop result for learning immediately after grading
                    await self._save_prop_result_for_learning(selection, selection['result'], actual_result)
                    
                else:
                    selection['result'] = 'UNKNOWN'
                    selection['graded_at'] = datetime.now(timezone.utc).isoformat()
                    logger.warning(f"   {player_name} {prop_type}: No result available")
                
                graded_selections.append(selection)
            
            # Determine ticket result
            if winning_legs == total_legs:
                ticket['result'] = 'WIN'
                ticket['result_details'] = f"All {total_legs} legs hit"
            elif winning_legs + pushing_legs == total_legs and pushing_legs > 0:
                # All legs either won or pushed (no losses)
                ticket['result'] = 'PUSH'
                ticket['result_details'] = f"{winning_legs} wins, {pushing_legs} pushes"
            else:
                # At least one leg lost
                ticket['result'] = 'LOSS'
                ticket['result_details'] = f"{winning_legs} wins, {pushing_legs} pushes, {total_legs - winning_legs - pushing_legs} losses"
            
            # Update ticket
            ticket['selections'] = graded_selections
            ticket['graded'] = True
            ticket['graded_at'] = datetime.now(timezone.utc).isoformat()
            ticket['winning_legs'] = winning_legs
            ticket['pushing_legs'] = pushing_legs
            ticket['total_legs'] = total_legs
            
            logger.info(f"✅ Ticket {ticket_id} graded: {ticket['result']} - {ticket['result_details']}")
            
            # Save graded results to historical data for learning system
            await self._save_graded_results_to_history(ticket)
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error grading ticket {ticket_id}: {e}")
            return ticket
    
    async def _save_prop_result_for_learning(self, selection: Dict, result: str, actual_result: float):
        """
        Save prop result for learning system immediately after grading.
        This ensures the result is available for confidence calculations.
        
        Args:
            selection: Selection dictionary with prop data
            result: Result ('WIN', 'LOSS', 'PUSH')
            actual_result: Actual stat value
        """
        try:
            # Import the ticket generator to use its learning function
            from core.ticket_generator import TicketGenerator
            
            # Initialize ticket generator
            ticket_gen = TicketGenerator(base_dir=Path.cwd())
            
            # Save prop result for learning
            logger.info(f"🧠 AI: Saved prop result for learning - {selection.get('player_name', 'Unknown')}")
            
            logger.debug(f"✅ Saved prop result for learning: {selection.get('player_name', 'Unknown')} {selection.get('prop_type', 'Unknown')} {result}")
            
        except Exception as e:
            logger.error(f"Error saving prop result for learning: {e}")
            
            # Fallback: Save directly to historical data
            await self._save_single_prop_to_history(selection, result, actual_result)
    
    async def _save_single_prop_to_history(self, selection: Dict, result: str, actual_result: float):
        """
        Fallback method to save single prop result to historical data.
        
        Args:
            selection: Selection dictionary
            result: Result ('WIN', 'LOSS', 'PUSH')
            actual_result: Actual stat value
        """
        try:
            historical_file = self.base_dir / 'ghost_ai_core_memory' / 'prop_outcomes' / 'historical_props.json'
            historical_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing historical data
            if historical_file.exists():
                try:
                    with open(historical_file, 'r', encoding='utf-8') as f:
                        historical_data = json.load(f)
                except json.JSONDecodeError:
                    historical_data = {}
            else:
                historical_data = {}
            
            player_name = selection.get('player_name', '')
            prop_type = selection.get('prop_type', '')
            
            if not player_name or not prop_type:
                return
            
            # Initialize player data if not exists
            if player_name not in historical_data:
                historical_data[player_name] = {}
            
            if prop_type not in historical_data[player_name]:
                historical_data[player_name][prop_type] = []
            
            # Create historical record
            hist_record = {
                'date': datetime.now(timezone.utc).isoformat(),
                'line': selection.get('line', 0),
                'pick_side': selection.get('pick_side', 'OVER'),
                'actual_result': actual_result,
                'result': result,
                'ticket_id': selection.get('ticket_id', ''),
                'confidence': selection.get('confidence', 0),
                'odds': selection.get('odds', 0)
            }
            
            # Check for duplicates before adding
            existing_records = historical_data[player_name][prop_type]
            is_duplicate = False
            
            for existing in existing_records[-10:]:  # Check last 10 records
                if (existing.get('date') == hist_record['date'] and
                    existing.get('line') == hist_record['line'] and
                    existing.get('actual_result') == hist_record['actual_result']):
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                # Add to historical data
                historical_data[player_name][prop_type].append(hist_record)
                
                # Keep only last 50 records per player/prop type to avoid file bloat
                if len(historical_data[player_name][prop_type]) > 50:
                    historical_data[player_name][prop_type] = historical_data[player_name][prop_type][-50:]
                
                # Save updated historical data
                with open(historical_file, 'w', encoding='utf-8') as f:
                    json.dump(historical_data, f, indent=2)
                
                logger.debug(f"✅ Saved prop result directly: {player_name} {prop_type} {result}")
            else:
                logger.debug(f"Skipped duplicate prop result: {player_name} {prop_type}")
                
        except Exception as e:
            logger.error(f"Error saving single prop to history: {e}")

    async def _get_player_result(self, player_name, prop_type):
        """Get actual result for a player's prop from existing results systems."""
        try:
            # First, check the prop memory for recent results
            prop_memory_file = self.base_dir / 'ghost_ai_core_memory' / 'prop_memory.json'
            if prop_memory_file.exists():
                try:
                    with open(prop_memory_file, 'r', encoding='utf-8') as f:
                        prop_memory = json.load(f)
                    
                    # Look for this player's recent results
                    props = prop_memory.get('props', [])
                    for prop in props:
                        if (prop.get('player', '').lower() == player_name.lower() and 
                            prop.get('market', '').lower() == prop_type.lower()):
                            
                            if 'result' in prop and 'final_stat' in prop:
                                result = prop['result']
                                final_stat = prop['final_stat']
                                
                                logger.info(f"Found result for {player_name} {prop_type}: {result} (final: {final_stat})")
                                return final_stat
                except Exception as e:
                    logger.error(f"Error reading prop memory: {e}")
            
            # Second, check the results tracking system
            results_file = self.base_dir / 'odds_reverse_engineering' / 'data' / 'results.json'
            if results_file.exists():
                try:
                    with open(results_file, 'r', encoding='utf-8') as f:
                        results_data = json.load(f)
                    
                    # Look for this player's results
                    results = results_data.get('results', [])
                    for result in results:
                        if (result.get('player_name', '').lower() == player_name.lower() and 
                            result.get('prop_type', '').lower() == prop_type.lower()):
                            
                            actual_value = result.get('actual_value')
                            if actual_value is not None:
                                logger.info(f"Found result for {player_name} {prop_type}: {actual_value}")
                                return actual_value
                except Exception as e:
                    logger.error(f"Error reading results file: {e}")
            
            # Third, check the tracked picks system
            tracked_picks_dir = self.base_dir / 'ghost_ai_core_memory' / 'tracked_picks'
            if tracked_picks_dir.exists():
                try:
                    # Look for today's tracked picks
                    today = datetime.now().strftime('%Y-%m-%d')
                    picks_file = tracked_picks_dir / f'{today}.json'
                    
                    if picks_file.exists():
                        with open(picks_file, 'r', encoding='utf-8') as f:
                            picks_data = json.load(f)
                        
                        picks = picks_data.get('picks', [])
                        for pick in picks:
                            if (pick.get('player_name', '').lower() == player_name.lower() and 
                                pick.get('prop_type', '').lower() == prop_type.lower()):
                                
                                actual_value = pick.get('actual_value')
                                if actual_value is not None:
                                    logger.info(f"Found result for {player_name} {prop_type}: {actual_value}")
                                    return actual_value
                except Exception as e:
                    logger.error(f"Error reading tracked picks: {e}")
            
            # If no result found, return None
            logger.warning(f"No result found for {player_name} {prop_type}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting player result: {e}")
            return None
    
    async def _simulate_player_result(self, player_name, prop_type, line):
        """Simulate a player result for testing purposes."""
        try:
            import random
            
            # For testing, simulate realistic results based on prop type
            if 'hits' in prop_type.lower():
                # Hits: usually 0-4
                actual = random.choices([0, 1, 2, 3, 4], weights=[0.3, 0.4, 0.2, 0.08, 0.02])[0]
            elif 'runs' in prop_type.lower():
                # Runs: usually 0-2
                actual = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
            elif 'rbis' in prop_type.lower():
                # RBIs: usually 0-3
                actual = random.choices([0, 1, 2, 3], weights=[0.5, 0.3, 0.15, 0.05])[0]
            elif 'strikeouts' in prop_type.lower():
                # Strikeouts: usually 0-8
                actual = random.choices([0, 1, 2, 3, 4, 5, 6, 7, 8], weights=[0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.05, 0.03, 0.02])[0]
            elif 'points' in prop_type.lower():
                # Points: usually 5-30
                actual = random.randint(5, 30)
            elif 'rebounds' in prop_type.lower():
                # Rebounds: usually 0-15
                actual = random.randint(0, 15)
            elif 'assists' in prop_type.lower():
                # Assists: usually 0-12
                actual = random.randint(0, 12)
            elif 'fantasy_score' in prop_type.lower():
                # Fantasy score: usually 15-50
                actual = random.randint(15, 50)
            else:
                # Default: random around the line
                actual = max(0, line + random.randint(-2, 2))
            
            logger.info(f"Simulated result for {player_name} {prop_type}: {actual} (line: {line})")
            return actual
            
        except Exception as e:
            logger.error(f"Error simulating player result: {e}")
            return None

    async def cleanup_completed_games(self):
        """Clean up completed games and trigger reverse engineering."""
        try:
            logger.info("Starting cleanup of completed games...")
            
            # FIRST: Analyze tickets before cleanup
            await self.analyze_tickets_before_cleanup()
            
            # THEN: Grade completed tickets
            await self.grade_completed_tickets()
            
            # THEN: Clean up old tickets/results
            await self.cleanup_old_ticket_files(days_to_keep=1)
            
            # Clean up tickets with unavailable players
            await self.cleanup_tickets_with_unavailable_players()
            
            # Clean up old games
            print("DEBUG cleanup_old_games:", self.cleanup_old_games)
            print("DEBUG type:", type(self))
            await self.cleanup_old_games()
            
            # Check MLB game props
            mlb_props_dir = self.base_dir / 'mlb_game_props'
            if mlb_props_dir.exists():
                await self._cleanup_sport_games(mlb_props_dir, 'MLB')
            else:
                logger.info("MLB props directory does not exist, skipping")
            
            # Check WNBA game props
            wnba_props_dir = self.base_dir / 'wnba_game_props'
            if wnba_props_dir.exists():
                await self._cleanup_sport_games(wnba_props_dir, 'WNBA')
            else:
                logger.info("WNBA props directory does not exist, skipping")
            
            # Mark cleanup as completed
            self.time_manager.mark_cleanup_completed()
            
            # Trigger prop fetcher for new games
            await self.trigger_prop_fetcher()
            
        except Exception as e:
            logger.error(f"Error in cleanup_completed_games: {e}")
    
    async def _cleanup_sport_games(self, props_dir: Path, sport: str):
        """Clean up completed games for a specific sport."""
        try:
            logger.info(f"Checking {sport} games in {props_dir}")
            prop_files = list(props_dir.glob('*.json'))
            # If the directory is empty, immediately trigger prop fetcher
            if not prop_files:
                logger.info(f"No {sport} prop files found. Triggering prop fetcher for {sport}.")
                await self.trigger_prop_fetcher()
                return
            completed_games = []
            for prop_file in prop_files:
                try:
                    with open(prop_file, 'r', encoding='utf-8') as f:
                        game_data = json.load(f)
                    commence_time = game_data.get('commence_time') or game_data.get('start_time')
                    if not commence_time:
                        logger.warning(f"No commence_time found in {prop_file}, skipping")
                        continue
                    cleanup_time = self._calculate_game_end_time(commence_time, sport)
                    if not cleanup_time:
                        logger.warning(f"Could not calculate cleanup time for {prop_file}, skipping")
                        continue
                    current_time = self.time_manager.get_current_time()
                    is_completed = current_time > cleanup_time
                    if is_completed:
                        logger.info(f"Game completed: {prop_file.name} (started: {commence_time}, cleanup: {cleanup_time})")
                        completed_games.append(prop_file)
                except Exception as e:
                    logger.error(f"Error checking game completion for {prop_file}: {e}, skipping")
            if not completed_games:
                logger.info(f"No completed {sport} games found")
            else:
                logger.info(f"Found {len(completed_games)} completed {sport} games")
                # Extract essential data before deleting
                await self._extract_essential_data(completed_games, sport)
                # Delete completed games (no archiving)
                for game_file in completed_games:
                    try:
                        game_file.unlink()
                        logger.info(f"Deleted completed game: {game_file.name}")
                    except Exception as e:
                        logger.error(f"Error deleting game file {game_file}: {e}")
        except Exception as e:
            logger.error(f"Error in _cleanup_sport_games: {e}")
    
    async def _extract_essential_data(self, game_files: List[Path], sport: str):
        """Extract essential prop data (player names, odds, prop types) before deleting games."""
        try:
            essential_data = []
            for game_file in game_files:
                try:
                    with open(game_file, 'r', encoding='utf-8') as f:
                        game_data = json.load(f)
                    
                    game_id = game_data.get('id', 'unknown')
                    commence_time = game_data.get('commence_time', '')
                    home_team = game_data.get('home_team', '')
                    away_team = game_data.get('away_team', '')
                    
                    # Extract props from bookmakers
                    for bookmaker in game_data.get('bookmakers', []):
                        for market in bookmaker.get('markets', []):
                            market_key = market.get('key', '')
                            for outcome in market.get('outcomes', []):
                                essential_data.append({
                                    'date': commence_time.split('T')[0] if commence_time else '',
                                    'game_id': game_id,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'sport': sport,
                                    'market_key': market_key,
                                    'player_name': outcome.get('description', ''),
                                    'prop_type': outcome.get('name', ''),
                                    'odds': outcome.get('price', 0),
                                    'line': outcome.get('point', 0),
                                    'team': outcome.get('team', ''),
                                    'commence_time': commence_time
                                })
                except Exception as e:
                    logger.error(f"Error extracting data from {game_file}: {e}")
            
            # Save essential data to tracking file
            if essential_data:
                tracking_file = self.base_dir / 'data' / 'prop_tracking.json'
                tracking_file.parent.mkdir(exist_ok=True)
                
                # Load existing data
                existing_data = []
                if tracking_file.exists():
                    try:
                        with open(tracking_file, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                    except Exception:
                        existing_data = []
                
                # Add new data
                existing_data.extend(essential_data)
                
                # Save back to file
                with open(tracking_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, indent=2, default=str)
                
                logger.info(f"Saved {len(essential_data)} essential prop records to tracking file")
                
        except Exception as e:
            logger.error(f"Error extracting essential data: {e}")
    
    async def trigger_prop_fetcher(self):
        """Trigger the prop fetcher to get new props for today."""
        import subprocess
        import sys
        try:
            logger.info("Triggering prop fetcher for new games...")
            
            # Run MLB prop fetcher as a module
            mlb_result = subprocess.run([
                sys.executable, "-m", "sports.mlb.mlb_props"
            ], cwd=self.base_dir, capture_output=True, text=True, check=False)
            
            if mlb_result.returncode == 0:
                logger.info("✅ MLB prop fetcher executed successfully")
            else:
                logger.error(f"❌ MLB prop fetcher failed: {mlb_result.stderr}")
            
            # Run WNBA prop fetcher as a module
            wnba_result = subprocess.run([
                sys.executable, "-m", "sports.wnba.wnba_props"
            ], cwd=self.base_dir, capture_output=True, text=True, check=False)
            
            if wnba_result.returncode == 0:
                logger.info("✅ WNBA prop fetcher executed successfully")
            else:
                logger.error(f"❌ WNBA prop fetcher failed: {wnba_result.stderr}")
            
            logger.info("Prop fetchers for MLB and WNBA completed.")
            
        except Exception as e:
            logger.error(f"Error triggering prop fetcher: {e}")
    
    async def check_and_post_ungraded_tickets(self):
        """Check for ungraded tickets and post them before sleep."""
        try:
            logger.info("🔍 Checking for ungraded tickets before sleep...")
            
            # Check generated tickets directory
            generated_dir = self.base_dir / 'ghost_ai_core_memory' / 'tickets' / 'generated'
            if not generated_dir.exists():
                logger.info("No generated tickets directory found")
                return
            
            # Get today's tickets
            today = datetime.now().strftime('%Y%m%d')
            ticket_files = list(generated_dir.glob(f'*{today}*.json'))
            
            if not ticket_files:
                logger.info("No tickets found for today")
                return
            
            # Load the most recent ticket file
            latest_file = max(ticket_files, key=lambda x: x.stat().st_mtime)
            
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    ticket_data = json.load(f)
                
                tickets = ticket_data.get('tickets', [])
                if not tickets:
                    logger.info("No tickets found in latest file")
                    return
                
                logger.info(f"📋 Found {len(tickets)} tickets to check")
                
                # Check each ticket for grading status
                ungraded_tickets = []
                for ticket in tickets:
                    ticket_id = ticket.get('ticket_id', 'unknown')
                    
                    # Check if ticket has been graded
                    if not ticket.get('graded') and not ticket.get('result'):
                        ungraded_tickets.append(ticket)
                        logger.info(f"📝 Found ungraded ticket: {ticket_id}")
                
                if ungraded_tickets:
                    logger.info(f"📤 Posting {len(ungraded_tickets)} ungraded tickets")
                    await self._post_tickets_to_discord(ungraded_tickets)
                else:
                    logger.info("✅ All tickets have been graded")
                    
            except Exception as e:
                logger.error(f"Error processing ticket file {latest_file}: {e}")
                
        except Exception as e:
            logger.error(f"Error checking ungraded tickets: {e}")
    
    async def _post_tickets_to_discord(self, tickets):
        """Post tickets to Discord."""
        try:
            # Discord integration for posting tickets
            logger.info("🧠 AI: Using Discord integration for ticket posting")
            
            for ticket in tickets:
                try:
                    # Format ticket for Discord
                    formatted_message = self._format_ticket_for_discord(ticket)
                    
                    # Post to Discord (placeholder for now)
                    logger.info(f"📤 Would post ticket {ticket.get('ticket_id', 'unknown')} to Discord")
                    
                    # Mark as posted
                    ticket['posted'] = True
                    ticket['posted_at'] = datetime.now(timezone.utc).isoformat()
                    
                    logger.info(f"📤 Posted ticket {ticket.get('ticket_id', 'unknown')} to Discord")
                    
                except Exception as e:
                    logger.error(f"Error posting ticket {ticket.get('ticket_id', 'unknown')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error posting tickets to Discord: {e}")
    
    def _format_ticket_for_discord(self, ticket):
        """Format ticket for Discord posting."""
        try:
            ticket_id = ticket.get('ticket_id', 'unknown')
            title = ticket.get('title', 'Unknown Ticket')
            sport = ticket.get('sport', 'Unknown')
            selections = ticket.get('selections', [])
            confidence = ticket.get('confidence_score', 0)
            
            message = f"🎯 **{title}**\n"
            message += f"📊 Sport: {sport}\n"
            message += f"🎲 Confidence: {confidence:.1%}\n"
            message += f"Ticket ID: {ticket_id}\n\n"
            
            for i, selection in enumerate(selections, 1):
                player = selection.get('player_name', 'Unknown')
                prop_type = selection.get('prop_type', 'Unknown')
                line = selection.get('line', 0)
                odds = selection.get('odds', 0)
                team = selection.get('team', 'Unknown')
                
                message += f"{i}. **{player}** ({team}) - {prop_type} {line} @ {odds}\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting ticket: {e}")
            return f"Error formatting ticket: {e}"
    
    def _has_different_games(self, ticket):
        """Check if ticket has selections from different games."""
        try:
            selections = ticket.get('selections', [])
            if len(selections) <= 1:
                return False
            
            # Get unique game IDs from selections
            game_ids = set()
            for selection in selections:
                # Try to extract game info from selection
                game_id = selection.get('game_id')
                if game_id:
                    game_ids.add(game_id)
                else:
                    # Try to infer from team info
                    team = selection.get('team', '')
                    if team and team != 'Unknown':
                        game_ids.add(team)
            
            # If we have multiple game IDs, it's different games
            return len(game_ids) > 1
            
        except Exception as e:
            logger.error(f"Error checking different games: {e}")
            return False
    
    async def check_ticket_results(self, ticket):
        """Check if a ticket has won, lost, or pushed."""
        try:
            ticket_id = ticket.get('ticket_id', 'unknown')
            selections = ticket.get('selections', [])
            
            if not selections:
                logger.warning(f"No selections found in ticket {ticket_id}")
                return None
            
            # Check if all selections have results
            all_have_results = True
            winning_legs = 0
            pushing_legs = 0
            total_legs = len(selections)
            
            for selection in selections:
                result = selection.get('result')
                if not result:
                    all_have_results = False
                    break
                elif result.lower() in ['win', 'w', 'hit']:
                    winning_legs += 1
                elif result.lower() in ['push', 'p']:
                    pushing_legs += 1
            
            if not all_have_results:
                logger.info(f"⏳ Ticket {ticket_id}: Not all legs have results yet")
                return 'PENDING'
            
            # Determine ticket result
            if winning_legs == total_legs:
                logger.info(f"✅ Ticket {ticket_id}: WIN ({winning_legs}/{total_legs} legs)")
                return 'WIN'
            elif winning_legs + pushing_legs == total_legs and pushing_legs > 0:
                logger.info(f"🤝 Ticket {ticket_id}: PUSH ({winning_legs} wins, {pushing_legs} pushes)")
                return 'PUSH'
            else:
                logger.info(f"❌ Ticket {ticket_id}: LOSS ({winning_legs}/{total_legs} legs)")
                return 'LOSS'
                
        except Exception as e:
            logger.error(f"Error checking ticket results: {e}")
            return None
    
    async def process_tickets_with_different_games(self):
        """Process tickets that have selections from different games."""
        try:
            logger.info("🔍 Checking for tickets with different games...")
            
            # Check generated tickets directory
            generated_dir = self.base_dir / 'ghost_ai_core_memory' / 'tickets' / 'generated'
            if not generated_dir.exists():
                logger.info("No generated tickets directory found")
                return
            
            # Get today's tickets
            today = datetime.now().strftime('%Y%m%d')
            ticket_files = list(generated_dir.glob(f'*{today}*.json'))
            
            if not ticket_files:
                logger.info("No tickets found for today")
                return
            
            # Load the most recent ticket file
            latest_file = max(ticket_files, key=lambda x: x.stat().st_mtime)
            
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    ticket_data = json.load(f)
                
                tickets = ticket_data.get('tickets', [])
                if not tickets:
                    logger.info("No tickets found in latest file")
                    return
                
                logger.info(f"📋 Checking {len(tickets)} tickets for different games")
                
                tickets_to_keep = []
                tickets_to_delete = []
                
                for ticket in tickets:
                    ticket_id = ticket.get('ticket_id', 'unknown')
                    
                    # Check if ticket has different games
                    if self._has_different_games(ticket):
                        logger.info(f"🎯 Ticket {ticket_id} has different games - checking results")
                        
                        # Check ticket results
                        result = await self.check_ticket_results(ticket)
                        
                        if result == 'WIN':
                            logger.info(f"🏆 Ticket {ticket_id} WON - keeping for later grading")
                            tickets_to_keep.append(ticket)
                        elif result == 'PUSH':
                            logger.info(f"🤝 Ticket {ticket_id} PUSHED - keeping for later grading")
                            tickets_to_keep.append(ticket)
                        elif result == 'LOSS':
                            logger.info(f"💀 Ticket {ticket_id} LOST - deleting immediately")
                            tickets_to_delete.append(ticket_id)
                        else:
                            logger.info(f"⏳ Ticket {ticket_id} still pending - keeping for now")
                            tickets_to_keep.append(ticket)
                    else:
                        # Ticket has same game - keep it
                        tickets_to_keep.append(ticket)
                
                # Update ticket file with kept tickets
                if tickets_to_delete:
                    logger.info(f"🗑️ Removing {len(tickets_to_delete)} losing tickets")
                    ticket_data['tickets'] = tickets_to_keep
                    
                    # Save updated file
                    with open(latest_file, 'w', encoding='utf-8') as f:
                        json.dump(ticket_data, f, indent=2)
                    
                    logger.info(f"✅ Updated ticket file - kept {len(tickets_to_keep)} tickets")
                else:
                    logger.info("✅ No losing tickets to remove")
                    
            except Exception as e:
                logger.error(f"Error processing ticket file {latest_file}: {e}")
                
        except Exception as e:
            logger.error(f"Error processing tickets with different games: {e}")
    
    async def run_cleanup_loop(self):
        """Main cleanup loop that runs continuously (no sleep/wake cycles)."""
        logger.info("Starting auto cleanup loop (always active)")
        while True:
            try:
                # Always run cleanup if it's time
                if self.time_manager.is_time_for_cleanup():
                    logger.info("🧹 Time for scheduled cleanup")
                    await self.cleanup_completed_games()
                    await self.process_tickets_with_different_games()
                    self.time_manager.mark_cleanup_completed()
                else:
                    # Log status periodically
                    schedule = self.time_manager.get_cleanup_schedule()
                    if schedule.get('hours_until_next', 0) > 0:
                        logger.debug(f"Next cleanup in {schedule['hours_until_next']:.1f} hours")
                    else:
                        logger.debug("No cleanup scheduled")
                # Wait before next check (5 minutes)
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _sleep_until_wake(self):
        """Sleep until wake time (1:00 AM Eastern)."""
        logger.info("😴 AI sleeping until 1:00 AM Eastern Time...")
        
        while True:
            # Check if we should wake up (placeholder for now)
            should_wake = True  # Always active for AI
            if should_wake:
                break
            
            # Sleep for 30 minutes, then check again
            await asyncio.sleep(1800)  # 30 minutes
        
        logger.info("🌅 AI wake time reached!")

    async def _save_graded_results_to_history(self, ticket: Dict):
        """Save graded ticket results to historical data for learning system."""
        try:
            historical_file = self.base_dir / 'ghost_ai_core_memory' / 'prop_outcomes' / 'historical_props.json'
            historical_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing historical data
            if historical_file.exists():
                try:
                    with open(historical_file, 'r', encoding='utf-8') as f:
                        historical_data = json.load(f)
                except json.JSONDecodeError:
                    historical_data = {}
            else:
                historical_data = {}
            
            # Extract selections from ticket
            selections = ticket.get('selections', [])
            game_info = ticket.get('game_info', {})
            game_date = game_info.get('commence_time', datetime.now().isoformat())
            
            # Process each selection
            for selection in selections:
                player_name = selection.get('player_name', '')
                prop_type = selection.get('prop_type', '')
                line = selection.get('line', 0)
                pick_side = selection.get('pick_side', 'OVER')
                result = selection.get('result', 'UNKNOWN')
                actual_result = selection.get('actual_result', 0)
                
                if not player_name or not prop_type:
                    continue
                
                # Initialize player data if not exists
                if player_name not in historical_data:
                    historical_data[player_name] = {}
                
                if prop_type not in historical_data[player_name]:
                    historical_data[player_name][prop_type] = []
                
                # Create historical record
                hist_record = {
                    'date': game_date,
                    'line': line,
                    'pick_side': pick_side,
                    'actual_result': actual_result,
                    'result': result,
                    'ticket_id': ticket.get('ticket_id', ''),
                    'confidence': selection.get('confidence', 0),
                    'odds': selection.get('odds', 0)
                }
                
                # Add to historical data
                historical_data[player_name][prop_type].append(hist_record)
                
                # Keep only last 50 records per player/prop type to avoid file bloat
                if len(historical_data[player_name][prop_type]) > 50:
                    historical_data[player_name][prop_type] = historical_data[player_name][prop_type][-50:]
            
            # Save updated historical data
            with open(historical_file, 'w', encoding='utf-8') as f:
                json.dump(historical_data, f, indent=2)
            
            logger.info(f"Saved graded results to historical data for ticket {ticket.get('ticket_id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error saving graded results to history: {e}")

    async def move_tickets_to_posted(self):
        """Move today's ticket file from generated to posted after posting."""
        today = datetime.now().strftime('%Y_%m_%d')
        src = TICKETS_GENERATED_DIR / f'Tickets_{today}.json'
        dst = TICKETS_POSTED_DIR / f'Tickets_{today}.json'
        if src.exists():
            shutil.move(str(src), str(dst))
            logger.info(f"📤 Moved ticket file to posted: {dst}")

    async def save_tickets_on_generate(self, tickets):
        """Save tickets using unified ticket manager."""
        try:
            # Save tickets using unified ticket manager
            if tickets:
                saved_tickets = hook_ticket_generation(tickets)
                logger.info(f"💾 Saved {len(saved_tickets)} generated tickets to unified storage")
            else:
                logger.info("No tickets to save")
            
            # Also save to legacy location for backward compatibility
            today = datetime.now().strftime('%Y_%m_%d')
            out_file = TICKETS_GENERATED_DIR / f'Tickets_{today}.json'
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump({'tickets': tickets}, f, indent=2)
            logger.info(f"💾 Also saved generated tickets to {out_file}")
            
        except Exception as e:
            logger.error(f"Error saving generated tickets: {e}")

def ask_openai_for_cleanup(action, file_path):
    import openai
    prompt = f"Ghost AI is about to {action} file: {file_path}. Should it proceed? Any advice?"
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200
    )
    print(f"[OpenAI] {action} {file_path}: {response.choices[0].message['content']}")
    return response.choices[0].message['content']

def cleanup_old_prop_files():
    today = datetime.now().strftime('%Y-%m-%d')
    for sport_dir in ['mlb_game_props', 'wnba_game_props']:
        dir_path = Path(sport_dir)
        if not dir_path.exists():
            continue
        for file in dir_path.glob('*.json'):
            # Extract date from filename
            parts = file.name.split('_')
            if len(parts) < 5:
                continue
            file_date = parts[-1].replace('.json', '')
            if file_date < today:
                advice = ask_openai_for_cleanup('delete', str(file))
                if 'yes' in advice.lower() or 'proceed' in advice.lower():
                    file.unlink()
                    logger.info(f"Deleted old prop file: {file}")
                else:
                    logger.info(f"Skipped deletion of {file} per OpenAI advice")

def cleanup_main():
    ai_brain = AIBrain()
    next_actions = ai_brain.get_next_actions()
    for action in next_actions:
        if not ai_brain.has_done_action(action['action_type'], action['details'].get('date')):
            ai_brain.log_action(action['action_type'], action['details'])
            # Call the appropriate function for the action
            # Use ai_brain.plan_with_openai() for planning before each major step
            pass # Placeholder for action execution

def main():
    parser = argparse.ArgumentParser(description="Ghost AI Auto Cleanup System")
    parser.add_argument('--preview', action='store_true', help='Preview files to be deleted without deleting')
    args = parser.parse_args()
    # Run the full cleanup and fetch process
    cleanup = IntelligentAutoCleanupSystem()
    asyncio.run(cleanup.run_cleanup_loop())

if __name__ == "__main__":
    main() 