"""
Self-Reflection Logger: Logs daily 'what I learned' events for future training.
"""
import logging
from datetime import datetime
import json

class SelfReflectionLogger:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("SelfReflectionLogger")

    def log_daily_reflection(self):
        """
        Logs a 1-liner for each prop: win/loss, expectation vs. result, stores learning events.
        """
        today = datetime.now().strftime('%Y-%m-%d')
        graded = self.history.get('graded_tickets', [])
        lines = []
        for graded_day in graded:
            for ticket in graded_day.get('tickets', []):
                for leg in ticket.get('legs', []):
                    exp = leg.get('expected', 'N/A')
                    actual = leg.get('actual_result', 'N/A')
                    result = leg.get('result_status') or leg.get('result')
                    lines.append(f"{today} | {leg.get('player_name','?')} | {leg.get('prop_type','?')} | Exp: {exp} | Actual: {actual} | Result: {result}")
        # Save to file
        try:
            with open(f'data/learning_logs/learned_{today}.log', 'a') as f:
                for line in lines:
                    f.write(line + '\n')
            self.logger.info(f"[SelfReflectionLogger] Logged {len(lines)} daily reflection events.")
        except Exception as e:
            self.logger.error(f"[SelfReflectionLogger] Error logging daily reflection: {e}") 