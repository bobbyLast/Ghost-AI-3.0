#!/usr/bin/env python3
"""
Simple Tennis Test - Quick test of tennis analysis
"""

import os
import json
import random
from datetime import datetime
from typing import Dict, List
# Add import for unified ticket manager
from ghost_ai_core_memory.tickets.integration_hooks import hook_ticket_generation

def generate_mock_fixtures():
    """Generate mock fixtures with star players"""
    return [
        {
            'home_player': 'Novak Djokovic',
            'away_player': 'Carlos Alcaraz',
            'tournament': 'Wimbledon'
        },
        {
            'home_player': 'Daniil Medvedev',
            'away_player': 'Jannik Sinner',
            'tournament': 'US Open'
        },
        {
            'home_player': 'Taylor Fritz',
            'away_player': 'Frances Tiafoe',
            'tournament': 'Miami Open'
        }
    ]

def generate_mock_stats(player_name: str) -> Dict:
    """Generate mock stats for a player"""
    base_stats = {
        'avg_games_per_match': random.uniform(18, 25),
        'win_rate': random.uniform(0.4, 0.8),
        'avg_aces_per_match': random.uniform(3, 12)
    }
    
    # Player-specific adjustments
    if 'Djokovic' in player_name:
        base_stats['win_rate'] = random.uniform(0.75, 0.85)
    elif 'Alcaraz' in player_name:
        base_stats['win_rate'] = random.uniform(0.70, 0.80)
    
    return base_stats

def generate_props(home_player: str, away_player: str, 
                  home_stats: Dict, away_stats: Dict) -> List[Dict]:
    """Generate props based on player stats"""
    props = []
    
    # Total Games
    total_games = home_stats['avg_games_per_match'] + away_stats['avg_games_per_match']
    props.append({
        'type': 'Total Games',
        'line': round(total_games * 2) / 2,
        'over_odds': random.randint(-120, -110),
        'under_odds': random.randint(-120, -110)
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
        'away_odds': away_odds
    })
    
    return props

def create_ticket(match_data: Dict) -> Dict:
    """Create a ticket from match data"""
    return {
        'sport': 'tennis',
        'match': f"{match_data['home_player']} vs {match_data['away_player']}",
        'confidence': random.uniform(0.7, 0.9),
        'reasoning': f"Analysis based on player stats",
        'props': match_data['props'],
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Main function"""
    print("=== Simple Tennis Test ===")
    
    # Generate mock fixtures
    fixtures = generate_mock_fixtures()
    print(f"Generated {len(fixtures)} mock fixtures")
    
    # Analyze matches
    tickets = []
    
    for fixture in fixtures:
        print(f"\nAnalyzing: {fixture['home_player']} vs {fixture['away_player']}")
        
        # Generate stats
        home_stats = generate_mock_stats(fixture['home_player'])
        away_stats = generate_mock_stats(fixture['away_player'])
        
        # Generate props
        props = generate_props(fixture['home_player'], fixture['away_player'], 
                             home_stats, away_stats)
        
        # Create match data
        match_data = {
            'home_player': fixture['home_player'],
            'away_player': fixture['away_player'],
            'props': props
        }
        
        # Create ticket
        ticket = create_ticket(match_data)
        tickets.append(ticket)
        
        print(f"  Generated {len(props)} props")
    
    # Display results
    print(f"\n=== Generated {len(tickets)} Tickets ===")
    
    for i, ticket in enumerate(tickets, 1):
        print(f"\nTicket {i}:")
        print(f"Match: {ticket['match']}")
        print(f"Confidence: {ticket['confidence']:.2f}")
        print("Props:")
        for prop in ticket['props']:
            if prop['type'] == 'Total Games':
                print(f"  - {prop['type']}: {prop['line']} (O: {prop['over_odds']}, U: {prop['under_odds']})")
            else:
                print(f"  - {prop['type']}: {prop['home_odds']} / {prop['away_odds']}")
    
    # Save results
    try:
        # Save tickets using unified ticket manager
        if tickets:
            saved_tickets = hook_ticket_generation(tickets)
            print(f"Saved {len(saved_tickets)} tickets to unified storage")
        else:
            print("No tickets to save")
    except Exception as e:
        print(f"Error saving results: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main() 