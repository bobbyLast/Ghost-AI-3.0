import requests
import json
import time
from datetime import datetime, timedelta
import os

# API Configuration
API_KEY = "6495210437952ec8ed91b19a0d110bbbc148a4f33a6ff5fd582578dab84a118c"
BASE_URL = "https://api.api-tennis.com/tennis/"

# ATP/WTA Top 50 Stars (hardcoded for reliability)
ATP_TOP_50 = [
    "N. Djokovic", "C. Alcaraz", "J. Sinner", "D. Medvedev", 
    "A. Zverev", "A. Rublev", "S. Tsitsipas", "H. Hurkacz",
    "C. Ruud", "T. Fritz", "G. Dimitrov", "A. de Minaur",
    "H. Rune", "T. Paul", "B. Shelton", "S. Korda",
    "F. Tiafoe", "F. Auger-Aliassime", "K. Khachanov", "N. Jarry",
    "U. Humbert", "A. Mannarino", "A. Tabilo", "S. Baez",
    "T. M. Etcheverry", "L. Musetti", "J. L. Struff", "A. Bublik",
    "T. Griekspoor", "J. Thompson", "C. Eubanks", "M. Purcell",
    "M. Giron", "D. Evans", "A. Murray", "S. Wawrinka",
    "D. Thiem", "G. Monfils", "R. Gasquet", "F. Fognini",
    "R. Bautista Agut", "P. Carreno Busta", "A. Ramos-Vinolas", "F. Coria",
    "P. Cachin", "T. Seyboth Wild", "F. Diaz Acosta", "L. Darderi",
    "F. Cobolli", "J. Mensik", "A. Fils", "L. Van Assche"
]

WTA_TOP_50 = [
    "I. Swiatek", "A. Sabalenka", "C. Gauff", "E. Rybakina",
    "J. Pegula", "O. Jabeur", "M. Vondrousova", "Q. Zheng",
    "M. Sakkari", "K. Muchova", "B. Krejcikova", "B. Haddad Maia",
    "D. Kasatkina", "L. Samsonova", "V. Kudermetova", "E. Alexandrova",
    "M. Keys", "E. Svitolina", "C. Garcia", "J. Ostapenko",
    "V. Azarenka", "A. Pavlyuchenkova", "S. Stephens", "S. Kenin",
    "D. Collins", "A. Riske-Amritraj", "B. Pera", "K. Siniakova",
    "P. Martic", "D. Vekic", "M. Bouzkova", "A. Kalinina",
    "M. Kostyuk", "L. Tsurenko", "V. Tomova", "A. Blinkova",
    "D. Parry", "C. Burel", "D. Shnaider", "M. Andreeva",
    "L. Noskova", "E. Navarro", "P. Stearns", "A. Krueger",
    "K. Day", "S. Vickery", "K. Volynets", "R. Montgomery",
    "C. Ngounoue", "L. Hovde", "A. Eala", "B. Fruhvirtova"
]

