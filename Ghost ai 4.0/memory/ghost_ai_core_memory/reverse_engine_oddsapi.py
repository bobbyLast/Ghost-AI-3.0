# Ghost AI Reverse Engineering Engine
"""
Uses OddsAPI to track prop outcomes and build confidence scores
"""

import os
import json
import logging
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('reverse_engine')

@dataclass
class PropOutcome:
    """Data class for prop outcomes"""
    event_id: str
    player: str
    market: str
    line: float
    side: str  # 'over' or 'under'
    odds: int
    bookmaker: str
    closing_time: str
    result: str  # 'hit' or 'miss'
    final_stat: float
    tags: List[str]
    confidence_predicted: Optional[float] = None
    ghost_pick: Optional[str] = None  # 'over' or 'under' or None

class ReverseEngineOddsAPI:
    """Reverse engineering engine using OddsAPI"""
    
    def __init__(self):
        self.api_key = os.getenv('ODDS_API_KEY')
        if not self.api_key:
            raise ValueError("ODDS_API_KEY not set in environment")
        
        self.base_url = "https://api.the-odds-api.com/v4"
        self.session = requests.Session()
        self.session.params = {'apiKey': self.api_key}
        
        # Directories
        self.used_props_dir = Path('ghost_ai_core_memory/used_props')
        self.used_props_dir.mkdir(parents=True, exist_ok=True)
        
        # Market mappings
        self.market_mappings = {
            'batter_total_bases': 'total_bases',
            'batter_hits': 'hits',
            'batter_home_runs': 'home_runs',
            'batter_runs_batted_in': 'rbis',
            'batter_walks': 'walks',
            'batter_strikeouts': 'strikeouts',
            'pitcher_strikeouts': 'strikeouts',
            'pitcher_hits_allowed': 'hits_allowed',
            'pitcher_walks': 'walks',
            'pitcher_earned_runs': 'earned_runs',
            'player_points': 'points',
            'player_assists': 'assists',
            'player_rebounds': 'rebounds',
            'player_points_rebounds_assists': 'fantasy_score'
        }
        
        # Confidence thresholds
        self.juiced_threshold = -150  # Odds worse than -150
        self.demon_threshold = 120    # Odds better than +120
        self.trap_threshold = -200    # Very juiced odds
        
    async def fetch_event_odds_history(self, sport: str, event_id: str) -> List[Dict]:
        """Fetch odds history for a specific event"""
        try:
            url = f"{self.base_url}/sports/{sport}/events/{event_id}/odds-history"
            params = {
                'regions': 'us',
                'markets': 'player_points,batter_total_bases,batter_hits,batter_home_runs,player_assists,player_rebounds'
            }
            
            logger.info(f"Fetching odds history for event {event_id}")
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Found {len(data)} odds entries for event {event_id}")
                return data
            else:
                logger.error(f"Error fetching odds history: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching odds history for {event_id}: {e}")
            return []
    
    async def fetch_closing_odds(self, sport: str, date: str) -> List[Dict]:
        """Fetch closing odds for all games on a date"""
        try:
            url = f"{self.base_url}/sports/{sport}/odds-history"
            params = {
                'regions': 'us',
                'date': date,
                'dateFormat': 'iso',
                'markets': 'player_points,batter_total_bases,batter_hits,batter_home_runs,player_assists,player_rebounds'
            }
            
            logger.info(f"Fetching closing odds for {sport} on {date}")
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Found {len(data)} games with closing odds")
                return data
            else:
                logger.error(f"Error fetching closing odds: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching closing odds for {date}: {e}")
            return []
    
    def extract_prop_data(self, game_data: Dict) -> List[Dict]:
        """Extract prop data from game odds"""
        props = []
        
        for bookmaker in game_data.get('bookmakers', []):
            if bookmaker.get('key') != 'fanduel':  # Focus on FanDuel
                continue
                
            for market in bookmaker.get('markets', []):
                market_key = market.get('key', '')
                
                # Only process player prop markets
                if market_key not in self.market_mappings:
                    continue
                
                for outcome in market.get('outcomes', []):
                    prop_data = {
                        'event_id': game_data.get('id', ''),
                        'game_time': game_data.get('commence_time', ''),
                        'home_team': game_data.get('home_team', ''),
                        'away_team': game_data.get('away_team', ''),
                        'market': market_key,
                        'player': outcome.get('description', ''),
                        'line': outcome.get('point', 0),
                        'side': outcome.get('name', '').lower(),  # 'over' or 'under'
                        'odds': outcome.get('price', 0),
                        'bookmaker': 'fanduel',
                        'timestamp': datetime.now().isoformat()
                    }
                    props.append(prop_data)
        
        return props
    
    def classify_prop(self, odds: int, result: str) -> List[str]:
        """Classify prop based on odds and result"""
        tags = []
        
        # Juiced odds that missed = trap
        if odds <= self.juiced_threshold and result == 'miss':
            tags.append('trap_line')
            tags.append('juiced_miss')
        
        # Juiced odds that hit = safe
        elif odds <= self.juiced_threshold and result == 'hit':
            tags.append('juiced_hit')
            tags.append('safe_line')
        
        # High odds that hit = demon
        elif odds >= self.demon_threshold and result == 'hit':
            tags.append('demon')
            tags.append('high_value')
        
        # High odds that missed = risky
        elif odds >= self.demon_threshold and result == 'miss':
            tags.append('risky_miss')
        
        # Very juiced odds = potential trap
        if odds <= self.trap_threshold:
            tags.append('very_juiced')
        
        return tags
    
    def calculate_implied_probability(self, odds: int) -> float:
        """Calculate implied probability from American odds"""
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def infer_result_from_stats(self, player: str, market: str, line: float, final_stats: Dict) -> Tuple[str, float]:
        """Infer prop result from final stats"""
        stat_key = self.market_mappings.get(market, market)
        final_stat = final_stats.get(stat_key, 0)
        
        if final_stat > line:
            return 'hit', final_stat
        elif final_stat < line:
            return 'miss', final_stat
        else:
            return 'push', final_stat
    
    async def fetch_final_stats(self, event_id: str, player: str) -> Dict:
        """Fetch final stats for a player (placeholder - implement with your preferred stat source)"""
        # This is a placeholder - you'll need to implement this with your preferred stat source
        # Options: RapidAPI, SportsDataIO, local stat files, etc.
        
        logger.info(f"Fetching final stats for {player} in event {event_id}")
        
        # For now, return mock data - replace with real implementation
        return {
            'total_bases': 2.0,
            'hits': 1,
            'home_runs': 0,
            'rbis': 1,
            'walks': 1,
            'strikeouts': 1,
            'points': 15,
            'assists': 5,
            'rebounds': 8,
            'fantasy_score': 28.0
        }
    
    def _get_used_props_filename(self, sport: str, date: str) -> Path:
        """Get the used props file path for a given sport and date (YYYY-MM-DD)."""
        return self.used_props_dir / f"used_props_{sport.lower()}_{date}.json"
    
    def save_prop_outcome(self, outcome: PropOutcome, sport: str = "mlb"):
        """Save prop outcome to the consolidated daily file."""
        try:
            if not sport:
                sport = "mlb"
            date_str = outcome.closing_time[:10]  # YYYY-MM-DD
            out_path = self._get_used_props_filename(sport, date_str)
            # Load existing outcomes if file exists
            if out_path.exists():
                try:
                    with open(out_path, 'r') as f:
                        outcomes = json.load(f)
                        if not isinstance(outcomes, list):
                            outcomes = []
                except Exception:
                    outcomes = []
            else:
                outcomes = []
            # Append new outcome
            outcome_dict = {
                'event_id': outcome.event_id,
                'player': outcome.player,
                'market': outcome.market,
                'line': outcome.line,
                'side': outcome.side,
                'odds': outcome.odds,
                'bookmaker': outcome.bookmaker,
                'closing_time': outcome.closing_time,
                'result': outcome.result,
                'final_stat': outcome.final_stat,
                'tags': outcome.tags,
                'confidence_predicted': outcome.confidence_predicted,
                'ghost_pick': outcome.ghost_pick,
                'implied_probability': self.calculate_implied_probability(outcome.odds)
            }
            outcomes.append(outcome_dict)
            with open(out_path, 'w') as f:
                json.dump(outcomes, f, indent=2)
            logger.info(f"Saved prop outcome to {out_path.name}")
        except Exception as e:
            logger.error(f"Error saving prop outcome: {e}")
    
    async def process_game_props(self, sport: str, event_id: str, ghost_picks: Union[List[Dict], None] = None):
        """Process all props for a game"""
        try:
            # Fetch odds history for this event
            odds_data = await self.fetch_event_odds_history(sport, event_id)
            
            if not odds_data:
                logger.warning(f"No odds data found for event {event_id}")
                return
            
            # Extract prop data
            all_props = []
            for game_data in odds_data:
                props = self.extract_prop_data(game_data)
                all_props.extend(props)
            
            logger.info(f"Found {len(all_props)} props for event {event_id}")
            
            # Process each prop
            for prop in all_props:
                # Check if this was a Ghost pick
                ghost_pick = None
                if ghost_picks:
                    for pick in ghost_picks:
                        if (pick.get('player') == prop['player'] and 
                            pick.get('market') == prop['market'] and
                            pick.get('event_id') == event_id):
                            ghost_pick = pick.get('side')  # 'over' or 'under'
                            break
                
                # Fetch final stats
                final_stats = await self.fetch_final_stats(event_id, prop['player'])
                
                # Infer result
                result, final_stat = self.infer_result_from_stats(
                    prop['player'], prop['market'], prop['line'], final_stats
                )
                
                # Classify prop
                tags = self.classify_prop(prop['odds'], result)
                
                # Calculate confidence
                confidence = self.calculate_implied_probability(prop['odds'])
                
                # Create outcome
                outcome = PropOutcome(
                    event_id=prop['event_id'],
                    player=prop['player'],
                    market=prop['market'],
                    line=prop['line'],
                    side=prop['side'],
                    odds=prop['odds'],
                    bookmaker=prop['bookmaker'],
                    closing_time=prop['timestamp'],
                    result=result,
                    final_stat=final_stat,
                    tags=tags,
                    confidence_predicted=confidence,
                    ghost_pick=ghost_pick
                )
                
                # Save outcome
                self.save_prop_outcome(outcome, sport)
            
            logger.info(f"Processed {len(all_props)} props for event {event_id}")
            
        except Exception as e:
            logger.error(f"Error processing game props for {event_id}: {e}")
    
    def analyze_historical_performance(self, player: Union[str, None] = None, market: Union[str, None] = None, sport: str = "mlb") -> Dict:
        """Analyze historical performance for confidence tuning using consolidated files."""
        try:
            if not sport:
                sport = "mlb"
            all_outcomes = []
            # Load all daily files for the sport
            for filepath in self.used_props_dir.glob(f"used_props_{sport.lower()}_*.json"):
                try:
                    with open(filepath, 'r') as f:
                        outcomes = json.load(f)
                        if isinstance(outcomes, list):
                            all_outcomes.extend(outcomes)
                except Exception:
                    continue
            # Filter by player and/or market
            if player:
                all_outcomes = [o for o in all_outcomes if o.get('player') == player]
            if market:
                all_outcomes = [o for o in all_outcomes if o.get('market') == market]
            if not all_outcomes:
                return {'error': 'No historical data found'}
            # Calculate statistics
            total_props = len(all_outcomes)
            hits = sum(1 for o in all_outcomes if o['result'] == 'hit')
            hit_rate = hits / total_props if total_props > 0 else 0
            
            # Analyze by odds ranges
            juiced_hits = sum(1 for o in all_outcomes if o['odds'] <= self.juiced_threshold and o['result'] == 'hit')
            juiced_misses = sum(1 for o in all_outcomes if o['odds'] <= self.juiced_threshold and o['result'] == 'miss')
            demon_hits = sum(1 for o in all_outcomes if o['odds'] >= self.demon_threshold and o['result'] == 'hit')
            demon_misses = sum(1 for o in all_outcomes if o['odds'] >= self.demon_threshold and o['result'] == 'miss')
            
            # Calculate trap rate
            total_juiced = juiced_hits + juiced_misses
            trap_rate = juiced_misses / total_juiced if total_juiced > 0 else 0
            
            # Calculate demon success rate
            total_demons = demon_hits + demon_misses
            demon_success_rate = demon_hits / total_demons if total_demons > 0 else 0
            
            analysis = {
                'total_props': total_props,
                'hits': hits,
                'misses': total_props - hits,
                'hit_rate': hit_rate,
                'juiced_props': {
                    'total': total_juiced,
                    'hits': juiced_hits,
                    'misses': juiced_misses,
                    'trap_rate': trap_rate
                },
                'demon_props': {
                    'total': total_demons,
                    'hits': demon_hits,
                    'misses': demon_misses,
                    'success_rate': demon_success_rate
                },
                'confidence_tuning': {
                    'juiced_confidence_boost': 0.1 if trap_rate < 0.3 else -0.1,
                    'demon_confidence_boost': 0.15 if demon_success_rate > 0.4 else -0.1
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing historical performance: {e}")
            return {'error': str(e)}
    
    async def run_daily_analysis(self, sport: str, date: str):
        """Run daily analysis for all games on a date"""
        try:
            logger.info(f"Running daily analysis for {sport} on {date}")
            
            # Fetch closing odds for the date
            games = await self.fetch_closing_odds(sport, date)
            
            for game in games:
                event_id = game.get('id', '')
                if event_id:
                    await self.process_game_props(sport, event_id)
            
            # Run historical analysis
            analysis = self.analyze_historical_performance(sport=sport)
            logger.info(f"Daily analysis complete: {analysis}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error running daily analysis: {e}")
            return None

# Example usage
async def main():
    """Example usage of the reverse engineering engine"""
    engine = ReverseEngineOddsAPI()
    
    # Process a specific game
    await engine.process_game_props('baseball_mlb', 'example_event_id')
    
    # Run daily analysis
    analysis = await engine.run_daily_analysis('baseball_mlb', '2024-06-20')
    print(f"Analysis: {analysis}")

if __name__ == "__main__":
    asyncio.run(main())