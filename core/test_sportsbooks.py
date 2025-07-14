import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
import warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
import sys

load_dotenv()
ODDS_API_KEY = os.getenv('ODDS_API_KEY')
if ODDS_API_KEY:
    print(f"[DEBUG] Script started. ODDS_API_KEY loaded: {ODDS_API_KEY[:3]}...{ODDS_API_KEY[-3:]}")
else:
    print("[ERROR] ODDS_API_KEY is missing! Check your .env file.")
    exit(1)
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
ODDS_API_ODDS = f"{ODDS_API_BASE_URL}/sports/{{sport_key}}/odds"
ODDS_API_EVENT_ODDS = f"{ODDS_API_BASE_URL}/sports/{{sport_key}}/events/{{event_id}}/odds"

MLB_KEY = 'baseball_mlb'
WNBA_KEY = 'basketball_wnba'

MLB_PROP_MARKETS = [
    'batter_home_runs', 'batter_hits', 'batter_total_bases', 'batter_rbis', 'batter_runs_scored',
    'batter_hits_runs_rbis', 'batter_singles', 'batter_doubles', 'batter_triples', 'batter_walks',
    'batter_strikeouts', 'batter_stolen_bases', 'pitcher_strikeouts', 'pitcher_record_a_win',
    'pitcher_hits_allowed', 'pitcher_walks', 'pitcher_earned_runs', 'pitcher_outs'
]
WNBA_PROP_MARKETS = [
    'player_points', 'player_rebounds', 'player_assists', 'player_threes', 'player_blocks',
    'player_steals', 'player_blocks_steals', 'player_turnovers', 'player_points_rebounds_assists',
    'player_points_rebounds', 'player_points_assists', 'player_rebounds_assists'
]

AUDIT_DIR = Path("sportsbook_prop_audit")
AUDIT_DIR.mkdir(exist_ok=True)

TENNIS_API_KEY = os.getenv('TENNIS_API_KEY')
TENNIS_API_HOST = os.getenv('TENNIS_API_HOST', 'tennisapi1.p.rapidapi.com')  # Example for RapidAPI

def fetch_tennisapi_matches():
    print("\n=== TennisAPI1 (RapidAPI/FreeWebAPI) Today's Matches ===")
    if not TENNIS_API_KEY:
        print("[ERROR] TENNIS_API_KEY not set in .env!")
        return
    url = f"https://{TENNIS_API_HOST}/getMatchList"
    today = datetime.now().strftime('%Y-%m-%d')
    headers = {
        "X-RapidAPI-Key": TENNIS_API_KEY,
        "X-RapidAPI-Host": TENNIS_API_HOST
    }
    params = {"date": today}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        matches = resp.json().get('matches', [])
        if not matches:
            print("No tennis matches found today from TennisAPI1.")
            return
        for match in matches[:10]:
            print(f"  {match.get('player1', '')} vs {match.get('player2', '')} @ {match.get('tournament', '')} ({match.get('start_time', '')})")
    except Exception as e:
        print(f"[ERROR] Fetching tennis matches from TennisAPI1: {e}")

def get_games(sport_key, region):
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": region,
        "markets": "h2h,spreads,totals"
    }
    print(f"[DEBUG] Fetching games for {sport_key} in region {region}...")
    try:
        resp = requests.get(ODDS_API_ODDS.format(sport_key=sport_key), params=params, verify=False, timeout=10)
        resp.raise_for_status()
        print(f"[DEBUG] Got games for {sport_key}.")
        return resp.json()
    except Exception as e:
        print(f"[ERROR] Fetching games for {sport_key}: {e}")
        return []

def get_event_player_props(sport_key, event_id, prop_market):
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "us",
        "markets": prop_market
    }
    url = ODDS_API_EVENT_ODDS.format(sport_key=sport_key, event_id=event_id)
    print(f"[DEBUG] Fetching player props for event {event_id} ({sport_key})...")
    try:
        resp = requests.get(url, params=params, verify=False, timeout=10)
        resp.raise_for_status()
        print(f"[DEBUG] Got player props for event {event_id}.")
        return resp.json()
    except Exception as e:
        print(f"[ERROR] Fetching player props for event {event_id}: {e}")
        return None

