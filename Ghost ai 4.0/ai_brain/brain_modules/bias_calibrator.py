"""
Bias Calibrator: Suppresses weak prop types/teams/players based on memory and recent performance.
"""
import logging
from collections import defaultdict

class BiasCalibrator:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("BiasCalibrator")
        self.cold_types = set()
        self.hot_types = set()
        self.cold_teams = set()
        self.hot_teams = set()
        self.cold_players = set()
        self.hot_players = set()

    def calibrate_bias(self, props):
        """
        Adjusts prop eligibility/confidence based on cold streaks or weak areas.
        """
        # Analyze history for cold/hot streaks
        graded = self.history.get('graded_tickets', [])
        type_results = defaultdict(list)
        team_results = defaultdict(list)
        player_results = defaultdict(list)
        for graded_day in graded:
            for ticket in graded_day.get('tickets', []):
                for leg in ticket.get('legs', []):
                    prop_type = leg.get('prop_type') or leg.get('market')
                    team = leg.get('team')
                    player = leg.get('player_name') or leg.get('player')
                    result = leg.get('result_status') or leg.get('result')
                    if prop_type:
                        type_results[prop_type].append(result)
                    if team:
                        team_results[team].append(result)
                    if player:
                        player_results[player].append(result)
        # Determine cold/hot by win rate
        def get_win_rate(results):
            wins = sum(1 for r in results if r == 'WIN')
            total = len(results)
            return wins / total if total else 0
        for t, results in type_results.items():
            rate = get_win_rate(results[-20:])
            if rate < 0.3:
                self.cold_types.add(t)
            elif rate > 0.7:
                self.hot_types.add(t)
        for t, results in team_results.items():
            rate = get_win_rate(results[-20:])
            if rate < 0.3:
                self.cold_teams.add(t)
            elif rate > 0.7:
                self.hot_teams.add(t)
        for p, results in player_results.items():
            rate = get_win_rate(results[-20:])
            if rate < 0.3:
                self.cold_players.add(p)
            elif rate > 0.7:
                self.hot_players.add(p)
        # Adjust props
        for prop in props:
            if prop.get('prop_type') in self.cold_types or prop.get('team') in self.cold_teams or prop.get('player_name') in self.cold_players:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.15)
                prop['bias_flag'] = 'cold'
            if prop.get('prop_type') in self.hot_types or prop.get('team') in self.hot_teams or prop.get('player_name') in self.hot_players:
                prop['confidence'] = min(1.0, prop.get('confidence', 0.5) + 0.10)
                prop['bias_flag'] = 'hot'
        self.logger.info(f"[BiasCalibrator] Cold types: {self.cold_types}, Hot types: {self.hot_types}, Cold teams: {self.cold_teams}, Hot teams: {self.hot_teams}")
        return props 