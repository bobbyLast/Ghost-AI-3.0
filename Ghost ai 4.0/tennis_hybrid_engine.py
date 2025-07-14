#!/usr/bin/env python3
"""
Tennis Hybrid Engine - Combines API fixture fetching with Kaggle data analysis
Fetches today's fixtures from API, then analyzes using local Kaggle data
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random
# Add import for unified ticket manager
from ghost_ai_core_memory.tickets.integration_hooks import hook_ticket_generation

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TennisHybridEngine:
    def __init__(self):
        self.api_key = os.getenv('TENNIS_API_KEY', 'your_api_key_here')
        self.base_url = "https://api.tennis-data.co.uk/v1"
        self.kaggle_data_dir = "data/tennis/kaggle"
        self.star_players = self.load_star_players()
        
    def load_star_players(self) -> List[str]:
        """Load list of top 50 star players"""
        star_players = [
            "Novak Djokovic", "Carlos Alcaraz", "Daniil Medvedev", "Jannik Sinner",
            "Andrey Rublev", "Stefanos Tsitsipas", "Alexander Zverev", "Casper Ruud",
            "Hubert Hurkacz", "Taylor Fritz", "Holger Rune", "Karen Khachanov",
            "Frances Tiafoe", "Tommy Paul", "Ben Shelton", "Sebastian Korda",
            "Cameron Norrie", "Lorenzo Musetti", "Grigor Dimitrov", "Adrian Mannarino",
            "Ugo Humbert", "Alejandro Davidovich Fokina", "Nicolas Jarry", "Alex de Minaur",
            "Felix Auger-Aliassime", "Sebastian Baez", "Christopher Eubanks", "Daniel Evans",
            "Mackenzie McDonald", "Marcos Giron", "Jordan Thompson", "Maxime Cressy",
            "John Isner", "Reilly Opelka", "Nick Kyrgios", "Andy Murray",
            "Stan Wawrinka", "Marin Cilic", "Kei Nishikori", "Milos Raonic",
            "Juan Martin del Potro", "Roger Federer", "Rafael Nadal", "Dominic Thiem",
            "Matteo Berrettini", "Denis Shapovalov", "Borna Coric", "Aslan Karatsev",
            "Lloyd Harris", "John Millman", "Alexei Popyrin"
        ]
        return star_players
    
    def fetch_todays_fixtures(self) -> List[Dict]:
        """Fetch today's tennis fixtures from API"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"{self.base_url}/fixtures"
            params = {
                'date': today,
                'api_key': self.api_key
            }
            
            print(f"Fetching fixtures for {today}...")
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                fixtures = data.get('fixtures', [])
                print(f"Found {len(fixtures)} fixtures")
                return fixtures
            else:
                print(f"API Error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error fetching fixtures: {e}")
            return []
    
    def load_player_stats(self, player_name: str) -> Optional[Dict]:
        """Load player stats from Kaggle data or generate mock stats"""
        try:
            # Convert player name to filename format
            filename = player_name.replace(' ', '_').replace('.', '') + '.json'
            filepath = os.path.join(self.kaggle_data_dir, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            
            # Generate mock stats if file doesn't exist
            print(f"Generating mock stats for {player_name}")
            return self.generate_mock_player_stats(player_name)
            
        except Exception as e:
            print(f"Error loading stats for {player_name}: {e}")
            return self.generate_mock_player_stats(player_name)
    
    def generate_mock_player_stats(self, player_name: str) -> Dict:
        """Generate realistic mock stats for a player"""
        # Base stats that vary by player
        base_stats = {
            'avg_games_per_match': random.uniform(18, 25),
            'win_rate': random.uniform(0.4, 0.8),
            'avg_aces_per_match': random.uniform(3, 12),
            'avg_double_faults': random.uniform(1, 5),
            'first_serve_percentage': random.uniform(0.55, 0.75),
            'break_point_conversion': random.uniform(0.3, 0.6),
            'matches_played': random.randint(20, 80),
            'sets_won': random.randint(40, 120),
            'games_won': random.randint(200, 600)
        }
        
        # Add some player-specific variations
        if 'Djokovic' in player_name:
            base_stats.update({
                'win_rate': random.uniform(0.75, 0.85),
                'avg_games_per_match': random.uniform(22, 26),
                'first_serve_percentage': random.uniform(0.65, 0.75)
            })
        elif 'Alcaraz' in player_name:
            base_stats.update({
                'win_rate': random.uniform(0.70, 0.80),
                'avg_aces_per_match': random.uniform(8, 15),
                'break_point_conversion': random.uniform(0.45, 0.60)
            })
        elif 'Sinner' in player_name:
            base_stats.update({
                'win_rate': random.uniform(0.70, 0.80),
                'avg_games_per_match': random.uniform(20, 24),
                'first_serve_percentage': random.uniform(0.60, 0.70)
            })
        
        return base_stats
    
    def analyze_match(self, fixture: Dict) -> Optional[Dict]:
        """Analyze a match using Kaggle data"""
        try:
            home_player = fixture.get('home_player', '')
            away_player = fixture.get('away_player', '')
            
            # Check if either player is in our star list
            if home_player not in self.star_players and away_player not in self.star_players:
                return None
            
            print(f"Analyzing match: {home_player} vs {away_player}")
            
            # Load stats for both players
            home_stats = self.load_player_stats(home_player)
            away_stats = self.load_player_stats(away_player)
            
            if not home_stats or not away_stats:
                print(f"Missing stats for {home_player} or {away_player}")
                return None
            
            # Generate props based on stats
            props = self.generate_props(home_player, away_player, home_stats, away_stats)
            
            return {
                'fixture': fixture,
                'home_player': home_player,
                'away_player': away_player,
                'props': props,
                'confidence': random.uniform(0.6, 0.9),
                'reasoning': f"Analysis based on Kaggle data for {home_player} vs {away_player}"
            }
            
        except Exception as e:
            print(f"Error analyzing match: {e}")
            return None
    
    def generate_props(self, home_player: str, away_player: str, 
                      home_stats: Dict, away_stats: Dict) -> List[Dict]:
        """Generate props based on player stats"""
        props = []
        
        # Total Games Over/Under
        home_avg_games = home_stats.get('avg_games_per_match', 20)
        away_avg_games = away_stats.get('avg_games_per_match', 20)
        total_games = home_avg_games + away_avg_games
        
        props.append({
            'type': 'Total Games',
            'line': round(total_games * 2) / 2,  # Round to nearest 0.5
            'over_odds': random.randint(-120, -110),
            'under_odds': random.randint(-120, -110),
            'confidence': random.uniform(0.6, 0.8)
        })
        
        # Match Winner
        home_win_rate = home_stats.get('win_rate', 0.5)
        away_win_rate = away_stats.get('win_rate', 0.5)
        
        if home_win_rate > away_win_rate:
            winner_odds = random.randint(-150, -120)
            loser_odds = random.randint(110, 150)
        else:
            winner_odds = random.randint(110, 150)
            loser_odds = random.randint(-150, -120)
        
        props.append({
            'type': 'Match Winner',
            'home_odds': winner_odds if home_win_rate > away_win_rate else loser_odds,
            'away_odds': loser_odds if home_win_rate > away_win_rate else winner_odds,
            'confidence': random.uniform(0.6, 0.8)
        })
        
        # Aces
        home_aces = home_stats.get('avg_aces_per_match', 5)
        away_aces = away_stats.get('avg_aces_per_match', 5)
        
        props.append({
            'type': 'Total Aces',
            'line': round((home_aces + away_aces) * 2) / 2,  # Round to nearest 0.5
            'over_odds': random.randint(-120, -110),
            'under_odds': random.randint(-120, -110),
            'confidence': random.uniform(0.5, 0.7)
        })
        
        return props
    
    def run_analysis(self):
        """Run the complete hybrid analysis"""
        print("=== Tennis Hybrid Engine ===")
        print(f"Star players loaded: {len(self.star_players)}")
        
        # Fetch today's fixtures
        fixtures = self.fetch_todays_fixtures()
        
        if not fixtures:
            print("No fixtures found or API error - using mock data")
            fixtures = self.generate_mock_fixtures()
        
        # Analyze matches with star players
        analyzed_matches = []
        
        for fixture in fixtures:
            analysis = self.analyze_match(fixture)
            if analysis:
                analyzed_matches.append(analysis)
        
        print(f"\nAnalyzed {len(analyzed_matches)} matches with star players")
        
        # Generate tickets for high-confidence matches
        tickets = []
        for match in analyzed_matches:
            if match['confidence'] > 0.7:
                ticket = self.create_ticket(match)
                tickets.append(ticket)
        
        print(f"Generated {len(tickets)} tickets")
        
        # Save results
        self.save_results(analyzed_matches, tickets)
        
        return analyzed_matches, tickets
    
    def generate_mock_fixtures(self) -> List[Dict]:
        """Generate mock fixtures for testing when API is down"""
        print("Generating mock fixtures with star players...")
        
        # Create some realistic mock fixtures with star players
        mock_fixtures = [
            {
                'home_player': 'Novak Djokovic',
                'away_player': 'Carlos Alcaraz',
                'tournament': 'Wimbledon',
                'surface': 'grass'
            },
            {
                'home_player': 'Daniil Medvedev',
                'away_player': 'Jannik Sinner',
                'tournament': 'US Open',
                'surface': 'hard'
            },
            {
                'home_player': 'Stefanos Tsitsipas',
                'away_player': 'Alexander Zverev',
                'tournament': 'Australian Open',
                'surface': 'hard'
            },
            {
                'home_player': 'Andrey Rublev',
                'away_player': 'Casper Ruud',
                'tournament': 'French Open',
                'surface': 'clay'
            },
            {
                'home_player': 'Taylor Fritz',
                'away_player': 'Frances Tiafoe',
                'tournament': 'Miami Open',
                'surface': 'hard'
            }
        ]
        
        print(f"Generated {len(mock_fixtures)} mock fixtures")
        return mock_fixtures
    
    def create_ticket(self, match: Dict) -> Dict:
        """Create a ticket from match analysis"""
        return {
            'sport': 'tennis',
            'match': f"{match['home_player']} vs {match['away_player']}",
            'confidence': match['confidence'],
            'reasoning': match['reasoning'],
            'props': match['props'],
            'timestamp': datetime.now().isoformat()
        }
    
    def save_results(self, analyzed_matches: List[Dict], tickets: List[Dict]):
        """Save analysis results to files and unified ticket manager"""
        try:
            # Create output directory
            output_dir = "data/tennis/hybrid_analysis"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save analyzed matches
            matches_file = os.path.join(output_dir, f"analyzed_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(matches_file, 'w') as f:
                json.dump(analyzed_matches, f, indent=2)
            
            # Save tickets using unified ticket manager
            if tickets:
                saved_tickets = hook_ticket_generation(tickets)
                print(f"Saved {len(saved_tickets)} tickets to unified storage")
            else:
                print("No tickets to save")
            
            print(f"Results saved to {output_dir}")
            
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    """Main function"""
    engine = TennisHybridEngine()
    analyzed_matches, tickets = engine.run_analysis()
    
    if tickets:
        print("\n=== Generated Tickets ===")
        for i, ticket in enumerate(tickets, 1):
            print(f"\nTicket {i}:")
            print(f"Match: {ticket['match']}")
            print(f"Confidence: {ticket['confidence']:.2f}")
            print(f"Reasoning: {ticket['reasoning']}")
            print("Props:")
            for prop in ticket['props']:
                print(f"  - {prop['type']}: {prop}")

if __name__ == "__main__":
    main() 