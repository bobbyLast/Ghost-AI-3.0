from core.tennis_api_client import get_fixtures
from datetime import datetime, timedelta
import json

def check_available_players():
    """Check what players are actually available in our API data."""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get all fixtures for today and tomorrow
    fixtures_today = get_fixtures(today, date_stop=today)
    fixtures_tomorrow = get_fixtures(tomorrow, date_stop=tomorrow)
    
    all_fixtures = (fixtures_today or []) + (fixtures_tomorrow or [])
    
    print(f"=== AVAILABLE PLAYERS ANALYSIS ===")
    print(f"Total fixtures: {len(all_fixtures)}")
    
    all_players = set()
    player_matches = {}
    
    for fixture in all_fixtures:
        player1 = fixture.get('event_first_player', '')
        player2 = fixture.get('event_second_player', '')
        tournament = fixture.get('tournament_name', 'Unknown')
        event_type = fixture.get('event_type_type', 'Unknown')
        
        if player1:
            all_players.add(player1)
            if player1 not in player_matches:
                player_matches[player1] = []
            player_matches[player1].append({
                'opponent': player2,
                'tournament': tournament,
                'event_type': event_type,
                'date': fixture.get('event_date', 'Unknown'),
                'time': fixture.get('event_time', 'Unknown')
            })
        
        if player2:
            all_players.add(player2)
            if player2 not in player_matches:
                player_matches[player2] = []
            player_matches[player2].append({
                'opponent': player1,
                'tournament': tournament,
                'event_type': event_type,
                'date': fixture.get('event_date', 'Unknown'),
                'time': fixture.get('event_time', 'Unknown')
            })
    
    print(f"Total unique players: {len(all_players)}")
    
    # Show all players
    print(f"\n=== ALL AVAILABLE PLAYERS ===")
    for i, player in enumerate(sorted(all_players), 1):
        print(f"{i:3d}. {player}")
    
    # Check for potential matches with Underdog players
    underdog_players = [
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
    
    print(f"\n=== POTENTIAL MATCHES WITH UNDERDOG PLAYERS ===")
    potential_matches = []
    
    for underdog_player in underdog_players:
        for api_player in all_players:
            # Check for partial matches
            if (underdog_player.lower() in api_player.lower() or 
                api_player.lower() in underdog_player.lower() or
                any(name in api_player.lower() for name in underdog_player.lower().split()) or
                any(name in underdog_player.lower() for name in api_player.lower().split())):
                
                potential_matches.append({
                    'underdog_player': underdog_player,
                    'api_player': api_player,
                    'matches': player_matches.get(api_player, [])
                })
                break
    
    print(f"Potential matches found: {len(potential_matches)}")
    for match in potential_matches:
        print(f"Underdog: {match['underdog_player']} -> API: {match['api_player']}")
        for game in match['matches'][:2]:  # Show first 2 matches
            print(f"  vs {game['opponent']} ({game['tournament']} - {game['event_type']})")
        if len(match['matches']) > 2:
            print(f"  ... and {len(match['matches']) - 2} more matches")
        print()
    
    # Save detailed results
    results = {
        'total_fixtures': len(all_fixtures),
        'total_players': len(all_players),
        'all_players': sorted(list(all_players)),
        'player_matches': player_matches,
        'potential_matches': potential_matches
    }
    
    with open('available_players_analysis.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Detailed results saved to available_players_analysis.json")

if __name__ == "__main__":
    check_available_players() 