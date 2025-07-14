from core.tennis_api_client import get_fixtures
from datetime import datetime, timedelta
import json
import re

def normalize_name(name):
    """Normalize player names for better matching."""
    # Remove extra spaces and convert to lowercase
    name = re.sub(r'\s+', ' ', name.strip().lower())
    # Remove common prefixes/suffixes
    name = re.sub(r'^(mr\.|mrs\.|ms\.|dr\.)\s*', '', name)
    return name

def extract_initials_and_surname(full_name):
    """Extract initials and surname from full name."""
    parts = full_name.split()
    if len(parts) >= 2:
        initials = '. '.join([part[0] for part in parts[:-1]]) + '.'
        surname = parts[-1]
        return initials, surname
    return None, None

def find_accurate_matches():
    """Find accurate matches between Underdog players and API data."""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    fixtures_today = get_fixtures(today, date_stop=today)
    fixtures_tomorrow = get_fixtures(tomorrow, date_stop=tomorrow)
    all_fixtures = (fixtures_today or []) + (fixtures_tomorrow or [])
    
    # Underdog players with their expected API variations
    underdog_players = {
        "Carlos Alcaraz": ["C. Alcaraz", "Carlos Alcaraz"],
        "Taylor Fritz": ["T. Fritz", "Taylor Fritz"],
        "Mariano Navone": ["M. Navone", "Mariano Navone"],
        "Filip Misolic": ["F. Misolic", "Filip Misolic"],
        "Lucrezia Stefanini": ["L. Stefanini", "Lucrezia Stefanini"],
        "Shelby Rogers": ["A. S. Rogers", "Shelby Rogers"],
        "Elisabetta Cocciaretto": ["E. Cocciaretto", "Elisabetta Cocciaretto"],
        "Antonia Ruzic": ["A. Ruzic", "Antonia Ruzic"],
        "Elizabeth Mandlik": ["E. Mandlik", "Elizabeth Mandlik"],
        "Clara Giavara": ["Giavara", "Clara Giavara"],
        "Juan Manuel Cerundolo": ["J. M. Cerundolo", "Juan Manuel Cerundolo"],
        "Alex Molcan": ["A. Molcan", "Alex Molcan"],
        "Tatjana Maria": ["T. Maria", "Tatjana Maria"],
        "Novak Djokovic": ["N. Djokovic", "Novak Djokovic"],
        "Jannik Sinner": ["J. Sinner", "Jannik Sinner"],
        "Matej Dodig": ["M. Dodig", "Matej Dodig"],
        "Lukas Neumayer": ["L. Neumayer", "Lukas Neumayer"],
        "Thiago Agustin Tirante": ["T. A. Tirante", "Thiago Agustin Tirante"],
        "Santiago Rodriguez Taverna": ["S. Rodriguez Taverna", "Santiago Rodriguez Taverna"],
        "Ryan Peniston": ["R. Peniston", "Ryan Peniston"],
        "Hamish Stewart": ["H. Stewart", "Hamish Stewart"],
        "Murkel Dellien": ["M. A. Dellien Velasco", "Murkel Dellien"],
        "Duje Ajdukovic": ["D. Ajdukovic", "Duje Ajdukovic"],
        "Edward Winter": ["E. Winter", "Edward Winter"],
        "Jack Pinnington Jones": ["J. Pinnington Jones", "Jack Pinnington Jones"],
        "Sumit Nagal": ["S. Nagal", "Sumit Nagal"],
        "Maxim Mrva": ["M. Mrva", "Maxim Mrva"],
        "Patrick Zahraj": ["P. Zahraj", "Patrick Zahraj"],
        "Kyle Edmund": ["K. Edmund", "Kyle Edmund"],
        "Radu Albot": ["R. Albot", "Radu Albot"],
        "Stan Wawrinka": ["S. Wawrinka", "Stan Wawrinka"],
        "Yi Zhou": ["Y. Zhou", "Yi Zhou"],
        "Andres Andrade": ["A. Andrade", "Andres Andrade"],
        "Lola Radivojevic": ["L. Radivojevic", "Lola Radivojevic"],
        "Petra Marcinko": ["P. Marcinko", "Petra Marcinko"],
        "Catherine McNally": ["C. McNally", "Catherine McNally"],
        "Mariam Bolkvadze": ["M. Bolkvadze", "Mariam Bolkvadze"],
        "Elvina Kalieva": ["E. Kalieva", "Elvina Kalieva"],
        "Carol Zhao": ["C. Zhao", "Carol Zhao"],
        "Elsa Jacquemot": ["E. Jacquemot", "Elsa Jacquemot"],
        "Simona Waltert": ["S. Waltert", "Simona Waltert"],
        "Rebeka Masarova": ["R. Masarova", "Rebeka Masarova"],
        "Francesca Jones": ["F. Jones", "Francesca Jones"],
        "Iga Swiatek": ["I. Swiatek", "Iga Swiatek"],
        "Amanda Anisimova": ["A. Anisimova", "Amanda Anisimova"],
        "Maiar Sherif Ahmed Abdelaziz": ["M. Sherif", "Maiar Sherif"],
        "Katarzyna Kawa": ["K. Kawa", "Katarzyna Kawa"],
        "Joao Lucas Reis Da Silva": ["J. Reis Da Silva", "Joao Lucas Reis Da Silva"],
        "Titouan Droguet": ["T. Droguet", "Titouan Droguet"],
        "Rio Noguchi": ["R. Noguchi", "Rio Noguchi"],
        "Liam Draxl": ["L. Draxl", "Liam Draxl"]
    }
    
    # Collect all API players
    api_players = set()
    player_matches = {}
    
    for fixture in all_fixtures:
        player1 = fixture.get('event_first_player', '')
        player2 = fixture.get('event_second_player', '')
        tournament = fixture.get('tournament_name', 'Unknown')
        event_type = fixture.get('event_type_type', 'Unknown')
        
        if player1:
            api_players.add(player1)
            if player1 not in player_matches:
                player_matches[player1] = []
            player_matches[player1].append({
                'opponent': player2,
                'tournament': tournament,
                'event_type': event_type,
                'date': fixture.get('event_date', 'Unknown'),
                'time': fixture.get('event_time', 'Unknown'),
                'fixture_data': fixture
            })
        
        if player2:
            api_players.add(player2)
            if player2 not in player_matches:
                player_matches[player2] = []
            player_matches[player2].append({
                'opponent': player1,
                'tournament': tournament,
                'event_type': event_type,
                'date': fixture.get('event_date', 'Unknown'),
                'time': fixture.get('event_time', 'Unknown'),
                'fixture_data': fixture
            })
    
    # Find accurate matches
    accurate_matches = []
    found_underdog_players = set()
    
    for underdog_player, api_variations in underdog_players.items():
        for api_player in api_players:
            # Check if API player matches any of the expected variations
            if api_player in api_variations:
                matches = player_matches.get(api_player, [])
                if matches:
                    accurate_matches.append({
                        'underdog_player': underdog_player,
                        'api_player': api_player,
                        'matches': matches
                    })
                    found_underdog_players.add(underdog_player)
                    break
    
    return accurate_matches, found_underdog_players, underdog_players

