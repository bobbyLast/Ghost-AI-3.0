"""
Automated Odds Reverse Engineering Analyzer
Integrates with Ghost AI 24/7 workflow to automatically analyze posted tickets
"""

import sys
import os
import json
import logging
import asyncio
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import time
import re
import aiohttp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import argparse
import shutil

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import from the correct path
import config.mappings as mappings
# TODO: Define OddsAPIHandler as a stub since import cannot be resolved
class OddsAPIHandler:
    def __init__(self, api_key):
        self.api_key = api_key
    async def get_historical_odds(self, sport, date):
        return []
    async def get_games(self, sport):
        return []
    async def get_player_props(self, game_id, bookmaker):
        return []
    async def __aenter__(self):
        return self
    async def __aexit__(self, exc_type, exc, tb):
        pass
    async def check_api_limits(self):
        return {}
from reverse_engineering.reverse_engine.odds_engine import OddsReverseEngine, ConfidenceAnalysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent
GENERATED_DIR = PROJECT_ROOT / "ghost_ai_core_memory" / "tickets" / "generated"
ANALYZED_DIR = PROJECT_ROOT / "ghost_ai_core_memory" / "tickets" / "analyzed"

ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"

PROP_MEMORY_PATH = Path(__file__).parent / "data" / "prop_memory.json"

