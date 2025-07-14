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

def extract_player_mapping(fixtures):
    """Extract player names and keys from fixtures"""
    player_mapping = {}
    
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
            
            # Try initial + last name format
            if len(star.split()) >= 2:
                star_initials = '. '.join([name[0] for name in star.split()[:-1]]) + '.'
                star_initials_last = f"{star_initials} {star.split()[-1]}"
                
                if star_initials_last == p1_name or star_initials_last == p2_name:
                    star_players.add(star)
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

def get_star_players_data():
    """Main function to get star players data for today"""
    print("=== Tennis Star Players Data Fetcher ===")
    
    # Fetch today's fixtures
    fixtures = fetch_today_fixtures()
    
    if not fixtures:
        return {
            'success': False,
            'error': 'No fixtures found for today',
            'data': None
        }
    
    # Extract player mapping
    player_mapping = extract_player_mapping(fixtures)
    print(f"Player mapping extracted: {len(player_mapping)} players")
    
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
                'player_data': {},
                'fixtures_count': len(fixtures)
            }
        }
    
    # Find matches involving star players and extract available data
    star_matches = []
    player_data = {}
    
    for fixture in fixtures:
        p1_name = fixture.get('event_first_player', '').strip()
        p2_name = fixture.get('event_second_player', '').strip()
        
        # Check if either player is a star
        p1_is_star = p1_name in star_players
        p2_is_star = p2_name in star_players
        
        if p1_is_star or p2_is_star:
            # Extract match data
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
                'has_star_players': True,
                'event_key': fixture.get('event_key', ''),
                'tournament_key': fixture.get('tournament_key', ''),
                'scores': fixture.get('scores', []),
                'statistics': fixture.get('statistics', [])
            }
            star_matches.append(match_info)
            
            # Collect player data from fixtures
            if p1_is_star and p1_name not in player_data:
                player_data[p1_name] = {
                    'player_key': fixture.get('first_player_key', ''),
                    'matches_today': [],
                    'total_matches': 0,
                    'tournaments': set()
                }
            
            if p2_is_star and p2_name not in player_data:
                player_data[p2_name] = {
                    'player_key': fixture.get('second_player_key', ''),
                    'matches_today': [],
                    'total_matches': 0,
                    'tournaments': set()
                }
            
            # Add match info to player data
            if p1_is_star:
                player_data[p1_name]['matches_today'].append(match_info)
                player_data[p1_name]['total_matches'] += 1
                player_data[p1_name]['tournaments'].add(fixture.get('tournament_name', ''))
            
            if p2_is_star:
                player_data[p2_name]['matches_today'].append(match_info)
                player_data[p2_name]['total_matches'] += 1
                player_data[p2_name]['tournaments'].add(fixture.get('tournament_name', ''))
    
    # Convert sets to lists for JSON serialization
    for player in player_data:
        player_data[player]['tournaments'] = list(player_data[player]['tournaments'])
    
    # Collect all data
    all_data = {
        'fetch_date': datetime.now().isoformat(),
        'star_players': star_players,
        'star_matches': star_matches,
        'player_data': player_data,
        'fixtures_count': len(fixtures),
        'star_matches_count': len(star_matches),
        'available_data': {
            'match_schedules': True,
            'tournament_info': True,
            'player_keys': True,
            'match_results': True,
            'scores': True,
            'statistics_from_fixtures': True
        }
    }
    
    return {
        'success': True,
        'message': f'Successfully identified {len(star_players)} star players in {len(star_matches)} matches with comprehensive match data',
        'data': all_data
    }

def save_star_players_data(data, filename=None):
    """Save star players data to file"""
    if filename is None:
        filename = f"tennis_star_players_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Data saved to: {filename}")
    return filename

def main():
    """Main execution function"""
    result = get_star_players_data()
    
    if result['success']:
        print(f"\n✅ {result['message']}")
        print(f"Star players found: {len(result['data']['star_players'])}")
        print(f"Star matches found: {len(result['data']['star_matches'])}")
        print(f"Players with data: {len(result['data']['player_data'])}")
        print(f"Total fixtures processed: {result['data']['fixtures_count']}")
        
        # Show star matches
        if result['data']['star_matches']:
            print(f"\nStar matches today:")
            for match in result['data']['star_matches']:
                print(f"  - {match['player1']} vs {match['player2']} ({match['tournament']} - {match['round']})")
        
        # Show players with data
        if result['data']['player_data']:
            print(f"\nPlayers with comprehensive data:")
            for player, data in result['data']['player_data'].items():
                print(f"  - {player}: {data['total_matches']} matches, tournaments: {', '.join(data['tournaments'])}")
        
        # Show available data types
        print(f"\nAvailable data types:")
        for data_type, available in result['data']['available_data'].items():
            status = "✅" if available else "❌"
            print(f"  {status} {data_type}")
        
        # Save data
        filename = save_star_players_data(result['data'])
        
        return {
            'success': True,
            'filename': filename,
            'data': result['data']
        }
    else:
        print(f"\n❌ {result['error']}")
        return {
            'success': False,
            'error': result['error']
        }

if __name__ == "__main__":
    main() 