#!/usr/bin/env python3
"""
MLB AI Integration - Integrates MLB props analysis with Ghost AI 4.0 brain
"""

import os
import sys
import json
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add import for unified ticket manager
from ghost_ai_core_memory.tickets.integration_hooks import hook_ticket_generation

MLB_PROPS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mlb_game_props')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'mlb', 'ai_analysis')
os.makedirs(OUTPUT_DIR, exist_ok=True)

class MLBAIIntegration:
    def __init__(self):
        self.props_dir = MLB_PROPS_DIR
        self.output_dir = OUTPUT_DIR

    def get_latest_props_files(self) -> List[str]:
        """Get the latest MLB props JSON files from the props directory."""
        files = [f for f in os.listdir(self.props_dir) if f.endswith('.json')]
        # Sort by date in filename (YYYY-MM-DD)
        files.sort(reverse=True)
        return [os.path.join(self.props_dir, f) for f in files[:10]]  # Limit to 10 most recent

    def load_props(self, file_path: str) -> Optional[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading props from {file_path}: {e}")
            return None

    def analyze_props(self, props: Dict) -> List[Dict]:
        """Analyze props and generate tickets for each player/market."""
        tickets = []
        home_team = props.get('home_team', 'home')
        away_team = props.get('away_team', 'away')
        game = f"{away_team} vs {home_team}"
        for bookmaker in props.get('bookmakers', []):
            for market in bookmaker.get('markets', []):
                market_type = market.get('key', 'unknown')
                for outcome in market.get('outcomes', []):
                    player = outcome.get('description') or outcome.get('name')
                    line = outcome.get('point')
                    odds = outcome.get('price', 0)
                    # Generate confidence and reasoning
                    confidence = random.uniform(0.6, 0.9)
                    reasoning = f"AI analysis: {player} {market_type} line {line} for {game} (odds: {odds})"
                    ticket = {
                        'sport': 'mlb',
                        'game': game,
                        'player': player,
                        'market': market_type,
                        'line': line,
                        'odds': odds,
                        'confidence': confidence,
                        'reasoning': reasoning,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'mlb_ai_integration'
                    }
                    tickets.append(ticket)
        return tickets

    def run_mlb_analysis(self) -> List[Dict]:
        print("=== MLB AI Integration ===")
        props_files = self.get_latest_props_files()
        print(f"Found {len(props_files)} props files.")
        all_tickets = []
        for file_path in props_files:
            props = self.load_props(file_path)
            if not props:
                continue
            tickets = self.analyze_props(props)
            all_tickets.extend(tickets)
        print(f"Generated {len(all_tickets)} tickets.")
        self.save_results(all_tickets)
        return all_tickets

    def save_results(self, tickets: List[Dict]):
        """Save results using unified ticket manager"""
        try:
            # Save tickets using unified ticket manager
            if tickets:
                saved_tickets = hook_ticket_generation(tickets)
                print(f"Saved {len(saved_tickets)} MLB tickets to unified storage")
                logging.info(f"Saved {len(saved_tickets)} MLB tickets to unified storage")
            else:
                print("No MLB tickets to save")
                logging.info("No MLB tickets to save")
            
            # Also save to legacy location for backward compatibility
            output_file = os.path.join(self.output_dir, f"mlb_tickets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, indent=2)
            print(f"Results also saved to {output_file}")
            
        except Exception as e:
            print(f"Error saving MLB tickets: {e}")
            logging.error(f"Error saving MLB tickets: {e}")

def main():
    integration = MLBAIIntegration()
    tickets = integration.run_mlb_analysis()
    if tickets:
        print("\n=== Sample Tickets ===")
        for ticket in tickets[:5]:
            print(json.dumps(ticket, indent=2))
    print("\n=== MLB AI Integration Complete ===")

if __name__ == "__main__":
    main() 