"""
Confidence Calibrator: Dynamically reweights confidence based on past results.
"""
import logging

class ConfidenceCalibrator:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("ConfidenceCalibrator")

    def calibrate_confidence(self, props):
        """
        Adjusts prop confidence based on past misses/hits and calibration loop.
        """
        # Track high-confidence misses
        graded = self.history.get('graded_tickets', [])
        high_conf_misses = 0
        high_conf_total = 0
        for graded_day in graded:
            for ticket in graded_day.get('tickets', []):
                for leg in ticket.get('legs', []):
                    conf = leg.get('confidence', 0.5)
                    result = leg.get('result_status') or leg.get('result')
                    if conf > 0.85:
                        high_conf_total += 1
                        if result == 'LOSS':
                            high_conf_misses += 1
        # If too many high-conf misses, tighten
        for prop in props:
            if high_conf_total > 0 and (high_conf_misses / high_conf_total) > 0.2 and prop.get('confidence', 0.5) > 0.85:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.08)
                prop['calibration_flag'] = 'tightened'
        self.logger.info(f"[ConfidenceCalibrator] High-conf misses: {high_conf_misses}/{high_conf_total}, calibration applied.")
        return props 