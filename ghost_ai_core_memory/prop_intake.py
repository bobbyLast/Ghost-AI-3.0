#!/usr/bin/env python3
"""
prop_intake.py - The Scout for Ghost AI 3.0
Pulls and normalizes props from all books, tags, and logs partial info for re-evaluation.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger('prop_intake')

PROP_TAGS = [
    'normal', 'combo', 'boost', 'trap', 'low-volume', 'fade-candidate', 'elite'
]

class PropIntake:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        logger.info("📥 Prop Intake initialized")

    def normalize_props(self, raw_props: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
        """
        Normalize raw props from a sportsbook or vault.
        Args:
            raw_props: List of raw prop dicts
            source: Source name (e.g., 'FanDuel', 'DK', 'Vault')
        Returns:
            List of normalized and tagged props
        """
        normalized = []
        for prop in raw_props:
            norm = self._normalize_single_prop(prop, source)
            tag = self._tag_prop(norm)
            norm['tag'] = tag
            norm['source'] = source
            norm['intake_time'] = datetime.now().isoformat()
            # Flag missing lines
            if self._has_missing_lines(norm):
                norm['flagged_missing'] = True
                self._log_partial_info(norm)
            normalized.append(norm)
        logger.info(f"📥 Normalized {len(normalized)} props from {source}")
        return normalized

    def _normalize_single_prop(self, prop: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Standardize prop fields across sources."""
        norm = {
            'player_name': prop.get('player', prop.get('player_name', 'Unknown')),
            'prop_type': prop.get('type', prop.get('prop_type', 'Unknown')),
            'line': prop.get('line', prop.get('value', 0)),
            'odds': prop.get('odds', 0),
            'pick_side': prop.get('side', prop.get('pick_side', 'Over')),
            'game_key': prop.get('game_key', ''),
            'team': prop.get('team', ''),
            'opponent': prop.get('opponent', ''),
            'sport': prop.get('sport', ''),
            'raw': prop,
        }
        return norm

    def _tag_prop(self, prop: Dict[str, Any]) -> str:
        """Tag prop as normal, combo, boost, trap, low-volume, fade-candidate, or elite."""
        # Combo
        if any(x in prop.get('prop_type', '').lower() for x in ['combo', 'hrr', '+']):
            return 'combo'
        # Boost
        if prop.get('odds', 0) > 300:
            return 'boost'
        # Trap
        if prop.get('odds', 0) < -170:
            return 'trap'
        # Low-volume
        if prop.get('line', 0) == 0.5:
            return 'low-volume'
        # Fade-candidate
        if prop.get('line', 0) < 1.0 and prop.get('odds', 0) < 0:
            return 'fade-candidate'
        # Elite
        if prop.get('odds', 0) >= 100 and prop.get('line', 0) > 2:
            return 'elite'
        # Normal
        return 'normal'

    def _has_missing_lines(self, prop: Dict[str, Any]) -> bool:
        """Detect if a prop is missing key lines (e.g., Hits present, but no RBIs)."""
        # Example: If prop_type is Hits, but no RBIs or HR for this player in memory
        player = prop.get('player_name', '')
        prop_type = prop.get('prop_type', '')
        if prop_type == 'Hits':
            # Check if RBIs or HR are missing for this player today
            today_props = self.memory_manager.memory['daily_tracking'][self.memory_manager.today]
            player_props = [p for p in today_props.get('props_used', set()) if player in p]
            if not any('RBIs' in p or 'Home Runs' in p for p in player_props):
                return True
        return False

    def _log_partial_info(self, prop: Dict[str, Any]):
        """Log partial info to memory for later re-evaluation."""
        # Store in memory manager under a 'partial_info' section
        self.memory_manager.memory.setdefault('partial_info', {})
        player = prop.get('player_name', 'Unknown')
        prop_type = prop.get('prop_type', 'Unknown')
        self.memory_manager.memory['partial_info'].setdefault(player, {})
        self.memory_manager.memory['partial_info'][player][prop_type] = {
            'prop': prop,
            'timestamp': datetime.now().isoformat()
        }
        self.memory_manager._save_memory()
        logger.info(f"📥 Logged partial info for {player} {prop_type}") 