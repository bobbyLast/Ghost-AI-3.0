import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_brain.tennis_api_client import (
    get_event_types, get_tournaments, get_fixtures, get_odds, get_players, get_standings, get_h2h, get_livescore
)
from ai_brain.ai_brain import AIBrain
from datetime import datetime
import json

def print_json(label, data):
    print(f'\n--- {label} ---')
    print(json.dumps(data, indent=2, ensure_ascii=False)[:4000])

def parse_set_scores(final_result):
    # e.g. "6-3, 6-4" -> [[6,3],[6,4]]
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

def show_props_for_real_match():
    today = datetime.now().strftime('%Y-%m-%d')
    fixtures = get_fixtures(today, date_stop=today)
    if not fixtures:
        print('No matches found for today.')
        return
    match = fixtures[0]
    player1 = match.get('event_first_player')
    player2 = match.get('event_second_player')
    player1_key = match.get('first_player_key')
    player2_key = match.get('second_player_key')
    match_time = f"{match.get('event_date')}T{match.get('event_time')}"
    tournament = match.get('tournament_name')
    surface = match.get('tournament_sourface', match.get('surface', 'Unknown'))
    print(f"\nProps for: {player1} vs {player2} | Time: {match_time} | Tournament: {tournament} | Surface: {surface}")
    # Get H2H and player stats
    h2h = get_h2h(player1_key, player2_key) if player1_key and player2_key else None
    p1_stats = get_players(player_key=player1_key) if player1_key else None
    p2_stats = get_players(player_key=player2_key) if player2_key else None
    final_result = None
    if h2h and 'H2H' in h2h and h2h['H2H']:
        final_result = h2h['H2H'][0].get('event_final_result')
    # Core match props
    sets = parse_set_scores(final_result)
    total_games_p1 = sum(s[0] for s in sets) if sets else None
    total_games_p2 = sum(s[1] for s in sets) if sets else None
    total_games_played = sum(sum(s) for s in sets) if sets else None
    total_sets_played = len(sets)
    first_set_winner = None
    if sets:
        if sets[0][0] > sets[0][1]:
            first_set_winner = player1
        elif sets[0][1] > sets[0][0]:
            first_set_winner = player2
    match_winner = None
    if sets:
        sets_won_p1 = sum(1 for set_score in sets if set_score[0] > set_score[1])
        sets_won_p2 = sum(1 for set_score in sets if set_score[1] > set_score[0])
        if sets_won_p1 > sets_won_p2:
            match_winner = player1
        elif sets_won_p2 > sets_won_p1:
            match_winner = player2
    print_json("Total Games Won", {player1: total_games_p1, player2: total_games_p2})
    print_json("Total Games Played", total_games_played)
    print_json("Total Sets Played", total_sets_played)
    print_json("First Set Winner", first_set_winner)
    print_json("Match Winner", match_winner)
    print_json("Set Betting (2-0, 2-1, etc.)", final_result)
    print_json("First Set Score", sets[0] if sets else None)
    print_json("1st Set Total Games", sum(sets[0]) if sets else None)
    # Player performance props (season/career, not per match)
    def extract_stat(stats, stat_name):
        if not stats or not isinstance(stats, list):
            return None
        for s in stats[0].get('stats', []):
            if stat_name in s:
                return s[stat_name]
        return None
    print_json("Aces (season/career)", {player1: extract_stat(p1_stats, 'aces'), player2: extract_stat(p2_stats, 'aces')})
    print_json("Double Faults (season/career)", {player1: extract_stat(p1_stats, 'double_faults'), player2: extract_stat(p2_stats, 'double_faults')})
    print_json("1st Serve % (season/career)", {player1: extract_stat(p1_stats, 'first_serve_percent'), player2: extract_stat(p2_stats, 'first_serve_percent')})
    # Specialty props
    tiebreaks = sum(1 for s in sets if 6 in s and max(s) == 7) if sets else 0
    print_json("Will there be a Tiebreak?", tiebreaks > 0)
    print_json("Total Tiebreaks in Match", tiebreaks)
    print_json("Match to Go to 3 Sets?", total_sets_played == 3)
    print_json("Player to Win a Set?", {player1: any(s[0] > s[1] for s in sets) if sets else None, player2: any(s[1] > s[0] for s in sets) if sets else None})
    print('\n--- End of props for real match ---')

