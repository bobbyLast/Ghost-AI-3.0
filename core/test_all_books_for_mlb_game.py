import os
import requests
from dotenv import load_dotenv

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
MLB_KEY = 'baseball_mlb'

def get_games(markets):
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": markets
    }
    resp = requests.get(f"{ODDS_API_BASE_URL}/sports/baseball_mlb/odds", params=params)
    resp.raise_for_status()
    return resp.json()

def print_books_for_all_markets(game, label):
    print(f"\n[{label}] Game: {game['home_team']} vs {game['away_team']}")
    for bookmaker in game.get('bookmakers', []):
        print(f"  Book: {bookmaker['title']} ({bookmaker['key']})")
        for market in bookmaker.get('markets', []):
            print(f"    Market: {market['key']}")

# Main lines
try:
    games_main = get_games("h2h,spreads,totals")
    if games_main:
        print_books_for_all_markets(games_main[0], "Main Lines (h2h,spreads,totals)")
    else:
        print("No MLB games found for main lines.")
except Exception as e:
    print(f"Error fetching main lines: {e}")

# Player props
try:
    games_props = get_games("player_props")
    if games_props:
        print_books_for_all_markets(games_props[0], "Player Props")
    else:
        print("No MLB games found for player props.")
except Exception as e:
    print(f"Error fetching player props: {e}") 