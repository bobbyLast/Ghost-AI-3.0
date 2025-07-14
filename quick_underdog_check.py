from core.tennis_api_client import get_fixtures
from datetime import datetime, timedelta

def quick_underdog_check():
    """Quick check of Underdog player coverage."""
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    fixtures_today = get_fixtures(today, date_stop=today)
    fixtures_tomorrow = get_fixtures(tomorrow, date_stop=tomorrow)
    all_fixtures = (fixtures_today or []) + (fixtures_tomorrow or [])
    
    print(f"=== QUICK UNDERDOG CHECK ===")
    print(f"Total fixtures: {len(all_fixtures)}")
    
    # Key Underdog players to check
    key_players = {
        "Carlos Alcaraz": ["C. Alcaraz"],
        "Taylor Fritz": ["T. Fritz"],
        "Novak Djokovic": ["N. Djokovic"],
        "Jannik Sinner": ["J. Sinner"],
        "Iga Swiatek": ["I. Swiatek"],
        "Amanda Anisimova": ["A. Anisimova"],
        "Mariano Navone": ["M. Navone"],
        "Filip Misolic": ["F. Misolic"],
        "Lucrezia Stefanini": ["L. Stefanini"],
        "Elisabetta Cocciaretto": ["E. Cocciaretto"]
    }
    
    found_players = []
    
    for underdog_player, api_variations in key_players.items():
        for fixture in all_fixtures:
            player1 = fixture.get('event_first_player', '')
            player2 = fixture.get('event_second_player', '')
            
            for api_variant in api_variations:
                if api_variant in player1 or api_variant in player2:
                    found_players.append({
                        'underdog_player': underdog_player,
                        'api_player': api_variant,
                        'match': f"{player1} vs {player2}",
                        'tournament': fixture.get('tournament_name', 'Unknown'),
                        'event_type': fixture.get('event_type_type', 'Unknown')
                    })
                    break
            else:
                continue
            break
    
    print(f"\nFound {len(found_players)} key Underdog players:")
    for player in found_players:
        print(f"✓ {player['underdog_player']} -> {player['api_player']}")
        print(f"  Match: {player['match']}")
        print(f"  Tournament: {player['tournament']}")
        print(f"  Type: {player['event_type']}")
        print()

if __name__ == "__main__":
    quick_underdog_check() 