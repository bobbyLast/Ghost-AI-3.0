"""
Self-Scouting Engine: Grades Ghost's own picks post-slate for CLV, market beat, and result analysis.
"""
import logging
from statistics import mean

class SelfScout:
    def __init__(self, history, logger=None):
        self.history = history
        self.logger = logger or logging.getLogger("SelfScout")
        self.summary = {}

    def run_self_scout(self):
        """
        Review all posted props, compare posted line vs. closing line (CLV), log market beat/result, and learn pick strengths/weaknesses.
        """
        graded = self.history.get('graded_tickets', [])
        clv_deltas = []
        market_beats = 0
        total = 0
        strengths = {}
        weaknesses = {}
        for graded_day in graded:
            for ticket in graded_day.get('tickets', []):
                for leg in ticket.get('legs', []):
                    posted_line = leg.get('line')
                    closing_line = leg.get('closing_line')
                    result = leg.get('result_status') or leg.get('result')
                    prop_type = leg.get('prop_type') or leg.get('market')
                    if posted_line is not None and closing_line is not None:
                        clv = closing_line - posted_line
                        clv_deltas.append(clv)
                        if (clv > 0 and leg.get('pick_side', '').upper() == 'OVER') or (clv < 0 and leg.get('pick_side', '').upper() == 'UNDER'):
                            market_beats += 1
                    if result == 'WIN':
                        strengths[prop_type] = strengths.get(prop_type, 0) + 1
                    elif result == 'LOSS':
                        weaknesses[prop_type] = weaknesses.get(prop_type, 0) + 1
                    total += 1
        avg_clv = mean(clv_deltas) if clv_deltas else 0
        market_beat_pct = (market_beats / total * 100) if total else 0
        self.summary = {
            'avg_clv': avg_clv,
            'market_beat_pct': market_beat_pct,
            'strengths': strengths,
            'weaknesses': weaknesses
        }
        self.logger.info(f"[SelfScout] CLV: {avg_clv:.2f}, Market Beat %: {market_beat_pct:.1f}, Strengths: {strengths}, Weaknesses: {weaknesses}")
        return self.summary 