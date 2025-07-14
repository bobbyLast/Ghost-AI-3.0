"""
prop_context_filter.py - Prop Context Filter for Ghost AI

Adjusts prop confidence based on moneyline context (sentiment, trap, blowout),
penalizes/boosts props, and blocks props that contradict the moneyline read.
"""

import logging
from typing import List, Dict

logger = logging.getLogger("prop_context_filter")

class PropContextFilter:
    """
    Applies moneyline context to prop confidence and eligibility.
    """
    def __init__(self):
        pass

    def apply_ml_context(self, props: List[Dict], ml_sentiment: Dict) -> List[Dict]:
        """
        Adjusts prop confidence and eligibility based on moneyline sentiment/trap/blowout.
        Returns a new list of props with updated confidence and flags.
        """
        updated = []
        for prop in props:
            team = prop.get('team') or prop.get('team_name')
            if not team or team not in ml_sentiment:
                updated.append(prop)
                continue
            sentiment = ml_sentiment[team]
            conf = prop.get('confidence', 0.5)
            # Penalize if trap or high blowout risk
            if sentiment.get('trap'):
                conf = max(0.0, conf - 0.12)
                prop['ml_flag'] = 'trap_penalty'
            if sentiment.get('blowout_risk', 0) > 0.5:
                conf = max(0.0, conf - 0.10)
                prop['ml_flag'] = 'blowout_penalty'
            # Boost if bullish
            if sentiment.get('sentiment') == 'bullish':
                conf = min(1.0, conf + 0.08)
                prop['ml_flag'] = 'bullish_boost'
            prop['confidence'] = conf
            updated.append(prop)
        return updated

    def block_contradictory_props(self, props: List[Dict], ml_sentiment: Dict) -> List[Dict]:
        """
        Removes or flags props that contradict the moneyline read (e.g., fading a star on a team we're backing ML).
        """
        filtered = []
        for prop in props:
            team = prop.get('team') or prop.get('team_name')
            if not team or team not in ml_sentiment:
                filtered.append(prop)
                continue
            sentiment = ml_sentiment[team]
            # Example: if ML is bullish but prop is an under/fade, block
            if sentiment.get('sentiment') == 'bullish' and prop.get('pick_side', '').lower() == 'under':
                prop['blocked'] = True
                prop['block_reason'] = 'contradicts ML bullish'
                continue
            filtered.append(prop)
        return filtered 