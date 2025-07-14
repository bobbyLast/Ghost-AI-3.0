from core.tennis_api_client import get_fixtures, get_major_tournament_fixtures
from datetime import datetime, timedelta
import json

def extract_underdog_players():
    """Extract all players from the Underdog tennis list."""
    
    # Parse the Underdog list to extract all unique players
    underdog_players = set()
    
    # From the provided list, extract all player names
    players_from_list = [
        "Carlos Alcaraz", "Taylor Fritz", "Mariano Navone", "Filip Misolic",
        "Lucrezia Stefanini", "Shelby Rogers", "Elisabetta Cocciaretto", "Antonia Ruzic",
        "Elizabeth Mandlik", "Clara Giavara", "Juan Manuel Cerundolo", "Alex Molcan",
        "Tatjana Maria", "Mai Hontama", "Novak Djokovic", "Jannik Sinner",
        "Matej Dodig", "Lukas Neumayer", "Thiago Agustin Tirante", "Santiago Rodriguez Taverna",
        "Ryan Peniston", "Hamish Stewart", "Murkel Dellien", "Duje Ajdukovic",
        "Edward Winter", "Jack Pinnington Jones", "Sumit Nagal", "Maxim Mrva",
        "Patrick Zahraj", "Kyle Edmund", "Radu Albot", "Stan Wawrinka",
        "Yi Zhou", "Andres Andrade", "Lola Radivojevic", "Petra Marcinko",
        "Catherine McNally", "Mariam Bolkvadze", "Elvina Kalieva", "Carol Zhao",
        "Elsa Jacquemot", "Simona Waltert", "Rebeka Masarova", "Francesca Jones",
        "Iga Swiatek", "Amanda Anisimova", "Maiar Sherif Ahmed Abdelaziz", "Katarzyna Kawa",
        "Joao Lucas Reis Da Silva", "Titouan Droguet", "Rio Noguchi", "Liam Draxl"
    ]
    
    for player in players_from_list:
        underdog_players.add(player.strip())
    
    return sorted(list(underdog_players))

def find_matching_matches(underdog_players):
    """Find matches that include Underdog players."""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get all fixtures for today and tomorrow
    fixtures_today = get_fixtures(today, date_stop=today)
    fixtures_tomorrow = get_fixtures(tomorrow, date_stop=tomorrow)
    
    all_fixtures = (fixtures_today or []) + (fixtures_tomorrow or [])
    
    matching_matches = []
    found_players = set()
    
    for fixture in all_fixtures:
        player1 = fixture.get('event_first_player', '')
        player2 = fixture.get('event_second_player', '')
        
        # Check if either player is in our Underdog list
        for underdog_player in underdog_players:
            if (underdog_player.lower() in player1.lower() or 
                underdog_player.lower() in player2.lower() or
                player1.lower() in underdog_player.lower() or
                player2.lower() in underdog_player.lower()):
                
                match_info = {
                    'match': f"{player1} vs {player2}",
                    'tournament': fixture.get('tournament_name', 'Unknown'),
                    'event_type': fixture.get('event_type_type', 'Unknown'),
                    'date': fixture.get('event_date', 'Unknown'),
                    'time': fixture.get('event_time', 'Unknown'),
                    'underdog_player': underdog_player,
                    'fixture_data': fixture
                }
                matching_matches.append(match_info)
                found_players.add(underdog_player)
                break
    
    return matching_matches, found_players

def analyze_coverage():
    """Analyze how many Underdog players we can cover."""
    underdog_players = extract_underdog_players()
    matching_matches, found_players = find_matching_matches(underdog_players)
    
    print("=== UNDERDOG PLAYER COVERAGE ANALYSIS ===")
    print(f"Total Underdog players: {len(underdog_players)}")
    print(f"Players found in API: {len(found_players)}")
    print(f"Coverage rate: {len(found_players)/len(underdog_players)*100:.1f}%")
    
    print(f"\n=== FOUND PLAYERS ({len(found_players)}) ===")
    for player in sorted(found_players):
        print(f"✓ {player}")
    
    print(f"\n=== MISSING PLAYERS ({len(underdog_players) - len(found_players)}) ===")
    missing_players = set(underdog_players) - found_players
    for player in sorted(missing_players):
        print(f"✗ {player}")
    
    print(f"\n=== MATCHING MATCHES ({len(matching_matches)}) ===")
    for i, match in enumerate(matching_matches, 1):
        print(f"{i}. {match['match']}")
        print(f"   Tournament: {match['tournament']}")
        print(f"   Type: {match['event_type']}")
        print(f"   Date: {match['date']} {match['time']}")
        print(f"   Underdog Player: {match['underdog_player']}")
        print()
    
    return matching_matches, found_players, underdog_players

def generate_underdog_props(matches):
    """Generate Underdog-style props for the matching matches."""
    from test_tennis_prop_estimation import generate_tennis_props
    
    all_props = []
    
    for match_info in matches:
        fixture = match_info['fixture_data']
        props = generate_tennis_props(fixture)
        
        for prop in props:
            prop['match_info'] = match_info['match']
            prop['tournament'] = match_info['tournament']
            prop['underdog_player'] = match_info['underdog_player']
            all_props.append(prop)
    
    return all_props

def main():
    print("=== UNDERDOG TENNIS PLAYER ANALYSIS ===")
    
    # Analyze coverage
    matching_matches, found_players, all_underdog_players = analyze_coverage()
    
    if matching_matches:
        print("\n=== GENERATING UNDERDOG-STYLE PROPS ===")
        props = generate_underdog_props(matching_matches)
        
        print(f"Generated {len(props)} props for {len(matching_matches)} matches")
        
        # Show sample props
        print("\nSample props:")
        for i, prop in enumerate(props[:5]):
            print(f"{i+1}. {prop['player']} - {prop['prop']} {prop['line']} ({prop['pick']})")
            print(f"   Confidence: {prop['confidence']}")
            print(f"   Reasoning: {prop['reasoning']}")
            print()
    
    # Save results
    results = {
        'total_underdog_players': len(all_underdog_players),
        'found_players': len(found_players),
        'coverage_rate': len(found_players)/len(all_underdog_players)*100,
        'found_players_list': sorted(list(found_players)),
        'missing_players_list': sorted(list(set(all_underdog_players) - found_players)),
        'matching_matches': matching_matches
    }
    
    with open('underdog_coverage_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to underdog_coverage_analysis.json")

if __name__ == "__main__":
    main() 