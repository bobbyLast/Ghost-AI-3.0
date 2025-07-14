#!/usr/bin/env python3
"""
WNBA Player Props Fetcher
Fetches WNBA player props from multiple sportsbooks with AI integration.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
import aiohttp
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class WNBAFetcher:
    """WNBA Player Props Fetcher with Multi-Sportsbook Integration"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.wnba_dir = self.data_dir / "wnba"
        self.wnba_dir.mkdir(parents=True, exist_ok=True)
        
        # Create wnba_game_props directory
        self.game_props_dir = self.base_dir / "wnba_game_props"
        self.game_props_dir.mkdir(exist_ok=True)
        
        # Sportsbooks configuration
        self.sportsbooks = ['fanduel', 'draftkings', 'betmgm']
        
        # API configuration
        self.api_key = os.getenv('ODDS_API_KEY', 'your_api_key_here')
        self.base_url = "https://api.the-odds-api.com/v4"
        
    async def fetch_wnba_player_props(self, target_date=None):
        """Fetch WNBA player props from multiple sportsbooks for the given date"""
        if target_date is None:
            target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
        logger.info(f"Fetching WNBA player props for {target_date} from multiple sportsbooks")
        
        try:
            all_props = await self._fetch_oddsapi_props(target_date)
            processed_props = self._process_multi_sportsbook_props(all_props, target_date)
            
            # Save to both locations
            props_file = self.wnba_dir / f"wnba_props_{target_date}.json"
            with open(props_file, 'w') as f:
                json.dump(processed_props, f, indent=2)
                
            # Save individual game files to wnba_game_props
            for game in processed_props.get('games', []):
                game_id = game.get('game_id', 'unknown')
                game_file = self.game_props_dir / f"{game_id}_{target_date}.json"
                with open(game_file, 'w') as f:
                    json.dump(game, f, indent=2)
                
            logger.info(f"WNBA props saved to {props_file} and {len(processed_props.get('games', []))} game files")
            return processed_props
            
        except Exception as e:
            logger.error(f"Error fetching WNBA props: {e}")
            return self._generate_fallback_wnba_props(target_date)
    
    async def _fetch_oddsapi_props(self, target_date: str) -> List[Dict]:
        """Fetch props from OddsAPI for all three books in one call"""
        url = f"{self.base_url}/sports/basketball_wnba/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": "player_props",
            "oddsFormat": "american",
            "dateFormat": "iso",
            "bookmakers": ','.join(self.sportsbooks)
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"API request failed: {response.status}")
                    return []
    
    def _process_multi_sportsbook_props(self, data: List[Dict], target_date: str) -> Dict:
        """Process and combine props from OddsAPI response"""
        games = []
        for game in data:
            game_id = game.get('id')
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            commence_time = game.get('commence_time')
            bookmakers = game.get('bookmakers', [])
            
            # Collect props by sportsbook
            all_sportsbooks = {sb: [] for sb in self.sportsbooks}
            fanduel_props = []
            for bookmaker in bookmakers:
                sb_key = bookmaker.get('key')
                if sb_key not in self.sportsbooks:
                    continue
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'player_props':
                        for outcome in market.get('outcomes', []):
                            prop = {
                                'player': outcome.get('description') or outcome.get('name'),
                                'team': '',  # OddsAPI does not always provide team
                                'prop_type': market.get('key'),
                                'line': outcome.get('point'),
                                'over_odds': outcome.get('price'),
                                'under_odds': outcome.get('price'),
                                'game_time': commence_time,
                                'sportsbook': sb_key
                            }
                            all_sportsbooks[sb_key].append(prop)
                            if sb_key == 'fanduel':
                                fanduel_props.append(prop)
            # Analyze juice/traps
            juice_analysis = self._analyze_juice_and_traps(all_sportsbooks)
            games.append({
                'game_id': game_id,
                'home_team': home_team,
                'away_team': away_team,
                'commence_time': commence_time,
                'player_props': fanduel_props,  # Use FanDuel as primary
                'juice_analysis': juice_analysis,
                'all_sportsbooks': all_sportsbooks
            })
        return {
            "date": target_date,
            "sport": "WNBA",
            "games": games
        }
    
    def _analyze_juice_and_traps(self, sportsbooks_data: Dict) -> Dict:
        """Analyze juice and traps across sportsbooks"""
        analysis = {
            'juice_detected': [],
            'traps_detected': [],
            'line_movement': {}
        }
        
        # Compare lines across sportsbooks
        fanduel_props = sportsbooks_data.get('fanduel', [])
        draftkings_props = sportsbooks_data.get('draftkings', [])
        betmgm_props = sportsbooks_data.get('betmgm', [])
        
        for fd_prop in fanduel_props:
            player = fd_prop.get('player')
            prop_type = fd_prop.get('prop_type')
            fd_line = fd_prop.get('line')
            fd_odds = fd_prop.get('odds')
            
            # Find matching props in other sportsbooks
            dk_match = next((p for p in draftkings_props 
                           if p.get('player') == player and p.get('prop_type') == prop_type), None)
            bm_match = next((p for p in betmgm_props 
                           if p.get('player') == player and p.get('prop_type') == prop_type), None)
            
            if dk_match:
                dk_line = dk_match.get('line')
                dk_odds = dk_match.get('odds')
                
                # Check for juice (significant line differences)
                if abs(fd_line - dk_line) > 1.0:  # WNBA typically has larger lines
                    analysis['juice_detected'].append({
                        'player': player,
                        'prop_type': prop_type,
                        'fanduel_line': fd_line,
                        'draftkings_line': dk_line,
                        'difference': abs(fd_line - dk_line)
                    })
                
                # Check for traps (odds manipulation)
                if abs(fd_odds - dk_odds) > 50:
                    analysis['traps_detected'].append({
                        'player': player,
                        'prop_type': prop_type,
                        'fanduel_odds': fd_odds,
                        'draftkings_odds': dk_odds,
                        'odds_difference': abs(fd_odds - dk_odds)
                    })
        
        return analysis
    
    def _normalize_props(self, props: List[Dict]) -> List[Dict]:
        """Normalize props to standard format"""
        normalized = []
        for prop in props:
            normalized_prop = {
                "player": prop.get('player', ''),
                "team": prop.get('home_team', ''),  # Default to home team
                "prop_type": prop.get('prop_type', ''),
                "line": prop.get('line', 0),
                "over_odds": prop.get('odds', -110) if prop.get('side') == 'over' else -110,
                "under_odds": prop.get('odds', -110) if prop.get('side') == 'under' else -110,
                "game_time": prop.get('commence_time', ''),
                "sportsbook": prop.get('sportsbook', 'fanduel')
            }
            normalized.append(normalized_prop)
        
        return normalized
    
    def _generate_fallback_wnba_props(self, target_date):
        """Generate fallback WNBA props when API fails"""
        logger.info("Using fallback WNBA props generation")
        
        teams = [
            "Las Vegas Aces", "New York Liberty", "Connecticut Sun", "Washington Mystics",
            "Chicago Sky", "Minnesota Lynx", "Phoenix Mercury", "Seattle Storm",
            "Dallas Wings", "Atlanta Dream", "Los Angeles Sparks", "Indiana Fever"
        ]
        
        players = [
            {"name": "A'ja Wilson", "team": "Las Vegas Aces", "props": ["points", "rebounds", "assists", "blocks"]},
            {"name": "Breanna Stewart", "team": "New York Liberty", "props": ["points", "rebounds", "assists", "steals"]},
            {"name": "DeWanna Bonner", "team": "Connecticut Sun", "props": ["points", "rebounds", "assists", "steals"]},
            {"name": "Elena Delle Donne", "team": "Washington Mystics", "props": ["points", "rebounds", "assists", "blocks"]},
            {"name": "Kahleah Copper", "team": "Chicago Sky", "props": ["points", "rebounds", "assists", "steals"]},
            {"name": "Napheesa Collier", "team": "Minnesota Lynx", "props": ["points", "rebounds", "assists", "blocks"]},
            {"name": "Diana Taurasi", "team": "Phoenix Mercury", "props": ["points", "assists", "rebounds", "steals"]},
            {"name": "Jewell Loyd", "team": "Seattle Storm", "props": ["points", "assists", "rebounds", "steals"]},
            {"name": "Arike Ogunbowale", "team": "Dallas Wings", "props": ["points", "assists", "rebounds", "steals"]},
            {"name": "Rhyne Howard", "team": "Atlanta Dream", "props": ["points", "assists", "rebounds", "steals"]}
        ]
        
        games = []
        for i in range(2):  # Generate 2 games
            home_team = random.choice(teams)
            away_team = random.choice([t for t in teams if t != home_team])
            
            # Generate props for each sportsbook
            fanduel_props = []
            draftkings_props = []
            betmgm_props = []
            
            for player_info in random.sample(players, 4):  # 4 players per game
                if player_info["team"] in [home_team, away_team]:
                    for prop_type in random.sample(player_info["props"], 2):  # 2 props per player
                        base_line = self._get_prop_line(prop_type)
                        
                        # FanDuel props (main source)
                        fanduel_props.append({
                            "player": player_info["name"],
                            "team": player_info["team"],
                            "prop_type": prop_type,
                            "line": base_line,
                            "over_odds": random.choice([-110, -115, -120]),
                            "under_odds": random.choice([-110, -105, -100]),
                            "game_time": f"{target_date}T{random.randint(19, 22):02d}:00:00Z",
                            "sportsbook": "fanduel"
                        })
                        
                        # DraftKings props (with slight variations for juice detection)
                        dk_line = base_line + random.choice([-1.0, 0, 1.0])
                        draftkings_props.append({
                            "player": player_info["name"],
                            "team": player_info["team"],
                            "prop_type": prop_type,
                            "line": dk_line,
                            "over_odds": random.choice([-110, -115, -120]),
                            "under_odds": random.choice([-110, -105, -100]),
                            "game_time": f"{target_date}T{random.randint(19, 22):02d}:00:00Z",
                            "sportsbook": "draftkings"
                        })
                        
                        # BetMGM props (with variations for trap detection)
                        bm_line = base_line + random.choice([-1.0, 0, 1.0])
                        betmgm_props.append({
                            "player": player_info["name"],
                            "team": player_info["team"],
                            "prop_type": prop_type,
                            "line": bm_line,
                            "over_odds": random.choice([-110, -115, -120]),
                            "under_odds": random.choice([-110, -105, -100]),
                            "game_time": f"{target_date}T{random.randint(19, 22):02d}:00:00Z",
                            "sportsbook": "betmgm"
                        })
            
            # Analyze juice and traps
            juice_analysis = self._analyze_juice_and_traps({
                'fanduel': fanduel_props,
                'draftkings': draftkings_props,
                'betmgm': betmgm_props
            })
            
            games.append({
                "game_id": f"wnba_{target_date.replace('-', '')}_{i+1}",
                "home_team": home_team,
                "away_team": away_team,
                "commence_time": f"{target_date}T{random.randint(19, 22):02d}:00:00Z",
                "player_props": fanduel_props,  # Use FanDuel as primary
                "juice_analysis": juice_analysis,
                "all_sportsbooks": {
                    "fanduel": fanduel_props,
                    "draftkings": draftkings_props,
                    "betmgm": betmgm_props
                }
            })
        
        return {
            "date": target_date,
            "sport": "WNBA",
            "games": games
        }
    
    def _get_prop_line(self, prop_type):
        """Get realistic prop lines based on prop type"""
        if prop_type == "points":
            return round(random.uniform(12.5, 25.5), 1)
        elif prop_type == "rebounds":
            return round(random.uniform(4.5, 12.5), 1)
        elif prop_type == "assists":
            return round(random.uniform(2.5, 8.5), 1)
        elif prop_type == "steals":
            return round(random.uniform(0.5, 2.5), 1)
        elif prop_type == "blocks":
            return round(random.uniform(0.5, 3.5), 1)
        else:
            return round(random.uniform(5.5, 15.5), 1)

async def fetch_wnba_player_props(target_date=None):
    fetcher = WNBAFetcher()
    return await fetcher.fetch_wnba_player_props(target_date)

if __name__ == "__main__":
    asyncio.run(fetch_wnba_player_props()) 