def build_prop_generator(match):
    """Given a match dict, return all available props with data source for each."""
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
    sets = parse_set_scores(final_result)
    props = {}
    props['Total Games Won'] = {
        'value': {player1: sum(s[0] for s in sets) if sets else None, player2: sum(s[1] for s in sets) if sets else None},
        'source': 'H2H/event_final_result'
    }
    props['Total Games Played'] = {
        'value': sum(sum(s) for s in sets) if sets else None,
        'source': 'H2H/event_final_result'
    }
    props['Total Sets Played'] = {
        'value': len(sets),
        'source': 'H2H/event_final_result'
    }
    props['First Set Winner'] = {
        'value': player1 if sets and sets[0][0] > sets[0][1] else player2 if sets and sets[0][1] > sets[0][0] else None,
        'source': 'H2H/event_final_result'
    }
    props['Match Winner'] = {
        'value': player1 if sets and sum(s[0] > s[1] for s in sets) > sum(s[1] > s[0] for s in sets) else player2 if sets and sum(s[1] > s[0] for s in sets) > sum(s[0] > s[1] for s in sets) else None,
        'source': 'H2H/event_final_result'
    }
    props['Set Betting (2-0, 2-1, etc.)'] = {
        'value': final_result,
        'source': 'H2H/event_final_result'
    }
    props['First Set Score'] = {
        'value': sets[0] if sets else None,
        'source': 'H2H/event_final_result'
    }
    props['1st Set Total Games'] = {
        'value': sum(sets[0]) if sets else None,
        'source': 'H2H/event_final_result'
    }
    def extract_stat(stats, stat_name):
        if not stats or not isinstance(stats, list):
            return None
        for s in stats[0].get('stats', []):
            if stat_name in s:
                return s[stat_name]
        return None
    props['Aces (season/career)'] = {
        'value': {player1: extract_stat(p1_stats, 'aces'), player2: extract_stat(p2_stats, 'aces')},
        'source': 'get_players(player_key)/stats'
    }
    props['Double Faults (season/career)'] = {
        'value': {player1: extract_stat(p1_stats, 'double_faults'), player2: extract_stat(p2_stats, 'double_faults')},
        'source': 'get_players(player_key)/stats'
    }
    props['1st Serve % (season/career)'] = {
        'value': {player1: extract_stat(p1_stats, 'first_serve_percent'), player2: extract_stat(p2_stats, 'first_serve_percent')},
        'source': 'get_players(player_key)/stats'
    }
    tiebreaks = sum(1 for s in sets if 6 in s and max(s) == 7) if sets else 0
    props['Will there be a Tiebreak?'] = {
        'value': tiebreaks > 0,
        'source': 'H2H/event_final_result'
    }
    props['Total Tiebreaks in Match'] = {
        'value': tiebreaks,
        'source': 'H2H/event_final_result'
    }
    props['Match to Go to 3 Sets?'] = {
        'value': len(sets) == 3 if sets else None,
        'source': 'H2H/event_final_result'
    }
    props['Player to Win a Set?'] = {
        'value': {player1: any(s[0] > s[1] for s in sets) if sets else None, player2: any(s[1] > s[0] for s in sets) if sets else None},
        'source': 'H2H/event_final_result'
    }
    return props

