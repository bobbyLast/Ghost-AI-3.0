import os
import requests
from dotenv import load_dotenv

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
MLB_KEY = 'baseball_mlb'

# Step 1: Get all MLB games
def get_games():
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "h2h"
    }
    resp = requests.get(f"{ODDS_API_BASE_URL}/sports/baseball_mlb/odds", params=params)
    resp.raise_for_status()
    return resp.json()

# Step 2: For a game, get player props via per-event endpoint
def get_player_props(game_id):
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": "batter_home_runs"  # Use a common MLB player prop market
    }
    url = f"{ODDS_API_BASE_URL}/sports/{MLB_KEY}/events/{game_id}/odds"
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

# Step 3: Print all books for player props for the game
def print_player_prop_books(props, home_team, away_team):
    print(f"\nPlayer Props for: {home_team} vs {away_team}")
    if not props or 'bookmakers' not in props:
        print("  No sportsbooks found for player props.")
        return
    for bookmaker in props['bookmakers']:
        print(f"  Book: {bookmaker['title']} ({bookmaker['key']})")
        for market in bookmaker.get('markets', []):
            print(f"    Market: {market['key']}")

games = get_games()
if games:
    game = games[0]
    props = get_player_props(game['id'])
    print_player_prop_books(props, game.get('home_team', 'Unknown'), game.get('away_team', 'Unknown'))
else:
    print("No MLB games found.") 