import os
import asyncio
import json
from pathlib import Path
from datetime import datetime
from core.data.data_fetcher import DataFetcher

MLB_KEY = 'baseball_mlb'
WNBA_KEY = 'basketball_wnba'

MLB_PROP_MARKETS = ','.join([
    'batter_home_runs', 'batter_hits', 'batter_total_bases', 'batter_rbis', 'batter_runs_scored',
    'batter_hits_runs_rbis', 'batter_singles', 'batter_doubles', 'batter_triples', 'batter_walks',
    'batter_strikeouts', 'batter_stolen_bases', 'pitcher_strikeouts', 'pitcher_record_a_win',
    'pitcher_hits_allowed', 'pitcher_walks', 'pitcher_earned_runs', 'pitcher_outs'
])
WNBA_PROP_MARKETS = ','.join([
    'player_points', 'player_rebounds', 'player_assists', 'player_threes', 'player_blocks',
    'player_steals', 'player_blocks_steals', 'player_turnovers', 'player_points_rebounds_assists',
    'player_points_rebounds', 'player_points_assists', 'player_rebounds_assists'
])

OUTPUT_DIR = Path("test_full_props_output")
OUTPUT_DIR.mkdir(exist_ok=True)

def normalize_team_name(name):
    return name.lower().replace(' ', '_').replace('/', '_')

async def fetch_and_save_props(sport_key, prop_markets, label):
    today = datetime.now().strftime('%Y-%m-%d')
    saved = 0
    async with DataFetcher() as fetcher:
        games = await fetcher.get_odds(sport=sport_key, regions='us', markets='h2h,spreads,totals', date=today)
        if not games:
            print(f"No {label} games found for today.")
            return 0
        for game in games:
            game_id = game.get('id')
            home_team = game.get('home_team', 'home')
            away_team = game.get('away_team', 'away')
            if not game_id:
                continue
            try:
                props = await fetcher.get_player_props(sport_key, game_id, prop_markets=prop_markets)
                if props:
                    matchup_file = OUTPUT_DIR / f"{label}_{normalize_team_name(home_team)}_vs_{normalize_team_name(away_team)}_{today}.json"
                    with open(matchup_file, "w", encoding="utf-8") as f:
                        json.dump(props, f, indent=2)
                    saved += 1
            except Exception as e:
                print(f"Error fetching props for {label} game {home_team} vs {away_team}: {e}")
    print(f"Saved {saved} {label} prop files to {OUTPUT_DIR}")
    return saved

async def main():
    mlb_count = await fetch_and_save_props(MLB_KEY, MLB_PROP_MARKETS, "MLB")
    wnba_count = await fetch_and_save_props(WNBA_KEY, WNBA_PROP_MARKETS, "WNBA")
    print(f"\nSummary: {mlb_count} MLB games, {wnba_count} WNBA games saved.")

if __name__ == "__main__":
    asyncio.run(main()) 