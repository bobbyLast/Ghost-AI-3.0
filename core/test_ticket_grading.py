import os
import json
import requests
from pathlib import Path
from datetime import datetime, timezone

ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
UNIFIED_TICKETS_DIR = Path('ghost_ai_core_memory/tickets/unified')


def fetch_game_results(sport_key, event_id):
    url = f"{ODDS_API_BASE_URL}/sports/{sport_key}/scores"
    params = {
        'apiKey': ODDS_API_KEY,
        'daysFrom': 1
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        print(f"Error fetching results: {resp.status_code} {resp.text}")
        return None
    data = resp.json()
    for event in data:
        if event.get('id') == event_id:
            return event
    return None

def grade_ticket(ticket, sport_key):
    event_id = ticket.get('game_id') or ticket.get('id')
    if not event_id:
        return None
    result = fetch_game_results(sport_key, event_id)
    if not result or not result.get('completed'):
        return None  # Game not finished or not found
    for selection in ticket.get('selections', []) + ticket.get('picks', []):
        stat_type = selection.get('prop_type') or selection.get('stat_type')
        player = selection.get('player_name') or selection.get('player')
        line = selection.get('line')
        pick = selection.get('pick', 'over').lower()
        player_stats = None
        for participant in result.get('participants', []):
            if player and player.lower() in participant.get('name', '').lower():
                player_stats = participant.get('statistics', {})
                break
        if player_stats and stat_type in player_stats:
            actual = player_stats[stat_type]
            if pick == 'over':
                selection['result'] = 'win' if actual > line else 'loss'
            elif pick == 'under':
                selection['result'] = 'win' if actual < line else 'loss'
            else:
                selection['result'] = 'push' if actual == line else 'loss'
        else:
            selection['result'] = 'unknown'
    ticket['graded'] = True
    return ticket

def main():
    ticket_files = list(UNIFIED_TICKETS_DIR.glob('*.json'))
    total = 0
    graded = 0
    streak_total = 0
    streak_graded = 0
    for ticket_file in ticket_files:
        with open(ticket_file, 'r', encoding='utf-8') as f:
            ticket = json.load(f)
        total += 1
        sport_key = ticket.get('sport_key', 'baseball_mlb')
        graded_ticket = grade_ticket(ticket, sport_key)
        if graded_ticket:
            graded += 1
        # Check for streak tickets
        ticket_type = ticket.get('ticket_type', '').lower()
        if 'streak' in ticket_type:
            streak_total += 1
            if graded_ticket:
                streak_graded += 1
    print(f"Graded {graded} out of {total} unified tickets.")
    print(f"Streak tickets graded: {streak_graded} out of {streak_total}.")

if __name__ == "__main__":
    main() 