def run_ai_tennis_analysis():
    """Run tennis analysis with AI integration"""
    print("\n🤖 Ghost AI 4.0 Tennis Analysis Starting...")
    
    # Initialize AI Brain
    ai_brain = AIBrain()
    
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'\nGetting all matches for today: {today}')
    fixtures = get_fixtures(today, date_stop=today)
    
    if not fixtures:
        print('No matches found for today.')
        return
    
    print(f"Found {len(fixtures)} matches for analysis")
    
    for i, match in enumerate(fixtures[:10]):  # Limit to 10 for AI analysis
        player1 = match.get('event_first_player')
        player2 = match.get('event_second_player')
        tournament = match.get('tournament_name')
        surface = match.get('tournament_sourface', match.get('surface', 'Unknown'))
        
        print(f"\n🎾 Analyzing Match {i+1}: {player1} vs {player2}")
        print(f"   Tournament: {tournament} | Surface: {surface}")
        
        # Get match data for AI analysis
        match_data = {
            'player1': player1,
            'player2': player2,
            'tournament': tournament,
            'surface': surface,
            'match_time': f"{match.get('event_date')}T{match.get('event_time')}",
            'player1_key': match.get('first_player_key'),
            'player2_key': match.get('second_player_key')
        }
        
        # Get H2H and stats for AI
        try:
            h2h = get_h2h(match_data['player1_key'], match_data['player2_key']) if match_data['player1_key'] and match_data['player2_key'] else None
            p1_stats = get_players(player_key=match_data['player1_key']) if match_data['player1_key'] else None
            p2_stats = get_players(player_key=match_data['player2_key']) if match_data['player2_key'] else None
            
            match_data['h2h'] = h2h
            match_data['player1_stats'] = p1_stats
            match_data['player2_stats'] = p2_stats
            
            # AI analysis
            ai_analysis = ai_brain.analyze_tennis_match(match_data)
            print(f"🤖 AI Analysis: {ai_analysis}")
            
        except Exception as e:
            print(f"⚠️ Failed to analyze match {player1} vs {player2}: {e}")
    
    print("\n✅ AI Tennis Analysis Complete!")

def run_full_tennis_api_test():
    api_key = os.getenv('TENNIS_API_KEY')
    if not api_key:
        print('❌ TENNIS_API_KEY is not set in your environment!')
        return
    today = datetime.now().strftime('%Y-%m-%d')
    print(f'\nGetting all matches for today: {today}')
    fixtures = get_fixtures(today, date_stop=today)
    if not fixtures:
        print('No matches found for today.')
        return
    for match in fixtures[:5]:  # Limit to 5 for brevity
        player1 = match.get('event_first_player')
        player2 = match.get('event_second_player')
        player1_key = match.get('first_player_key')
        player2_key = match.get('second_player_key')
        match_time = f"{match.get('event_date')}T{match.get('event_time')}"
        tournament = match.get('tournament_name')
        surface = match.get('tournament_sourface', match.get('surface', 'Unknown'))
        print(f"\nMatch: {player1} vs {player2} | Time: {match_time} | Tournament: {tournament} | Surface: {surface}")
        # Player 1 stats
        if player1_key:
            try:
                p1_stats = get_players(player_key=player1_key)
                print_json(f"{player1} stats", p1_stats)
            except Exception as e:
                print(f"⚠️ Failed to get stats for {player1}: {e}")
        # Player 2 stats
        if player2_key:
            try:
                p2_stats = get_players(player_key=player2_key)
                print_json(f"{player2} stats", p2_stats)
            except Exception as e:
                print(f"⚠️ Failed to get stats for {player2}: {e}")
        # H2H
        if player1_key and player2_key:
            try:
                h2h = get_h2h(player1_key, player2_key)
                print_json(f"H2H {player1} vs {player2}", h2h)
            except Exception as e:
                print(f"⚠️ Failed to get H2H: {e}")
        # Live score
        if match.get('event_live') == '1':
            try:
                livescore = get_livescore(match_key=match.get('event_key'))
                print_json(f"Live score {player1} vs {player2}", livescore)
            except Exception as e:
                print(f"⚠️ Failed to get live score: {e}")
        # Last 3 completed matches for each player (from stats)
        for player, key in [(player1, player1_key), (player2, player2_key)]:
            if key:
                try:
                    stats = get_players(player_key=key)
                    if stats and isinstance(stats, list) and 'tournaments' in stats[0]:
                        tournaments = stats[0]['tournaments']
                        print_json(f"{player} tournaments (last 3)", tournaments[:3])
                except Exception as e:
                    print(f"⚠️ Failed to get last 3 matches for {player}: {e}")
    print('\n✅ Full Tennis API test completed!')

if __name__ == '__main__':
    print('\n🎾 Ghost AI 4.0 Tennis Fetch System')
    print('=' * 50)
    
    # Run AI-powered tennis analysis
    run_ai_tennis_analysis()
    
    print('\n=== PROPS FOR REAL MATCH ===')
    show_props_for_real_match()
    print('\n=== PROP GENERATOR DEMO ===')
    today = datetime.now().strftime('%Y-%m-%d')
    fixtures = get_fixtures(today, date_stop=today)
    if fixtures:
        props = build_prop_generator(fixtures[0])
        print_json('All props for first match (with data source)', props)
    print('\n✅ Tennis prop extraction/generation test complete!') 