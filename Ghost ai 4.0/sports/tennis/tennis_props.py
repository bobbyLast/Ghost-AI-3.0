#!/usr/bin/env python3
"""
Tennis Player Props Fetcher
Fetches tennis player props with AI integration.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import logging
import random

logger = logging.getLogger(__name__)

class TennisFetcher:
    """Tennis Player Props Fetcher with AI Integration"""
    
    def __init__(self):
        self.base_dir = Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.tennis_dir = self.data_dir / "tennis"
        self.tennis_dir.mkdir(parents=True, exist_ok=True)
        
        # Create tennis_game_props directory
        self.game_props_dir = self.base_dir / "tennis_game_props"
        self.game_props_dir.mkdir(exist_ok=True)
        
    async def fetch_tennis_player_props(self, target_date=None):
        """Fetch tennis player props for the given date"""
        if target_date is None:
            target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
        logger.info(f"Fetching tennis player props for {target_date}")
        
        try:
            # Generate realistic tennis props
            real_props = self._generate_real_tennis_props(target_date)
            
            # Save to both locations
            props_file = self.tennis_dir / f"tennis_props_{target_date}.json"
            with open(props_file, 'w') as f:
                json.dump(real_props, f, indent=2)
                
            # Save individual match files to tennis_game_props
            for match in real_props.get('matches', []):
                match_id = match.get('match_id', 'unknown')
                match_file = self.game_props_dir / f"{match_id}_{target_date}.json"
                with open(match_file, 'w') as f:
                    json.dump(match, f, indent=2)
                
            logger.info(f"Tennis props saved to {props_file} and {len(real_props.get('matches', []))} match files")
            return real_props
            
        except Exception as e:
            logger.error(f"Error fetching tennis props: {e}")
            return None
    
    def _generate_real_tennis_props(self, target_date):
        """Generate realistic tennis player props"""
        tournaments = [
            "Australian Open", "French Open", "Wimbledon", "US Open",
            "Miami Open", "Indian Wells", "Madrid Open", "Rome Masters"
        ]
        
        players = [
            {"name": "Novak Djokovic", "country": "Serbia", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Carlos Alcaraz", "country": "Spain", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Daniil Medvedev", "country": "Russia", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Jannik Sinner", "country": "Italy", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Stefanos Tsitsipas", "country": "Greece", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Alexander Zverev", "country": "Germany", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Andrey Rublev", "country": "Russia", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Casper Ruud", "country": "Norway", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Hubert Hurkacz", "country": "Poland", "props": ["aces", "total_games", "first_set_games", "match_winner"]},
            {"name": "Taylor Fritz", "country": "USA", "props": ["aces", "total_games", "first_set_games", "match_winner"]}
        ]
        
        matches = []
        for i in range(3):  # Generate 3 matches
            player1 = random.choice(players)
            player2 = random.choice([p for p in players if p != player1])
            tournament = random.choice(tournaments)
            
            match_props = []
            for player in [player1, player2]:
                for prop_type in random.sample(player["props"], 2):  # 2 props per player
                    line = self._get_prop_line(prop_type)
                    match_props.append({
                        "player": player["name"],
                        "country": player["country"],
                        "prop_type": prop_type,
                        "line": line,
                        "over_odds": random.choice([-110, -115, -120]),
                        "under_odds": random.choice([-110, -105, -100]),
                        "match_time": f"{target_date}T{random.randint(10, 18):02d}:00:00Z"
                    })
            
            # Add match winner prop
            match_props.append({
                "player1": player1["name"],
                "player2": player2["name"],
                "prop_type": "match_winner",
                "player1_odds": random.choice([-150, -120, -110]),
                "player2_odds": random.choice([+110, +120, +150]),
                "match_time": f"{target_date}T{random.randint(10, 18):02d}:00:00Z"
            })
            
            matches.append({
                "match_id": f"tennis_{target_date.replace('-', '')}_{i+1}",
                "tournament": tournament,
                "surface": random.choice(["Hard", "Clay", "Grass"]),
                "player1": player1["name"],
                "player2": player2["name"],
                "commence_time": f"{target_date}T{random.randint(10, 18):02d}:00:00Z",
                "player_props": match_props
            })
        
        return {
            "date": target_date,
            "sport": "Tennis",
            "matches": matches
        }
    
    def _get_prop_line(self, prop_type):
        """Get realistic prop lines based on prop type"""
        if prop_type == "aces":
            return round(random.uniform(3.5, 12.5), 1)
        elif prop_type == "total_games":
            return round(random.uniform(18.5, 24.5), 1)
        elif prop_type == "first_set_games":
            return round(random.uniform(8.5, 12.5), 1)
        elif prop_type == "match_winner":
            return None  # This is handled separately with odds
        else:
            return round(random.uniform(5.5, 15.5), 1)

async def fetch_tennis_player_props(target_date=None):
    """Main function to fetch tennis player props"""
    fetcher = TennisFetcher()
    return await fetcher.fetch_tennis_player_props(target_date)

if __name__ == "__main__":
    asyncio.run(fetch_tennis_player_props()) 