import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

TENNIS_API_KEY = os.getenv('TENNIS_API_KEY')
BASE_URL = 'https://api.api-tennis.com/tennis/'

def _api_call(method: str, params: Optional[Dict[str, Any]] = None) -> Any:
    if not TENNIS_API_KEY:
        raise RuntimeError('TENNIS_API_KEY not set in .env!')
    params = params or {}
    params['method'] = method
    params['APIkey'] = TENNIS_API_KEY
    response = requests.get(BASE_URL, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    if not data.get('success'):
        raise RuntimeError(f"API error: {data}")
    return data.get('result')

def get_event_types() -> Any:
    """Get all event types (ATP, WTA, Challenger, etc)."""
    return _api_call('get_events')

def get_tournaments(event_type_key: Optional[str] = None) -> Any:
    """Get all tournaments, optionally filter by event_type_key."""
    params = {}
    if event_type_key:
        params['event_type_key'] = event_type_key
    return _api_call('get_tournaments', params)

def get_fixtures(date_start: str, date_stop: Optional[str] = None, event_type_key: Optional[str] = None, tournament_key: Optional[str] = None) -> Any:
    """Get fixtures (matches) for a date range, optionally filter by event/tournament."""
    params = {'date_start': date_start}
    if date_stop:
        params['date_stop'] = date_stop
    if event_type_key:
        params['event_type_key'] = event_type_key
    if tournament_key:
        params['tournament_key'] = tournament_key
    return _api_call('get_fixtures', params)

def get_odds(match_key: str) -> Any:
    """Get pre-match odds for a specific match."""
    params = {'match_key': match_key}
    return _api_call('get_odds', params)

def get_live_odds(event_type_key: Optional[str] = None, tournament_key: Optional[str] = None, match_key: Optional[str] = None) -> Any:
    """Get live odds for matches (optionally filter by event/tournament/match)."""
    params = {}
    if event_type_key:
        params['event_type_key'] = event_type_key
    if tournament_key:
        params['tournament_key'] = tournament_key
    if match_key:
        params['match_key'] = match_key
    return _api_call('get_live_odds', params)

def get_players(player_key: Optional[str] = None) -> Any:
    """Get all players, or details for a specific player if player_key is provided."""
    params = {}
    if player_key:
        params['player_key'] = player_key
    return _api_call('get_players', params)

def get_standings(event_type: Optional[str] = None, tournament_key: Optional[str] = None) -> Any:
    """Get standings for an event type (string, e.g. 'Atp Singles') or tournament."""
    params = {}
    if event_type:
        params['event_type'] = event_type
    if tournament_key:
        params['tournament_key'] = tournament_key
    return _api_call('get_standings', params)

def get_h2h(player1_key: str, player2_key: str) -> Any:
    """Get head-to-head stats for two players using first_player_key and second_player_key as parameters."""
    params = {'first_player_key': str(player1_key), 'second_player_key': str(player2_key)}
    return _api_call('get_H2H', params)

def get_livescore(event_type_key: Optional[str] = None, tournament_key: Optional[str] = None, match_key: Optional[str] = None) -> Any:
    """Get live scores for matches (optionally filter by event/tournament/match)."""
    params = {}
    if event_type_key:
        params['event_type_key'] = event_type_key
    if tournament_key:
        params['tournament_key'] = tournament_key
    if match_key:
        params['match_key'] = match_key
    return _api_call('get_livescore', params) 