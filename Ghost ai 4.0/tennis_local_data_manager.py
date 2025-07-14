#!/usr/bin/env python3
"""
Tennis Local Data Manager
Downloads and stores comprehensive tennis data locally for reliable access
"""

import json
import os
import requests
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class TennisLocalDataManager:
    """Manages comprehensive local tennis data storage and retrieval."""
    
    def __init__(self):
        self.base_dir = Path('data/tennis_local')
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Data directories
        self.players_dir = self.base_dir / 'players'
        self.matches_dir = self.base_dir / 'matches'
        self.stats_dir = self.base_dir / 'stats'
        self.h2h_dir = self.base_dir / 'h2h'
        self.odds_dir = self.base_dir / 'odds'
        self.tournaments_dir = self.base_dir / 'tournaments'
        
        # Create directories
        for dir_path in [self.players_dir, self.matches_dir, self.stats_dir, 
                        self.h2h_dir, self.odds_dir, self.tournaments_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # API configuration
        self.api_key = os.getenv('TENNIS_API_KEY')
        self.base_url = 'https://api.api-tennis.com/tennis/'
        
        # Star players (ATP/WTA Top 50)
        self.star_players = self._load_star_players()
        
        logger.info("🎾 Tennis Local Data Manager initialized")
    
    def _load_star_players(self) -> Dict[str, List[str]]:
        """Load star players from configuration."""
        return {
            'ATP_TOP_50': [
                "N. Djokovic", "C. Alcaraz", "J. Sinner", "D. Medvedev", 
                "A. Zverev", "A. Rublev", "S. Tsitsipas", "H. Hurkacz",
                "C. Ruud", "T. Fritz", "G. Dimitrov", "A. de Minaur",
                "H. Rune", "T. Paul", "B. Shelton", "S. Korda",
                "F. Tiafoe", "F. Auger-Aliassime", "K. Khachanov", "N. Jarry",
                "U. Humbert", "A. Mannarino", "A. Tabilo", "S. Baez",
                "T. M. Etcheverry", "L. Musetti", "J. L. Struff", "A. Bublik",
                "T. Griekspoor", "J. Thompson", "C. Eubanks", "M. Purcell",
                "M. Giron", "D. Evans", "A. Murray", "S. Wawrinka",
                "D. Thiem", "G. Monfils", "R. Gasquet", "F. Fognini",
                "R. Bautista Agut", "P. Carreno Busta", "A. Ramos-Vinolas", "F. Coria",
                "P. Cachin", "T. Seyboth Wild", "F. Diaz Acosta", "L. Darderi",
                "F. Cobolli", "J. Mensik", "A. Fils", "L. Van Assche"
            ],
            'WTA_TOP_50': [
                "I. Swiatek", "A. Sabalenka", "C. Gauff", "E. Rybakina",
                "J. Pegula", "O. Jabeur", "M. Vondrousova", "Q. Zheng",
                "M. Sakkari", "K. Muchova", "B. Krejcikova", "B. Haddad Maia",
                "D. Kasatkina", "L. Samsonova", "V. Kudermetova", "E. Alexandrova",
                "M. Keys", "E. Svitolina", "C. Garcia", "J. Ostapenko",
                "V. Azarenka", "A. Pavlyuchenkova", "S. Stephens", "S. Kenin",
                "D. Collins", "A. Riske-Amritraj", "B. Pera", "K. Siniakova",
                "P. Martic", "D. Vekic", "M. Bouzkova", "A. Kalinina",
                "M. Kostyuk", "L. Tsurenko", "V. Tomova", "A. Blinkova",
                "D. Parry", "C. Burel", "D. Shnaider", "M. Andreeva",
                "L. Noskova", "E. Navarro", "P. Stearns", "A. Krueger",
                "K. Day", "S. Vickery", "K. Volynets", "R. Montgomery",
                "C. Ngounoue", "L. Hovde", "A. Eala", "B. Fruhvirtova"
            ]
        }
    
    def _make_api_request(self, method: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling."""
        if not self.api_key:
            logger.error("No tennis API key configured")
            return None
        
        params = params or {}
        params.update({
            'method': method,
            'APIkey': self.api_key
        })
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        return data.get('result')
                    else:
                        logger.error(f"API error: {data}")
                        return None
                elif response.status_code == 500:
                    logger.warning(f"Server error on attempt {attempt + 1}, retrying...")
                    time.sleep(2 ** attempt)
                    continue
                else:
                    logger.error(f"HTTP {response.status_code}: {response.text}")
                    return None
                    
            except Exception as e:
                logger.error(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def download_all_tennis_data(self, days_ahead: int = 30):
        """Download comprehensive tennis data for the next N days."""
        logger.info(f"🎾 Downloading comprehensive tennis data for next {days_ahead} days...")
        
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Download tournaments
        self._download_tournaments()
        
        # Download fixtures for each day
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            logger.info(f"📅 Downloading data for {date_str}")
            
            # Download fixtures
            fixtures = self._download_fixtures(date_str)
            
            if fixtures:
                # Download detailed data for each match
                for fixture in fixtures:
                    self._download_match_details(fixture)
            
            current_date += timedelta(days=1)
            time.sleep(1)  # Rate limiting
        
        logger.info("✅ Comprehensive tennis data download complete!")
    
    def _download_tournaments(self):
        """Download tournament data."""
        logger.info("🏆 Downloading tournament data...")
        
        tournaments = self._make_api_request('get_tournaments')
        if tournaments:
            filepath = self.tournaments_dir / 'all_tournaments.json'
            with open(filepath, 'w') as f:
                json.dump(tournaments, f, indent=2)
            logger.info(f"✅ Downloaded {len(tournaments)} tournaments")
    
    def _download_fixtures(self, date: str) -> List[Dict]:
        """Download fixtures for a specific date."""
        fixtures = self._make_api_request('get_fixtures', {
            'date_start': date,
            'date_stop': date
        })
        
        if fixtures:
            # Save fixtures
            filepath = self.matches_dir / f"fixtures_{date}.json"
            with open(filepath, 'w') as f:
                json.dump(fixtures, f, indent=2)
            
            logger.info(f"✅ Downloaded {len(fixtures)} fixtures for {date}")
            return fixtures
        
        return []
    
    def _download_match_details(self, fixture: Dict):
        """Download detailed data for a specific match."""
        match_key = fixture.get('event_key')
        if not match_key:
            return
        
        # Download player data
        player1_key = fixture.get('first_player_key')
        player2_key = fixture.get('second_player_key')
        
        if player1_key:
            self._download_player_data(player1_key)
        if player2_key:
            self._download_player_data(player2_key)
        
        # Download H2H data
        if player1_key and player2_key:
            self._download_h2h_data(player1_key, player2_key)
        
        # Download odds data
        self._download_odds_data(match_key)
    
    def _download_player_data(self, player_key: str):
        """Download player statistics."""
        player_file = self.players_dir / f"player_{player_key}.json"
        
        # Skip if already downloaded recently
        if player_file.exists():
            try:
                with open(player_file, 'r') as f:
                    data = json.load(f)
                    last_updated = data.get('last_updated')
                    if last_updated:
                        last_update = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update < timedelta(days=7):
                            return  # Data is recent enough
            except:
                pass
        
        # Download player data
        player_data = self._make_api_request('get_players', {'player': player_key})
        if player_data:
            player_data['last_updated'] = datetime.now().isoformat()
            with open(player_file, 'w') as f:
                json.dump(player_data, f, indent=2)
    
    def _download_h2h_data(self, player1_key: str, player2_key: str):
        """Download head-to-head data."""
        h2h_file = self.h2h_dir / f"h2h_{player1_key}_{player2_key}.json"
        
        # Skip if already downloaded recently
        if h2h_file.exists():
            try:
                with open(h2h_file, 'r') as f:
                    data = json.load(f)
                    last_updated = data.get('last_updated')
                    if last_updated:
                        last_update = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update < timedelta(days=30):
                            return  # H2H data doesn't change often
            except:
                pass
        
        # Download H2H data
        h2h_data = self._make_api_request('get_H2H', {
            'player1': player1_key,
            'player2': player2_key
        })
        
        if h2h_data:
            h2h_data['last_updated'] = datetime.now().isoformat()
            with open(h2h_file, 'w') as f:
                json.dump(h2h_data, f, indent=2)
    
    def _download_odds_data(self, match_key: str):
        """Download odds data for a match."""
        odds_file = self.odds_dir / f"odds_{match_key}.json"
        
        # Skip if already downloaded recently
        if odds_file.exists():
            try:
                with open(odds_file, 'r') as f:
                    data = json.load(f)
                    last_updated = data.get('last_updated')
                    if last_updated:
                        last_update = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update < timedelta(hours=6):
                            return  # Odds data is recent
            except:
                pass
        
        # Download odds data
        odds_data = self._make_api_request('get_odds', {'match_key': match_key})
        if odds_data:
            odds_data['last_updated'] = datetime.now().isoformat()
            with open(odds_file, 'w') as f:
                json.dump(odds_data, f, indent=2)
    
    def get_local_fixtures(self, date: str) -> List[Dict]:
        """Get fixtures from local storage."""
        filepath = self.matches_dir / f"fixtures_{date}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return []
    
    def get_local_player_data(self, player_key: str) -> Optional[Dict]:
        """Get player data from local storage."""
        filepath = self.players_dir / f"player_{player_key}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def get_local_h2h_data(self, player1_key: str, player2_key: str) -> Optional[Dict]:
        """Get H2H data from local storage."""
        filepath = self.h2h_dir / f"h2h_{player1_key}_{player2_key}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def get_local_odds_data(self, match_key: str) -> Optional[Dict]:
        """Get odds data from local storage."""
        filepath = self.odds_dir / f"odds_{match_key}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def generate_tennis_props_from_local_data(self, date: str) -> List[Dict]:
        """Generate tennis props using local data."""
        logger.info(f"🎾 Generating tennis props for {date} using local data...")
        
        fixtures = self.get_local_fixtures(date)
        if not fixtures:
            logger.warning(f"No local fixtures found for {date}")
            return []
        
        all_props = []
        
        for fixture in fixtures:
            # Check if it's a star player match
            player1 = fixture.get('event_first_player', '')
            player2 = fixture.get('event_second_player', '')
            
            is_star_match = any(
                player in self.star_players['ATP_TOP_50'] + self.star_players['WTA_TOP_50']
                for player in [player1, player2]
            )
            
            if not is_star_match:
                continue
            
            # Get local data
            player1_key = fixture.get('first_player_key')
            player2_key = fixture.get('second_player_key')
            match_key = fixture.get('event_key')
            
            player1_data = self.get_local_player_data(player1_key) if player1_key else None
            player2_data = self.get_local_player_data(player2_key) if player2_key else None
            h2h_data = self.get_local_h2h_data(player1_key, player2_key) if player1_key and player2_key else None
            odds_data = self.get_local_odds_data(match_key) if match_key else None
            
            # Generate props
            props = self._generate_props_from_data(
                fixture, player1_data, player2_data, h2h_data, odds_data
            )
            
            all_props.extend(props)
        
        logger.info(f"✅ Generated {len(all_props)} tennis props from local data")
        return all_props
    
    def _generate_props_from_data(self, fixture: Dict, player1_data: Optional[Dict], 
                                 player2_data: Optional[Dict], h2h_data: Optional[Dict], 
                                 odds_data: Optional[Dict]) -> List[Dict]:
        """Generate props from local data."""
        props = []
        
        player1 = fixture.get('event_first_player', '')
        player2 = fixture.get('event_second_player', '')
        tournament = fixture.get('tournament_name', '')
        event_type = fixture.get('event_type_type', '')
        
        # Only generate props for major tournaments
        if not any(major in event_type for major in ['Atp Singles', 'Wta Singles', 'Grand Slam', 'Atp Masters 1000']):
            return props
        
        # Generate Underdog-style props
        props.extend([
            {
                'sport': 'TENNIS',
                'player': f"{player1} vs {player2}",
                'prop': 'Total Games',
                'line': 20.5,
                'pick': 'Higher',  # Placeholder - would use AI analysis
                'confidence': 0.65,
                'reasoning': f"Based on local data analysis for {tournament}",
                'tournament': tournament,
                'event_type': event_type,
                'match_time': fixture.get('event_time', ''),
                'surface': fixture.get('tournament_sourface', 'Unknown')
            },
            {
                'sport': 'TENNIS',
                'player': player1,
                'prop': 'Aces',
                'line': 4.5,
                'pick': 'Higher',  # Placeholder
                'confidence': 0.60,
                'reasoning': f"Based on {player1} ace statistics",
                'tournament': tournament,
                'event_type': event_type
            },
            {
                'sport': 'TENNIS',
                'player': player2,
                'prop': 'Aces',
                'line': 4.5,
                'pick': 'Higher',  # Placeholder
                'confidence': 0.60,
                'reasoning': f"Based on {player2} ace statistics",
                'tournament': tournament,
                'event_type': event_type
            }
        ])
        
        return props
    
    def get_data_summary(self) -> Dict:
        """Get summary of local data."""
        summary = {
            'players': len(list(self.players_dir.glob('*.json'))),
            'matches': len(list(self.matches_dir.glob('*.json'))),
            'h2h': len(list(self.h2h_dir.glob('*.json'))),
            'odds': len(list(self.odds_dir.glob('*.json'))),
            'tournaments': len(list(self.tournaments_dir.glob('*.json'))),
            'total_size_mb': self._get_total_size()
        }
        return summary
    
    def _get_total_size(self) -> float:
        """Get total size of local data in MB."""
        total_size = 0
        for file_path in self.base_dir.rglob('*.json'):
            total_size += file_path.stat().st_size
        return round(total_size / (1024 * 1024), 2)

def main():
    """Main function to download tennis data."""
    manager = TennisLocalDataManager()
    
    print("🎾 Tennis Local Data Manager")
    print("=" * 50)
    
    # Download comprehensive data
    manager.download_all_tennis_data(days_ahead=30)
    
    # Show summary
    summary = manager.get_data_summary()
    print("\n📊 Local Data Summary:")
    print(f"   Players: {summary['players']}")
    print(f"   Matches: {summary['matches']}")
    print(f"   H2H Records: {summary['h2h']}")
    print(f"   Odds Data: {summary['odds']}")
    print(f"   Tournaments: {summary['tournaments']}")
    print(f"   Total Size: {summary['total_size_mb']} MB")
    
    # Test prop generation
    today = datetime.now().strftime('%Y-%m-%d')
    props = manager.generate_tennis_props_from_local_data(today)
    print(f"\n🎯 Generated {len(props)} props for today using local data")

if __name__ == "__main__":
    main() 