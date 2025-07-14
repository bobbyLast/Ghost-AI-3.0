from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

def find_best_roster_match(clean_name_variations, roster_data) -> Optional[Tuple[str, str]]:
    """Find the best matching player/team from roster data given name variations."""
    best_match = None
    best_score = 0
    for roster_player, player_info in roster_data.items():
        roster_clean = roster_player.strip().lower()
        for variation in clean_name_variations:
            if variation in roster_clean or roster_clean in variation:
                score = len(set(variation.split()) & set(roster_clean.split()))
                if score > best_score:
                    best_score = score
                    best_match = (roster_player, player_info['team'])
            if (variation == roster_clean.replace(' jr', '').replace(' sr', '').replace(' iii', '').replace(' ii', '').replace(' iv', '')):
                best_match = (roster_player, player_info['team'])
                break
    return best_match 