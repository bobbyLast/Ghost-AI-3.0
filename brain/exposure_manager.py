"""
Exposure Manager: Balances risk/exposure across teams, prop types, confidence, and time.
"""
import logging
from collections import defaultdict

class ExposureManager:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("ExposureManager")

    def balance_exposure(self, props):
        """
        Suppresses or boosts props to avoid overexposure by team/type/confidence/time.
        """
        # Count exposure
        team_count = defaultdict(int)
        type_count = defaultdict(int)
        conf_count = defaultdict(int)
        for prop in props:
            team_count[prop.get('team')] += 1
            type_count[prop.get('prop_type')] += 1
            conf = 'high' if prop.get('confidence', 0.5) > 0.7 else 'med' if prop.get('confidence', 0.5) > 0.5 else 'low'
            conf_count[conf] += 1
        # Throttle if overexposed
        for prop in props:
            if team_count[prop.get('team')] > 3:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.1)
                prop['exposure_flag'] = 'team_overexposed'
            if type_count[prop.get('prop_type')] > 4:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.08)
                prop['exposure_flag'] = 'type_overexposed'
            if conf_count['high'] > 5 and prop.get('confidence', 0.5) > 0.7:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.07)
                prop['exposure_flag'] = 'high_conf_overexposed'
        self.logger.info(f"[ExposureManager] Exposure by team: {dict(team_count)}, type: {dict(type_count)}, conf: {dict(conf_count)}")
        return props 