"""
moneyline_sentiment.py - Moneyline Sentiment & Trap Analyzer for Ghost AI

Aggregates moneyline odds, detects consensus, reverse line movement, juice traps, blowout risk,
and assigns sentiment/trap scores for each team.
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger("moneyline_sentiment")

class MoneylineSentimentAnalyzer:
    """
    Analyzes moneyline odds to assign sentiment, trap, and blowout risk for each team.
    """
    def __init__(self):
        pass

    def aggregate_moneylines(self, moneyline_data: List[Dict]) -> Dict:
        """
        Aggregate moneyline odds from all books for each game/team.
        Returns a dict keyed by team with consensus odds and movement info.
        """
        consensus = {}
        for ml in moneyline_data:
            for team, odds in [(ml.get('team1_name'), ml.get('team1_odds')), (ml.get('team2_name'), ml.get('team2_odds'))]:
                if not team:
                    continue
                if team not in consensus:
                    consensus[team] = {'odds': [], 'books': set()}
                consensus[team]['odds'].append(odds)
                consensus[team]['books'].add(ml.get('sportsbook'))
        # Calculate consensus odds
        for team in consensus:
            odds_list = consensus[team]['odds']
            consensus[team]['consensus_odds'] = int(sum(odds_list) / len(odds_list)) if odds_list else 0
            consensus[team]['books'] = list(consensus[team]['books'])
        return consensus

    def detect_reverse_line_movement(self, team: str, odds_history: List[int]) -> bool:
        """
        Detects reverse line movement for a team given odds history.
        Returns True if RLM detected, else False.
        """
        if len(odds_history) < 2:
            return False
        # RLM: odds get worse for favorite despite public action
        return odds_history[-1] > odds_history[0]

    def detect_juice_trap(self, odds_list: List[int]) -> bool:
        """
        Detects heavy juice or outlier odds (trap signals).
        Returns True if trap detected, else False.
        """
        if not odds_list:
            return False
        avg = sum(odds_list) / len(odds_list)
        # Trap if any odds are much worse than average (e.g., > 50 points off)
        for o in odds_list:
            if abs(o - avg) > 50:
                return True
        # Trap if all odds are very juiced (e.g., < -180)
        if all(o < -180 for o in odds_list):
            return True
        return False

    def assess_blowout_risk(self, team: str, consensus_odds: int, opponent_odds: int) -> float:
        """
        Assigns a blowout risk score (0.0-1.0) based on odds gap.
        """
        gap = abs(consensus_odds - opponent_odds)
        if gap > 200:
            return 0.8
        elif gap > 150:
            return 0.6
        elif gap > 100:
            return 0.4
        elif gap > 50:
            return 0.2
        else:
            return 0.1

    def assign_sentiment(self, team: str, consensus_odds: int) -> str:
        """
        Assigns sentiment: 'bullish', 'bearish', or 'neutral' based on consensus odds.
        """
        if consensus_odds < -130:
            return 'bullish'
        elif consensus_odds > 130:
            return 'bearish'
        else:
            return 'neutral'

    def analyze_game(self, game_moneylines: List[Dict]) -> Dict:
        """
        Full analysis for a single game: returns dict with sentiment, trap, blowout, and all findings.
        """
        consensus = self.aggregate_moneylines(game_moneylines)
        result = {}
        teams = list(consensus.keys())
        if len(teams) < 2:
            return result
        t1, t2 = teams[0], teams[1]
        t1_odds = consensus[t1]['consensus_odds']
        t2_odds = consensus[t2]['consensus_odds']
        result[t1] = {
            'sentiment': self.assign_sentiment(t1, t1_odds),
            'trap': self.detect_juice_trap(consensus[t1]['odds']),
            'blowout_risk': self.assess_blowout_risk(t1, t1_odds, t2_odds),
            'consensus_odds': t1_odds
        }
        result[t2] = {
            'sentiment': self.assign_sentiment(t2, t2_odds),
            'trap': self.detect_juice_trap(consensus[t2]['odds']),
            'blowout_risk': self.assess_blowout_risk(t2, t2_odds, t1_odds),
            'consensus_odds': t2_odds
        }
        logger.info(f"Moneyline sentiment analysis: {result}")
        return result 