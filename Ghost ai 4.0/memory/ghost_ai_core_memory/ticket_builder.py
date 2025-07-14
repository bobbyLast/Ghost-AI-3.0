#!/usr/bin/env python3
"""
ticket_builder.py - The Architect for Ghost AI 3.0
Centralizes all ticket construction logic. Enforces no-dup logic.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger('ticket_builder')

class TicketBuilder:
    def __init__(self, memory_manager, ghost_brain=None):
        self.memory_manager = memory_manager
        self.ghost_brain = ghost_brain  # Injected GhostBrain for odds/sharp logic
        logger.info("🧩 Ticket Builder initialized")

    def build_tickets(self, props: List[Dict[str, Any]], max_tickets: int = 10, max_legs: int = 3) -> List[Dict[str, Any]]:
        """
        Build diverse, optimized tickets. Enforce no-dup logic.
        Args:
            props: List of scored props
            max_tickets: Max tickets to build
            max_legs: Max legs per ticket
        Returns:
            List of valid tickets
        """
        tickets = []
        used_players = set()
        used_combos = set()
        for _ in range(max_tickets):
            selections = self._select_ticket_legs(props, max_legs, used_players, used_combos)
            if not selections:
                break
            ticket = {
                'selections': selections,
                'confidence': sum(s.get('confidence', 0) for s in selections) / len(selections),
                'ticket_type': self._determine_ticket_type(selections),
                'created_at': datetime.now().isoformat()
            }
            # No dups: check ticket hash
            if self.memory_manager.is_ticket_posted_today(ticket):
                logger.info("[NO-DUP] Skipping duplicate ticket")
                continue
            tickets.append(ticket)
            self.memory_manager.mark_ticket_posted(ticket, ticket_id=f"auto_{len(tickets)}")
            # Mark players/combos as used for this run
            for s in selections:
                used_players.add(s['player_name'])
                if 'combo' in s.get('tag', ''):
                    used_combos.add(s['prop_type'])
        logger.info(f"🧩 Built {len(tickets)} tickets (no dups)")
        return tickets

    def _select_ticket_legs(self, props, max_legs, used_players, used_combos):
        selections = []
        for prop in props:
            if len(selections) >= max_legs:
                break
            player = prop.get('player_name', '')
            prop_type = prop.get('prop_type', '')
            tag = prop.get('tag', '')
            # Odds/sharp eligibility check
            if self.ghost_brain:
                eligible, reason = self.ghost_brain._prop_is_odds_eligible(prop)
                if not eligible:
                    logger.info(f"⛔ Skipped {player} {prop_type} for ticket: {reason}")
                    continue
            # No dup players
            if player in used_players:
                continue
            # Max 1 combo per ticket
            if 'combo' in tag and any('combo' in s.get('tag', '') for s in selections):
                continue
            # No dup stat types
            if any(s.get('prop_type', '') == prop_type for s in selections):
                continue
            # Spread across teams/games
            if any(s.get('game_key', '') == prop.get('game_key', '') for s in selections):
                continue
            # If combo, require all components strong
            if 'combo' in tag and self.ghost_brain:
                combo = self.ghost_brain.build_combo_if_strong([prop])
                if not combo:
                    logger.info(f"⛔ Combo {prop_type} suppressed for ticket: not all components strong")
                    continue
            selections.append(prop)
        return selections if len(selections) == max_legs else []

    def _determine_ticket_type(self, selections):
        if any('combo' in s.get('tag', '') for s in selections):
            return 'Power Play'
        if any('fantasy' in s.get('prop_type', '').lower() for s in selections):
            return 'Fantasy Under'
        return 'Standard' 