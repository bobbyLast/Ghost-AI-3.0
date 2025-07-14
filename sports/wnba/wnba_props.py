"""
WNBA Props Fetcher

Fetches and processes WNBA player props from various sources.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set

import aiohttp
from dotenv import load_dotenv
from core.data.data_fetcher import DataFetcher
# from ghost_core.data_fetcher import DataFetcher
# from ghost_core.config.wnba_prop_types import ALL_PROPS as WNBA_ALL_PROPS
# from ghost_core.utils.fantasy_score_calculator import FantasyScoreCalculator
from sports.shared.player_utils import find_best_roster_match
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher

# Load environment variables
load_dotenv(override=True)

# Set up logging
logger = logging.getLogger(__name__)

def normalize_player_name(name: str) -> str:
    """Normalize player name for consistent matching."""
    if not name:
        return ""
    # Remove common suffixes and normalize
    name = name.strip().lower()
    name = name.replace(' jr.', '').replace(' sr.', '').replace(' iii', '').replace(' ii', '').replace(' iv', '')
    name = name.replace(' jr', '').replace(' sr', '')
    return name

def load_roster(roster_path: str = "data/wnba/rosters/wnba_rosters_2025.json") -> Dict[str, Dict[str, str]]:
    player_map = {}
    try:
        with open(roster_path, "r", encoding="utf-8") as f:
            roster = json.load(f)
            for team in roster.get("teams", []):
                team_name = team.get("team", "Unknown")
                for player in team.get("players", []):
                    raw_name = player.get("name", "")
                    name = normalize_player_name(raw_name)
                    if name:
                        player_map[name] = {
                            "team": team_name,
                            "position": player.get("position", "Unknown")
                        }
    except Exception as e:
        logger.error(f"Error loading WNBA roster: {e}")
    return player_map

def find_player_team_from_roster(player_name: str, roster_data: Dict[str, Dict[str, str]]) -> str:
    """Find player's team from roster data with improved name matching."""
    if not roster_data:
        logger.warning(f"No roster data available for {player_name}")
        return 'Unknown'
    
    # Clean player name for matching
    clean_player_name = player_name.strip().lower()
    
    # Remove common suffixes and variations
    clean_name_variations = [
        clean_player_name,
        clean_player_name.replace(' jr', '').replace(' sr', '').replace(' iii', '').replace(' ii', '').replace(' iv', ''),
        clean_player_name.replace(' jr.', '').replace(' sr.', ''),
    ]
    
    # Try exact match first
    for variation in clean_name_variations:
        if variation in roster_data:
            team = roster_data[variation]['team']
            logger.debug(f"Found exact match for {player_name} (variation: {variation}): {team}")
            return team
    
    # Use shared utility for best match
    best_match = find_best_roster_match(clean_name_variations, roster_data)
    if best_match:
        logger.debug(f"Found partial match for {player_name} -> {best_match[0]}: {best_match[1]}")
        return best_match[1]
    
    # Special handling for known WNBA players not in roster
    special_players = {
        'caitlin clark': 'Indiana Fever',
        'aliyah boston': 'Indiana Fever',
        'kelsey mitchell': 'Indiana Fever',
        'nafeesa collier': 'Minnesota Lynx',
        'dearica hamby': 'Los Angeles Sparks',
        'angel reese': 'Chicago Sky',
        'kamilla cardoso': 'Chicago Sky',
        'diamond deShields': 'Chicago Sky',
        'marina mabrey': 'Chicago Sky',
        'elizabeth williams': 'Chicago Sky',
        'dana evans': 'Chicago Sky',
        'isabelle harrison': 'Chicago Sky',
        'morgan bertsch': 'Chicago Sky',
        'brianna turner': 'Chicago Sky',
        'kayla thornton': 'New York Liberty',
        'stefanie dolson': 'New York Liberty',
        'marine johannes': 'New York Liberty',
        'sug sutton': 'New York Liberty',
        'nyara sabally': 'New York Liberty',
        'kayla mcbride': 'New York Liberty',
    }
    
    for special_name, team in special_players.items():
        if clean_player_name == special_name:
            logger.info(f"Found special WNBA player match for {player_name}: {team}")
            return team
    
    logger.warning(f"No team found for WNBA player: {player_name}")
    return 'Unknown'

