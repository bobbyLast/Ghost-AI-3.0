"""
MLB Teams and Players Configuration
"""

import json
from pathlib import Path
from typing import Dict, List, Any

def load_mlb_rosters() -> Dict[str, Dict[str, Any]]:
    """Load MLB rosters from the roster file and convert to MLB_PLAYERS format."""
    try:
        roster_file = Path(__file__).parent.parent / "data" / "mlb" / "rosters" / "mlb_rosters_2024.json"
        if not roster_file.exists():
            print(f"Warning: MLB roster file not found at {roster_file}")
            return {}
        
        with open(roster_file, 'r', encoding='utf-8') as f:
            roster_data = json.load(f)
        
        mlb_players = {}
        
        for team_data in roster_data.get('teams', []):
            team_name = team_data.get('team', '')
            if not team_name:
                continue
                
            players = {}
            for player in team_data.get('players', []):
                player_name = player.get('name', '')
                if player_name:
                    players[player_name] = {
                        'position': player.get('position', ''),
                        'status': player.get('status', 'Active')
                    }
            
            if players:
                mlb_players[team_name] = players
        
        print(f"Loaded {len(mlb_players)} MLB teams with {sum(len(players) for players in mlb_players.values())} total players")
        return mlb_players
        
    except Exception as e:
        print(f"Error loading MLB rosters: {e}")
        return {}

# Load MLB players data
MLB_PLAYERS = load_mlb_rosters()

def get_team_abbreviation(team_name: str) -> str:
    """Get team abbreviation from full team name."""
    team_abbreviations = {
        "Arizona Diamondbacks": "ARI",
        "Atlanta Braves": "ATL", 
        "Baltimore Orioles": "BAL",
        "Boston Red Sox": "BOS",
        "Chicago Cubs": "CHC",
        "Chicago White Sox": "CWS",
        "Cincinnati Reds": "CIN",
        "Cleveland Guardians": "CLE",
        "Colorado Rockies": "COL",
        "Detroit Tigers": "DET",
        "Houston Astros": "HOU",
        "Kansas City Royals": "KC",
        "Los Angeles Angels": "LAA",
        "Los Angeles Dodgers": "LAD",
        "Miami Marlins": "MIA",
        "Milwaukee Brewers": "MIL",
        "Minnesota Twins": "MIN",
        "New York Mets": "NYM",
        "New York Yankees": "NYY",
        "Oakland Athletics": "OAK",
        "Philadelphia Phillies": "PHI",
        "Pittsburgh Pirates": "PIT",
        "San Diego Padres": "SD",
        "San Francisco Giants": "SF",
        "Seattle Mariners": "SEA",
        "St. Louis Cardinals": "STL",
        "Tampa Bay Rays": "TB",
        "Texas Rangers": "TEX",
        "Toronto Blue Jays": "TOR",
        "Washington Nationals": "WSH"
    }
    
    return team_abbreviations.get(team_name, team_name[:3].upper())

def get_player_team(player_name: str) -> str:
    """Get the team name for a given player."""
    for team_name, players in MLB_PLAYERS.items():
        if player_name in players:
            return team_name
    return ""

def get_team_players(team_name: str) -> List[str]:
    """Get list of player names for a given team."""
    return list(MLB_PLAYERS.get(team_name, {}).keys())