def audit_props_for_games(sport_key, games, prop_markets, sport_label):
    summary = {}
    for game in games:
        home = game.get('home_team', 'home')
        away = game.get('away_team', 'away')
        game_id = game.get('id')
        matchup = f"{home}_vs_{away}"
        game_result = {}
        for prop_market in prop_markets:
            props = get_event_player_props(sport_key, game_id, prop_market)
            books = set()
            if props and 'bookmakers' in props:
                for book in props['bookmakers']:
                    books.add((book['key'], book['title']))
            game_result[prop_market] = sorted(list(books))
            # Tally for summary
            for key, title in books:
                summary.setdefault(key, {'title': title, 'count': 0})
                summary[key]['count'] += 1
        # Save per-game audit
        out_file = AUDIT_DIR / f"{sport_label}_{matchup}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(game_result, f, indent=2)
        print(f"Saved audit for {sport_label} {matchup}")
    return summary

def print_summary(summary, sport_label):
    print(f"\n=== {sport_label} Sportsbook Prop Coverage Summary ===")
    sorted_books = sorted(summary.items(), key=lambda x: -x[1]['count'])
    for key, info in sorted_books:
        print(f"  {info['title']} ({key}): {info['count']} props offered")

def get_tennis_golf_props(sport_key, prop_markets):
    print(f"\n=== {sport_key.upper()} Player Props ===")
    games = get_games(sport_key, "us") # Default to 'us' for props
    if not games:
        print(f"No games found for {sport_key}")
        return
    for i, game in enumerate(games):
        if i >= 2:
            print(f"[DEBUG] Only fetching first 2 events for {sport_key} (skipping rest).")
            break
        event_id = game.get('id')
        home = game.get('home_team', '')
        away = game.get('away_team', '')
        if not event_id:
            continue
        props = get_event_player_props(sport_key, event_id, prop_markets)
        if not props or 'bookmakers' not in props:
            print(f"  No player props for {home} vs {away}")
            continue
        print(f"\n  {home} vs {away}")
        for bookmaker in props['bookmakers']:
            print(f"    Bookmaker: {bookmaker.get('title')} ({bookmaker.get('key')})")
            for market in bookmaker.get('markets', []):
                print(f"      Market: {market.get('key')}")
                for outcome in market.get('outcomes', []):
                    print(f"        {outcome.get('description') or outcome.get('name')}: {outcome.get('price')} @ {outcome.get('point')}")

def print_tennis_golf_players(sport_key, region):
    print(f"\n=== {sport_key.upper()} Events & Players ===")
    games = get_games(sport_key, region)
    if not games:
        print(f"No games found for {sport_key}")
        return
    for i, game in enumerate(games):
        if i >= 10:
            print(f"[DEBUG] Only showing first 10 events for {sport_key} (skipping rest).")
            break
        home = game.get('home_team', '')
        away = game.get('away_team', '')
        commence = game.get('commence_time', '')
        print(f"  {home} vs {away} @ {commence}")

ALL_TENNIS_ENDPOINTS = [
    'tennis_atp',
    'tennis_wta',
    'tennis_atp_challenger',
    'tennis_wta_challenger',
    'tennis_itf',
    'tennis_usta',
    'tennis_exhibition'
]
ALL_GOLF_ENDPOINTS = [
    'golf_pga',
    'golf_lpga',
    'golf_european',
    'golf_kornferry',
    'golf_challenge'
]