class WNBAFetcher:
    """Handles fetching and processing WNBA player props."""
    
    def __init__(self, data_fetcher: Optional[Any] = None, player_map: Optional[Dict[str, Dict[str, str]]] = None):
        # self.data_fetcher = data_fetcher or DataFetcher()
        # Load WNBA roster for team detection
        self.player_map = player_map or load_roster()
        
        # Only use FanDuel-supported WNBA player prop markets
        self.prop_keys = [
            'player_points',
            'player_assists',
            'player_rebounds',
            'player_threes',
            'player_points_rebounds_assists',
            'player_points_rebounds',
            'player_points_assists',
            'player_rebounds_assists',
            'player_first_basket',
            'player_first_team_basket',
            'player_double_double',
            'player_points_alternate',
            'player_rebounds_alternate',
            'player_assists_alternate'
        ]
        
        # Fantasy score calculation support
        self.fantasy_score_supported = True
        
    # async def fetch_games(self, date: Optional[str] = None) -> List[Dict]:
    #     if date is None:
    #         date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    #     logger.info(f"Fetching WNBA games for {date}")
    #     games = await self.data_fetcher.get_odds(
    #         sport='basketball_wnba',
    #         regions='us',
    #         markets='h2h,spreads,totals',
    #         date=date
    #     )
    #     if not games:
    #         logger.warning(f"No WNBA games found for {date}")
    #         return []
    #     logger.info(f"Found {len(games)} WNBA games")
    #     return games

    # async def fetch_player_props(self, game_id: str) -> Optional[Dict]:
    #     endpoint = f"/sports/basketball_wnba/events/{game_id}/odds"
    #     params = {
    #         'regions': 'us',
    #         markets': ','.join(self.prop_keys),
    #         'oddsFormat': 'american',
    #         'dateFormat': 'iso'
    #     }
    #     try:
    #         data = await self.data_fetcher._make_api_request(endpoint, params)
    #         if data:
    #                 new_players = self.enrich_with_roster(data)
    #                 return data, new_players
    #     except Exception as e:
    #         logger.error(f"Error fetching props for game {game_id}: {str(e)}")
    #         return None, {}

    def enrich_with_roster(self, props_data: Dict) -> Dict[str, Dict]:
        """Add team and position info to each player prop outcome using OddsAPI data first, then roster, then fallback logic."""
        home_team = props_data.get('home_team', '')
        away_team = props_data.get('away_team', '')
        
        new_players_discovered = {}
        
        # Process each outcome to ensure proper team and position information
        for bookmaker in props_data.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    player_name = outcome.get('description', '') or outcome.get('name', '')
                    current_team = outcome.get('team', '')
                    current_position = outcome.get('position', '')
                    # Always normalize player name for lookup
                    normalized_name = normalize_player_name(player_name)
                    roster_info = self.player_map.get(normalized_name)
                    if roster_info:
                        outcome['team'] = roster_info['team']
                        outcome['position'] = roster_info.get('position', 'Unknown')
                        logger.debug(f"WNBA: Matched player '{player_name}' (normalized: '{normalized_name}') to team '{roster_info['team']}'")
                    elif current_team and current_team != 'Unknown':
                        outcome['team'] = current_team
                        outcome['position'] = current_position or 'Unknown'
                        logger.debug(f"WNBA: Used OddsAPI team for player '{player_name}' (normalized: '{normalized_name}'): '{current_team}'")
                    else:
                        # Fallback logic
                        fallback_team = self._get_fallback_team(player_name, home_team, away_team)
                        if fallback_team:
                            outcome['team'] = fallback_team
                            outcome['position'] = 'Unknown'
                            logger.debug(f"WNBA: Used fallback team for player '{player_name}' (normalized: '{normalized_name}'): '{fallback_team}'")
                        else:
                            outcome['team'] = 'Unknown'
                            outcome['position'] = 'Unknown'
                            logger.debug(f"WNBA: No team found for player '{player_name}' (normalized: '{normalized_name}'). Team set to 'Unknown'")
        
        # Log discovered players for potential roster updates
        if new_players_discovered:
            logger.info(f"Discovered {len(new_players_discovered)} new players that could be added to roster:")
            for player, info in new_players_discovered.items():
                logger.info(f"  {player}: {info['team']} - {info['position']} ({info['game']})")
        
        # At the end of outcome processing, guarantee 'team' is always set for every outcome
        for bookmaker in props_data.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                for outcome in market.get('outcomes', []):
                    if not outcome.get('team'):
                        outcome['team'] = 'Unknown'
        
        return new_players_discovered

    def _get_fallback_team(self, player_name: str, home_team: str, away_team: str) -> Optional[str]:
        """Get team for a player using fallback logic based on known player-team associations."""
        # Comprehensive mapping of known WNBA players to teams
        known_players = {
            # New York Liberty players
            'Breanna Stewart': 'New York Liberty',
            'Sabrina Ionescu': 'New York Liberty',
            'Betnijah Laney': 'New York Liberty',
            'Jonquel Jones': 'New York Liberty',
            'Kayla Thornton': 'New York Liberty',
            'Stefanie Dolson': 'New York Liberty',
            'Marine Johannes': 'New York Liberty',
            'Sug Sutton': 'New York Liberty',
            'Nyara Sabally': 'New York Liberty',
            'Kayla McBride': 'New York Liberty',
            
            # Las Vegas Aces players
            'A\'ja Wilson': 'Las Vegas Aces',
            'Kelsey Plum': 'Las Vegas Aces',
            'Jackie Young': 'Las Vegas Aces',
            'Chelsea Gray': 'Las Vegas Aces',
            'Candace Parker': 'Las Vegas Aces',
            'Alysha Clark': 'Las Vegas Aces',
            'Kiah Stokes': 'Las Vegas Aces',
            'Sydney Colson': 'Las Vegas Aces',
            'Cayla George': 'Las Vegas Aces',
            
            # Connecticut Sun players
            'DeWanna Bonner': 'Connecticut Sun',
            'Alyssa Thomas': 'Connecticut Sun',
            'Brionna Jones': 'Connecticut Sun',
            'Natisha Hiedeman': 'Connecticut Sun',
            'Tiffany Hayes': 'Connecticut Sun',
            'Tyasha Harris': 'Connecticut Sun',
            'DiJonai Carrington': 'Connecticut Sun',
            'Rebecca Allen': 'Connecticut Sun',
            'Olivia Nelson-Ododa': 'Connecticut Sun',
            
            # Washington Mystics players
            'Elena Delle Donne': 'Washington Mystics',
            'Shakira Austin': 'Washington Mystics',
            'Natasha Cloud': 'Washington Mystics',
            'Ariel Atkins': 'Washington Mystics',
            'Brittney Sykes': 'Washington Mystics',
            'Kristi Toliver': 'Washington Mystics',
            'Myisha Hines-Allen': 'Washington Mystics',
            'Shatori Walker-Kimbrough': 'Washington Mystics',
            
            # Add more players as needed...
        }
        
        # Check if player is in our known list
        if player_name in known_players:
            known_team = known_players[player_name]
            # Verify the team is actually playing in this game
            if known_team in [home_team, away_team]:
                return known_team
        
        return None

    # def calculate_fantasy_scores(self, props_data: Dict) -> Dict[str, float]:
    #     """Calculate fantasy scores for all players in the props data."""
    #     try:
    #         fantasy_scores = FantasyScoreCalculator.calculate_from_props(props_data, 'wnba', 'fanduel')
    #         return fantasy_scores
    #     except Exception as e:
    #         logger.error(f"Error calculating fantasy scores: {e}")
    #         return {}

