import os
from dotenv import load_dotenv
import requests

# Load API key from .env if needed
load_dotenv()
API_KEY = os.getenv('ODDS_API_KEY')  # Change to your actual env var if different

# API endpoint and parameters
API_URL = "https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/"
params = {
    'regions': 'us_dfs',
    'bookmakers': 'prizepicks',
    'markets': 'player_props',
    'apiKey': API_KEY,
    'oddsFormat': 'american',
    'dateFormat': 'iso',
}

print("Testing DFS API PrizePicks player props...")
try:
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()
    if not data:
        print("No data returned. Check if there are games today or if the API key is correct.")
    else:
        print(f"Found {len(data)} games with player props on PrizePicks:")
        for game in data[:3]:  # Print first 3 games
            print(f"Game: {game.get('home_team')} vs {game.get('away_team')}")
            for bookmaker in game.get('bookmakers', []):
                print(f"  Bookmaker: {bookmaker.get('title')}")
                for market in bookmaker.get('markets', []):
                    print(f"    Market: {market.get('key')}")
                    for outcome in market.get('outcomes', []):
                        print(f"      Player: {outcome.get('description', outcome.get('name'))}, Line: {outcome.get('point')}, Odds: {outcome.get('price')}")
except Exception as e:
    print(f"❌ API test failed: {e}") 