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
        print(f"\nChecking available markets for {bookmaker_name} ({sport_name})...")
        API_URL = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/"
        params = {
            'regions': 'us_dfs',
            'bookmakers': bookmaker_key,
            'apiKey': API_KEY,
            'oddsFormat': 'american',
            'dateFormat': 'iso',
        }
        try:
            response = requests.get(API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            market_keys = set()
            for game in data:
                for bookmaker in game.get('bookmakers', []):
                    for market in bookmaker.get('markets', []):
                        market_keys.add(market.get('key'))
            if market_keys:
                print(f"Markets found for {bookmaker_name} {sport_name}: {sorted(market_keys)}")
            else:
                print(f"No markets found for {bookmaker_name} {sport_name}. (No games or props today?)")
        except Exception as e:
            print(f"❌ API test failed for {bookmaker_name} {sport_name}: {e}") 