def analyze_accurate_coverage():
    """Analyze accurate coverage of Underdog players."""
    accurate_matches, found_players, all_underdog_players = find_accurate_matches()
    
    print("=== ACCURATE UNDERDOG PLAYER COVERAGE ===")
    print(f"Total Underdog players: {len(all_underdog_players)}")
    print(f"Players found in API: {len(found_players)}")
    print(f"Coverage rate: {len(found_players)/len(all_underdog_players)*100:.1f}%")
    
    print(f"\n=== FOUND PLAYERS ({len(found_players)}) ===")
    for player in sorted(found_players):
        print(f"✓ {player}")
    
    print(f"\n=== MISSING PLAYERS ({len(all_underdog_players) - len(found_players)}) ===")
    missing_players = set(all_underdog_players.keys()) - found_players
    for player in sorted(missing_players):
        print(f"✗ {player}")
    
    print(f"\n=== ACCURATE MATCHES ({len(accurate_matches)}) ===")
    for match in accurate_matches:
        print(f"Underdog: {match['underdog_player']}")
        print(f"API: {match['api_player']}")
        for game in match['matches']:
            print(f"  vs {game['opponent']} ({game['tournament']} - {game['event_type']})")
            print(f"  Date: {game['date']} {game['time']}")
        print()
    
    return accurate_matches, found_players, all_underdog_players

