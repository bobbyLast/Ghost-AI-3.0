"""
Prop Types Configuration

This file contains all the prop types supported by the OddsAPI for different sports.
"""

# Basketball (NBA, WNBA, NCAAB) Player Props
BASKETBALL_PROPS = {
    'standard': [
        'player_points',
        'player_points_q1',
        'player_rebounds',
        'player_rebounds_q1',
        'player_assists',
        'player_assists_q1',
        'player_threes',
        'player_blocks',
        'player_steals',
        'player_blocks_steals',
        'player_turnovers',
        'player_points_rebounds_assists',
        'player_points_rebounds',
        'player_points_assists',
        'player_rebounds_assists',
        'player_field_goals',
        'player_frees_made',
        'player_frees_attempts',
        'player_first_basket',
        'player_first_team_basket',
        'player_double_double',
        'player_triple_double',
        'player_method_of_first_basket'
    ],
    'alternate': [
        'player_points_alternate',
        'player_rebounds_alternate',
        'player_assists_alternate',
        'player_blocks_alternate',
        'player_steals_alternate',
        'player_turnovers_alternate',
        'player_threes_alternate',
        'player_points_assists_alternate',
        'player_points_rebounds_alternate',
        'player_rebounds_assists_alternate',
        'player_points_rebounds_assists_alternate'
    ]
}

# MLB Player Props
MLB_PROPS = {
    'batter': [
        'batter_home_runs',
        'batter_first_home_run',
        'batter_hits',
        'batter_total_bases',
        'batter_rbis',
        'batter_runs_scored',
        'batter_hits_runs_rbis',
        'batter_singles',
        'batter_doubles',
        'batter_triples',
        'batter_walks',
        'batter_strikeouts',
        'batter_stolen_bases'
    ],
    'pitcher': [
        'pitcher_strikeouts',
        'pitcher_record_a_win',
        'pitcher_hits_allowed',
        'pitcher_walks',
        'pitcher_earned_runs',
        'pitcher_outs'
    ],
    'alternate': [
        'batter_total_bases_alternate',
        'batter_home_runs_alternate',
        'batter_hits_alternate',
        'batter_rbis_alternate',
        'batter_walks_alternate',
        'pitcher_hits_allowed_alternate',
        'pitcher_walks_alternate',
        'pitcher_strikeouts_alternate'
    ]
}

# Helper functions to get all props for a sport
def get_all_basketball_props() -> list:
    """Get all basketball prop types."""
    return BASKETBALL_PROPS['standard'] + BASKETBALL_PROPS['alternate']

def get_all_mlb_props() -> list:
    """Get all MLB prop types."""
    return (MLB_PROPS['batter'] + 
            MLB_PROPS['pitcher'] + 
            MLB_PROPS['alternate'])

def get_props_by_sport(sport: str) -> list:
    """Get all prop types for a specific sport."""
    sport = sport.lower()
    if sport in ['basketball_nba', 'basketball_wnba', 'basketball_ncaab']:
        return get_all_basketball_props()
    elif sport == 'baseball_mlb':
        return get_all_mlb_props()
    else:
        return []

def is_alternate_prop(prop_type: str) -> bool:
    """Check if a prop type is an alternate prop."""
    return prop_type.endswith('_alternate')

def get_prop_category(prop_type: str) -> str:
    """Get the category of a prop type."""
    if prop_type in MLB_PROPS['batter']:
        return 'batter'
    elif prop_type in MLB_PROPS['pitcher']:
        return 'pitcher'
    elif prop_type in MLB_PROPS['alternate']:
        return 'alternate'
    elif prop_type in BASKETBALL_PROPS['standard']:
        return 'standard'
    elif prop_type in BASKETBALL_PROPS['alternate']:
        return 'alternate'
    else:
        return 'unknown' 