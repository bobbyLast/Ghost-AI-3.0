"""
Basketball Prop Market Definitions

This file contains all available player prop markets for basketball (NBA, WNBA, NCAAB).
"""

# Standard Player Prop Markets
STANDARD_PLAYER_PROPS = [
    # Basic Stats
    'player_points',  # Points (Over/Under)
    'player_rebounds',  # Rebounds (Over/Under)
    'player_assists',  # Assists (Over/Under)
    'player_threes',  # Threes (Over/Under)
    'player_blocks',  # Blocks (Over/Under)
    'player_steals',  # Steals (Over/Under)
    'player_turnovers',  # Turnovers (Over/Under)
    
    # Combined Stats
    'player_blocks_steals',  # Blocks + Steals (Over/Under)
    'player_points_rebounds',  # Points + Rebounds (Over/Under)
    'player_points_assists',  # Points + Assists (Over/Under)
    'player_rebounds_assists',  # Rebounds + Assists (Over/Under)
    'player_points_rebounds_assists',  # Pts + Reb + Ast (Over/Under)
    
    # Shooting
    'player_field_goals',  # Field Goals (Over/Under)
    'player_frees_made',  # Frees made (Over/Under)
    'player_frees_attempts',  # Frees attempted (Over/Under)
    
    # Quarter Props
    'player_points_q1',  # 1st Quarter Points (Over/Under)
    'player_rebounds_q1',  # 1st Quarter Rebounds (Over/Under)
    'player_assists_q1',  # 1st Quarter Assists (Over/Under)
    
    # Specials
    'player_first_basket',  # First Basket Scorer (Yes/No)
    'player_first_team_basket',  # First Basket Scorer on Team (Yes/No)
    'player_double_double',  # Double Double (Yes/No)
    'player_triple_double',  # Triple Double (Yes/No)
    'player_method_of_first_basket'  # Method of First Basket (Various)
]

# Alternate Player Prop Markets (X+ lines and alternate lines)
ALTERNATE_PLAYER_PROPS = [
    'player_points_alternate',  # Alternate Points (Over/Under)
    'player_rebounds_alternate',  # Alternate Rebounds (Over/Under)
    'player_assists_alternate',  # Alternate Assists (Over/Under)
    'player_blocks_alternate',  # Alternate Blocks (Over/Under)
    'player_steals_alternate',  # Alternate Steals (Over/Under)
    'player_turnovers_alternate',  # Alternate Turnovers (Over/Under)
    'player_threes_alternate',  # Alternate Threes (Over/Under)
    'player_points_assists_alternate',  # Alternate Points + Assists (Over/Under)
    'player_points_rebounds_alternate',  # Alternate Points + Rebounds (Over/Under)
    'player_rebounds_assists_alternate',  # Alternate Rebounds + Assists (Over/Under)
    'player_points_rebounds_assists_alternate'  # Alternate Pts + Reb + Ast (Over/Under)
]

# All available player props
ALL_PLAYER_PROPS = STANDARD_PLAYER_PROPS + ALTERNATE_PLAYER_PROPS

# Prop categories for filtering
PROP_CATEGORIES = {
    'scoring': ['player_points', 'player_threes', 'player_points_q1'],
    'rebounding': ['player_rebounds', 'player_rebounds_q1'],
    'playmaking': ['player_assists', 'player_assists_q1', 'player_turnovers'],
    'defense': ['player_blocks', 'player_steals', 'player_blocks_steals'],
    'combined': [
        'player_points_rebounds',
        'player_points_assists',
        'player_rebounds_assists',
        'player_points_rebounds_assists'
    ],
    'shooting': [
        'player_field_goals',
        'player_frees_made',
        'player_frees_attempts',
        'player_threes'
    ],
    'specials': [
        'player_first_basket',
        'player_first_team_basket',
        'player_double_double',
        'player_triple_double',
        'player_method_of_first_basket'
    ]
}

def get_props_by_category(category: str) -> list:
    """
    Get all props in a specific category.
    
    Args:
        category: The category name (e.g., 'scoring', 'defense')
        
    Returns:
        List of prop market keys in the category
    """
    return PROP_CATEGORIES.get(category.lower(), [])

def is_valid_prop(prop_key: str) -> bool:
    """
    Check if a prop key is valid.
    
    Args:
        prop_key: The prop market key to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    return prop_key in ALL_PLAYER_PROPS

def is_alternate_prop(prop_key: str) -> bool:
    """
    Check if a prop is an alternate line.
    
    Args:
        prop_key: The prop market key to check
        
    Returns:
        bool: True if alternate, False otherwise
    """
    return prop_key in ALTERNATE_PLAYER_PROPS