def generate_underdog_props_from_matches(matches):
    """Generate Underdog-style props for the accurately matched players."""
    from test_tennis_prop_estimation import generate_tennis_props
    
    all_props = []
    total_players = len(matches)
    
    print(f"\n=== GENERATING UNDERDOG-STYLE PROPS ===")
    print(f"Processing {total_players} players...")
    
    for i, match_info in enumerate(matches, 1):
        underdog_player = match_info['underdog_player']
        api_player = match_info['api_player']
        
        print(f"Processing player {i}/{total_players}: {underdog_player}")
        
        for j, game in enumerate(match_info['matches'], 1):
            fixture = game['fixture_data']
            print(f"  Generating props for match {j}/{len(match_info['matches'])}: {fixture.get('event_first_player')} vs {fixture.get('event_second_player')}")
            
            try:
                props = generate_tennis_props(fixture)
                
                for prop in props:
                    prop['underdog_player'] = underdog_player
                    prop['api_player'] = api_player
                    prop['match_info'] = f"{fixture.get('event_first_player')} vs {fixture.get('event_second_player')}"
                    prop['tournament'] = fixture.get('tournament_name', 'Unknown')
                    prop['event_type'] = fixture.get('event_type_type', 'Unknown')
                    all_props.append(prop)
                
                print(f"    Generated {len(props)} props")
                
            except Exception as e:
                print(f"    Error generating props: {e}")
                continue
    
    print(f"\nTotal props generated: {len(all_props)}")
    return all_props

def main():
    print("=== ACCURATE UNDERDOG TENNIS PLAYER ANALYSIS ===")
    
    # Analyze accurate coverage
    accurate_matches, found_players, all_underdog_players = analyze_accurate_coverage()
    
    if accurate_matches:
        # Generate props with progress logging
        props = generate_underdog_props_from_matches(accurate_matches)
        
        # Show sample props (only first 5)
        print(f"\n=== SAMPLE PROPS (First 5) ===")
        for i, prop in enumerate(props[:5]):
            print(f"{i+1}. {prop['underdog_player']} - {prop['prop']} {prop['line']} ({prop['pick']})")
            print(f"   Match: {prop['match_info']}")
            print(f"   Tournament: {prop['tournament']}")
            print(f"   Confidence: {prop['confidence']}")
            print()
        
        if len(props) > 5:
            print(f"... and {len(props) - 5} more props")
    
    # Save results
    results = {
        'total_underdog_players': len(all_underdog_players),
        'found_players': len(found_players),
        'coverage_rate': len(found_players)/len(all_underdog_players)*100,
        'found_players_list': sorted(list(found_players)),
        'missing_players_list': sorted(list(set(all_underdog_players.keys()) - found_players)),
        'accurate_matches': accurate_matches,
        'all_props': props if 'props' in locals() else []
    }
    
    with open('accurate_underdog_coverage.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Save props separately
    if 'props' in locals() and props:
        with open('underdog_props.json', 'w') as f:
            json.dump(props, f, indent=2, default=str)
        print(f"\nAll props saved to underdog_props.json")
    
    print(f"\nResults saved to accurate_underdog_coverage.json")

if __name__ == "__main__":
    main() 