"""
Context Engine: Adds context-aware logic to prop confidence scoring.
"""
import logging

class ContextEngine:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("ContextEngine")

    def apply_context(self, props):
        """
        Adjusts prop confidence based on volatility, combo alignment, and internal tags.
        """
        for prop in props:
            # Example: Avoid fantasy unders on volatile players
            if prop.get('prop_type') == 'fantasy' and prop.get('pick_side', '').upper() == 'UNDER' and prop.get('volatility', 0) > 0.7:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.2)
                prop['context_flag'] = 'volatile_avoid_unders'
            # Boost combos when all parts align
            if prop.get('is_combo') and prop.get('combo_parts_solid'):
                prop['confidence'] = min(1.0, prop.get('confidence', 0.5) + 0.15)
                prop['context_flag'] = 'combo_boost'
            # Downgrade if opponent is flagged red
            if prop.get('opponent_tag') in ['Pace Killer', 'Trap Magnet']:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.12)
                prop['context_flag'] = 'opponent_red_flag'
        self.logger.info("[ContextEngine] Applied context-aware confidence adjustments.")
        return props 