def normalize_team_name(name: str) -> str:
    return name.lower().replace(' ', '_')

def cleanup_old_and_duplicate_files(output_path: Path, valid_filenames: set, dry_run: bool = False):
    """
    Remove files not in today's set and deduplicate by team-vs-team name.
    This ensures only files for the current valid games (today/tomorrow) are kept.
    If dry_run is True, only log what would be deleted.
    """
    seen = set()
    for file in output_path.glob('props_wnba_*.json'):
        matchup = file.name
        if matchup in seen or matchup not in valid_filenames:
            if dry_run:
                logger.info(f"[DRY RUN] Would remove duplicate or old props file: {file}")
            else:
                try:
                    file.unlink()
                    logger.info(f"Removed duplicate or old props file: {file}")
                except Exception as e:
                    logger.error(f"Error removing file {file}: {e}")
        else:
            seen.add(matchup)
            logger.info(f"Kept valid props file: {file}")

async def fetch_wnba_player_props(date: str, output_dir = "wnba_game_props"):
    from pathlib import Path
    import json
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    wnba_player_prop_markets = ','.join([
        'player_points',
        'player_rebounds',
        'player_assists',
        'player_threes',
        'player_blocks',
        'player_steals',
        'player_blocks_steals',
        'player_turnovers',
        'player_points_rebounds_assists',
        'player_points_rebounds',
        'player_points_assists',
        'player_rebounds_assists'
    ])
    async with DataFetcher() as fetcher:
        print(f"Fetching WNBA games from OddsAPI for {date}...")
        games = await fetcher.get_odds(
            sport='basketball_wnba',
            regions='us',
            markets='h2h,spreads,totals',
            date=date
        )
        if not games:
            print("No WNBA games found for today.")
            return
        for game in games:
            game_id = game.get('id')
            home_team = game.get('home_team', 'home')
            away_team = game.get('away_team', 'away')
            if not game_id:
                continue
            try:
                props = await fetcher.get_player_props('basketball_wnba', game_id, prop_markets=wnba_player_prop_markets)
                if props and props.get('bookmakers'):
                    fanduel = [b for b in props['bookmakers'] if b.get('title') == 'FanDuel']
                    others = [b for b in props['bookmakers'] if b.get('title') in {"DraftKings", "Caesars"}]
                    if not fanduel:
                        continue
                    props['bookmakers'] = fanduel + others
                    player_map = load_roster()
                    fetcher_obj = WNBAFetcher(player_map=player_map)
                    fetcher_obj.enrich_with_roster(props)
                    def normalize_team_name(name):
                        return name.lower().replace(' ', '_').replace('/', '_')
                    matchup_file = output_dir / f"props_wnba_{normalize_team_name(home_team)}_vs_{normalize_team_name(away_team)}_{date}.json"
                    with open(matchup_file, "w", encoding="utf-8") as f:
                        json.dump(props, f, indent=2)
            except Exception as e:
                print(f"Error fetching props for game {game_id}: {e}")

class WNBAPropsFetcher(WNBAFetcher):
    """Alias for WNBAFetcher for compatibility with ghost_ai.py"""
    pass
            
if __name__ == "__main__":
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    asyncio.run(fetch_wnba_player_props(today))