def make_api_request(method, params=None):
    """Make API request with retry logic and error handling"""
    if params is None:
        params = {}
    
    params.update({
        'method': method,
        'APIkey': API_KEY
    })
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 500:
                print(f"  500 error on attempt {attempt + 1}, retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
                continue
            else:
                print(f"  Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  Request error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
    
    print(f"  Failed after {max_retries} attempts")
    return None

def fetch_today_fixtures():
    """Fetch today's tennis fixtures"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetching today's fixtures ({today})...")
    
    response = make_api_request('get_fixtures', {
        'date_start': today,
        'date_stop': today
    })
    
    if response and 'result' in response:
        fixtures = response['result']
        print(f"Found {len(fixtures)} fixtures today")
        return fixtures
    else:
        print("No fixtures found for today")
        return []

def get_star_players_in_fixtures(fixtures):
    """Find which star players appear in the fixtures"""
    all_stars = ATP_TOP_50 + WTA_TOP_50
    star_players = set()
    
    for fixture in fixtures:
        p1_name = fixture.get('event_first_player', '').strip()
        p2_name = fixture.get('event_second_player', '').strip()
        
        # Check exact matches and various name formats
        for star in all_stars:
            # Direct match
            if star == p1_name or star == p2_name:
                star_players.add(star)
                continue
            
            # Try to match by last name only
            star_last_name = star.split()[-1]
            p1_last_name = p1_name.split()[-1] if p1_name else ""
            p2_last_name = p2_name.split()[-1] if p2_name else ""
            
            if star_last_name == p1_last_name or star_last_name == p2_last_name:
                star_players.add(star)
                continue
    
    return list(star_players)

def fetch_player_statistics(player_key):
    """Fetch detailed statistics for a player using the get_statistics method"""
    print(f"  Fetching statistics for player {player_key}...")
    
    response = make_api_request('get_statistics', {
        'player': player_key
    })
    
    if response and 'result' in response:
        return response['result']
    return None

def fetch_h2h_data(player1_key, player2_key):
    """Fetch head-to-head data between two players using correct parameter names and debug output"""
    print(f"  Fetching H2H data for player1={player1_key} vs player2={player2_key}...")
    params = {
        'method': 'get_H2H',
        'APIkey': API_KEY,
        'player1': str(player1_key),
        'player2': str(player2_key)
    }
    response = requests.get(BASE_URL, params=params, timeout=30)
    print("  Request URL:", response.url)
    print("  Status Code:", response.status_code)
    print("  Response Text:", response.text[:500])  # Print first 500 chars for brevity
    if response.status_code == 200:
        try:
            return response.json().get('result', response.json())
        except Exception as e:
            print(f"  JSON decode error: {e}")
            return None
    else:
        print(f"  Error {response.status_code}: {response.text}")
        return None

def fetch_player_standings(player_key):
    """Fetch player standings/rankings"""
    print(f"  Fetching standings for player {player_key}...")
    
    response = make_api_request('get_standings', {
        'player': player_key
    })
    
    if response and 'result' in response:
        return response['result']
    return None

def fetch_match_odds(match_key):
    """Fetch odds for a specific match"""
    print(f"  Fetching odds for match {match_key}...")
    
    response = make_api_request('get_odds', {
        'match_key': match_key
    })
    
    if response and 'result' in response:
        return response['result']
    return None

def get_comprehensive_tennis_data():
    """Main function to get comprehensive tennis data for star players"""
    print("=== Comprehensive Tennis Data Fetcher ===")
    
    # Fetch today's fixtures
    fixtures = fetch_today_fixtures()
    
    if not fixtures:
        return {
            'success': False,
            'error': 'No fixtures found for today',
            'data': None
        }
    
    # Find star players in fixtures
    star_players = get_star_players_in_fixtures(fixtures)
    print(f"Star players found: {len(star_players)}")
    for player in star_players:
        print(f"  - {player}")
    
    if not star_players:
        return {
            'success': True,
            'message': 'No star players found today',
            'data': {
                'star_players': [],
                'star_matches': [],
                'player_statistics': {},
                'h2h_data': {},
                'player_standings': {},
                'match_odds': {},
                'fixtures_count': len(fixtures)
            }
        }
    
    # Find matches involving star players
    star_matches = []
    player_keys = {}
    
    for fixture in fixtures:
        p1_name = fixture.get('event_first_player', '').strip()
        p2_name = fixture.get('event_second_player', '').strip()
        
        # Check if either player is a star
        p1_is_star = p1_name in star_players
        p2_is_star = p2_name in star_players
        
        if p1_is_star or p2_is_star:
            match_info = {
                'tournament': fixture.get('tournament_name', ''),
                'round': fixture.get('tournament_round', ''),
                'player1': p1_name,
                'player2': p2_name,
                'player1_key': fixture.get('first_player_key', ''),
                'player2_key': fixture.get('second_player_key', ''),
                'match_time': fixture.get('event_time', ''),
                'match_date': fixture.get('event_date', ''),
                'status': fixture.get('event_status', ''),
                'result': fixture.get('event_final_result', ''),
                'event_key': fixture.get('event_key', ''),
                'tournament_key': fixture.get('tournament_key', ''),
                'scores': fixture.get('scores', []),
                'statistics': fixture.get('statistics', [])
            }
            star_matches.append(match_info)
            
            # Store player keys
            if p1_is_star:
                player_keys[p1_name] = fixture.get('first_player_key', '')
            if p2_is_star:
                player_keys[p2_name] = fixture.get('second_player_key', '')
    
    # Collect comprehensive data
    all_data = {
        'fetch_date': datetime.now().isoformat(),
        'star_players': star_players,
        'star_matches': star_matches,
        'player_statistics': {},
        'h2h_data': {},
        'player_standings': {},
        'match_odds': {},
        'fixtures_count': len(fixtures),
        'star_matches_count': len(star_matches)
    }
    
    # Fetch player statistics (limit to avoid API overload)
    print(f"\nFetching player statistics...")
    for i, player in enumerate(star_players[:3]):  # Limit to first 3
        player_key = player_keys.get(player)
        if player_key:
            print(f"  Fetching stats for {player} ({i+1}/3)...")
            stats = fetch_player_statistics(player_key)
            if stats:
                all_data['player_statistics'][player] = {
                    'player_key': player_key,
                    'statistics': stats
                }
                print(f"    ✅ Statistics fetched successfully")
            else:
                print(f"    ❌ Failed to fetch statistics")
        time.sleep(2)  # Rate limiting
    
    # Fetch H2H data for star player pairs
    print(f"\nFetching head-to-head data...")
    h2h_pairs_fetched = 0
    for match in star_matches:
        if h2h_pairs_fetched >= 2:  # Limit to 2 H2H requests
            break
            
        player1_key = match.get('player1_key', '')
        player2_key = match.get('player2_key', '')
        
        if player1_key and player2_key:
            print(f"  Fetching H2H: {match['player1']} vs {match['player2']}")
            h2h = fetch_h2h_data(player1_key, player2_key)
            if h2h:
                pair_key = f"{match['player1']} vs {match['player2']}"
                all_data['h2h_data'][pair_key] = {
                    'player1_key': player1_key,
                    'player2_key': player2_key,
                    'h2h': h2h
                }
                print(f"    ✅ H2H data fetched successfully")
                h2h_pairs_fetched += 1
            else:
                print(f"    ❌ Failed to fetch H2H data")
        time.sleep(2)  # Rate limiting
    
    # Fetch player standings (rankings)
    print(f"\nFetching player standings...")
    for i, player in enumerate(star_players[:2]):  # Limit to first 2
        player_key = player_keys.get(player)
        if player_key:
            print(f"  Fetching standings for {player} ({i+1}/2)...")
            standings = fetch_player_standings(player_key)
            if standings:
                all_data['player_standings'][player] = {
                    'player_key': player_key,
                    'standings': standings
                }
                print(f"    ✅ Standings fetched successfully")
            else:
                print(f"    ❌ Failed to fetch standings")
        time.sleep(2)  # Rate limiting
    
    # Fetch match odds for star matches
    print(f"\nFetching match odds...")
    for i, match in enumerate(star_matches[:2]):  # Limit to first 2
        match_key = match.get('event_key', '')
        if match_key:
            print(f"  Fetching odds for match {i+1}/2...")
            odds = fetch_match_odds(match_key)
            if odds:
                all_data['match_odds'][match_key] = {
                    'match_info': match,
                    'odds': odds
                }
                print(f"    ✅ Odds fetched successfully")
            else:
                print(f"    ❌ Failed to fetch odds")
        time.sleep(2)  # Rate limiting
    
    return {
        'success': True,
        'message': f'Successfully collected comprehensive data for {len(star_players)} star players',
        'data': all_data
    }

def save_comprehensive_data(data, filename=None):
    """Save comprehensive tennis data to file"""
    if filename is None:
        filename = f"tennis_comprehensive_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Comprehensive data saved to: {filename}")
    return filename

def main():
    """Main execution function"""
    print("Starting single-player tennis player-data fetch via H2H workaround...")
    print(f"API Key: {API_KEY[:10]}...")
    print(f"Base URL: {BASE_URL}")
    
    fixtures = fetch_today_fixtures()
    if not fixtures:
        print("No fixtures found for today.")
        return
    star_players = get_star_players_in_fixtures(fixtures)
    if not star_players:
        print("No star players found in today's fixtures.")
        return
    found = False
    for player in star_players:
        player_key = None
        dummy_key = None
        for fixture in fixtures:
            if fixture.get('event_first_player', '').strip() == player:
                player_key = fixture.get('first_player_key', '')
                dummy_key = fixture.get('second_player_key', '')
                break
            if fixture.get('event_second_player', '').strip() == player:
                player_key = fixture.get('second_player_key', '')
                dummy_key = fixture.get('first_player_key', '')
                break
        # Check that both keys are non-empty and not None
        if player_key and dummy_key and str(player_key).strip() and str(dummy_key).strip():
            print(f"Attempting to fetch player data for: {player}")
            print(f"Using player_key={player_key}, dummy_key={dummy_key}")
            h2h_data = fetch_h2h_data(player_key, dummy_key)
            print(f"Raw H2H response: {h2h_data}")
            if isinstance(h2h_data, dict):
                print(f"\nH2H data for {player} (key {player_key}):\n{json.dumps(h2h_data, indent=2)}")
                player1_info = h2h_data.get('player1', {})
                print("\nExtracted Player Info:")
                for k, v in player1_info.items():
                    print(f"  {k}: {v}")
                if 'player1_last_matches' in h2h_data:
                    print("\nRecent Matches:")
                    for match in h2h_data['player1_last_matches'][:3]:
                        print(f"  {match}")
                found = True
            elif isinstance(h2h_data, list):
                print(f"API returned an error list: {h2h_data}")
            else:
                print(f"Failed to fetch player data for {player} (key {player_key}) via H2H.")
            break
    if not found:
        print("Could not find any star player in today's fixtures with both a valid player key and a dummy key.")

if __name__ == "__main__":
    main() 