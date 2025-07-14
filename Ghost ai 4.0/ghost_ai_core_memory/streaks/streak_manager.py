import json
import os
from datetime import datetime

STREAKS_FILE = os.path.join(os.path.dirname(__file__), 'active_streaks.json')
MAX_STREAKS = 3
MIN_ODDS = -120  # Minimum allowed odds for streak picks

def load_streaks():
    if not os.path.exists(STREAKS_FILE):
        return []
    with open(STREAKS_FILE, 'r') as f:
        return json.load(f)

def save_streaks(streaks):
    with open(STREAKS_FILE, 'w') as f:
        json.dump(streaks, f, indent=2)

def get_active_streaks():
    streaks = load_streaks()
    return [s for s in streaks if s.get('status', 'active') == 'active']

def can_create_streak():
    return len(get_active_streaks()) < MAX_STREAKS

def create_streak(player_name, prop, odds):
    if odds < MIN_ODDS:
        return None  # Do not allow low-odds streaks
    if not can_create_streak():
        return None
    streaks = load_streaks()
    streak = {
        'id': f'streak_{len(streaks)+1}',
        'player_name': player_name,
        'prop': prop,
        'odds': odds,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'active',
        'wins': 0,
        'losses': 0
    }
    streaks.append(streak)
    save_streaks(streaks)
    return streak

def update_streak_win(streak_id):
    streaks = load_streaks()
    for s in streaks:
        if s['id'] == streak_id and s['status'] == 'active':
            s['wins'] += 1
            s['last_updated'] = datetime.utcnow().isoformat()
    save_streaks(streaks)

def end_streak(streak_id):
    streaks = load_streaks()
    for s in streaks:
        if s['id'] == streak_id and s['status'] == 'active':
            s['status'] = 'ended'
            s['ended_at'] = datetime.utcnow().isoformat()
            s['losses'] += 1
    save_streaks(streaks) 