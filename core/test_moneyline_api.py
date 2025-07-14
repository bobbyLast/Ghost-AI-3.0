import os
import requests
from dotenv import load_dotenv

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
MLB_KEY = 'baseball_mlb'
WNBA_KEY = 'basketball_wnba'

if not ODDS_API_KEY:
    print('No ODDS_API_KEY found in .env!')
    exit(1)

params = {
    "apiKey": ODDS_API_KEY,
    "regions": "us",
    "markets": "h2h",
    "oddsFormat": "american"
}

def print_moneyline_odds(sport_key, sport_name):
    url = f"{ODDS_API_BASE_URL}/sports/{sport_key}/odds"
    print(f"\nRequesting: {url} [{sport_name}]\n")
    try:
        resp = requests.get(url, params=params)
        print(f"Status code: {resp.status_code}")
        resp.raise_for_status()
        data = resp.json()
        print(f"Number of games returned: {len(data)}")
        if data:
            for game in data[:3]:  # Print first 3 games for brevity
                print(f"Game: {game.get('away_team')} @ {game.get('home_team')}")
                for book in game.get('bookmakers', []):
                    print(f"  Sportsbook: {book.get('title')} ({book.get('key')})")
                    for market in book.get('markets', []):
                        if market.get('key') == 'h2h':
                            for outcome in market.get('outcomes', []):
                                print(f"    {outcome.get('name')}: {outcome.get('price')}")
        else:
            print("No games returned.")
    except Exception as e:
        print(f"Error fetching moneyline odds for {sport_name}: {e}")

print_moneyline_odds(MLB_KEY, "MLB")
print_moneyline_odds(WNBA_KEY, "WNBA") 