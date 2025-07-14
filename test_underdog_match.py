from core.tennis_prop_fetcher import TennisPropFetcher

def test_underdog_player_matching():
    """Test if the fetcher finds any players from the Underdog list."""
    
    # Underdog players from your list
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
    
    print("=== TESTING UNDERDOG PLAYER MATCHING ===")
    print(f"Looking for {len(underdog_players)} Underdog players")
    
    # Run the fetcher
    fetcher = TennisPropFetcher()
    matches = fetcher.get_available_matches()
    filtered_matches = fetcher.filter_underdog_quality_matches(matches)
    unique_players = fetcher.get_unique_players_from_matches(filtered_matches)
    
    print(f"\nFound {len(unique_players)} players from fetcher:")
    for i, player_info in enumerate(unique_players, 1):
        print(f"{i:2d}. {player_info['player']} ({player_info['tournament']})")
    
    # Check for matches
    found_underdog_players = []
    for player_info in unique_players:
        api_player = player_info['player']
        
        for underdog_player in underdog_players:
            # Check for exact matches or partial matches
            if (api_player.lower() in underdog_player.lower() or 
                underdog_player.lower() in api_player.lower() or
                any(name in api_player.lower() for name in underdog_player.lower().split()) or
                any(name in underdog_player.lower() for name in api_player.lower().split())):
                
                found_underdog_players.append({
                    'underdog_player': underdog_player,
                    'api_player': api_player,
                    'tournament': player_info['tournament'],
                    'event_type': player_info['event_type']
                })
                break
    
    print(f"\n=== MATCHES FOUND ({len(found_underdog_players)}) ===")
    for match in found_underdog_players:
        print(f"✓ Underdog: {match['underdog_player']}")
        print(f"  API: {match['api_player']}")
        print(f"  Tournament: {match['tournament']}")
        print(f"  Type: {match['event_type']}")
        print()
    
    print(f"Match rate: {len(found_underdog_players)}/{len(underdog_players)} ({len(found_underdog_players)/len(underdog_players)*100:.1f}%)")
    
    if found_underdog_players:
        print("✅ SUCCESS: Found Underdog players in the fetcher!")
    else:
        print("❌ No Underdog players found. May need to adjust filtering.")

if __name__ == "__main__":
    test_underdog_player_matching() 