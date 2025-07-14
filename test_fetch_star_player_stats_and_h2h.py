import requests
import json
import time
from datetime import datetime, timedelta
import os

# API Configuration
API_KEY = "6495210437952ec8ed91b19a0d110bbbc148a4f33a6ff5fd582578dab84a118c"
BASE_URL = "https://api.api-tennis.com/tennis/"

# ATP/WTA Top 50 Stars (hardcoded for reliability) - Updated to match API format
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

def fetch_recent_fixtures(days_back=30):
    """Fetch recent fixtures instead of full year to avoid 500 errors"""
    print(f"Fetching fixtures from last {days_back} days...")
    
    all_fixtures = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"  Fetching {date_str}...")
        
        response = make_api_request('get_fixtures', {
            'date_start': date_str,
            'date_stop': date_str
        })
        
        if response and 'result' in response:
            fixtures = response['result']
            if fixtures:
                all_fixtures.extend(fixtures)
                print(f"    {len(fixtures)} fixtures found")
            else:
                print(f"    No fixtures found")
        else:
            print(f"    Error fetching fixtures")
        
        current_date += timedelta(days=1)
        time.sleep(0.5)  # Rate limiting
    
    return all_fixtures

def extract_player_mapping(fixtures):
    """Extract player names and keys from fixtures"""
    player_mapping = {}
    
    # Debug: Check first few fixtures
    if fixtures:
        print(f"Sample fixture structure:")
        print(json.dumps(fixtures[0], indent=2))
        
        # Also check a few more to see patterns
        print(f"\nChecking first 3 fixtures for player fields:")
        for i, fixture in enumerate(fixtures[:3]):
            print(f"\nFixture {i+1} keys: {list(fixture.keys())}")
            for key, value in fixture.items():
                if 'player' in key.lower():
                    print(f"  {key}: {value}")
    
    for fixture in fixtures:
        # Use the correct field names from the fixture structure
        p1_name = fixture.get('event_first_player', '').strip()
        p1_key = fixture.get('first_player_key', '')
        p2_name = fixture.get('event_second_player', '').strip()
        p2_key = fixture.get('second_player_key', '')
        
        if p1_name and p1_key:
            player_mapping[p1_name] = p1_key
        if p2_name and p2_key:
            player_mapping[p2_name] = p2_key
    
    return player_mapping

def get_star_players_in_fixtures(fixtures):
    """Find which star players appear in the fixtures"""
    all_stars = ATP_TOP_50 + WTA_TOP_50
    star_players = set()
    
    # Debug: Show some actual player names from fixtures
    print(f"\nSample players from fixtures:")
    sample_players = set()
    for fixture in fixtures[:20]:  # Check first 20 fixtures
        p1_name = fixture.get('event_first_player', '').strip()
        p2_name = fixture.get('event_second_player', '').strip()
        if p1_name:
            sample_players.add(p1_name)
        if p2_name:
            sample_players.add(p2_name)
    
    for player in sorted(list(sample_players))[:10]:  # Show first 10
        print(f"  - {player}")
    
    print(f"\nChecking for star player matches...")
    for fixture in fixtures:
        p1_name = fixture.get('event_first_player', '').strip()
        p2_name = fixture.get('event_second_player', '').strip()
        
        # Check exact matches and various name formats
        for star in all_stars:
            # Direct match
            if star == p1_name or star == p2_name:
                star_players.add(star)
                print(f"  Found star player: {star} (exact match)")
                continue
            
            # Try to match by last name only
            star_last_name = star.split()[-1]
            p1_last_name = p1_name.split()[-1] if p1_name else ""
            p2_last_name = p2_name.split()[-1] if p2_name else ""
            
            if star_last_name == p1_last_name or star_last_name == p2_last_name:
                star_players.add(star)
                print(f"  Found star player: {star} (last name match with {p1_name if star_last_name == p1_last_name else p2_name})")
                continue
            
            # Try initial + last name format
            if len(star.split()) >= 2:
                star_initials = '. '.join([name[0] for name in star.split()[:-1]]) + '.'
                star_initials_last = f"{star_initials} {star.split()[-1]}"
                
                if star_initials_last == p1_name or star_initials_last == p2_name:
                    star_players.add(star)
                    print(f"  Found star player: {star} (initials format match)")
                    continue
    
    return list(star_players)

