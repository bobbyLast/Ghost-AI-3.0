"""
Throttle Based on Form: Adjusts aggression based on win/loss streaks.
"""
import logging

class ThrottleBasedOnForm:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("ThrottleBasedOnForm")

    def throttle_by_form(self, props):
        """
        Adjusts pick aggression (legs, risk) based on recent streaks.
        """
        # Analyze recent streak
        graded = self.history.get('graded_tickets', [])
        streak = 0
        for graded_day in reversed(graded):
            for ticket in graded_day.get('tickets', []):
                result = ticket.get('result_status') or ticket.get('result')
                if result == 'WIN':
                    streak = streak + 1 if streak >= 0 else 1
                elif result == 'LOSS':
                    streak = streak - 1 if streak <= 0 else -1
        for prop in props:
            if streak >= 7:
                prop['confidence'] = min(1.0, prop.get('confidence', 0.5) + 0.12)
                prop['form_flag'] = 'heater_bold'
            elif streak <= -3:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.15)
                prop['form_flag'] = 'cold_conservative'
        self.logger.info(f"[ThrottleBasedOnForm] Streak: {streak}, adjusted aggression.")
        return props 