#!/usr/bin/env python3
"""
fade_detector.py - The Sniper for Ghost AI 3.0
Centralizes all fade detection logic and triggers auto-fades. Enforces no-dup logic.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger('fade_detector')

class FadeDetector:
    def __init__(self, memory_manager, fantasy_calculator):
        self.memory_manager = memory_manager
        self.fantasy_calculator = fantasy_calculator
        logger.info("🔥 Fade Detector initialized")

    def detect_fades(self, props: List[Dict[str, Any]], sport: str) -> List[Dict[str, Any]]:
        """
        Detect and return auto-fade picks. Enforce no-dup logic.
        Args:
            props: List of normalized props
            sport: Sport type
        Returns:
            List of fade picks (auto-under)
        """
        fades = []
        for player, player_props in self._group_by_player(props).items():
            if self.memory_manager.is_player_used_today(player):
                logger.info(f"[NO-DUP] Skipping fade for already used player: {player}")
                continue
            fade_pick = self._detect_fade_for_player(player_props, sport)
            if fade_pick and not self.memory_manager.is_prop_used_today(fade_pick):
                fades.append(fade_pick)
                self.memory_manager.mark_prop_used(fade_pick, player)
        logger.info(f"🔥 Detected {len(fades)} auto-fades (no dups)")
        return fades

    def _group_by_player(self, props: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        grouped = {}
        for prop in props:
            player = prop.get('player_name', '')
            if player:
                grouped.setdefault(player, []).append(prop)
        return grouped

    def _detect_fade_for_player(self, player_props: List[Dict[str, Any]], sport: str) -> Any:
        # Fantasy score threshold
        is_low, fantasy_score = self.fantasy_calculator.is_low_fantasy_player(player_props, sport)
        if is_low:
            # Only 0.5 lines or missing combos
            has_only_low_lines = self.fantasy_calculator._has_only_low_lines(player_props, sport)
            has_combo = any('combo' in p.get('tag', '') or '+' in p.get('prop_type', '').lower() for p in player_props)
            if has_only_low_lines or not has_combo:
                # Auto-fade: post under on fantasy or HRR
                fade_pick = self.fantasy_calculator.get_fantasy_fade_pick(player_props, sport)
                if fade_pick:
                    fade_pick['auto_fade'] = True
                    fade_pick['fade_reason'] = f"Low fantasy ({fantasy_score}), weak board, no combos"
                    return fade_pick
        return None 