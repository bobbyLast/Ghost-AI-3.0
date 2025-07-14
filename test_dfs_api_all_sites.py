import os
from dotenv import load_dotenv
import requests

# Load API key from .env
load_dotenv()
API_KEY = os.getenv('ODDS_API_KEY')

sports = [
    ('baseball_mlb', 'MLB'),
    ('basketball_wnba', 'WNBA')
]
bookmakers = [
    ('prizepicks', 'PrizePicks'),
    ('pick6', 'DraftKings Pick6'),
    ('underdog', 'Underdog Fantasy')
]

for sport_key, sport_name in sports:
    for bookmaker_key, bookmaker_name in bookmakers:
        print(f"\nTesting {bookmaker_name} player props for {sport_name}...")
        API_URL = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        params = {
            'regions': 'us_dfs',
            'bookmakers': bookmaker_key,
            'markets': 'player_props',
            'apiKey': API_KEY,
            'oddsFormat': 'american',
            'dateFormat': 'iso',
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if not data:
                print(f"No data returned for {bookmaker_name} {sport_name}. Check if there are games today or if the API key is correct.")
            else:
                print(f"Found {len(data)} games with player props on {bookmaker_name}:")
                for game in data[:3]:  # Print first 3 games
                    print(f"  Game: {game.get('home_team')} vs {game.get('away_team')}")
                    for bookmaker in game.get('bookmakers', []):
                        print(f"    Bookmaker: {bookmaker.get('title')}")
                        for market in bookmaker.get('markets', []):
                            print(f"      Market: {market.get('key')}")
                            for outcome in market.get('outcomes', []):
                                print(f"        Player: {outcome.get('description', outcome.get('name'))}, Line: {outcome.get('point')}, Odds: {outcome.get('price')}")
        except Exception as e:
            print(f"❌ API test failed for {bookmaker_name} {sport_name}: {e}") 