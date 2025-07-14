#!/usr/bin/env python3
"""
poster.py - The Enforcer for Ghost AI 3.0
Centralizes all posting logic, caps, cooldowns, and Discord formatting. Enforces no-dup logic.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger('poster')

class Poster:
    def __init__(self, memory_manager, discord_bot=None, max_tickets=10, ghost_brain=None):
        self.memory_manager = memory_manager
        self.discord_bot = discord_bot
        self.max_tickets = max_tickets
        self.cooldown = False
        self.ghost_brain = ghost_brain  # Injected GhostBrain for odds/memory/trap checks
        logger.info("📤 Poster initialized")

    def should_post(self, tickets: List[Dict[str, Any]], min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Enforce daily cap, cooldown, and confidence threshold. Enforce no-dup logic.
        Args:
            tickets: List of tickets
            min_confidence: Minimum confidence to post
        Returns:
            List of tickets to post
        """
        if self.cooldown:
            logger.info("[COOLDOWN] No tickets posted due to cooldown mode")
            return []
        posted_today = self.memory_manager.get_daily_summary().get('tickets_posted', 0)
        allowed = max(0, self.max_tickets - posted_today)
        filtered = [t for t in tickets if t.get('confidence', 0) >= min_confidence]
        filtered = [t for t in filtered if not self.memory_manager.is_ticket_posted_today(t)]
        # Enforce odds/memory/trap checks for all tickets/props
        if self.ghost_brain:
            eligible_tickets = []
            for t in filtered:
                all_eligible = True
                for prop in t.get('selections', []):
                    eligible, reason = self.ghost_brain._prop_is_odds_eligible(prop)
                    if not eligible:
                        logger.info(f"⛔ Skipped ticket: {prop.get('player_name','?')} {prop.get('prop_type','?')} failed: {reason}")
                        all_eligible = False
                        break
                if all_eligible:
                    eligible_tickets.append(t)
            filtered = eligible_tickets
        logger.info(f"📤 {len(filtered[:allowed])} tickets allowed to post (cap: {self.max_tickets}, posted: {posted_today})")
        return filtered[:allowed]

    def post_tickets(self, tickets: List[Dict[str, Any]], channel=None):
        """
        Post tickets to Discord and log results. Enforce no-dup logic.
        Args:
            tickets: List of tickets to post
            channel: Discord channel (optional)
        """
        for ticket in tickets:
            if self.memory_manager.is_ticket_posted_today(ticket):
                logger.info("[NO-DUP] Skipping already posted ticket")
                continue
            self.memory_manager.mark_ticket_posted(ticket, ticket_id=ticket.get('ticket_id', 'auto'))
            self._log_post(ticket)
            if self.discord_bot and channel:
                self._post_to_discord(ticket, channel)

    def _post_to_discord(self, ticket: Dict[str, Any], channel):
        # Format and send to Discord
        msg = self._format_ticket(ticket)
        # Placeholder: replace with actual Discord bot call
        logger.info(f"[DISCORD] Would post to {channel}:\n{msg}")

    def _format_ticket(self, ticket: Dict[str, Any]) -> str:
        selections = ticket.get('selections', [])
        lines = [f"{s.get('player_name', 'Unknown')} {s.get('prop_type', '')} {s.get('line', '')} ({s.get('confidence', 0):.0%})" for s in selections]
        return f"Ticket ({ticket.get('ticket_type', 'Standard')}):\n" + "\n".join(lines)

    def _log_post(self, ticket: Dict[str, Any]):
        # Log win/loss posting
        logger.info(f"[POSTED] {ticket.get('ticket_type', 'Standard')} @ {ticket.get('confidence', 0):.2f} - {ticket.get('selections', [])}") 