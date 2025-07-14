"""
MLB Props Fetcher

Fetches and processes MLB player props from various sources.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import unicodedata
import re

from dotenv import load_dotenv
from sports.shared.player_utils import find_best_roster_match
from core.data.data_fetcher import DataFetcher
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher

# Import from ghost_core
# from data.data_fetcher import DataFetcher
# from config.mlb_prop_types import STANDARD_PROPS as MLB_STANDARD_PROPS, alternate_props as MLB_ALTERNATE_PROPS
# from intelligence.fantasy_score_calculator import FantasyScoreCalculator

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# --- Player name normalization ---
def normalize_player_name(name: str) -> str:
    if not name:
        return ''
    # Remove accents
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    # Remove punctuation
    name = re.sub(r'[\.,\-\'\"]', '', name)
    # Remove common suffixes
    name = re.sub(r'\b(jr|sr|ii|iii|iv|v)\b', '', name, flags=re.IGNORECASE)
    # Remove extra whitespace and lowercase
    return ' '.join(name.lower().split())

# --- Load MLB roster and build player map ---
def load_roster(roster_path: str = "data/mlb/rosters/mlb_rosters_2024.json") -> Dict[str, Dict[str, str]]:
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
        logger.error(f"Error loading MLB roster: {e}")
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
        clean_player_name.replace(' (2002)', '').replace(' (2001)', '').replace(' (2000)', ''),
        clean_player_name.replace(' (2003)', '').replace(' (2004)', ''),
    ]
    
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
    
    # Special handling for known players not in roster
    special_players = {
        'jasson domínguez': 'New York Yankees',
        'jasson dominguez': 'New York Yankees',
        'jacob wilson': 'Oakland Athletics',  # Based on the game context
        'willie maciver': 'Oakland Athletics',  # Based on the game context
        'luis urias': 'Oakland Athletics',  # Based on the game context
        'denzel clarke': 'Oakland Athletics',  # Based on the game context
        'nick kurtz': 'Oakland Athletics',  # Based on the game context
        'max muncy': 'Oakland Athletics',  # Based on the game context
    }
    
    for special_name, team in special_players.items():
        if clean_player_name == special_name or clean_player_name.replace(' (2002)', '') == special_name:
            logger.info(f"Found special player match for {player_name}: {team}")
            return team
    
    logger.warning(f"No team found for player: {player_name}")
    return 'Unknown'

class MLBFetcher:
    """Handles fetching and processing MLB player props."""

    def __init__(self, data_fetcher: Optional[Any] = None, player_map: Optional[Dict[str, Dict[str, str]]] = None):
        # self.data_fetcher = data_fetcher or DataFetcher()
        # Only use FanDuel-supported batter and pitcher props
        self.prop_keys = [
            # Batter props
            'batter_hits',
            'batter_home_runs',
            'batter_total_bases',
            'batter_rbis',
            'batter_runs_scored',
            'batter_stolen_bases',
            'batter_singles',
            'batter_doubles',
            'batter_triples',
            'batter_walks',
            # Pitcher props
            'pitcher_strikeouts',
            'pitcher_strikeouts_alternate',
        ]
        
        # Fantasy score calculation support
        self.fantasy_score_supported = True
        self.player_map = player_map or {}
        
    # async def fetch_games(self, date: Optional[str] = None) -> List[Dict]:
    #     if date is None:
    #         date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    #     logger.info(f"Fetching MLB games for {date}")
    #     games = await self.data_fetcher.get_odds(
    #         sport='baseball_mlb',
    #         regions='us',
    #         markets='h2h,spreads,totals',
    #         date=date
    #     )
    #     if not games:
    #         logger.warning(f"No MLB games found for {date}")
    #         return []
    #     logger.info(f"Found {len(games)} MLB games")
    #     return games

    # async def fetch_player_props(self, game_id: str) -> Optional[Dict]:
    #     endpoint = f"/sports/baseball_mlb/events/{game_id}/odds"
    #     params = {
    #         'regions': 'us',
    #         'markets': ','.join(self.prop_keys),
    #         'oddsFormat': 'american',
    #         'dateFormat': 'iso'
    #     }
    #     try:
    #         data = await self.data_fetcher._make_api_request(endpoint, params)
    #         if data:
    #             new_players = self.enrich_with_roster(data)
    #             return data, new_players
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
                    normalized_name = normalize_player_name(player_name)
                    roster_info = self.player_map.get(normalized_name)
                    if roster_info:
                        outcome['team'] = roster_info['team']
                        outcome['position'] = roster_info.get('position', 'Unknown')
                        logger.debug(f"MLB: Matched player '{player_name}' (normalized: '{normalized_name}') to team '{roster_info['team']}'")
                    elif current_team and current_team != 'Unknown':
                        outcome['team'] = current_team
                        outcome['position'] = current_position or 'Unknown'
                        logger.debug(f"MLB: Used OddsAPI team for player '{player_name}' (normalized: '{normalized_name}'): '{current_team}'")
                    else:
                        # Fallback logic
                        fallback_team = self._get_fallback_team(player_name, home_team, away_team)
                        if fallback_team:
                            outcome['team'] = fallback_team
                            outcome['position'] = 'Unknown'
                            logger.debug(f"MLB: Used fallback team for player '{player_name}' (normalized: '{normalized_name}'): '{fallback_team}'")
                        else:
                            outcome['team'] = 'Unknown'
                            outcome['position'] = 'Unknown'
                            logger.debug(f"MLB: No team found for player '{player_name}' (normalized: '{normalized_name}'). Team set to 'Unknown'")
                    
                    # Priority 2: If OddsAPI team is "Unknown" or missing, try improved roster lookup
                    # This block is removed as per the new_code, as the logic is now integrated.
                    
                    # Track new players for potential roster update
                    if outcome['team'] == 'Unknown':
                        if player_name not in new_players_discovered:
                            new_players_discovered[player_name] = {
                                'team': 'Unknown',
                                'position': 'Unknown',
                                'game': f"{away_team} vs {home_team}"
                            }
                        logger.debug(f"Player {player_name} has unknown team for game {home_team} vs {away_team}")
        
        # Log discovered players for potential roster updates
        if new_players_discovered:
            logger.info(f"Discovered {len(new_players_discovered)} new players that could be added to roster:")
            for player, info in new_players_discovered.items():
                logger.info(f"  {player}: {info['team']} - {info['position']} ({info['game']})")
        
        return new_players_discovered
    
    # def calculate_fantasy_scores(self, props_data: Dict) -> Dict[str, float]:
    #     """Calculate fantasy scores for all players in the props data."""
    #     try:
    #         fantasy_scores = FantasyScoreCalculator.calculate_from_props(props_data, 'mlb', 'fanduel')
    #         return fantasy_scores
    #     except Exception as e:
    #         logger.error(f"Error calculating fantasy scores: {e}")
    #         return {}
    
    def _get_fallback_team(self, player_name: str, home_team: str, away_team: str) -> Optional[str]:
        """Get team for a player using fallback logic based on known player-team associations."""
        # Comprehensive mapping of known players to teams
        known_players = {
            # Yankees players
            'Giancarlo Stanton': 'New York Yankees',
            'Aaron Judge': 'New York Yankees',
            'Juan Soto': 'New York Yankees',
            'Gleyber Torres': 'New York Yankees',
            'Anthony Volpe': 'New York Yankees',
            'DJ LeMahieu': 'New York Yankees',
            'Alex Verdugo': 'New York Yankees',
            'Jose Trevino': 'New York Yankees',
            'Austin Wells': 'New York Yankees',
            'Oswaldo Cabrera': 'New York Yankees',
            'Trent Grisham': 'New York Yankees',
            'Jon Berti': 'New York Yankees',
            'Jasson Domínguez': 'New York Yankees',
            'Jasson Dominguez': 'New York Yankees',
            
            # Athletics players
            'Jacob Wilson': 'Oakland Athletics',
            'Willie MacIver': 'Oakland Athletics',
            'Luis Urias': 'Oakland Athletics',
            'Denzel Clarke': 'Oakland Athletics',
            'Nick Kurtz': 'Oakland Athletics',
            'Max Muncy': 'Oakland Athletics',
            'Lawrence Butler': 'Oakland Athletics',
            'Brent Rooker': 'Oakland Athletics',
            'Tyler Soderstrom': 'Oakland Athletics',
            
            # Reds players
            'Elly De La Cruz': 'Cincinnati Reds',
            'Spencer Steer': 'Cincinnati Reds',
            'Jonathan India': 'Cincinnati Reds',
            'TJ Friedl': 'Cincinnati Reds',
            'Jake Fraley': 'Cincinnati Reds',
            'Will Benson': 'Cincinnati Reds',
            'Tyler Stephenson': 'Cincinnati Reds',
            'Jeimer Candelario': 'Cincinnati Reds',
            'Stuart Fairchild': 'Cincinnati Reds',
            'Nick Martini': 'Cincinnati Reds',
            'Luke Maile': 'Cincinnati Reds',
            'Santiago Espinal': 'Cincinnati Reds',
            'Christian Encarnacion-Strand': 'Cincinnati Reds',
            
            # Phillies players
            'Alec Bohm': 'Philadelphia Phillies',
            'Trea Turner': 'Philadelphia Phillies',
            'Kyle Schwarber': 'Philadelphia Phillies',
            'Nick Castellanos': 'Philadelphia Phillies',
            'J.T. Realmuto': 'Philadelphia Phillies',
            'Johan Rojas': 'Philadelphia Phillies',
            'Edmundo Sosa': 'Philadelphia Phillies',
            'Otto Kemp': 'Philadelphia Phillies',
            'Buddy Kennedy': 'Philadelphia Phillies',
            
            # Astros players
            'Jose Altuve': 'Houston Astros',
            'Jeremy Pena': 'Houston Astros',
            'Yainer Diaz': 'Houston Astros',
            'Mauricio Dubon': 'Houston Astros',
            'Jake Meyers': 'Houston Astros',
            'Victor Caratini': 'Houston Astros',
            
            # Angels players
            'Mike Trout': 'Los Angeles Angels',
            'Taylor Ward': 'Los Angeles Angels',
            'Jo Adell': 'Los Angeles Angels',
            'Nolan Schanuel': 'Los Angeles Angels',
            'Luis Rengifo': 'Los Angeles Angels',
            'Logan O\'Hoppe': 'Los Angeles Angels',
            'Zach Neto': 'Los Angeles Angels',
            
            # Nationals players
            'CJ Abrams': 'Washington Nationals',
            'Brady House': 'Washington Nationals',
            'Jacob Young': 'Washington Nationals',
            'Drew Millas': 'Washington Nationals',
            'Daylen Lile': 'Washington Nationals',
            'James Wood': 'Washington Nationals',
            'Christian Moore': 'Washington Nationals',
            'Luis Garcia Jr.': 'Washington Nationals',
            'Riley Adams': 'Washington Nationals',
            
            # Other players from the logs
            'Isaac Paredes': 'Tampa Bay Rays',
            'Cam Smith': 'Miami Marlins',
            'Christian Walker': 'Arizona Diamondbacks',
            'Scott Kingery': 'Free Agent',
            
            # Braves players
            'Ronald Acuña Jr.': 'Atlanta Braves',
            'Matt Olson': 'Atlanta Braves',
            'Austin Riley': 'Atlanta Braves',
            'Ozzie Albies': 'Atlanta Braves',
            'Marcell Ozuna': 'Atlanta Braves',
            'Sean Murphy': 'Atlanta Braves',
            'Michael Harris II': 'Atlanta Braves',
            'Orlando Arcia': 'Atlanta Braves',
            
            # Mets players
            'Francisco Lindor': 'New York Mets',
            'Pete Alonso': 'New York Mets',
            'Brandon Nimmo': 'New York Mets',
            'Starling Marte': 'New York Mets',
            'Jeff McNeil': 'New York Mets',
            'Luisangel Acuña': 'New York Mets',
            'Ronny Mauricio': 'New York Mets',
            'Luis Torrens': 'New York Mets',
            
            # Add more players as needed...
        }
        
        # Check if player is in our known list
        if player_name in known_players:
            known_team = known_players[player_name]
            # Verify the team is actually playing in this game
            if known_team in [home_team, away_team]:
                return known_team
        
        # If not found in known list, try to infer from game context
        # For players with "Unknown" team, we can sometimes infer based on the game
        # This is a fallback for when the roster lookup fails
        logger.debug(f"Player {player_name} not found in known list for game {away_team} vs {home_team}")
        
        return None

def normalize_team_name(name: str) -> str:
    return name.lower().replace(' ', '_')

def update_roster_with_new_players(new_players: Dict[str, Dict], roster_path: str = "data/mlb/rosters/mlb_rosters_2024.json"):
    """Update the roster file with newly discovered players."""
    try:
        # Load existing roster
        with open(roster_path, "r", encoding="utf-8") as f:
            roster = json.load(f)
        
        # Track which teams need updates
        team_updates = {}
        
        # Group new players by team
        for player_name, info in new_players.items():
            team = info.get('team')
            if team and team != 'Unknown':
                if team not in team_updates:
                    team_updates[team] = []
                team_updates[team].append({
                    'name': player_name,
                    'position': info.get('position', 'Unknown'),
                    'status': 'Active'
                })
        
        # Update roster with new players
        updated = False
        for team_name, new_players_list in team_updates.items():
            # Find the team in the roster
            for team in roster.get('teams', []):
                if team.get('team') == team_name:
                    existing_players = {p.get('name') for p in team.get('players', [])}
                    
                    # Add new players that aren't already in the roster
                    for new_player in new_players_list:
                        if new_player['name'] not in existing_players:
                            team['players'].append(new_player)
                            updated = True
                            logger.info(f"Added {new_player['name']} to {team_name} roster")
                    break
        
        # Save updated roster if changes were made
        if updated:
            with open(roster_path, "w", encoding="utf-8") as f:
                json.dump(roster, f, indent=2)
            logger.info(f"Updated roster file with {len([p for players in team_updates.values() for p in players])} new players")
        
    except Exception as e:
        logger.error(f"Error updating roster: {e}")

def cleanup_old_and_duplicate_files(output_path: Path, valid_filenames: set, dry_run: bool = False):
    """Remove files not in today's set and deduplicate by team-vs-team name. If dry_run is True, only log what would be deleted."""
    seen = set()
    for file in output_path.glob('props_mlb_*.json'):
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

