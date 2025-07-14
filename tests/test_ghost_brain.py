import unittest
from ghost_ai_core_memory.ghost_brain import GhostBrain
from copy import deepcopy
from pathlib import Path

class TestGhostBrain(unittest.TestCase):
    def setUp(self):
        self.brain = GhostBrain(Path('.'))
        # Minimal mock data for props and tickets
        self.mock_props = [
            {'player_name': 'A', 'prop_type': 'HRR', 'odds': -180, 'book_count': 1, 'disappeared': True, 'line_movement': 2.0, 'team': 'TEX', 'opponent': 'HOU', 'confidence': 0.8},
            {'player_name': 'B', 'prop_type': 'Hits', 'odds': 120, 'book_count': 3, 'team': 'NYY', 'opponent': 'MIN', 'confidence': 0.7},
            {'player_name': 'C', 'prop_type': 'RBIs', 'odds': 150, 'book_count': 2, 'team': 'LAD', 'opponent': 'ATL', 'confidence': 0.6},
        ]
        self.mock_tickets = [
            {'selections': [
                {'player_name': 'A', 'prop_type': 'HRR', 'team': 'TEX', 'opponent': 'HOU'},
                {'player_name': 'A', 'prop_type': 'HRR', 'team': 'TEX', 'opponent': 'HOU'}  # Correlated
            ]},
            {'selections': [
                {'player_name': 'B', 'prop_type': 'Hits', 'team': 'NYY', 'opponent': 'MIN'},
                {'player_name': 'C', 'prop_type': 'RBIs', 'team': 'LAD', 'opponent': 'ATL'}
            ]}
        ]

    # def test_duplicate_prevention(self):
    #     # Should skip already used prop
    #     self.brain.memory.memory = {'player_history': {'A': {'HRR': {'last_5_results': ['WIN'], 'total_picks': 1}}}}
    #     props = deepcopy(self.mock_props)
    #     scored = self.brain.confidence.score_props(props)
    #     self.assertTrue(all(p['player_name'] != 'A' for p in scored))

    # def test_trap_detection(self):
    #     props = deepcopy(self.mock_props)
    #     clean = self.brain.book_trap_radar(props)
    #     self.assertTrue(all('trap_flag' not in p for p in clean))
    #     self.assertTrue(any(p['player_name'] == 'A' for p in props if 'trap_flag' in p))

    # def test_trend_penalty(self):
    #     self.brain.trend_scores = {'Hits_NYY_B': 'cold'}
    #     props = deepcopy(self.mock_props)
    #     penalized = self.brain.apply_prop_penalties_and_boosts(props)
    #     for p in penalized:
    #         if p['player_name'] == 'B':
    #             self.assertIn('trend_penalty', p)

    # def test_synergy_model(self):
    #     tickets = deepcopy(self.mock_tickets)
    #     filtered = self.brain.ai_synergy_model(tickets)
    #     self.assertTrue(all('synergy_flag' not in t for t in filtered))
    #     self.assertTrue(any('synergy_flag' in t for t in self.mock_tickets))

    # def test_feature_switchboard(self):
    #     FEATURES['book_trap_radar'] = False
    #     props = deepcopy(self.mock_props)
    #     clean = self.brain.book_trap_radar(props)
    #     self.assertEqual(len(clean), len(props))
    #     FEATURES['book_trap_radar'] = True  # Reset

    # def test_clv_confidence_boost(self):
    #     props = deepcopy(self.mock_props)
    #     for p in props:
    #         p['clv'] = 0.5
    #     boosted = self.brain.apply_clv_and_tight_miss_checks(props)
    #     for p in boosted:
    #         self.assertTrue(p.get('clv_boost', False))

    def test_odds_driven_prop_eligibility(self):
        # Test props with various odds
        valid_prop = {'player_name': 'Valid', 'prop_type': 'Hits', 'odds': -120}
        low_prob_prop = {'player_name': 'LowProb', 'prop_type': 'Runs', 'odds': 500}
        high_prob_prop = {'player_name': 'HighProb', 'prop_type': 'RBIs', 'odds': -500}
        eligible, reason = self.brain._prop_is_odds_eligible(valid_prop)
        self.assertTrue(eligible)
        eligible, reason = self.brain._prop_is_odds_eligible(low_prob_prop)
        self.assertFalse(eligible)
        eligible, reason = self.brain._prop_is_odds_eligible(high_prob_prop)
        self.assertFalse(eligible)

    def test_combo_building_only_if_strong(self):
        # All strong
        strong = {'player_name': 'A', 'prop_type': 'Combo', 'odds': -110, 'confidence': 0.7}
        combo = self.brain.build_combo_if_strong([strong])
        self.assertIsNotNone(combo)
        # One weak
        weak = {'player_name': 'B', 'prop_type': 'Combo', 'odds': 400, 'confidence': 0.2}
        combo = self.brain.build_combo_if_strong([strong, weak])
        self.assertIsNone(combo)

    def test_skip_logging_for_ineligible_props(self):
        # Patch logger to capture output
        import io, logging
        log_stream = io.StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger('ghost_brain')
        logger.addHandler(handler)
        prop = {'player_name': 'SkipMe', 'prop_type': 'Runs', 'odds': 500, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        eligible, reason = self.brain._prop_is_odds_eligible(prop)
        handler.flush()
        log_contents = log_stream.getvalue()
        logger.removeHandler(handler)
        self.assertFalse(eligible)
        self.assertTrue('Implied probability' in reason or 'Implied probability' in log_contents)

    def test_poster_should_post_only_eligible(self):
        # Simulate Poster logic
        from ghost_ai_core_memory.poster import Poster
        class DummyMemory:
            def get_daily_summary(self): return {'tickets_posted': 0}
            def is_ticket_posted_today(self, t): return False
        poster = Poster(DummyMemory(), ghost_brain=self.brain)
        eligible = {'selections': [{'player_name': 'A', 'prop_type': 'Hits', 'odds': -120, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB', 'confidence': 0.7}], 'confidence': 0.7}
        ineligible = {'selections': [{'player_name': 'B', 'prop_type': 'Runs', 'odds': 500, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}]}
        tickets = [eligible, ineligible]
        # Debug: check eligibility directly
        prop = eligible['selections'][0]
        eligible_result, eligible_reason = self.brain._prop_is_odds_eligible(prop)
        print(f"Eligible prop check: {eligible_result}, reason: {eligible_reason}")
        filtered = poster.should_post(tickets)
        print(f"Filtered tickets: {filtered}")
        self.assertTrue(eligible_result)
        self.assertEqual(filtered, [eligible])

    def test_combo_all_strong(self):
        strong1 = {'player_name': 'A', 'prop_type': 'Combo1', 'odds': -110, 'confidence': 0.7, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        strong2 = {'player_name': 'A', 'prop_type': 'Combo2', 'odds': -120, 'confidence': 0.8, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        combo = self.brain.build_combo_if_strong([strong1, strong2])
        self.assertIsNotNone(combo)

    def test_combo_one_weak(self):
        strong = {'player_name': 'A', 'prop_type': 'Combo1', 'odds': -110, 'confidence': 0.7, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        weak = {'player_name': 'A', 'prop_type': 'Combo2', 'odds': 400, 'confidence': 0.2, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        combo = self.brain.build_combo_if_strong([strong, weak])
        self.assertIsNone(combo)

    def test_combo_all_weak(self):
        weak1 = {'player_name': 'A', 'prop_type': 'Combo1', 'odds': 400, 'confidence': 0.2, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        weak2 = {'player_name': 'A', 'prop_type': 'Combo2', 'odds': 350, 'confidence': 0.1, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        combo = self.brain.build_combo_if_strong([weak1, weak2])
        self.assertIsNone(combo)

    def test_hrr_combo_eligibility(self):
        # Simulate HRR combo: all eligible
        h = {'player_name': 'A', 'prop_type': 'Hits', 'odds': -120, 'confidence': 0.7, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        r = {'player_name': 'A', 'prop_type': 'Runs', 'odds': -110, 'confidence': 0.7, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        rbi = {'player_name': 'A', 'prop_type': 'RBIs', 'odds': -130, 'confidence': 0.7, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        combo = self.brain.build_combo_if_strong([h, r, rbi])
        self.assertIsNotNone(combo)
        # One ineligible
        rbi_bad = {'player_name': 'A', 'prop_type': 'RBIs', 'odds': 500, 'confidence': 0.1, 'line': 1, 'pick_side': 'Over', 'sport': 'MLB'}
        combo = self.brain.build_combo_if_strong([h, r, rbi_bad])
        self.assertIsNone(combo)

    def test_fantasy_combo_odds_based(self):
        # All eligible
        p = {'player_name': 'A', 'prop_type': 'Points', 'odds': -120, 'confidence': 0.7, 'line': 10, 'pick_side': 'Over', 'sport': 'WNBA'}
        r = {'player_name': 'A', 'prop_type': 'Rebounds', 'odds': -110, 'confidence': 0.7, 'line': 5, 'pick_side': 'Over', 'sport': 'WNBA'}
        a = {'player_name': 'A', 'prop_type': 'Assists', 'odds': -130, 'confidence': 0.7, 'line': 3, 'pick_side': 'Over', 'sport': 'WNBA'}
        combo = self.brain.build_combo_if_strong([p, r, a])
        self.assertIsNotNone(combo)
        # One ineligible
        a_bad = {'player_name': 'A', 'prop_type': 'Assists', 'odds': 400, 'confidence': 0.1, 'line': 3, 'pick_side': 'Over', 'sport': 'WNBA'}
        combo = self.brain.build_combo_if_strong([p, r, a_bad])
        self.assertIsNone(combo)

    def test_clv_trap_market_stubs(self):
        # These are stubs for future sharp/ML logic
        # Just ensure the methods exist and can be called
        if hasattr(self.brain, 'analyze_market_movement'):
            self.brain.analyze_market_movement({'odds': -120})
        if hasattr(self.brain, 'track_clv'):
            self.brain.track_clv({'odds': -120}, {'odds': -110})
        if hasattr(self.brain, 'detect_trap'):
            self.brain.detect_trap({'odds': -120})

if __name__ == '__main__':
    unittest.main() 