ALL_SOCCER_ENDPOINTS = [
    'soccer_epl',
    'soccer_spain_la_liga',
    'soccer_italy_serie_a',
    'soccer_germany_bundesliga',
    'soccer_france_ligue_one',
    'soccer_usa_mls',
    'soccer_uefa_champs_league',
    'soccer_uefa_europa_league',
    'soccer_brazil_campeonato',
    'soccer_argentina_primera_division',
    'soccer_netherlands_eredivisie',
    'soccer_portugal_primeira_liga',
    'soccer_turkey_super_lig',
    'soccer_russia_premier_league',
    'soccer_belgium_first_div',
    'soccer_scotland_premiership',
    'soccer_greece_super_league',
    'soccer_mexico_liga_mx',
    'soccer_world_cup',
    'soccer_euro_qualification',
    'soccer_africa_cup_of_nations',
    'soccer_asian_cup',
    'soccer_copa_libertadores',
    'soccer_copa_sudamericana',
    'soccer_gold_cup',
    'soccer_concacaf_champions_league',
    'soccer_afc_champions_league',
    'soccer_fifa_club_world_cup'
]

def get_games_underdog(sport_key, region):
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": region,
        "markets": "h2h,spreads,totals,player_props",
        "bookmakers": "underdog"
    }
    print(f"[DEBUG] Fetching Underdog games for {sport_key} in region {region}...")
    try:
        resp = requests.get(ODDS_API_ODDS.format(sport_key=sport_key), params=params, verify=False, timeout=10)
        resp.raise_for_status()
        print(f"[DEBUG] Got games for {sport_key} (Underdog only).")
        return resp.json()
    except Exception as e:
        print(f"[ERROR] Fetching Underdog games for {sport_key}: {e}")
        return []

def print_underdog_soccer(sport_key, region):
    print(f"\n=== {sport_key.upper()} Underdog Matches & Markets ===")
    games = get_games_underdog(sport_key, region)
    if not games:
        print(f"No Underdog matches found for {sport_key}")
        return
    for game in games:
        home = game.get('home_team', '')
        away = game.get('away_team', '')
        commence = game.get('commence_time', '')
        found = False
        for bookmaker in game.get('bookmakers', []):
            if bookmaker.get('key') == 'underdog':
                found = True
                print(f"  {home} vs {away} @ {commence}")
                for market in bookmaker.get('markets', []):
                    print(f"    Market: {market.get('key')}")
                    for outcome in market.get('outcomes', []):
                        print(f"      {outcome.get('name')}: {outcome.get('price')} @ {outcome.get('point')}")
        if not found:
            print(f"  {home} vs {away} @ {commence} (No Underdog markets)")

def discover_and_log_sports(region):
    print("\n=== Discovering All Available Sports from OddsAPI ===")
    url = "https://api.the-odds-api.com/v4/sports"
    params = {
        "apiKey": ODDS_API_KEY,
        "all": "true"
    }
    try:
        resp = requests.get(url, params=params, verify=False, timeout=10)
        resp.raise_for_status()
        sports = resp.json()
        print(f"Found {len(sports)} sports endpoints:")
        for sport in sports:
            print(f"  Key: {sport.get('key')}, Group: {sport.get('group')}, Title: {sport.get('title')}")
            # Optionally, fetch a sample of games for each sport
            # games = get_games(sport.get('key'), region)
            # if games:
            #     print(f"    Sample matchup: {games[0].get('home_team', '')} vs {games[0].get('away_team', '')} @ {games[0].get('commence_time', '')}")
    except Exception as e:
        print(f"[ERROR] Discovering sports: {e}")

def main():
    # Parse command-line args
    if len(sys.argv) > 1:
        date = sys.argv[1]
    else:
        date = datetime.now().strftime('%Y-%m-%d')
    if len(sys.argv) > 2:
        region = sys.argv[2]
    else:
        region = 'us'
    print(f"Ghost AI Sports Discovery for {date} (region: {region})...")
    discover_and_log_sports(region)
    fetch_tennisapi_matches()
    # You can add more logic here to auto-learn props, fetch games, etc.

if __name__ == "__main__":
    main() 