async def fetch_mlb_player_props(date: str, output_dir = "mlb_game_props"):
    from pathlib import Path
    import json
    output_dir = Path(output_dir)  # Ensure output_dir is a Path object
    output_dir.mkdir(exist_ok=True)
    mlb_player_prop_markets = ','.join([
        'batter_home_runs',
        'batter_hits',
        'batter_total_bases',
        'batter_rbis',
        'batter_runs_scored',
        'batter_hits_runs_rbis',
        'batter_singles',
        'batter_doubles',
        'batter_triples',
        'batter_walks',
        'batter_strikeouts',
        'batter_stolen_bases',
        'pitcher_strikeouts',
        'pitcher_record_a_win',
        'pitcher_hits_allowed',
        'pitcher_walks',
        'pitcher_earned_runs',
        'pitcher_outs'
    ])
    target_books = {"FanDuel", "DraftKings", "Caesars"}
    async with DataFetcher() as fetcher:
        print(f"Fetching MLB games from OddsAPI for {date}...")
        games = await fetcher.get_odds(
            sport='baseball_mlb',
            regions='us',
            markets='h2h,spreads,totals',
            date=date
        )
        if not games:
            print("No MLB games found for today.")
            return
        for game in games:
            game_id = game.get('id')
            home_team = game.get('home_team', 'home')
            away_team = game.get('away_team', 'away')
            if not game_id:
                continue
            try:
                props = await fetcher.get_player_props('baseball_mlb', game_id, prop_markets=mlb_player_prop_markets)
                if props:
                    if props.get('bookmakers'):
                        # Filter to only target books and handle Caesars alias
                        target_bookmakers = []
                        for bookmaker in props['bookmakers']:
                            title = bookmaker.get('title', '')
                            key = bookmaker.get('key', '')
                            # Check if this is one of our target books
                            if (title == 'FanDuel' or key == 'fanduel' or
                                title == 'DraftKings' or key == 'draftkings' or
                                title == 'Caesars' or key == 'caesars' or
                                key == 'williamhill_us'):  # Caesars alias
                                # Normalize Caesars title
                                if key == 'williamhill_us':
                                    bookmaker['title'] = 'Caesars'
                                    bookmaker['key'] = 'caesars'
                            target_bookmakers.append(bookmaker)
                    # Require FanDuel to be present
                    fanduel_present = any(b.get('title') == 'FanDuel' or b.get('key') == 'fanduel' 
                                        for b in target_bookmakers)
                    if not fanduel_present:
                        continue
                    # Order: FanDuel first, then others
                    fanduel = [b for b in target_bookmakers if b.get('title') == 'FanDuel' or b.get('key') == 'fanduel']
                    others = [b for b in target_bookmakers if b.get('title') != 'FanDuel' and b.get('key') != 'fanduel']
                    props['bookmakers'] = fanduel + others
                    # Log which sportsbooks were found
                    found_books = [b.get('title') for b in props['bookmakers']]
                    print(f"✅ {home_team} vs {away_team}: Found sportsbooks: {found_books}")
                    player_map = load_roster()
                    fetcher_obj = MLBFetcher(player_map=player_map)
                    fetcher_obj.enrich_with_roster(props)
                    def normalize_team_name(name):
                        return name.lower().replace(' ', '_').replace('/', '_')
                    matchup_file = output_dir / f"props_mlb_{normalize_team_name(home_team)}_vs_{normalize_team_name(away_team)}_{date}.json"
                    with open(matchup_file, "w", encoding="utf-8") as f:
                        json.dump(props, f, indent=2)
            except Exception as e:
                print(f"Error fetching props for game {game_id}: {e}")

class MLBPropsFetcher(MLBFetcher):
    """Alias for MLBFetcher for compatibility with ghost_ai.py"""
    pass

# Add fetch_all_props to MLBFetcher
setattr(MLBFetcher, 'fetch_all_props', staticmethod(lambda: fetch_mlb_player_props(datetime.now().strftime('%Y-%m-%d'))))
            
if __name__ == "__main__":
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    asyncio.run(fetch_mlb_player_props(today)) 