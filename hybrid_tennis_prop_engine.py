#!/usr/bin/env python3
"""
Hybrid Tennis Prop Engine for Ghost AI 4.0
Combines Tennis API (for fixtures) and Kaggle data (for stats/analysis)
Generates prop picks for each match with full reasoning, but only for matches involving top 50 star players (ATP or WTA).
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import sys

# --- Import local Kaggle prop generator ---
from tennis_prop_generator import TennisPropGenerator

# --- Import tennis API client (assume get_fixtures is available) ---
try:
    from core.tennis_api_client import get_fixtures
except ImportError:
    # Fallback: try local ai_brain/tennis_ai_fixtures_test.py for get_fixtures
    from ai_brain.tennis_ai_fixtures_test import get_fixtures

logger = logging.getLogger('hybrid_tennis_prop_engine')

def normalize_name(name):
    """Normalize player names for matching."""
    return name.replace(' ', '').replace('.', '').replace("'", '').lower()

def find_kaggle_player(player_name, kaggle_players):
    """Find the best match for a player in Kaggle data."""
    norm = normalize_name(player_name)
    for k in kaggle_players:
        if norm in normalize_name(k) or normalize_name(k) in norm:
            return k
    return None

def load_star_players():
    """Load ATP and WTA top 50 star players from tennis_star_players_*.json."""
    import glob
    star_players = set()
    for fname in glob.glob("tennis_star_players_*.json"):
        with open(fname, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                for k, v in data.items():
                    if isinstance(v, list):
                        star_players.update(v)
            elif isinstance(data, list):
                star_players.update(data)
    return set([s.replace("'", "").replace(".", "").replace(" ", "").lower() for s in star_players])

def analyze_match(player1, player2, generator):
    """Analyze a match using Kaggle data and generate prop picks."""
    # Try to generate props for this matchup
    props = generator.generate_match_props(player1, player2)
    if not props:
        return {
            'match': f'{player1} vs {player2}',
            'error': 'No sufficient data for this matchup.'
        }
    # Pick the best prop (highest confidence)
    best_prop = max(props, key=lambda p: p.get('confidence', 0.0))
    return {
        'match': f'{player1} vs {player2}',
        'best_prop': best_prop,
        'all_props': props
    }

def main():
    print("🎾 Hybrid Tennis Prop Engine (API + Kaggle)")
    print("=" * 60)
    generator = TennisPropGenerator()
    kaggle_players = list(generator.players_data.keys())
    star_players = load_star_players()
    print(f"Loaded {len(star_players)} star players (ATP+WTA)")
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"Fetching today's matches from API for {today}...")
    try:
        fixtures = get_fixtures(today)
    except Exception as e:
        print(f"❌ Failed to fetch fixtures: {e}")
        return
    if not fixtures:
        print("No matches found for today.")
        return
    print(f"Found {len(fixtures)} matches.")
    results = []
    for match in fixtures:
        p1 = match.get('event_first_player')
        p2 = match.get('event_second_player')
        if not p1 or not p2:
            continue
        # Only analyze if at least one player is a star
        norm_p1 = normalize_name(p1)
        norm_p2 = normalize_name(p2)
        if norm_p1 not in star_players and norm_p2 not in star_players:
            print(f"Skipping: {p1} vs {p2} (neither is a top 50 star)")
            continue
        kaggle_p1 = find_kaggle_player(p1, kaggle_players)
        kaggle_p2 = find_kaggle_player(p2, kaggle_players)
        print(f"\nAnalyzing: {p1} vs {p2}")
        if not kaggle_p1 or not kaggle_p2:
            print(f"  ⚠️  Could not match both players in Kaggle data: {p1}={kaggle_p1}, {p2}={kaggle_p2}")
            results.append({'match': f'{p1} vs {p2}', 'error': 'Player(s) not found in Kaggle data.'})
            continue
        analysis = analyze_match(kaggle_p1, kaggle_p2, generator)
        results.append(analysis)
        if 'best_prop' in analysis:
            bp = analysis['best_prop']
            print(f"  ✅ Best Prop: {bp['prop']} | Line: {bp['line']} | Pick: {bp['pick']} | Confidence: {bp['confidence']}\n    Reasoning: {bp['reasoning']}")
        else:
            print(f"  ⚠️  {analysis.get('error')}")
    # Save results
    out_path = Path('data/tennis_kaggle/hybrid_prop_results_' + today + '.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to {out_path.resolve()}")
    print("\n🎾 Hybrid Tennis Prop Engine complete!")

if __name__ == "__main__":
    main() 