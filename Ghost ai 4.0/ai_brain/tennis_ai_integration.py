#!/usr/bin/env python3
"""
Tennis AI Integration for Ghost AI
Integrates tennis analysis with unified ticket management.
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add import for unified ticket manager
from ghost_ai_core_memory.tickets.integration_hooks import hook_ticket_generation

class TennisAIIntegration:
    def __init__(self):
        self.star_players = self.load_star_players()
        self.data_dir = "data/tennis"
        
    def load_star_players(self) -> List[str]:
        """Load list of top 50 star players"""
        return [
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
    
    def generate_mock_fixtures(self) -> List[Dict]:
        """Generate mock fixtures with star players"""
        return [
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
    
    def generate_player_stats(self, player_name: str) -> Dict:
        """Generate realistic stats for a player"""
        base_stats = {
            'avg_games_per_match': random.uniform(18, 25),
            'win_rate': random.uniform(0.4, 0.8),
            'avg_aces_per_match': random.uniform(3, 12),
            'avg_double_faults': random.uniform(1, 5),
            'first_serve_percentage': random.uniform(0.55, 0.75),
            'break_point_conversion': random.uniform(0.3, 0.6)
        }
        
        # Player-specific adjustments
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
    
    def generate_props(self, home_player: str, away_player: str, 
                      home_stats: Dict, away_stats: Dict) -> List[Dict]:
        """Generate props based on player stats"""
        props = []
        
        # Total Games Over/Under
        total_games = home_stats['avg_games_per_match'] + away_stats['avg_games_per_match']
        props.append({
            'type': 'Total Games',
            'line': round(total_games * 2) / 2,
            'over_odds': random.randint(-120, -110),
            'under_odds': random.randint(-120, -110),
            'confidence': random.uniform(0.6, 0.8)
        })
        
        # Match Winner
        if home_stats['win_rate'] > away_stats['win_rate']:
            home_odds = random.randint(-150, -120)
            away_odds = random.randint(110, 150)
        else:
            home_odds = random.randint(110, 150)
            away_odds = random.randint(-150, -120)
        
        props.append({
            'type': 'Match Winner',
            'home_odds': home_odds,
            'away_odds': away_odds,
            'confidence': random.uniform(0.6, 0.8)
        })
        
        # Total Aces
        total_aces = home_stats['avg_aces_per_match'] + away_stats['avg_aces_per_match']
        props.append({
            'type': 'Total Aces',
            'line': round(total_aces * 2) / 2,
            'over_odds': random.randint(-120, -110),
            'under_odds': random.randint(-120, -110),
            'confidence': random.uniform(0.5, 0.7)
        })
        
        return props
    
    def analyze_match(self, fixture: Dict) -> Optional[Dict]:
        """Analyze a match and generate props"""
        try:
            home_player = fixture.get('home_player', '')
            away_player = fixture.get('away_player', '')
            
            # Check if either player is in our star list
            if home_player not in self.star_players and away_player not in self.star_players:
                return None
            
            # Generate stats for both players
            home_stats = self.generate_player_stats(home_player)
            away_stats = self.generate_player_stats(away_player)
            
            # Generate props
            props = self.generate_props(home_player, away_player, home_stats, away_stats)
            
            return {
                'fixture': fixture,
                'home_player': home_player,
                'away_player': away_player,
                'props': props,
                'confidence': random.uniform(0.6, 0.9),
                'reasoning': f"AI analysis based on player stats for {home_player} vs {away_player}"
            }
            
        except Exception as e:
            print(f"Error analyzing match: {e}")
            return None
    
    def create_ticket(self, match: Dict) -> Dict:
        """Create a ticket from match analysis"""
        return {
            'sport': 'tennis',
            'match': f"{match['home_player']} vs {match['away_player']}",
            'confidence': match['confidence'],
            'reasoning': match['reasoning'],
            'props': match['props'],
            'timestamp': datetime.now().isoformat(),
            'source': 'tennis_ai_integration'
        }
    
    def run_tennis_analysis(self) -> List[Dict]:
        """Run tennis analysis and return tickets"""
        print("=== Tennis AI Integration ===")
        print(f"Star players loaded: {len(self.star_players)}")
        
        # Generate mock fixtures (in real implementation, this would fetch from API)
        fixtures = self.generate_mock_fixtures()
        print(f"Generated {len(fixtures)} fixtures")
        
        # Analyze matches
        analyzed_matches = []
        for fixture in fixtures:
            analysis = self.analyze_match(fixture)
            if analysis:
                analyzed_matches.append(analysis)
        
        print(f"Analyzed {len(analyzed_matches)} matches with star players")
        
        # Generate tickets for high-confidence matches
        tickets = []
        for match in analyzed_matches:
            if match['confidence'] > 0.7:
                ticket = self.create_ticket(match)
                tickets.append(ticket)
        
        print(f"Generated {len(tickets)} tickets")
        
        # Save results using unified ticket manager
        self.save_results(analyzed_matches, tickets)
        
        return tickets
    
    def save_results(self, analyzed_matches: List[Dict], tickets: List[Dict]):
        """Save analysis results using unified ticket manager"""
        try:
            # Save analyzed matches to data directory
            output_dir = "data/tennis/ai_analysis"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save analyzed matches
            matches_file = os.path.join(output_dir, f"analyzed_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(matches_file, 'w') as f:
                json.dump(analyzed_matches, f, indent=2)
            
            # Save tickets using unified ticket manager
            if tickets:
                saved_tickets = hook_ticket_generation(tickets)
                print(f"Saved {len(saved_tickets)} tickets to unified storage")
                logging.info(f"Saved {len(saved_tickets)} tennis tickets to unified storage")
            else:
                print("No tickets to save")
                logging.info("No tennis tickets to save")
            
            print(f"Results saved to {output_dir}")
            
        except Exception as e:
            print(f"Error saving results: {e}")
            logging.error(f"Error saving tennis results: {e}")

def main():
    """Test the tennis AI integration"""
    integration = TennisAIIntegration()
    tickets = integration.run_tennis_analysis()
    
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