def fetch_player_stats(player_name, player_key):
    """Fetch detailed stats for a player"""
    print(f"  Fetching stats for {player_name}...")
    
    stats_response = make_api_request('get_statistics', {
        'player': player_key
    })
    
    if stats_response and 'result' in stats_response:
        return stats_response['result']
    return None

def fetch_h2h_data(player1_key, player2_key):
    """Fetch head-to-head data between two players"""
    print(f"  Fetching H2H data...")
    
    h2h_response = make_api_request('get_H2H', {
        'player1': player1_key,
        'player2': player2_key
    })
    
    if h2h_response and 'result' in h2h_response:
        return h2h_response['result']
    return None

def main():
    print("=== Testing star player detection (today's fixtures only) ===")
    
    # Only fetch today's fixtures to avoid 500 errors
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Fetching today's fixtures ({today})...")
    
    response = make_api_request('get_fixtures', {
        'date_start': today,
        'date_stop': today
    })
    
    if not response or 'result' not in response:
        print("No fixtures found for today. Exiting.")
        return
    
    fixtures = response['result']
    print(f"Total fixtures found today: {len(fixtures)}")
    
    # Extract player mapping
    player_mapping = extract_player_mapping(fixtures)
    print(f"Player mapping extracted: {len(player_mapping)} players")
    
    # Find star players in fixtures
    star_players = get_star_players_in_fixtures(fixtures)
    print(f"Star players found in fixtures: {len(star_players)}")
    for player in star_players:
        print(f"  - {player}")
    
    if not star_players:
        print("No star players found today.")
        return
    
    # Collect all data
    all_data = {
        'fetch_date': datetime.now().isoformat(),
        'star_players_found': star_players,
        'player_stats': {},
        'h2h_data': {},
        'fixtures_sample': fixtures[:5] if fixtures else []  # Sample for reference
    }
    
    # Fetch stats for each star player (limit to first 3 to avoid 500 errors)
    for i, player in enumerate(star_players[:3]):
        player_key = player_mapping.get(player)
        if player_key:
            print(f"\nFetching stats for {player} (player {i+1}/3)...")
            stats = fetch_player_stats(player, player_key)
            if stats:
                all_data['player_stats'][player] = {
                    'player_key': player_key,
                    'stats': stats
                }
        time.sleep(2)  # More rate limiting
    
    # Fetch H2H data for star player pairs (limit to first 2 pairs)
    star_pairs = []
    for i, player1 in enumerate(star_players[:2]):
        for player2 in star_players[i+1:3]:
            star_pairs.append((player1, player2))
    
    print(f"\nFetching H2H data for {len(star_pairs)} star player pairs...")
    
    for player1, player2 in star_pairs:
        player1_key = player_mapping.get(player1)
        player2_key = player_mapping.get(player2)
        
        if player1_key and player2_key:
            print(f"  Fetching H2H: {player1} vs {player2}")
            h2h = fetch_h2h_data(player1_key, player2_key)
            if h2h:
                pair_key = f"{player1} vs {player2}"
                all_data['h2h_data'][pair_key] = {
                    'player1_key': player1_key,
                    'player2_key': player2_key,
                    'h2h': h2h
                }
        time.sleep(2)  # More rate limiting
    
    # Save data
    output_file = f"star_players_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=2)
    
    print(f"\nData saved to: {output_file}")
    print(f"Star players with stats: {len(all_data['player_stats'])}")
    print(f"Star player H2H pairs: {len(all_data['h2h_data'])}")
    print(f"Total fixtures processed: {len(fixtures)}")

if __name__ == "__main__":
    main() 