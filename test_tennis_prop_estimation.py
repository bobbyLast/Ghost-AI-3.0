from core.tennis_api_client import get_fixtures, get_players, get_h2h, get_major_tournament_fixtures, get_event_types, get_tournaments, get_odds, get_live_odds, get_standings
from datetime import datetime, timedelta
import os
import json

def test_full_api_capabilities():
    """Test all API endpoints to see what data we can extract."""
    print("=== COMPREHENSIVE API KEY TESTING ===")
    
    # Test different dates
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n1. TESTING DIFFERENT DATES:")
    print(f"Today ({today}):")
    fixtures_today = get_fixtures(today, date_stop=today)
    print(f"  - {len(fixtures_today) if fixtures_today else 0} matches")
    
    print(f"Yesterday ({yesterday}):")
    fixtures_yesterday = get_fixtures(yesterday, date_stop=yesterday)
    print(f"  - {len(fixtures_yesterday) if fixtures_yesterday else 0} matches")
    
    print(f"Tomorrow ({tomorrow}):")
    fixtures_tomorrow = get_fixtures(tomorrow, date_stop=tomorrow)
    print(f"  - {len(fixtures_tomorrow) if fixtures_tomorrow else 0} matches")
    
    # Test different date ranges
    print(f"\n2. TESTING DATE RANGES:")
    week_range = get_fixtures(today, date_stop=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
    print(f"Week range: {len(week_range) if week_range else 0} matches")
    
    # Test tournaments
    print(f"\n3. TESTING TOURNAMENTS:")
    tournaments = get_tournaments()
    if tournaments:
        print(f"Available tournaments: {len(tournaments)}")
        print("Sample tournaments:")
        for i, tourney in enumerate(tournaments[:5]):
            print(f"  {i+1}. {tourney.get('tournament_name', 'Unknown')} ({tourney.get('event_type_type', 'Unknown')})")
    
    # Test live odds
    print(f"\n4. TESTING LIVE ODDS:")
    try:
        live_odds = get_live_odds()
        if live_odds:
            print(f"Live matches: {len(live_odds)}")
            for match_key, match_data in list(live_odds.items())[:3]:
                player1 = match_data.get('event_first_player', 'Unknown')
                player2 = match_data.get('event_second_player', 'Unknown')
                print(f"  - {player1} vs {player2}")
        else:
            print("No live matches available")
    except Exception as e:
        print(f"Live odds not available: {e}")
    
    # Test specific tournament filtering
    print(f"\n5. TESTING TOURNAMENT FILTERING:")
    if fixtures_today:
        # Get unique tournaments from today's fixtures
        tournaments_today = set()
        for fixture in fixtures_today:
            tourney = fixture.get('tournament_name', 'Unknown')
            event_type = fixture.get('event_type_type', 'Unknown')
            tournaments_today.add(f"{tourney} ({event_type})")
        
        print(f"Tournaments today: {len(tournaments_today)}")
        for tourney in list(tournaments_today)[:5]:
            print(f"  - {tourney}")
    
    # Test player data
    print(f"\n6. TESTING PLAYER DATA:")
    if fixtures_today and len(fixtures_today) > 0:
        sample_match = fixtures_today[0]
        player1_key = sample_match.get('first_player_key')
        player2_key = sample_match.get('second_player_key')
        
        if player1_key:
            player1_data = get_players(player_key=player1_key)
            print(f"Player 1 data available: {player1_data is not None}")
        
        if player2_key:
            player2_data = get_players(player_key=player2_key)
            print(f"Player 2 data available: {player2_data is not None}")
    
    # Test odds data
    print(f"\n7. TESTING ODDS DATA:")
    if fixtures_today and len(fixtures_today) > 0:
        sample_match = fixtures_today[0]
        match_key = sample_match.get('event_key')
        if match_key:
            odds_data = get_odds(match_key)
            print(f"Odds data available: {odds_data is not None}")
            if odds_data:
                print(f"Odds markets: {len(odds_data.get(str(match_key), {})) if odds_data else 0}")
    
    # Test standings
    print(f"\n8. TESTING STANDINGS:")
    standings = get_standings(event_type='Atp Singles')
    print(f"ATP Singles standings available: {standings is not None}")

def check_available_event_types():
    """Check what event types are available from the API."""
    print("=== CHECKING AVAILABLE EVENT TYPES ===")
    event_types = get_event_types()
    if event_types:
        print("Available event types:")
        for event in event_types:
            event_key = event.get('event_type_key', 'Unknown')
            event_type = event.get('event_type_type', 'Unknown')
            print(f"  {event_key}: {event_type}")
    else:
        print("No event types found")

def check_all_fixtures():
    """Check all fixtures without filtering to see what's available."""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n=== CHECKING ALL FIXTURES FOR {today} ===")
    all_fixtures = get_fixtures(today, date_stop=today)
    
    if not all_fixtures:
        print("No fixtures found for today.")
        return
    
    print(f"Total fixtures found: {len(all_fixtures)}")
    
    # Group by event type
    event_type_counts = {}
    for fixture in all_fixtures:
        event_type = fixture.get('event_type_type', 'Unknown')
        event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
    
    print("\nFixtures by event type:")
    for event_type, count in sorted(event_type_counts.items()):
        print(f"  {event_type}: {count} matches")

def estimate_stat(stats, stat_name):
    if not stats or not isinstance(stats, list):
        return None
    for s in stats[0].get('stats', []):
        if stat_name in s:
            return s[stat_name]
    return None

def generate_tennis_props(match):
    player1 = match.get('event_first_player')
    player2 = match.get('event_second_player')
    player1_key = match.get('first_player_key')
    player2_key = match.get('second_player_key')
    h2h = get_h2h(player1_key, player2_key) if player1_key and player2_key else None
    p1_stats = get_players(player_key=player1_key) if player1_key else None
    p2_stats = get_players(player_key=player2_key) if player2_key else None
    final_result = None
    if h2h and 'H2H' in h2h and h2h['H2H']:
        final_result = h2h['H2H'][0].get('event_final_result')
    # Parse set scores
    def parse_set_scores(final_result):
        sets = []
        if not final_result:
            return sets
        for s in final_result.split(','):
            s = s.strip()
            if '-' in s:
                try:
                    a, b = map(int, s.split('-'))
                    sets.append([a, b])
                except Exception:
                    continue
        return sets
    sets = parse_set_scores(final_result)
    props = []
    
    # --- UNDERDOG-STYLE TENNIS PROPS (EXACT FORMAT) ---
    
    # Games Played (Higher/Lower) - Total games in the match
    total_games = sum(sum(s) for s in sets) if sets else None
    if total_games is not None:
        props.append({
            'player': f"{player1} vs {player2}",
            'prop': 'Games Played',
            'line': 20.5,
            'pick': 'Higher' if total_games > 20.5 else 'Lower',
            'confidence': 0.7,
            'reasoning': f"Actual from H2H: {total_games} total games played."
        })
    else:
        # Estimate from player stats if available
        avg_games = estimate_stat(p1_stats, 'games_played_avg')
        if avg_games:
            props.append({
                'player': f"{player1} vs {player2}",
                'prop': 'Games Played',
                'line': 20.5,
                'pick': 'Higher' if float(avg_games) > 20.5 else 'Lower',
                'confidence': 0.6,
                'reasoning': f"(est.) Based on season avg: {avg_games} games played per match."
            })
    
    # Games Won (Higher/Lower) for each player
    for player, stats in [(player1, p1_stats), (player2, p2_stats)]:
        games_won = sum(s[0] if player == player1 else s[1] for s in sets) if sets else None
        if games_won is not None:
            props.append({
                'player': player,
                'prop': 'Games Won',
                'line': 10.5,
                'pick': 'Higher' if games_won > 10.5 else 'Lower',
                'confidence': 0.7,
                'reasoning': f"Actual from H2H: {games_won} games won."
            })
        else:
            avg_games = estimate_stat(stats, 'games_won_avg')
            if avg_games:
                props.append({
                    'player': player,
                    'prop': 'Games Won',
                    'line': 10.5,
                    'pick': 'Higher' if float(avg_games) > 10.5 else 'Lower',
                    'confidence': 0.6,
                    'reasoning': f"(est.) Based on season avg: {avg_games} games won per match."
                })
    
    # Sets won (Higher/Lower) for each player
    for player, stats in [(player1, p1_stats), (player2, p2_stats)]:
        sets_won = sum(1 for s in sets if (s[0] > s[1] if player == player1 else s[1] > s[0])) if sets else None
        if sets_won is not None:
            props.append({
                'player': player,
                'prop': 'Sets won',
                'line': 0.5,
                'pick': 'Higher' if sets_won > 0.5 else 'Lower',
                'confidence': 0.7,
                'reasoning': f"Actual from H2H: {sets_won} sets won."
            })
        else:
            avg_sets = estimate_stat(stats, 'sets_won_avg')
            if avg_sets:
                props.append({
                    'player': player,
                    'prop': 'Sets won',
                    'line': 0.5,
                    'pick': 'Higher' if float(avg_sets) > 0.5 else 'Lower',
                    'confidence': 0.6,
                    'reasoning': f"(est.) Based on season avg: {avg_sets} sets won per match."
                })
    
    # 1st Set Games Played (Higher/Lower)
    if sets and len(sets) > 0:
        first_set_games = sum(sets[0])
        props.append({
            'player': f"{player1} vs {player2}",
            'prop': '1st Set Games Played',
            'line': 9.5,
            'pick': 'Higher' if first_set_games > 9.5 else 'Lower',
            'confidence': 0.7,
            'reasoning': f"Actual from H2H: {first_set_games} games in 1st set."
        })
    else:
        avg_first_set = estimate_stat(p1_stats, 'first_set_games_avg')
        if avg_first_set:
            props.append({
                'player': f"{player1} vs {player2}",
                'prop': '1st Set Games Played',
                'line': 9.5,
                'pick': 'Higher' if float(avg_first_set) > 9.5 else 'Lower',
                'confidence': 0.6,
                'reasoning': f"(est.) Based on season avg: {avg_first_set} games in 1st set."
            })
    
    # Breakpoints Won (Higher/Lower) for each player
    bp_won = estimate_stat(p1_stats, 'breakpoints_won')
    if bp_won:
        props.append({
            'player': player1,
            'prop': 'Breakpoints Won',
            'line': 2.5,
            'pick': 'Higher' if float(bp_won) > 2.5 else 'Lower',
            'confidence': 0.6,
            'reasoning': f"(est.) Based on season avg: {bp_won} breakpoints won per match."
        })
    
    bp_won2 = estimate_stat(p2_stats, 'breakpoints_won')
    if bp_won2:
        props.append({
            'player': player2,
            'prop': 'Breakpoints Won',
            'line': 2.5,
            'pick': 'Higher' if float(bp_won2) > 2.5 else 'Lower',
            'confidence': 0.6,
            'reasoning': f"(est.) Based on season avg: {bp_won2} breakpoints won per match."
        })
    
    # Aces (Higher/Lower) for each player
    avg_aces = estimate_stat(p1_stats, 'aces')
    if avg_aces:
        props.append({
            'player': player1,
            'prop': 'Aces',
            'line': 4.5,
            'pick': 'Higher' if float(avg_aces) > 4.5 else 'Lower',
            'confidence': 0.6,
            'reasoning': f"(est.) Based on season/career avg: {avg_aces} aces per match."
        })
    
    avg_aces2 = estimate_stat(p2_stats, 'aces')
    if avg_aces2:
        props.append({
            'player': player2,
            'prop': 'Aces',
            'line': 4.5,
            'pick': 'Higher' if float(avg_aces2) > 4.5 else 'Lower',
            'confidence': 0.6,
            'reasoning': f"(est.) Based on season/career avg: {avg_aces2} aces per match."
        })
    
    return props

def main():
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Comprehensive API testing
    test_full_api_capabilities()
    
    # Check what event types are available
    check_available_event_types()
    
    # Check all fixtures
    check_all_fixtures()
    
    # Now check major tournament fixtures
    fixtures = get_major_tournament_fixtures(today, date_stop=today)
    if not fixtures:
        print('\nNo major tournament matches found for today.')
        return
    
    print(f"\n=== MAJOR TOURNAMENT MATCHES (UNDERDOG-ELIGIBLE) ===")
    print(f"Date: {today}")
    print(f"Total major matches found: {len(fixtures)}")
    print("\n")
    
    # Show all major tournament matches
    for i, match in enumerate(fixtures[:10], 1):  # Show first 10 matches
        player1 = match.get('event_first_player', 'Unknown')
        player2 = match.get('event_second_player', 'Unknown')
        tournament = match.get('tournament_name', 'Unknown')
        event_type = match.get('event_type_type', 'Unknown')
        event_time = match.get('event_time', 'Unknown')
        
        print(f"{i}. {player1} vs {player2}")
        print(f"   Tournament: {tournament}")
        print(f"   Type: {event_type}")
        print(f"   Time: {event_time}")
        print()
    
    if len(fixtures) > 10:
        print(f"... and {len(fixtures) - 10} more major matches")
    
    print("\n=== GENERATING PROPS FOR FIRST MAJOR MATCH ===")
    # Generate props for the first major tournament match
    match = fixtures[0]
    print(f"\nProps for: {match.get('event_first_player')} vs {match.get('event_second_player')}")
    props = generate_tennis_props(match)
    for p in props:
        print(json.dumps(p, indent=2))

if __name__ == "__main__":
    main() 