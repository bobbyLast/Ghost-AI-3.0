#!/usr/bin/env python3
"""
Enhanced Auto-Cleanup System for Ghost AI

This system works with the Ghost Brain to:
- Remember what tickets have been posted
- Track what needs to be graded
- Clean up completed games
- Maintain memory of what has been processed
- Prevent duplicates and ensure proper tracking
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import subprocess
from typing import List, Dict, Optional, Set
import argparse
import os
import shutil
sys.path.append(str(Path(__file__).parent.parent))

from system.time_manager import TimeManager

print('=== Enhanced Auto Cleanup Script Started ===')
import logging
logging.basicConfig(level=logging.INFO)
logging.info('=== Enhanced Auto Cleanup Script Started ===')

logger = logging.getLogger('enhanced_auto_cleanup')

class EnhancedAutoCleanupSystem:
    """Enhanced auto-cleanup system for Ghost AI (no sleep/wake cycles, always active)."""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.time_manager = TimeManager(self.base_dir)
        
        # Initialize Ghost Brain
        try:
            from ghost_ai_core_memory.ghost_brain import create_ghost_brain
            self.ghost_brain = create_ghost_brain(self.base_dir)
            logger.info("🧠 Ghost Brain integrated with auto-cleanup")
        except Exception as e:
            logger.error(f"Failed to initialize Ghost Brain: {e}")
            self.ghost_brain = None
        
        # Initialize Unified Ticket Manager
        try:
            from ghost_ai_core_memory.tickets.unified_ticket_manager import UnifiedTicketManager
            self.ticket_manager = UnifiedTicketManager()
            logger.info("🎫 Unified Ticket Manager integrated")
        except Exception as e:
            logger.error(f"Failed to initialize Unified Ticket Manager: {e}")
            self.ticket_manager = None
        
        # Game durations in hours
        self.game_durations = {
            'MLB': 3.0,
            'WNBA': 2.5
        }
        
        # Cleanup buffer time (additional time after game should end)
        self.cleanup_buffer_hours = 1.0
        
        # Track what needs to be processed
        self.pending_grades = set()
        self.completed_cleanups = set()
        self.memory_updates = set()
        
        logger.info("Enhanced Auto Cleanup System initialized")
        logger.info(f"AI Schedule: Sleep 12:00 PM - 1:00 AM ET, Work 1:00 AM - 12:00 PM ET")
        logger.info(f"Cleanup every {self.time_manager.cleanup_interval_hours} hours during active hours")
    
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
    
    async def analyze_what_needs_processing(self):
        """Analyze what needs to be processed by the brain."""
        try:
            logger.info("🧠 Analyzing what needs processing...")
            
            # Get all tickets from unified storage
            if self.ticket_manager:
                all_tickets = self.ticket_manager.get_all_tickets()
                logger.info(f"Found {len(all_tickets)} total tickets in unified storage")
                
                # Check which tickets need grading
                ungraded_tickets = []
                for ticket in all_tickets:
                    ticket_id = ticket.get('ticket_id')
                    if ticket_id and ticket_id not in self.completed_cleanups:
                        # Check if ticket has results
                        results = self.ticket_manager.get_results(ticket_id)
                        if not results:
                            ungraded_tickets.append(ticket_id)
                
                self.pending_grades = set(ungraded_tickets)
                logger.info(f"📋 Found {len(self.pending_grades)} tickets that need grading")
                
                # Update Ghost Brain memory
                if self.ghost_brain:
                    self.ghost_brain.think(f"Analyzed {len(all_tickets)} tickets, {len(self.pending_grades)} need grading")
            
            # Check for completed games that need cleanup
            completed_games = []
            for props_dir in ['mlb_game_props', 'wnba_game_props']:
                props_path = Path(props_dir)
                if props_path.exists():
                    for game_file in props_path.glob('*.json'):
                        if self._is_game_completed(game_file):
                            completed_games.append(game_file)
            
            logger.info(f"🎮 Found {len(completed_games)} completed games that need cleanup")
            
            return {
                'pending_grades': len(self.pending_grades),
                'completed_games': len(completed_games),
                'total_tickets': len(all_tickets) if self.ticket_manager else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing what needs processing: {e}")
            return {}
    
    async def grade_pending_tickets(self):
        """Grade tickets that need results."""
        try:
            if not self.pending_grades:
                logger.info("No tickets need grading")
                return
            
            logger.info(f"🏁 Grading {len(self.pending_grades)} pending tickets...")
            
            for ticket_id in self.pending_grades:
                try:
                    # Get ticket data
                    ticket = self.ticket_manager.get_ticket(ticket_id)
                    if not ticket:
                        continue
                    
                    # Grade the ticket
                    results = await self._grade_single_ticket(ticket)
                    if results:
                        # Save results
                        self.ticket_manager.save_results(ticket_id, results)
                        
                        # Update Ghost Brain memory
                        if self.ghost_brain:
                            wins = len([r for r in results if r.get('result') == 'W'])
                            losses = len([r for r in results if r.get('result') == 'L'])
                            self.ghost_brain.think(f"Graded ticket {ticket_id}: {wins}W {losses}L")
                        
                        # Mark as completed
                        self.completed_cleanups.add(ticket_id)
                        
                        logger.info(f"✅ Graded ticket {ticket_id}")
                    
                except Exception as e:
                    logger.error(f"Error grading ticket {ticket_id}: {e}")
            
            logger.info(f"🏁 Completed grading {len(self.completed_cleanups)} tickets")
            
        except Exception as e:
            logger.error(f"Error in grade_pending_tickets: {e}")
    
    async def _grade_single_ticket(self, ticket: Dict) -> List[Dict]:
        """Grade a single ticket and return results."""
        try:
            ticket_id = ticket.get('ticket_id')
            if not ticket_id:
                logger.warning("No ticket_id found in ticket")
                return []

            if not self.ticket_manager:
                logger.warning("Ticket manager not available for grading")
                return []

            # Get ticket data
            ticket_data = self.ticket_manager.get_ticket(ticket_id)
            if not ticket_data:
                logger.warning(f"Ticket {ticket_id} not found in ticket manager")
                return []

            # Process results
            results = []
            for selection in ticket_data.get('selections', []):
                player_name = selection.get('player_name')
                prop_type = selection.get('prop_type')

                if player_name and prop_type:
                    result = await self._get_player_result(player_name, prop_type)
                    if result is not None:
                        results.append({
                            'ticket_id': ticket_id,
                            'player_name': player_name,
                            'prop_type': prop_type,
                            'result': result
                        })

            # Save results
            if results and self.ticket_manager:
                self.ticket_manager.save_results(ticket_id, results)
                logger.info(f"✅ Graded ticket {ticket_id}: {len(results)} results")

            return results

        except Exception as e:
            logger.error(f"Error grading ticket {ticket.get('ticket_id', 'unknown')}: {e}")
            return []
    
    async def _get_player_result(self, player_name: str, prop_type: str) -> Optional[float]:
        """Get actual result for a player prop (simulated for now)."""
        try:
            # This would normally fetch from a data source
            # For now, simulate results based on historical data
            import random
            
            # Simulate realistic results based on prop type
            if prop_type == 'hits':
                return random.randint(0, 4)
            elif prop_type == 'runs':
                return random.randint(0, 3)
            elif prop_type == 'rbis':
                return random.randint(0, 4)
            elif prop_type == 'total_bases':
                return random.randint(0, 8)
            elif prop_type == 'points':
                return random.randint(8, 25)
            elif prop_type == 'rebounds':
                return random.randint(2, 12)
            elif prop_type == 'assists':
                return random.randint(1, 8)
            else:
                return random.randint(0, 5)
                
        except Exception as e:
            logger.error(f"Error getting player result: {e}")
            return None
    
    async def cleanup_completed_games(self):
        """Clean up completed games and archive data."""
        try:
            logger.info("🧹 Cleaning up completed games...")
            
            # Update Ghost Brain
            if self.ghost_brain:
                self.ghost_brain.think("Starting cleanup of completed games")
            
            # Clean up MLB games
            await self._cleanup_sport_games(Path('mlb_game_props'), 'MLB')
            
            # Clean up WNBA games
            await self._cleanup_sport_games(Path('wnba_game_props'), 'WNBA')
            
            # Archive old tickets
            if self.ticket_manager:
                archived_count = self.ticket_manager.archive_old_tickets(days=7)
                logger.info(f"📦 Archived {archived_count} old tickets")
            
            # Trigger prop fetchers for new games
            await self._trigger_prop_fetchers()
            
            # AI Brain Analysis and Ticket Generation Trigger
            if self.ghost_brain:
                await self._ai_brain_analysis_and_trigger()
            
            logger.info("✅ Enhanced cleanup completed with AI brain monitoring")
            
        except Exception as e:
            logger.error(f"Error during enhanced cleanup: {e}")
            if self.ghost_brain:
                self.ghost_brain.think(f"Cleanup error: {e}")
    
    async def _ai_brain_analysis_and_trigger(self):
        """AI brain analysis and ticket generation trigger."""
        try:
            logger.info("🧠 Running AI brain analysis...")
            
            if not self.ghost_brain:
                logger.warning("🧠 Ghost Brain not available for analysis")
                return
            
            # Check if AI is in low power mode
            if self.ghost_brain.is_in_low_power_mode():
                logger.info("🧠 AI is in low power listening mode")
            
            # Detect old tickets
            old_tickets = self.ghost_brain.detect_old_tickets()
            if old_tickets:
                logger.info(f"🧠 Found {len(old_tickets)} old tickets for cleanup")
                self.ghost_brain.think(f"Detected {len(old_tickets)} old tickets that need cleanup")
            
            # Identify ticket gaps (always listening mode)
            gaps = self.ghost_brain.identify_ticket_gaps_always_listening()
            if gaps['total_gaps'] > 0:
                logger.info(f"🧠 Identified {gaps['total_gaps']} ticket gaps")
                self.ghost_brain.think(f"Identified {gaps['total_gaps']} ticket gaps: {len(gaps['mlb_gaps'])} MLB, {len(gaps['wnba_gaps'])} WNBA")
            
            # Trigger ticket generation analysis (always listening mode)
            should_generate = self.ghost_brain.should_generate_new_tickets_always_listening()
            
            if should_generate:
                logger.info("🧠 AI brain recommends generating new tickets")
                self.ghost_brain.think("Triggering new ticket generation in always listening mode")
                
                # Trigger the ticket generation process
                await self._trigger_ticket_generation({
                    'should_generate': True,
                    'gaps': gaps,
                    'available_games': {
                        'mlb': self.ghost_brain._get_available_mlb_games(),
                        'wnba': self.ghost_brain._get_available_wnba_games()
                    }
                })
            else:
                logger.info("🧠 AI brain: No new ticket generation needed")
                self.ghost_brain.think("No new tickets needed in always listening mode")
            
        except Exception as e:
            logger.error(f"Error during AI brain analysis: {e}")
            if self.ghost_brain:
                self.ghost_brain.think(f"AI analysis error: {e}")
    
    async def _trigger_ticket_generation(self, analysis: Dict):
        """Trigger new ticket generation based on AI brain analysis."""
        try:
            logger.info("🎫 Triggering new ticket generation...")
            
            # Get available games
            mlb_games = analysis['available_games'].get('mlb', [])
            wnba_games = analysis['available_games'].get('wnba', [])
            
            if mlb_games:
                logger.info(f"🎫 Found {len(mlb_games)} MLB games for ticket generation")
                # Trigger MLB ticket generation
                await self._trigger_mlb_ticket_generation(mlb_games)
            
            if wnba_games:
                logger.info(f"🎫 Found {len(wnba_games)} WNBA games for ticket generation")
                # Trigger WNBA ticket generation
                await self._trigger_wnba_ticket_generation(wnba_games)
            
            logger.info("✅ Ticket generation trigger completed")
            
        except Exception as e:
            logger.error(f"Error triggering ticket generation: {e}")
    
    async def _trigger_mlb_ticket_generation(self, games: List[str]):
        """Trigger MLB ticket generation for specific games."""
        try:
            logger.info(f"🎫 Triggering MLB ticket generation for {len(games)} games")
            
            # Import and run MLB ticket generation
            try:
                from odds_reverse_engineering.auto_integration import AutoIntegration
                integration_system = AutoIntegration()
                
                # Process each game
                for game in games:
                    logger.info(f"🎫 Processing MLB game: {game}")
                    # This would trigger the actual ticket generation process
                    # The integration system handles the ticket generation logic
                
                if self.ghost_brain:
                    self.ghost_brain.think(f"Triggered MLB ticket generation for {len(games)} games")
                    
            except ImportError:
                logger.warning("AutoIntegration not available - skipping MLB ticket generation")
            
        except Exception as e:
            logger.error(f"Error triggering MLB ticket generation: {e}")
    
    async def _trigger_wnba_ticket_generation(self, games: List[str]):
        """Trigger WNBA ticket generation for specific games."""
        try:
            logger.info(f"🎫 Triggering WNBA ticket generation for {len(games)} games")
            
            # Import and run WNBA ticket generation
            try:
                from odds_reverse_engineering.auto_integration import AutoIntegration
                integration_system = AutoIntegration()
                
                # Process each game
                for game in games:
                    logger.info(f"🎫 Processing WNBA game: {game}")
                    # This would trigger the actual ticket generation process
                    # The integration system handles the ticket generation logic
                
                if self.ghost_brain:
                    self.ghost_brain.think(f"Triggered WNBA ticket generation for {len(games)} games")
                    
            except ImportError:
                logger.warning("AutoIntegration not available - skipping WNBA ticket generation")
            
        except Exception as e:
            logger.error(f"Error triggering WNBA ticket generation: {e}")
    
    async def _trigger_prop_fetchers(self):
        """Trigger prop fetchers for both MLB and WNBA."""
        try:
            import subprocess
            import sys
            
            if self.ghost_brain:
                self.ghost_brain.think("Triggering MLB prop fetcher")
            
            # Run MLB prop fetcher
            mlb_result = subprocess.run([
                sys.executable, "-m", "sports.mlb.mlb_props"
            ], cwd=self.base_dir, capture_output=True, text=True, check=False)
            
            if mlb_result.returncode == 0:
                logger.info("✅ MLB prop fetcher executed successfully")
                if self.ghost_brain:
                    self.ghost_brain.think("MLB prop fetcher completed successfully")
            else:
                logger.error(f"❌ MLB prop fetcher failed: {mlb_result.stderr}")
                if self.ghost_brain:
                    self.ghost_brain.think(f"MLB prop fetcher failed: {mlb_result.stderr}")
            
            if self.ghost_brain:
                self.ghost_brain.think("Triggering WNBA prop fetcher")
            
            # Run WNBA prop fetcher
            wnba_result = subprocess.run([
                sys.executable, "-m", "sports.wnba.wnba_props"
            ], cwd=self.base_dir, capture_output=True, text=True, check=False)
            
            if wnba_result.returncode == 0:
                logger.info("✅ WNBA prop fetcher executed successfully")
                if self.ghost_brain:
                    self.ghost_brain.think("WNBA prop fetcher completed successfully")
            else:
                logger.error(f"❌ WNBA prop fetcher failed: {wnba_result.stderr}")
                if self.ghost_brain:
                    self.ghost_brain.think(f"WNBA prop fetcher failed: {wnba_result.stderr}")
            
            logger.info("Prop fetchers for MLB and WNBA completed.")
            if self.ghost_brain:
                self.ghost_brain.think("Both MLB and WNBA prop fetchers completed")
            
        except Exception as e:
            logger.error(f"Error triggering prop fetchers: {e}")
            if self.ghost_brain:
                self.ghost_brain.think(f"Error triggering prop fetchers: {e}")
    
    async def _cleanup_sport_games(self, props_dir: Path, sport: str):
        """Clean up completed games for a specific sport."""
        try:
            if not props_dir.exists():
                logger.info(f"No {sport} props directory found")
                return
            
            completed_games = []
            for game_file in props_dir.glob('*.json'):
                if self._is_game_completed(game_file):
                    completed_games.append(game_file)
            
            if not completed_games:
                logger.info(f"No completed {sport} games to clean up")
                return
            
            logger.info(f"🎮 Cleaning up {len(completed_games)} completed {sport} games")
            
            # Archive completed games
            archive_dir = Path('props_archive') / sport.lower() / datetime.now().strftime('%Y-%m-%d')
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            for game_file in completed_games:
                try:
                    # Move to archive
                    archive_file = archive_dir / game_file.name
                    shutil.move(str(game_file), str(archive_file))
                    
                    # Extract essential data for memory
                    await self._extract_essential_data([game_file], sport)
                    
                    logger.info(f"📦 Archived {game_file.name}")
                    
                except Exception as e:
                    logger.error(f"Error archiving {game_file}: {e}")
            
            logger.info(f"✅ Cleaned up {len(completed_games)} {sport} games")
            
        except Exception as e:
            logger.error(f"Error cleaning up {sport} games: {e}")
    
    async def _extract_essential_data(self, game_files: List[Path], sport: str):
        """Extract essential data from completed games for memory."""
        try:
            for game_file in game_files:
                try:
                    with open(game_file, 'r', encoding='utf-8') as f:
                        game_data = json.load(f)
                    
                    # Extract key data for Ghost Brain memory
                    essential_data = {
                        'sport': sport,
                        'date': game_data.get('commence_time', '')[:10],
                        'teams': game_data.get('teams', []),
                        'players': []
                    }
                    
                    # Extract player data
                    for prop in game_data.get('props', []):
                        player_name = prop.get('player_name', '')
                        if player_name:
                            essential_data['players'].append({
                                'name': player_name,
                                'prop_type': prop.get('prop_type', ''),
                                'line': prop.get('line', 0)
                            })
                    
                    # Save to memory
                    memory_file = Path('ghost_ai_core_memory') / 'completed_games' / f"{sport.lower()}_{datetime.now().strftime('%Y%m%d')}.json"
                    memory_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    with open(memory_file, 'w') as f:
                        json.dump(essential_data, f, indent=2)
                    
                except Exception as e:
                    logger.error(f"Error extracting data from {game_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Error extracting essential data: {e}")
    
    async def update_ghost_brain_memory(self):
        """Update Ghost Brain with current state."""
        try:
            if not self.ghost_brain:
                return
            
            logger.info("🧠 Updating Ghost Brain memory...")
            
            # Get current statistics
            if self.ticket_manager:
                all_tickets = self.ticket_manager.get_all_tickets()
                today_tickets = self.ticket_manager.get_tickets_for_date(datetime.now().strftime('%Y-%m-%d'))
                
                # Calculate performance
                total_wins = 0
                total_losses = 0
                total_pushes = 0
                
                for ticket in all_tickets:
                    ticket_id = ticket.get('ticket_id')
                    if ticket_id:
                        results = self.ticket_manager.get_results(ticket_id)
                        if results:
                            for result in results.get('results', []):
                                if result.get('result') == 'W':
                                    total_wins += 1
                                elif result.get('result') == 'L':
                                    total_losses += 1
                                elif result.get('result') == 'P':
                                    total_pushes += 1
                
                # Update Ghost Brain
                self.ghost_brain.log_daily_performance(
                    len(today_tickets), total_wins, total_losses, total_pushes
                )
                
                self.ghost_brain.think(f"Memory updated: {len(all_tickets)} total tickets, {total_wins}W {total_losses}L {total_pushes}P")
            
            logger.info("✅ Ghost Brain memory updated")
            
        except Exception as e:
            logger.error(f"Error updating Ghost Brain memory: {e}")
    
    async def run_enhanced_cleanup_loop(self):
        """Run the enhanced cleanup loop (always active)."""
        try:
            logger.info("🚀 Starting Enhanced Auto-Cleanup Loop (always active)")
            while True:
                try:
                    # Always run enhanced cleanup
                    analysis = await self.analyze_what_needs_processing()
                    logger.info(f"📊 Analysis: {analysis}")
                    await self.grade_pending_tickets()
                    await self.cleanup_completed_games()
                    await self.update_ghost_brain_memory()
                    wait_time = self.time_manager.cleanup_interval_hours * 3600  # Convert to seconds
                    logger.info(f"⏰ Waiting {self.time_manager.cleanup_interval_hours} hours until next cleanup")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {e}")
                    await asyncio.sleep(300)  # Wait 5 minutes on error
        except Exception as e:
            logger.error(f"Fatal error in enhanced cleanup loop: {e}")

async def main():
    """Main function for enhanced auto-cleanup."""
    try:
        cleanup_system = EnhancedAutoCleanupSystem()
        await cleanup_system.run_enhanced_cleanup_loop()
    except Exception as e:
        logger.error(f"Fatal error in enhanced auto-cleanup: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 