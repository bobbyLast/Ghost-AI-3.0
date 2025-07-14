"""
Pattern Mutator: Rotates pick style to avoid predictability by books.
"""
import logging
from datetime import datetime

class PatternMutator:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("PatternMutator")

    def mutate_pattern(self, props):
        """
        Rotates pick style (e.g., fantasy-heavy, combo, ML, etc.) based on day/cycle and recent results.
        """
        day = datetime.now().day % 7
        style = 'fantasy' if day < 3 else 'combo' if day < 6 else 'ml'
        for prop in props:
            if style == 'fantasy' and prop.get('prop_type') != 'fantasy':
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.1)
                prop['pattern_flag'] = 'not_today_style'
            elif style == 'combo' and not prop.get('is_combo'):
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.1)
                prop['pattern_flag'] = 'not_today_style'
            elif style == 'ml' and prop.get('prop_type') != 'moneyline':
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.1)
                prop['pattern_flag'] = 'not_today_style'
        self.logger.info(f"[PatternMutator] Rotated pick style to {style}.")
        return props 