"""
ev_evaluator.py - EV Evaluator for Moneyline Bets in Ghost AI

Calculates true expected value (EV) for every ML bet, only posts ML bets with EV > 0.08,
and flags premium MLs. Logs all calculations for transparency.
"""

import logging
from typing import Dict

logger = logging.getLogger("ev_evaluator")

class EVEvaluator:
    """
    Evaluates expected value (EV) for moneyline bets.
    """
    def __init__(self):
        pass

    def calculate_ev(self, ghost_win_prob: float, payout: float) -> float:
        """
        Calculates expected value (EV) for a moneyline bet.
        EV = (ghost_win_prob * payout) - ((1 - ghost_win_prob) * 1)
        Returns EV as a float (e.g., 0.12 for 12% ROI).
        """
        # payout is decimal odds (e.g., 1.91 for -110)
        ev = (ghost_win_prob * payout) - (1 - ghost_win_prob)
        return round(ev, 4)

    def is_premium_ev(self, ev: float) -> bool:
        """
        Returns True if EV is above the premium threshold (e.g., 0.08).
        """
        return ev > 0.08

    def log_ev_calculation(self, team: str, odds: int, ghost_win_prob: float, ev: float):
        """
        Logs the EV calculation for transparency and audit.
        """
        logger.info(f"EV for {team}: odds={odds}, ghost_win_prob={ghost_win_prob:.3f}, EV={ev:.3f}") 