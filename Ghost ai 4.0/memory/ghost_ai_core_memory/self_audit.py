#!/usr/bin/env python3
"""
self_audit.py - The Conscience for Ghost AI 3.0
Centralizes end-of-day review, self-reflection, and improvement logging. Enforces no-dup logic.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger('self_audit')

class SelfAudit:
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        logger.info("🪞 Self-Audit initialized")

    def run_end_of_day_audit(self, posted_tickets: List[Dict[str, Any]], all_props: List[Dict[str, Any]]):
        """
        Review daily decisions, log missed fades/rules, and store reflections. Enforce no-dup logic.
        Args:
            posted_tickets: List of tickets posted today
            all_props: All props seen today
        """
        reflections = []
        # Missed fades: props that should have been faded but were posted
        for ticket in posted_tickets:
            for selection in ticket.get('selections', []):
                if self._should_have_faded(selection):
                    msg = f"Missed fade on {selection.get('player_name')} {selection.get('prop_type')} ({selection.get('line')})"
                    if not self._already_logged(msg):
                        self._log_reflection(msg)
                        reflections.append(msg)
        # Missed rules: e.g., posted a 3-stat player with <7.0 fantasy
        for prop in all_props:
            if self._should_suppress(prop):
                msg = f"Auto-suppress rule: {prop.get('player_name')} {prop.get('prop_type')} <7.0 fantasy"
                if not self._already_logged(msg):
                    self._log_reflection(msg)
                    reflections.append(msg)
        logger.info(f"🪞 Self-audit complete. {len(reflections)} new reflections logged.")
        return reflections

    def _should_have_faded(self, selection: Dict[str, Any]) -> bool:
        # Example: missed fade if fantasy under threshold and not posted as under
        if 'fantasy' in selection.get('prop_type', '').lower() and selection.get('pick_side', 'Over') != 'Under':
            if selection.get('line', 99) < 7.0:
                return True
        return False

    def _should_suppress(self, prop: Dict[str, Any]) -> bool:
        # Example: 3-stat player with <7.0 fantasy
        if prop.get('prop_type', '') in ['Hits', 'RBIs', 'Runs'] and prop.get('line', 99) < 1.0:
            return True
        if 'fantasy' in prop.get('prop_type', '').lower() and prop.get('line', 99) < 7.0:
            return True
        return False

    def _already_logged(self, msg: str) -> bool:
        # Check if this reflection is already in memory
        self.memory_manager.memory.setdefault('self_audit', {})
        today = self.memory_manager.today
        return msg in self.memory_manager.memory['self_audit'].get(today, [])

    def _log_reflection(self, msg: str):
        today = self.memory_manager.today
        self.memory_manager.memory.setdefault('self_audit', {})
        self.memory_manager.memory['self_audit'].setdefault(today, []).append(msg)
        self.memory_manager._save_memory()
        logger.info(f"🪞 Logged self-audit reflection: {msg}") 