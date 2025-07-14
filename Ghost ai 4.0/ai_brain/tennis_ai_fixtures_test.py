#!/usr/bin/env python3
"""
Ghost AI 4.0 - Tennis AI Fixture & Player Test
AI-centric test for fetching tennis fixtures, star player detection, and prop generation.
"""

from ai_brain.tennis_api_client import get_fixtures, get_players, get_h2h, get_event_types, get_tournaments, get_odds, get_live_odds, get_standings
from datetime import datetime, timedelta
import json

AI_STAR_PLAYERS = set([
    # ATP Top 50
    "N. Djokovic", "C. Alcaraz", "J. Sinner", "D. Medvedev", "A. Zverev", "A. Rublev", "S. Tsitsipas", "H. Hurkacz",
    "C. Ruud", "T. Fritz", "G. Dimitrov", "A. de Minaur", "H. Rune", "T. Paul", "B. Shelton", "S. Korda",
    "F. Tiafoe", "F. Auger-Aliassime", "K. Khachanov", "N. Jarry", "U. Humbert", "A. Mannarino", "A. Tabilo", "S. Baez",
    "T. M. Etcheverry", "L. Musetti", "J. L. Struff", "A. Bublik", "T. Griekspoor", "J. Thompson", "C. Eubanks", "M. Purcell",
    "M. Giron", "D. Evans", "A. Murray", "S. Wawrinka", "D. Thiem", "G. Monfils", "R. Gasquet", "F. Fognini",
    "R. Bautista Agut", "P. Carreno Busta", "A. Ramos-Vinolas", "F. Coria", "P. Cachin", "T. Seyboth Wild", "F. Diaz Acosta", "L. Darderi",
    "F. Cobolli", "J. Mensik", "A. Fils", "L. Van Assche",
    # WTA Top 50
    "I. Swiatek", "A. Sabalenka", "C. Gauff", "E. Rybakina", "J. Pegula", "O. Jabeur", "M. Vondrousova", "Q. Zheng",
    "M. Sakkari", "K. Muchova", "B. Krejcikova", "B. Haddad Maia", "D. Kasatkina", "L. Samsonova", "V. Kudermetova", "E. Alexandrova",
    "M. Keys", "E. Svitolina", "C. Garcia", "J. Ostapenko", "V. Azarenka", "A. Pavlyuchenkova", "S. Stephens", "S. Kenin",
    "D. Collins", "A. Riske-Amritraj", "B. Pera", "K. Siniakova", "P. Martic", "D. Vekic", "M. Bouzkova", "A. Kalinina",
    "M. Kostyuk", "L. Tsurenko", "V. Tomova", "A. Blinkova", "D. Parry", "C. Burel", "D. Shnaider", "M. Andreeva",
    "L. Noskova", "E. Navarro", "P. Stearns", "A. Krueger", "K. Day", "S. Vickery", "K. Volynets", "R. Montgomery",
    "C. Ngounoue", "L. Hovde", "A. Eala", "B. Fruhvirtova"
])


def ai_fixtures_and_star_players_test():
    """AI-driven test: fetch fixtures, detect star players, and print props."""
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"\n[AI] Fetching tennis fixtures for {today}...")
    fixtures = get_fixtures(today, date_stop=today)
    if not fixtures:
        print("[AI] No fixtures found for today.")
        return
    print(f"[AI] Total fixtures: {len(fixtures)}")

    # Detect star player matches
    star_matches = []
    for match in fixtures:
        p1 = match.get('event_first_player', '').strip()
        p2 = match.get('event_second_player', '').strip()
        if p1 in AI_STAR_PLAYERS or p2 in AI_STAR_PLAYERS:
            star_matches.append(match)
    print(f"[AI] Star player matches: {len(star_matches)}")
    for i, match in enumerate(star_matches[:10], 1):
        p1 = match.get('event_first_player', 'Unknown')
        p2 = match.get('event_second_player', 'Unknown')
        tournament = match.get('tournament_name', 'Unknown')
        event_type = match.get('event_type_type', 'Unknown')
        event_time = match.get('event_time', 'Unknown')
        print(f"  {i}. {p1} vs {p2} | {tournament} | {event_type} | {event_time}")

    # Optionally, generate props for the first star match
    if star_matches:
        print("\n[AI] Generating props for first star match:")
        match = star_matches[0]
        props = ai_generate_tennis_props(match)
        for p in props:
            print(json.dumps(p, indent=2))


def ai_generate_tennis_props(match):
    """AI-style prop generation for a tennis match."""
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
    # Add more prop logic as needed...
    return props


def main():
    print("\n=== Ghost AI 4.0 Tennis AI Fixture & Player Test ===")
    ai_fixtures_and_star_players_test()

if __name__ == "__main__":
    main() 