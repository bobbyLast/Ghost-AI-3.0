"""
ml_ticket_trigger.py - ML Ticket Trigger & Correlation Guard for Ghost AI

Triggers ML tickets if enough props for a team are high-confidence, checks for contradictions,
and ensures no duplicate/conflicting ML/prop tickets.
"""

import logging
from typing import List, Dict

logger = logging.getLogger("ml_ticket_trigger")

class MLTicketTrigger:
    """
    Triggers moneyline tickets based on prop alignment and correlation checks.
    """
    def __init__(self):
        pass

    def should_post_ml(self, props: List[Dict], ml_sentiment: Dict) -> bool:
        """
        Returns True if enough props align for a team and no contradictions exist.
        """
        # Example: at least 2 props with confidence > 0.7 and not blocked
        aligned = [p for p in props if p.get('confidence', 0) > 0.7 and not p.get('blocked')]
        if len(aligned) >= 2:
            logger.info(f"ML trigger: {len(aligned)} high-confidence props align for ML.")
            return True
        logger.info("ML trigger: Not enough high-confidence props for ML.")
        return False

    def check_contradictions(self, props: List[Dict], ml_team: str) -> bool:
        """
        Returns True if there is a contradiction (e.g., ML + fade star), else False.
        """
        for p in props:
            if p.get('team') == ml_team and p.get('pick_side', '').lower() == 'under' and not p.get('blocked'):
                logger.info(f"ML contradiction: Prop under/fade on ML team {ml_team}.")
                return True
        return False

    def is_duplicate_ml_ticket(self, team: str, posted_ml_tickets: List[str]) -> bool:
        """
        Returns True if this ML ticket has already been posted.
        """
        if team in posted_ml_tickets:
            logger.info(f"Duplicate ML ticket detected for {team}.")
            return True
        return False 