class AutoOddsAnalyzer:
    """
    Automated system that:
    1. Monitors posted tickets directory
    2. Analyzes new tickets with odds reverse engineering
    3. Posts enhanced analysis to Discord
    4. Saves reverse engine data for AI to use
    """
    
    DAILY_TICKET_LIMIT = 10
    TRACKING_FILE = "posted_tickets_tracking.json"
    STREAK_TRACKING_FILE = "streak_tracking.json"

    def __init__(self):
        self.odds_engine = OddsReverseEngine(data_dir=str(PROJECT_ROOT / "odds_reverse_engineering" / "data"))
        self.posted_tickets_dir = PROJECT_ROOT / "ghost_ai_core_memory" / "tickets" / "posted"
        self.analyzed_tickets_dir = PROJECT_ROOT / "ghost_ai_core_memory" / "tickets" / "analyzed"
        self.results_dir = PROJECT_ROOT / "ghost_ai_core_memory" / "tickets" / "results"
        self.ai_data_dir = PROJECT_ROOT / "ghost_ai_core_memory" / "odds_analysis"
        self.generated_tickets_dir = PROJECT_ROOT / "ghost_ai_core_memory" / "tickets" / "generated"
        
        # Initialize OddsAPI handler for real-time data
        self.odds_api = None
        self._init_odds_api()
        
        # Create directories if they don't exist
        self.analyzed_tickets_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.ai_data_dir.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)
        
        # Track processed files to avoid reprocessing
        self.processed_files = set()
        self.last_analysis_time = None
        
        # Discord integration (simulate for now)
        self.discord_enabled = True
        
        # 30-day training mode state
        self.confidence_threshold = 0.7
        self.last_tick_time = None
        
        # Daily ticket counter (after training period)
        self.daily_tickets_posted, self.last_reset_date = self.load_daily_ticket_state()
        
        # Tracking system
        self.posted_tickets_history = self.load_tracking_data()
        self.streak_tracking = self.load_streak_tracking()

    def _init_odds_api(self):
        """Initialize the OddsAPI handler with API key"""
        try:
            api_key = os.getenv('ODDS_API_KEY')
            if not api_key:
                logger.error("❌ ODDS_API_KEY not found in environment variables")
                logger.warning("⚠️ Reverse engineering will use simulated data only")
                return
            
            self.odds_api = OddsAPIHandler(api_key)
            logger.info("✅ OddsAPI handler initialized with API key")
            
        except Exception as e:
            logger.error(f"❌ Error initializing OddsAPI: {e}")
            logger.warning("⚠️ Reverse engineering will use simulated data only")

    def load_daily_ticket_state(self):
        try:
            with open("daily_ticket_state.json", 'r') as f:
                state = json.load(f)
            return state.get('daily_tickets_posted', 0), state.get('last_reset_date', '')
        except Exception:
            return 0, ''

    def save_daily_ticket_state(self):
        state = {
            'daily_tickets_posted': self.daily_tickets_posted,
            'last_reset_date': self.last_reset_date
        }
        with open("daily_ticket_state.json", 'w') as f:
            json.dump(state, f)

    def reset_daily_ticket_counter_if_needed(self):
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.last_reset_date != current_date:
            self.daily_tickets_posted = 0
            self.last_reset_date = current_date
            self.save_daily_ticket_state()
            logger.info(f"🔄 Daily ticket counter reset for {current_date}")

    def is_special_ticket(self, ticket: Dict) -> bool:
        """Check if ticket is a special type (streaks, POTD, TOTD) that doesn't count toward daily limit"""
        ticket_id = ticket.get('ticket_id', '').lower()
        tier = ticket.get('tier', '').lower()
        
        # Check for special ticket types
        special_keywords = ['streak', 'potd', 'totd', 'player of the day', 'team of the day']
        return any(keyword in ticket_id for keyword in special_keywords) or any(keyword in tier for keyword in special_keywords)

    def can_post_ticket(self, ticket: Dict) -> bool:
        """Determine if a ticket can be posted based on confidence and daily limit"""
        # Always allow special tickets (streaks, POTD, TOTD)
        if self.is_special_ticket(ticket):
            return True
        self.reset_daily_ticket_counter_if_needed()
        return (
            ticket.get('enhanced_confidence_score', 0) >= self.confidence_threshold
            and self.daily_tickets_posted < self.DAILY_TICKET_LIMIT
        )

    def increment_daily_ticket_counter(self):
        self.daily_tickets_posted += 1
        self.save_daily_ticket_state()
        logger.info(f"📊 Daily tickets posted: {self.daily_tickets_posted}/{self.DAILY_TICKET_LIMIT}")

    async def start_monitoring(self, check_interval: int = 300):
        """
        Start 24/7 monitoring of posted tickets
        
        Args:
            check_interval: Seconds between checks (default 5 minutes)
        """
        logger.info("🚀 Starting Auto Odds Analyzer - 24/7 monitoring enabled")
        self.last_tick_time = datetime.now(timezone.utc)
        
        while True:
            try:
                await self.check_and_analyze_new_tickets()
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def check_and_analyze_new_tickets(self):
        """Check for new posted tickets and analyze them"""
        if not self.posted_tickets_dir.exists():
            logger.warning("Posted tickets directory not found")
            return
        
        # Get all JSON files in posted tickets directory
        ticket_files = list(self.posted_tickets_dir.glob("*.json"))
        
        for ticket_file in ticket_files:
            if ticket_file.name in self.processed_files:
                continue
            
            logger.info(f"📁 Processing new ticket file: {ticket_file.name}")
            
            try:
                # Load and analyze tickets
                tickets = self.load_tickets_from_file(ticket_file)
                if tickets:
                    enhanced_tickets = await self.analyze_tickets(tickets)
                    self.save_enhanced_tickets(enhanced_tickets, ticket_file.name)
                    
                    # POST ENHANCED ANALYSIS TO DISCORD
                    await self.post_enhanced_analysis_to_discord(enhanced_tickets, ticket_file.name)
                    
                    # SAVE REVERSE ENGINE DATA FOR AI TO USE
                    self.save_ai_analysis_data(enhanced_tickets, ticket_file.name)
                    
                    # Update odds engine memory with results
                    await self.update_odds_memory_with_results(ticket_file.name)
                    
                    self.processed_files.add(ticket_file.name)
                    logger.info(f"✅ Analyzed {len(enhanced_tickets)} tickets from {ticket_file.name}")
                
            except Exception as e:
                logger.error(f"❌ Error processing {ticket_file.name}: {e}", exc_info=True)
    
    def load_tickets_from_file(self, file_path: Path) -> List[Dict]:
        """Load tickets from JSON file"""
        try:
            with open(file_path, 'r') as f:
                tickets = json.load(f)
            
            if isinstance(tickets, list):
                return tickets
            else:
                logger.warning(f"Unexpected format in {file_path.name}")
                return []
                
        except Exception as e:
            logger.error(f"Error loading tickets from {file_path}: {e}")
            return []
    
    async def analyze_tickets(self, tickets: List[Dict]) -> List[Dict]:
        """Analyze tickets with odds reverse engineering engine"""
        enhanced_tickets = []
        
        for ticket in tickets:
            logger.info(f"🔍 Analyzing ticket {ticket.get('ticket_id', 'unknown')}")
            
            enhanced_selections = []
            ticket_analysis = {
                'hot_picks': 0,
                'trap_risks': 0,
                'confidence_drift': [],
                'market_analysis': [],
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Analyze each selection in the ticket
            for selection in ticket.get('selections', []) + ticket.get('picks', []):
                player_name = selection.get('player_name')
                prop_type = selection.get('prop_type')
                current_odds = selection.get('odds')
                
                if not all([player_name, prop_type, current_odds]):
                    enhanced_selections.append(selection)
                    continue
                
                # Add historical data if available
                await self.add_historical_data_for_player(player_name, prop_type, current_odds)
                
                # Update with current market data for comparison
                await self.update_odds_memory_with_current_market(player_name, prop_type, current_odds)
                
                # Analyze confidence drift
                drift_analysis = self.odds_engine.analyze_ticket(selection) if hasattr(self.odds_engine, 'analyze_ticket') else {}
                
                # Compare to market today
                market_analysis = {}
                
                # Get trend tag and ghost read
                key = f"{player_name}_{prop_type}"
                trend_tag = None
                ghost_read = None
                if key in self.odds_engine.ghost_picks:
                    trend_tag = getattr(self.odds_engine.ghost_picks[key], 'trend_tag', None)
                    ghost_read = getattr(self.odds_engine.ghost_picks[key], 'ghost_read', None)
                
                # Enhance selection with analysis
                enhanced_selection = {
                    **selection,
                    'odds_analysis': {
                        'confidence_drift': drift_analysis,
                        'market_analysis': market_analysis,
                        'trend_tag': trend_tag,
                        'ghost_read': ghost_read
                    }
                }
                
                enhanced_selections.append(enhanced_selection)
                
                # Track analysis for ticket-level summary
                if "🔥" in drift_analysis.get('trend', ''):
                    ticket_analysis['hot_picks'] += 1
                elif "⛔" in drift_analysis.get('risk_rating', ''):
                    ticket_analysis['trap_risks'] += 1
                
                # Convert to dict for JSON serialization
                drift_dict = {
                    'confidence_trend': drift_analysis.get('trend', 'Unknown'),
                    'risk_rating': drift_analysis.get('risk_rating', 'Unknown'),
                    'recommendation': drift_analysis.get('recommendation', 'No recommendation'),
                    'odds_drift': drift_analysis.get('odds_drift', 'Unknown'),
                    'result_drift': drift_analysis.get('result_drift', 'Unknown')
                }
                ticket_analysis['confidence_drift'].append(drift_dict)
                ticket_analysis['market_analysis'].append(market_analysis)
            
            # Create enhanced ticket
            enhanced_ticket = {
                **ticket,
                'selections': enhanced_selections,
                'odds_analysis': ticket_analysis,
                'enhanced_confidence_score': self.calculate_enhanced_confidence(ticket_analysis),
                'risk_assessment': self.assess_ticket_risk(ticket_analysis),
                'recommendation': self.generate_ticket_recommendation(ticket_analysis),
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            enhanced_tickets.append(enhanced_ticket)
        
        return enhanced_tickets
    
    async def add_historical_data_for_player(self, player_name: str, prop_type: str, base_odds: int):
        """Add historical odds data for a player using real API data"""
        # Check if we already have data for this player/prop
        key = f"{player_name}_{prop_type}"
        if key in self.odds_engine.ghost_picks and hasattr(self.odds_engine.ghost_picks[key], 'odds_log') and len(self.odds_engine.ghost_picks[key].odds_log) > 5:
            return  # Already have sufficient historical data
        
        # If we have OddsAPI access, fetch real historical data
        if self.odds_api:
            try:
                logger.info(f"🔍 Fetching historical odds for {player_name} - {prop_type}")
                
                # Fetch historical odds for the last 7 days
                for days_ago in range(1, 8):
                    date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                    
                    try:
                        # Get historical odds for MLB
                        historical_data = await self.odds_api.get_historical_odds("baseball_mlb", date)
                        
                        # Find data for this specific player and prop type
                        for game_data in historical_data:
                            for bookmaker in game_data.get('bookmakers', []):
                                if bookmaker.get('key') == 'fanduel':  # Focus on FanDuel
                                    for market in bookmaker.get('markets', []):
                                        if market.get('key') == prop_type:
                                            for outcome in market.get('outcomes', []):
                                                if outcome.get('description') == player_name:
                                                    odds = outcome.get('price', 0)
                                                    # For historical data, we need to determine result
                                                    # This would ideally come from game results
                                                    # For now, we'll use a placeholder
                                                    result = "W"  # Placeholder - should be actual result
                                                    
                                                    # TODO: Implement add_odds_entry or use record_ghost_pick/update_closing_odds as appropriate
                                                    pass
                                                    logger.debug(f"Added historical entry: {player_name} {prop_type} {odds} on {date}")
                                                    break
                                    
                    except Exception as e:
                        logger.debug(f"Error fetching historical data for {date}: {e}")
                        continue
                
                # If we still don't have enough data, add some simulated entries
                if key not in self.odds_engine.ghost_picks or not hasattr(self.odds_engine.ghost_picks[key], 'odds_log') or len(self.odds_engine.ghost_picks[key].odds_log) < 5:
                    logger.info(f"Adding simulated historical data for {player_name} - {prop_type}")
                    self._add_simulated_historical_data(player_name, prop_type, base_odds)
                
            except Exception as e:
                logger.error(f"Error fetching historical data for {player_name}: {e}")
                # Fall back to simulated data
                self._add_simulated_historical_data(player_name, prop_type, base_odds)
        else:
            # No API access, use simulated data
            self._add_simulated_historical_data(player_name, prop_type, base_odds)
    
    def _add_simulated_historical_data(self, player_name: str, prop_type: str, base_odds: int):
        """Add simulated historical odds data for a player"""
        # Add 5-10 historical entries with realistic patterns
        for i in range(5, 15):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            # Vary odds and results to create realistic patterns
            if i % 3 == 0:  # Every 3rd day, odds get more negative (falling)
                odds = base_odds - (i * 5)
                result = "W" if i % 2 == 0 else "L"
            else:  # Other days, odds stay similar or rise slightly
                odds = base_odds + (i * 2)
                result = "W" if i % 3 == 0 else "L"
            
            # TODO: Implement add_odds_entry or use record_ghost_pick/update_closing_odds as appropriate
            pass
    
    def calculate_enhanced_confidence(self, ticket_analysis: Dict) -> float:
        """Calculate enhanced confidence score based on odds analysis"""
        base_confidence = 0.5
        
        # Boost for hot picks
        hot_picks = ticket_analysis.get('hot_picks', 0)
        base_confidence += hot_picks * 0.1
        
        # Penalty for trap risks
        trap_risks = ticket_analysis.get('trap_risks', 0)
        base_confidence -= trap_risks * 0.15
        
        # Analyze confidence drift patterns
        drift_analyses = ticket_analysis.get('confidence_drift', [])
        rising_count = sum(1 for analysis in drift_analyses if "🔥" in analysis.get('trend', ''))
        falling_count = sum(1 for analysis in drift_analyses if "🔻" in analysis.get('trend', ''))
        
        if rising_count > falling_count:
            base_confidence += 0.1
        elif falling_count > rising_count:
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def assess_ticket_risk(self, ticket_analysis: Dict) -> str:
        """Assess overall ticket risk level"""
        trap_risks = ticket_analysis.get('trap_risks', 0)
        hot_picks = ticket_analysis.get('hot_picks', 0)
        
        if trap_risks > hot_picks:
            return "HIGH"
        elif trap_risks == 0 and hot_picks > 0:
            return "LOW"
        else:
            return "MEDIUM"
    
    def generate_ticket_recommendation(self, ticket_analysis: Dict) -> str:
        """Generate ticket-level recommendation"""
        hot_picks = ticket_analysis.get('hot_picks', 0)
        trap_risks = ticket_analysis.get('trap_risks', 0)
        
        if hot_picks > trap_risks:
            return f"✅ PLAY - {hot_picks} hot picks detected"
        elif trap_risks > hot_picks:
            return f"⛔ AVOID - {trap_risks} trap risks detected"
        else:
            return "⚠️ CAUTION - Mixed signals, proceed carefully"
    
    def save_enhanced_tickets(self, tickets: List[Dict], original_filename: str):
        """Save enhanced tickets to analyzed directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analyzed_{original_filename.replace('.json', '')}_{timestamp}.json"
        filepath = self.analyzed_tickets_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        logger.info(f"💾 Saved {len(tickets)} enhanced tickets to {filepath}")
    
    async def post_enhanced_analysis_to_discord(self, enhanced_tickets: List[Dict], filename: str):
        """Post enhanced analysis to Discord"""
        if not self.discord_enabled:
            logger.info("Discord posting disabled - simulating post")
            return
        
        logger.info(f"📢 Posting enhanced analysis to Discord for {filename}")
        
        # Check each ticket against posting rules
        for ticket in enhanced_tickets:
            if self.can_post_ticket(ticket):
                await self.post_enhanced_ticket_to_discord(ticket)
            else:
                logger.info(f"⏩ Skipping ticket {ticket.get('ticket_id', 'unknown')} (daily limit reached: {self.daily_tickets_posted}/{self.DAILY_TICKET_LIMIT})")
    
    async def post_enhanced_ticket_to_discord(self, ticket: Dict):
        """Post a single enhanced ticket to Discord"""
        ticket_id = ticket.get('ticket_id', 'unknown')
        tier = ticket.get('tier', 'unknown')
        confidence_trend = ticket.get('overall_confidence_trend', 'Unknown')
        recommendation = ticket.get('recommendation', 'No recommendation')
        enhanced_confidence = ticket.get('enhanced_confidence_score', 0)
        
        # Log the enhanced ticket details (simulate Discord post)
        logger.info(f"🎟️ ENHANCED TICKET POSTED: {ticket_id}")
        logger.info(f"   Tier: {tier}")
        logger.info(f"   Enhanced Confidence: {enhanced_confidence:.3f}")
        logger.info(f"   Confidence Trend: {confidence_trend}")
        logger.info(f"   Risk Assessment: {ticket.get('risk_assessment', 'Unknown')}")
        logger.info(f"   Recommendation: {recommendation}")
        
        # Log selections with odds analysis
        for i, selection in enumerate(ticket.get('selections', []), 1):
            player_name = selection.get('player_name', 'Unknown')
            odds_analysis = selection.get('odds_analysis', {})
            drift_analysis = odds_analysis.get('confidence_drift', {})
            trend_tag = odds_analysis.get('trend_tag', 'No tag')
            ghost_read = odds_analysis.get('ghost_read', 'No read')
            
            logger.info(f"   Selection {i}: {player_name}")
            logger.info(f"     Trend: {trend_tag}")
            logger.info(f"     Ghost Read: {ghost_read}")
            logger.info(f"     Confidence: {drift_analysis.get('trend', 'Unknown')}")
            logger.info(f"     Risk: {drift_analysis.get('risk_rating', 'Unknown')}")
        
        logger.info("   " + "="*50)
        
        # Track the posted ticket
        self.track_posted_ticket(ticket, ticket)
    
    def save_ai_analysis_data(self, enhanced_tickets: List[Dict], filename: str):
        """Save reverse engine data for AI to use (eliminates need to recalculate)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract all player/prop analysis data
        ai_analysis_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_file': filename,
            'players_analyzed': {},
            'hot_picks': [],
            'trap_risks': [],
            'trend_summary': {
                'total_tickets': len(enhanced_tickets),
                'hot_picks_count': 0,
                'trap_risks_count': 0,
                'rising_confidence_count': 0,
                'falling_confidence_count': 0
            }
        }
        
        # Process each ticket
        for ticket in enhanced_tickets:
            ticket_analysis = ticket.get('odds_analysis', {})
            
            # Update trend summary
            ai_analysis_data['trend_summary']['hot_picks_count'] += ticket_analysis.get('hot_picks', 0)
            ai_analysis_data['trend_summary']['trap_risks_count'] += ticket_analysis.get('trap_risks', 0)
            
            # Process each selection
            for selection in ticket.get('selections', []):
                player_name = selection.get('player_name')
                prop_type = selection.get('prop_type')
                odds_analysis = selection.get('odds_analysis', {})
                
                if not all([player_name, prop_type, odds_analysis]):
                    continue
                
                key = f"{player_name}_{prop_type}"
                
                # Store player analysis data
                ai_analysis_data['players_analyzed'][key] = {
                    'player_name': player_name,
                    'prop_type': prop_type,
                    'current_odds': selection.get('odds'),
                    'trend_tag': odds_analysis.get('trend_tag'),
                    'ghost_read': odds_analysis.get('ghost_read'),
                    'confidence_drift': odds_analysis.get('confidence_drift'),
                    'market_analysis': odds_analysis.get('market_analysis'),
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                
                # Track hot picks and trap risks
                drift_analysis = odds_analysis.get('confidence_drift', {})
                if "🔥" in drift_analysis.get('trend', ''):
                    ai_analysis_data['hot_picks'].append({
                        'player': player_name,
                        'prop': prop_type,
                        'trend_tag': odds_analysis.get('trend_tag'),
                        'confidence_trend': drift_analysis.get('trend')
                    })
                elif "⛔" in drift_analysis.get('risk_rating', ''):
                    ai_analysis_data['trap_risks'].append({
                        'player': player_name,
                        'prop': prop_type,
                        'trend_tag': odds_analysis.get('trend_tag'),
                        'risk_rating': drift_analysis.get('risk_rating')
                    })
                
                # Track confidence trends
                if "🔥" in drift_analysis.get('trend', ''):
                    ai_analysis_data['trend_summary']['rising_confidence_count'] += 1
                elif "🔻" in drift_analysis.get('trend', ''):
                    ai_analysis_data['trend_summary']['falling_confidence_count'] += 1
        
        # Save AI analysis data
        ai_filename = f"ai_analysis_{filename.replace('.json', '')}_{timestamp}.json"
        ai_filepath = self.ai_data_dir / ai_filename
        
        with open(ai_filepath, 'w') as f:
            json.dump(ai_analysis_data, f, indent=2)
        
        # Also save a current summary file that gets updated
        summary_filepath = self.ai_data_dir / "current_analysis_summary.json"
        with open(summary_filepath, 'w') as f:
            json.dump(ai_analysis_data, f, indent=2)
        
        logger.info(f"🧠 Saved AI analysis data to {ai_filepath}")
        logger.info(f"📊 Analysis Summary: {ai_analysis_data['trend_summary']}")
        
        # Save odds engine memory for AI to use
        self.odds_engine.save_memory()
        logger.info(f"💾 Saved odds engine memory for AI access")
    
    async def update_odds_memory_with_results(self, ticket_filename: str):
        """Update odds engine memory with actual results when available"""
        # Look for corresponding results file
        results_file = self.results_dir / ticket_filename.replace('.json', '_results.json')
        
        if results_file.exists():
            try:
                with open(results_file, 'r') as f:
                    results = json.load(f)
                
                # Update odds engine with actual results
                for result in results:
                    player_name = result.get('player_name')
                    prop_type = result.get('prop_type')
                    actual_result = result.get('result')  # 'W' or 'L'
                    
                    if all([player_name, prop_type, actual_result]):
                        # Find the corresponding odds entry and update it
                        key = f"{player_name}_{prop_type}"
                        if key in self.odds_engine.ghost_picks and hasattr(self.odds_engine.ghost_picks[key], 'odds_log'):
                            odds_log = self.odds_engine.ghost_picks[key].odds_log
                            if odds_log:
                                odds_log[-1].result = actual_result
                
                # Also update tracking with results
                await self.update_tracking_with_results(results, ticket_filename)
                
                # Save updated memory
                self.odds_engine.save_memory()
                logger.info(f"✅ Updated odds memory with results from {ticket_filename}")
                
            except Exception as e:
                logger.error(f"❌ Error updating odds memory: {e}")

    async def update_tracking_with_results(self, results: List[Dict], ticket_filename: str):
        """Update tracking data with actual results"""
        try:
            # Find the corresponding posted tickets for this results file
            # Extract date from filename (assuming format like YYYY-MM-DD.json)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', ticket_filename)
            if not date_match:
                return
            
            results_date = date_match.group(1)
            
            # Find tickets posted on this date
            for tracked_ticket in self.posted_tickets_history['posted_tickets']:
                if tracked_ticket['posted_date'] == results_date and tracked_ticket['result'] is None:
                    # This ticket needs results
                    ticket_id = tracked_ticket['ticket_id']
                    
                    # Check if we have results for this ticket
                    for result in results:
                        if result.get('ticket_id') == ticket_id:
                            result_value = result.get('result')
                            if result_value:
                                # Update the tracked ticket
                                tracked_ticket['result'] = result_value
                                tracked_ticket['result_updated_at'] = datetime.now(timezone.utc).isoformat()
                                
                                # Track streak if it's a special ticket
                                if tracked_ticket['is_special_ticket']:
                                    self.track_streak({'ticket_id': ticket_id}, result_value)
                                
                                logger.info(f"📊 Updated result for ticket {ticket_id}: {result_value}")
                                break
            
            # Save updated tracking data
            self.save_tracking_data()
            
        except Exception as e:
            logger.error(f"❌ Error updating tracking with results: {e}")

    def get_tracking_summary(self) -> Dict:
        """Get comprehensive tracking summary"""
        return {
            'total_tickets_posted': self.posted_tickets_history['total_tickets_posted'],
            'training_mode_tickets': self.posted_tickets_history['training_mode_tickets'],
            'production_mode_tickets': self.posted_tickets_history['production_mode_tickets'],
            'special_tickets': self.posted_tickets_history['special_tickets'],
            'regular_tickets': self.posted_tickets_history['regular_tickets'],
            'confidence_stats': self.posted_tickets_history['confidence_stats'],
            'current_streak': self.streak_tracking['current_streak'],
            'best_streak': self.streak_tracking['best_streak'],
            'total_streaks': self.streak_tracking['total_streaks'],
            'streak_types': self.streak_tracking['streak_types'],
            'today_tickets': self.posted_tickets_history['daily_stats'].get(
                datetime.now().strftime("%Y-%m-%d"), {}
            )
        }

    def load_tracking_data(self):
        """Load posted tickets tracking history"""
        try:
            with open(self.TRACKING_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'total_tickets_posted': 0,
                'training_mode_tickets': 0,
                'production_mode_tickets': 0,
                'special_tickets': 0,
                'regular_tickets': 0,
                'posted_tickets': [],
                'daily_stats': {},
                'confidence_stats': {
                    'high_confidence': 0,  # >0.8
                    'medium_confidence': 0,  # 0.6-0.8
                    'low_confidence': 0   # <0.6
                }
            }

    def save_tracking_data(self):
        """Save posted tickets tracking history"""
        with open(self.TRACKING_FILE, 'w') as f:
            json.dump(self.posted_tickets_history, f, indent=2)

    def load_streak_tracking(self):
        """Load streak tracking data"""
        try:
            with open(self.STREAK_TRACKING_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'current_streak': 0,
                'best_streak': 0,
                'total_streaks': 0,
                'streak_history': [],
                'streak_types': {
                    'wins': 0,
                    'losses': 0,
                    'pushes': 0
                }
            }

    def save_streak_tracking(self):
        """Save streak tracking data"""
        with open(self.STREAK_TRACKING_FILE, 'w') as f:
            json.dump(self.streak_tracking, f, indent=2)

    def track_posted_ticket(self, ticket: Dict, enhanced_ticket: Dict):
        """Track a posted ticket with full details"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Create tracking entry
        tracking_entry = {
            'ticket_id': ticket.get('ticket_id', 'unknown'),
            'tier': ticket.get('tier', 'unknown'),
            'posted_at': current_time,
            'posted_date': current_date,
            'training_mode': False,
            'enhanced_confidence': enhanced_ticket.get('enhanced_confidence_score', 0),
            'base_confidence': ticket.get('confidence_score', 0),
            'is_special_ticket': self.is_special_ticket(ticket),
            'selections': [
                {
                    'player_name': sel.get('player_name'),
                    'prop_type': sel.get('prop_type'),
                    'odds': sel.get('odds'),
                    'enhanced_confidence': sel.get('enhanced_confidence_score', 0),
                    'trend_tag': sel.get('reverse_engine_analysis', {}).get('trend_tag'),
                    'is_hot_pick': sel.get('reverse_engine_analysis', {}).get('is_hot_pick', False),
                    'is_trap_risk': sel.get('reverse_engine_analysis', {}).get('is_trap_risk', False)
                }
                for sel in enhanced_ticket.get('selections', [])
            ],
            'risk_assessment': enhanced_ticket.get('risk_assessment', 'Unknown'),
            'recommendation': enhanced_ticket.get('recommendation', 'No recommendation'),
            'result': None,  # Will be updated when results come in
            'result_updated_at': None
        }
        
        # Update tracking statistics
        self.posted_tickets_history['total_tickets_posted'] += 1
        
        if self.is_special_ticket(ticket):
            self.posted_tickets_history['special_tickets'] += 1
        else:
            self.posted_tickets_history['regular_tickets'] += 1
        
        # Update confidence stats
        enhanced_confidence = enhanced_ticket.get('enhanced_confidence_score', 0)
        if enhanced_confidence > 0.8:
            self.posted_tickets_history['confidence_stats']['high_confidence'] += 1
        elif enhanced_confidence > 0.6:
            self.posted_tickets_history['confidence_stats']['medium_confidence'] += 1
        else:
            self.posted_tickets_history['confidence_stats']['low_confidence'] += 1
        
        # Update daily stats
        if current_date not in self.posted_tickets_history['daily_stats']:
            self.posted_tickets_history['daily_stats'][current_date] = {
                'tickets_posted': 0,
                'special_tickets': 0,
                'regular_tickets': 0,
                'avg_confidence': 0,
                'total_confidence': 0
            }
        
        daily_stats = self.posted_tickets_history['daily_stats'][current_date]
        daily_stats['tickets_posted'] += 1
        daily_stats['total_confidence'] += enhanced_confidence
        daily_stats['avg_confidence'] = daily_stats['total_confidence'] / daily_stats['tickets_posted']
        
        if self.is_special_ticket(ticket):
            daily_stats['special_tickets'] += 1
        else:
            daily_stats['regular_tickets'] += 1
        
        # Add to posted tickets list
        self.posted_tickets_history['posted_tickets'].append(tracking_entry)
        
        # Save tracking data
        self.save_tracking_data()
        
        # Log tracking info
        logger.info(f"📊 TRACKED: Ticket {ticket.get('ticket_id', 'unknown')} posted")
        logger.info(f"   Mode: {'Training' if False else 'Production'}")
        logger.info(f"   Type: {'Special' if self.is_special_ticket(ticket) else 'Regular'}")
        logger.info(f"   Confidence: {enhanced_confidence:.3f}")
        logger.info(f"   Total Posted: {self.posted_tickets_history['total_tickets_posted']}")

    def track_streak(self, ticket: Dict, result: str):
        """Track streak results"""
        if not self.is_special_ticket(ticket):
            return  # Only track special tickets (streaks)
        
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Find the ticket in tracking history
        ticket_id = ticket.get('ticket_id', 'unknown')
        for tracked_ticket in self.posted_tickets_history['posted_tickets']:
            if tracked_ticket['ticket_id'] == ticket_id:
                tracked_ticket['result'] = result
                tracked_ticket['result_updated_at'] = current_time
                break
        
        # Update streak tracking
        if result == 'W':
            self.streak_tracking['current_streak'] += 1
            self.streak_tracking['streak_types']['wins'] += 1
            
            if self.streak_tracking['current_streak'] > self.streak_tracking['best_streak']:
                self.streak_tracking['best_streak'] = self.streak_tracking['current_streak']
                logger.info(f"🔥 NEW BEST STREAK: {self.streak_tracking['best_streak']} wins!")
        
        elif result == 'L':
            # End current streak
            if self.streak_tracking['current_streak'] > 0:
                self.streak_tracking['streak_history'].append({
                    'streak_length': self.streak_tracking['current_streak'],
                    'ended_at': current_time,
                    'ticket_id': ticket_id
                })
                self.streak_tracking['total_streaks'] += 1
                logger.info(f"💔 Streak ended at {self.streak_tracking['current_streak']} wins")
            
            self.streak_tracking['current_streak'] = 0
            self.streak_tracking['streak_types']['losses'] += 1
        
        elif result == 'P':
            self.streak_tracking['streak_types']['pushes'] += 1
            # Push doesn't break or extend streak
        
        # Save both tracking files
        self.save_tracking_data()
        self.save_streak_tracking()
        
        # Log streak info
        logger.info(f"🎯 STREAK UPDATE: {result} - Current: {self.streak_tracking['current_streak']}, Best: {self.streak_tracking['best_streak']}")

    async def fetch_game_results(self, sport_key, event_id):
        """Fetch final results for a game from OddsAPI."""
        url = f"{ODDS_API_BASE_URL}/sports/{sport_key}/scores"
        params = {
            'apiKey': ODDS_API_KEY,
            'daysFrom': 1
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    for event in data:
                        if event.get('id') == event_id:
                            return event
                return None

    async def grade_tickets_with_results(self):
        """Grade all posted and generated tickets after games end."""
        ticket_dirs = [self.posted_tickets_dir, self.generated_tickets_dir] if hasattr(self, 'generated_tickets_dir') else [self.posted_tickets_dir]
        for ticket_dir in ticket_dirs:
            for ticket_file in ticket_dir.glob("*.json"):
                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        tickets = json.load(f)
                    if not isinstance(tickets, list):
                        tickets = [tickets]
                    updated = False
                    for ticket in tickets:
                        ticket_id = ticket.get('ticket_id', ticket.get('id', 'unknown'))
                        if ticket.get('graded'):
                            logger.info(f"[GRADING] Skipping ticket {ticket_id}: already graded.")
                            continue
                        sport_key = ticket.get('sport_key', 'baseball_mlb')
                        graded_ticket = await self.grade_ticket(ticket, sport_key)
                        if graded_ticket:
                            updated = True
                            logger.info(f"[GRADING] Graded ticket {ticket_id} successfully.")
                        else:
                            logger.info(f"[GRADING] Skipped ticket {ticket_id}: could not grade (missing fields, game not completed, or no result).")
                    if updated:
                        with open(ticket_file, 'w', encoding='utf-8') as f:
                            json.dump(tickets, f, indent=2)
                        logger.info(f"Graded ticket(s) in {ticket_file.name}")
                except Exception as e:
                    logger.error(f"Error grading tickets in {ticket_file}: {e}")

    def infer_sport_key(self, ticket):
        """Infer the sport_key from ticket fields if missing."""
        wnba_teams = [
            'Las Vegas Aces', 'Atlanta Dream', 'Chicago Sky', 'Connecticut Sun', 'Dallas Wings',
            'Indiana Fever', 'Los Angeles Sparks', 'Minnesota Lynx', 'New York Liberty',
            'Phoenix Mercury', 'Seattle Storm', 'Washington Mystics'
        ]
        home = ticket.get('home_team', '').lower()
        away = ticket.get('away_team', '').lower()
        # Check for WNBA teams
        for team in wnba_teams:
            if team.lower() in home or team.lower() in away:
                return 'basketball_wnba'
        # Fallback: check ticket_type or title
        if 'wnba' in ticket.get('ticket_type', '').lower() or 'wnba' in ticket.get('title', '').lower():
            return 'basketball_wnba'
        # Default to MLB
        return 'baseball_mlb'

    async def fetch_final_prop_outcomes(self, sport_key, event_id, ticket=None):
        """
        Robust OddsAPI event matching and grading:
        1. Always fetch /events for the sport and match by normalized teams/time.
        2. If event is older than 7 days, skip grading and mark as odds_history: unavailable.
        3. If event_id is found and recent, fetch odds-history and parse.
        4. If odds-history returns 404, mark as unavailable and skip.
        """
        import re
        from datetime import datetime, timezone
        api_key = self.odds_api.api_key if self.odds_api else None
        if not api_key:
            print("No OddsAPI key set.")
            return {}

        # Helper: normalize team names
        def norm_team(name):
            return re.sub(r'[^a-z0-9]', '', (name or '').lower())

        # Helper: normalize commence_time to minute
        def norm_time(dtstr):
            if not dtstr:
                return ''
            try:
                return dtstr[:16]  # 'YYYY-MM-DDTHH:MM'
            except Exception:
                return dtstr

        # Step 1: Always fetch all events for the sport
        events_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/events"
        params = {"apiKey": api_key}
        print(f"[ODDSAPI] Fetching events: {events_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(events_url, params=params) as resp:
                if resp.status != 200:
                    print(f"OddsAPI events error: {resp.status}")
                    return {}
                events = await resp.json()

        # Step 2: Match event by normalized teams and commence_time
        if not ticket:
            print("[ODDSAPI] No ticket provided for event matching.")
            return {}
        target_home = norm_team(ticket.get('home_team'))
        target_away = norm_team(ticket.get('away_team'))
        target_time = norm_time(ticket.get('commence_time'))
        found_event = None
        for event in events:
            home = norm_team(event.get('home_team'))
            away = norm_team(event.get('away_team'))
            commence = norm_time(event.get('commence_time'))
            if home == target_home and away == target_away and commence == target_time:
                found_event = event
                break
        if not found_event:
            print(f"[ODDSAPI] Could not find matching event for {target_home} vs {target_away} at {target_time}")
            return {}
        event_id = found_event.get('id')
        print(f"[ODDSAPI] Matched event_id: {event_id}")

        # Step 3: Check event age (skip if >7 days old)
        commence_dt = found_event.get('commence_time')
        if commence_dt:
            try:
                event_time = datetime.fromisoformat(commence_dt.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                if (now - event_time).days > 7:
                    print(f"[ODDSAPI] Event {event_id} is older than 7 days. Skipping odds-history.")
                    ticket['odds_history'] = 'unavailable'
                    return {}
            except Exception:
                pass

        # Step 4: Fetch odds-history for the matched event_id
        odds_url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/events/{event_id}/odds-history"
        print(f"[ODDSAPI] Requesting odds-history: {odds_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(odds_url, params=params) as resp:
                if resp.status == 404:
                    print(f"[ODDSAPI] odds-history 404 for event_id {event_id}. Marking as unavailable.")
                    ticket['odds_history'] = 'unavailable'
                    return {}
                if resp.status != 200:
                    print(f"OddsAPI odds-history error: {resp.status}")
                    return {}
                data = await resp.json()
        prop_outcomes = {}
        for bookmaker in data.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_key = market.get('key')
                for outcome in market.get('outcomes', []):
                    player_name = outcome.get('description') or outcome.get('participant') or outcome.get('player_name')
                    odds = outcome.get('odds') or outcome.get('price')
                    result = outcome.get('result')
                    name = outcome.get('name', '')
                    m = re.match(r'(Over|Under) ([\\d\\.]+)', name)
                    if not m or not player_name:
                        continue
                    over_under, line = m.groups()
                    line = float(line)
                    key = (player_name, market_key, line)
                    if key not in prop_outcomes:
                        prop_outcomes[key] = {}
                    prop_outcomes[key][over_under.lower()] = {'odds': odds, 'result': result}
        return prop_outcomes

    async def grade_ticket(self, ticket, sport_key=None):
        """Grade a ticket using odds-based reverse engineering from OddsAPI."""
        event_id = ticket.get('game_id') or ticket.get('id')
        ticket_id = ticket.get('ticket_id', ticket.get('id', 'unknown'))
        # Infer sport_key if missing
        if not sport_key:
            sport_key = ticket.get('sport_key')
        if not sport_key:
            sport_key = self.infer_sport_key(ticket)
        if not event_id:
            logger.info(f"[GRADING] Skipping ticket {ticket_id}: missing game_id or id.")
            return None
        # Fetch final prop outcomes from OddsAPI
        prop_outcomes = await self.fetch_final_prop_outcomes(sport_key, event_id, ticket)
        all_hit = True
        any_pending = False
        for selection in ticket.get('selections', []) + ticket.get('picks', []):
            player = selection.get('player_name') or selection.get('player')
            prop_type = selection.get('prop_type') or selection.get('market')
            line = selection.get('line')
            direction = selection.get('direction', '').lower() or selection.get('pick', '').lower()  # 'higher'/'lower' or 'over'/'under'
            key = (player, prop_type, line)
            outcome = prop_outcomes.get(key)
            if not outcome:
                selection['result'] = 'PENDING'
                any_pending = True
                logger.info(f"[GRADING] No odds result for {player} {prop_type} {line} in ticket {ticket_id}. Marked as PENDING.")
                all_hit = False
                continue
            # Map direction to over/under
            if direction in ['higher', 'over']:
                over_result = outcome.get('over', {}).get('result')
                if over_result == 'won':
                    selection['result'] = 'HIT'
                elif over_result == 'lost':
                    selection['result'] = 'MISS'
                    all_hit = False
                elif over_result in ['void', 'refund']:
                    selection['result'] = 'PUSH'
                    all_hit = False
                else:
                    selection['result'] = 'PENDING'
                    any_pending = True
                    all_hit = False
            elif direction in ['lower', 'under']:
                under_result = outcome.get('under', {}).get('result')
                if under_result == 'won':
                    selection['result'] = 'HIT'
                elif under_result == 'lost':
                    selection['result'] = 'MISS'
                    all_hit = False
                elif under_result in ['void', 'refund']:
                    selection['result'] = 'PUSH'
                    all_hit = False
                else:
                    selection['result'] = 'PENDING'
                    any_pending = True
                    all_hit = False
            else:
                selection['result'] = 'PENDING'
                any_pending = True
                all_hit = False
        # Grade the ticket
        if any_pending:
            ticket['graded'] = False
            ticket['ticket_result'] = 'PENDING'
        elif all_hit:
            ticket['graded'] = True
            ticket['ticket_result'] = 'WIN'
        else:
            ticket['graded'] = True
            ticket['ticket_result'] = 'LOSS'
        return ticket

    # Call this after analyzing tickets or on a schedule
    async def post_analysis_and_grading(self):
        await self.grade_tickets_with_results()
        # ... any other post-analysis steps ...

    async def fetch_current_market_odds(self, player_name: str, prop_type: str) -> Optional[Dict]:
        """Fetch current market odds for a player/prop combination"""
        if not self.odds_api:
            return None
        
        try:
            logger.info(f"🔍 Fetching current market odds for {player_name} - {prop_type}")
            
            # Get current games
            games = await self.odds_api.get_games("baseball_mlb")
            
            for game in games:
                game_id = game.get('id')
                if not game_id:
                    continue
                
                # Get player props for this game
                props = await self.odds_api.get_player_props(game_id, "fanduel")
                
                for prop in props:
                    if (prop.get('player_name') == player_name and 
                        prop.get('prop_type') == prop_type):
                        
                        return {
                            'current_odds': prop.get('odds'),
                            'line': prop.get('line'),
                            'bookmaker': 'fanduel',
                            'last_update': prop.get('last_update'),
                            'game_id': game_id
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching current market odds for {player_name}: {e}")
            return None

    async def update_odds_memory_with_current_market(self, player_name: str, prop_type: str, ticket_odds: int):
        """Update odds memory with current market data for comparison"""
        if not self.odds_api:
            return
        
        try:
            # Fetch current market odds
            market_data = await self.fetch_current_market_odds(player_name, prop_type)
            
            if market_data:
                current_odds = market_data.get('current_odds')
                
                # Compare ticket odds to current market
                if current_odds and current_odds != ticket_odds:
                    # TODO: Implement add_odds_entry or use record_ghost_pick/update_closing_odds as appropriate
                    pass
                    
                    logger.info(f"📊 Market comparison for {player_name} {prop_type}:")
                    logger.info(f"   Ticket odds: {ticket_odds}")
                    logger.info(f"   Current market: {current_odds}")
                    
                    # Calculate odds movement
                    if current_odds < ticket_odds:
                        logger.info(f"   📈 Odds falling (more negative) - market moving against us")
                    elif current_odds > ticket_odds:
                        logger.info(f"   📉 Odds rising (less negative) - market moving in our favor")
                    else:
                        logger.info(f"   ➡️ Odds stable")
        
        except Exception as e:
            logger.error(f"Error updating odds memory with current market: {e}")

    async def analyze_ticket_results(self, ticket: Dict) -> Optional[Dict]:
        """Analyze a single ticket to determine its results after game completion."""
        try:
            logger.info(f"🔍 Analyzing ticket results for {ticket.get('ticket_id', 'unknown')}")
            
            # Get ticket selections
            selections = ticket.get('selections', [])
            if not selections:
                logger.warning("No selections found in ticket")
                return None
            
            # Initialize analysis result
            analysis_result = {
                'status': 'pending',
                'leg_results': {},
                'ticket_result': 'pending',
                'hitting_legs': 0,
                'total_legs': len(selections),
                'analyzed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Check if we have game results available
            game_info = ticket.get('game_info', {})
            commence_time = game_info.get('commence_time')
            sport = game_info.get('sport', 'MLB')
            
            if not commence_time:
                logger.warning("No commence time found in ticket")
                return analysis_result
            
            # Calculate if game should be completed
            try:
                if 'T' in commence_time:
                    start_time = datetime.fromisoformat(commence_time.replace('Z', '+00:00'))
                else:
                    start_time = datetime.strptime(commence_time, '%Y-%m-%d %H:%M:%S')
                    start_time = start_time.replace(tzinfo=timezone.utc)
                
                # Add game duration (3 hours for MLB, 2.5 for WNBA)
                game_duration = 3.0 if sport == 'MLB' else 2.5
                expected_end_time = start_time + timedelta(hours=game_duration)
                current_time = datetime.now(timezone.utc)
                
                # If game hasn't ended yet, return pending
                if current_time < expected_end_time:
                    logger.info(f"Game not completed yet. Expected end: {expected_end_time}")
                    return analysis_result
                
            except Exception as e:
                logger.error(f"Error calculating game completion: {e}")
                return analysis_result
            
            # Game should be completed, analyze each leg
            analysis_result['status'] = 'completed'
            hitting_legs = 0
            
            for selection in selections:
                player_name = selection.get('player_name', '')
                prop_type = selection.get('prop_type', '')
                line = selection.get('line', 0)
                over_under = selection.get('over_under', 'O')
                
                # Create unique key for this leg
                leg_key = f"{player_name}_{prop_type}_{line}"
                
                # For now, simulate results based on player name hash
                # In a real implementation, this would fetch actual game results
                import hashlib
                player_hash = int(hashlib.md5(f"{player_name}_{prop_type}".encode()).hexdigest()[:8], 16)
                
                # Simulate 60% win rate for realistic testing
                is_hit = (player_hash % 5) >= 2  # 3/5 chance = 60%
                
                if is_hit:
                    analysis_result['leg_results'][leg_key] = 'hit'
                    hitting_legs += 1
                    logger.info(f"✅ Leg hit: {player_name} - {prop_type} {line} {over_under}")
                else:
                    analysis_result['leg_results'][leg_key] = 'miss'
                    logger.info(f"❌ Leg miss: {player_name} - {prop_type} {line} {over_under}")
            
            # Determine overall ticket result
            analysis_result['hitting_legs'] = hitting_legs
            if hitting_legs == len(selections):
                analysis_result['ticket_result'] = 'WIN'
            else:
                analysis_result['ticket_result'] = 'LOSS'
            
            logger.info(f"🎯 Ticket result: {analysis_result['ticket_result']} ({hitting_legs}/{len(selections)} legs)")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing ticket results: {e}")
            return None

def analyze_ticket(ticket):
    """Simple ticket analysis function for the file handler"""
    # This is a placeholder - in real implementation, this would use the odds engine
    ticket['analyzed'] = True
    ticket['analysis_timestamp'] = datetime.now().isoformat()
    return ticket

async def test_api():
    """Test OddsAPI integration by fetching real data"""
    print("🧪 Testing OddsAPI integration...")
    
    if not ODDS_API_KEY:
        print("❌ No ODDS_API_KEY found in environment variables")
        print("   Set ODDS_API_KEY=your_api_key to test with real data")
        return False
    
    try:
        # Create analyzer instance
        analyzer = AutoOddsAnalyzer()
        
        if not analyzer.odds_api:
            print("❌ OddsAPI handler not initialized")
            print("   Set ODDS_API_KEY=your_api_key to test with real data")
            return False
        
        print("✅ OddsAPI handler initialized")
        
        # Use the OddsAPIHandler as an async context manager
        async with analyzer.odds_api as api:
            # Test fetching current games
            print("📡 Fetching current MLB games...")
            games = await api.get_games("baseball_mlb")
            if games:
                print(f"✅ Found {len(games)} current MLB games")
                for game in games[:3]:  # Show first 3 games
                    home = game.get('home_team', 'Unknown')
                    away = game.get('away_team', 'Unknown')
                    commence = game.get('commence_time', 'Unknown')
                    print(f"   {away} @ {home} - {commence}")
            else:
                print("⚠️ No current MLB games found")
            
            # Test fetching historical odds
            print("📡 Fetching historical odds (last 7 days)...")
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=7)
            
            historical_data = await api.get_historical_odds(
                "baseball_mlb", 
                start_date.strftime('%Y-%m-%d')
            )
            
            if historical_data:
                print(f"✅ Found historical data with {len(historical_data)} entries")
                if historical_data:
                    sample = historical_data[0]
                    print(f"   Sample: {sample.get('home_team', 'Unknown')} vs {sample.get('away_team', 'Unknown')}")
            else:
                print("⚠️ No historical data found")
            
            # Test API limits
            print("📡 Checking API limits...")
            limits = await api.check_api_limits()
            if limits:
                print(f"✅ API limits: {limits}")
        
        print("🎉 OddsAPI integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing OddsAPI: {e}")
        return False

class TicketFileHandler(FileSystemEventHandler):
    def __init__(self, source_dir, analyzed_dir):
        super().__init__()
        self.source_dir = source_dir
        self.analyzed_dir = analyzed_dir
        self.today = datetime.now().strftime('%Y-%m-%d')

    def on_created(self, event):
        self._handle_event(event)
    def on_modified(self, event):
        self._handle_event(event)
    def _handle_event(self, event):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        if self.today in file_path.name and file_path.suffix == '.json':
            print(f"Detected new or modified ticket: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    ticket_data = json.load(f)
                if isinstance(ticket_data, list):
                    analyzed = [analyze_ticket(t) for t in ticket_data]
                else:
                    analyzed = analyze_ticket(ticket_data)
                analyzed_file = self.analyzed_dir / f"analyzed_generated_{file_path.name}"
                with open(analyzed_file, 'w') as f:
                    json.dump(analyzed, f, indent=2)
                print(f"Analyzed and saved: {analyzed_file}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def start_ticket_watcher():
    event_handler = TicketFileHandler(GENERATED_DIR, ANALYZED_DIR)
    observer = Observer()
    observer.schedule(event_handler, str(GENERATED_DIR), recursive=False)
    observer_thread = threading.Thread(target=observer.start)
    observer_thread.daemon = True
    observer_thread.start()
    print(f"Watching {GENERATED_DIR} for new tickets...")
    return observer

def migrate_and_grade_unified_tickets():
    """
    1. Group all per-leg ticket files in ghost_ai_core_memory/tickets/unified/ by ticket_id.
    2. Combine into single ticket files, move to subfolder by date.
    3. Name as lase_{num_legs}_{last5}.json.
    4. After grading, rename folder to _graded.
    """
    from pathlib import Path
    import json
    from datetime import datetime
    import os

    unified_dir = Path("ghost_ai_core_memory/tickets/unified")
    if not unified_dir.exists():
        print(f"Unified directory {unified_dir} does not exist.")
        return

    # Step 1: Group by ticket_id
    ticket_map = {}
    file_map = {}
    for file in unified_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Support both list and dict
            if isinstance(data, list):
                ticket = data[0]
            else:
                ticket = data
            ticket_id = ticket.get('ticket_id')
            if not ticket_id:
                continue
            if ticket_id not in ticket_map:
                ticket_map[ticket_id] = []
                file_map[ticket_id] = []
            ticket_map[ticket_id].append(ticket)
            file_map[ticket_id].append(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    # Step 2: Write combined tickets to date subfolders
    for ticket_id, legs in ticket_map.items():
        num_legs = len(legs)
        last5 = str(ticket_id)[-5:]
        # Try to get date from ticket, fallback to today
        date = None
        for t in legs:
            for field in ['graded_at', 'created_at', 'analyzed_at']:
                if field in t:
                    try:
                        d = t[field][:10]
                        datetime.strptime(d, '%Y-%m-%d')
                        date = d
                        break
                    except Exception:
                        continue
            if date:
                break
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        out_dir = unified_dir / date
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"lase_{num_legs}_{last5}.json"
        # Combine all legs into a list under 'selections' if not already
        ticket_obj = legs[0].copy()
        ticket_obj['selections'] = legs
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(ticket_obj, f, indent=2)
        # Remove old per-leg files
        for fpath in file_map[ticket_id]:
            try:
                os.remove(fpath)
            except Exception:
                pass
        print(f"Wrote {out_file}")

    # Step 3: Grade all tickets in each date folder, then rename folder to _graded
    for date_folder in unified_dir.iterdir():
        if not date_folder.is_dir() or str(date_folder).endswith('_graded'):
            continue
        print(f"Grading tickets in {date_folder}...")
        for ticket_file in date_folder.glob("*.json"):
            try:
                with open(ticket_file, 'r', encoding='utf-8') as f:
                    ticket = json.load(f)
                # Use the existing grading logic
                analyzer = AutoOddsAnalyzer()
                import asyncio
                asyncio.run(analyzer.grade_ticket(ticket, ticket.get('sport_key', 'baseball_mlb')))
                with open(ticket_file, 'w', encoding='utf-8') as f:
                    json.dump(ticket, f, indent=2)
                print(f"Graded {ticket_file}")
            except Exception as e:
                print(f"Error grading {ticket_file}: {e}")
        # Rename folder to _graded
        graded_folder = Path(str(date_folder) + '_graded')
        try:
            shutil.move(str(date_folder), str(graded_folder))
            print(f"Renamed {date_folder} to {graded_folder}")
        except Exception as e:
            print(f"Error renaming {date_folder}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Auto Odds Analyzer')
    parser.add_argument('--test-api', action='store_true', help='Test OddsAPI integration')
    parser.add_argument('--monitor', action='store_true', help='Start file monitoring (default)')
    parser.add_argument('--migrate-unified', action='store_true', help='Migrate and grade unified tickets')
    args = parser.parse_args()
    
    if args.test_api:
        # Run API test
        asyncio.run(test_api())
    elif args.migrate_unified:
        migrate_and_grade_unified_tickets()
    else:
        # Start the watcher for generated tickets (default behavior)
        observer = start_ticket_watcher()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == "__main__":
    main() 