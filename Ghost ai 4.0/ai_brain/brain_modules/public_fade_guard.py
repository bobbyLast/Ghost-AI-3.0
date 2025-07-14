"""
public_fade_guard.py - Public Fade Guard for Ghost AI

Uses public bet % and line movement to detect fade-the-public spots, auto-fades MLs/props that are public traps,
and applies confidence penalties or blocks posting as needed.
"""

import logging
from typing import Dict

logger = logging.getLogger("public_fade_guard")

class PublicFadeGuard:
    """
    Detects and blocks public trap spots for MLs and props.
    """
    def __init__(self):
        pass

    def is_trap(self, team: str, odds: int, public_bet_pct: float, line_movement: int) -> bool:
        """
        Returns True if this is a public trap spot (e.g., 70%+ public, odds move against).
        """
        trap = False
        if public_bet_pct >= 0.7 and line_movement > 0:
            trap = True
        if trap:
            logger.info(f"Public trap detected for {team}: {public_bet_pct*100:.1f}% public, line moved {line_movement} against")
        return trap

    def apply_penalty(self, confidence: float) -> float:
        """
        Applies a confidence penalty for public trap spots.
        """
        penalty = 0.15
        new_conf = max(0.0, confidence - penalty)
        logger.info(f"Applied public fade penalty: {confidence:.2f} -> {new_conf:.2f}")
        return new_conf 