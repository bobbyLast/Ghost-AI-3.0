#!/usr/bin/env python3
"""
confidence_scoring.py - The Analyst for Ghost AI 3.0
Centralizes all confidence scoring logic and buckets props. Enforces no-dup logic.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger('confidence_scoring')

CONFIDENCE_BUCKETS = [
    ('Elite', 0.80),
    ('Reliable', 0.70),
    ('Playable', 0.60),
    ('Fade', 0.00)
]

class ConfidenceScorer:
    def __init__(self, memory_manager, reverse_engine=None):
        self.memory_manager = memory_manager
        self.reverse_engine = reverse_engine
        logger.info("📈 Confidence Scorer initialized")

    def score_props(self, props: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score and bucket each prop. Enforce no-dup logic.
        Args:
            props: List of normalized props
        Returns:
            List of props with confidence and bucket
        """
        scored = []
        for prop in props:
            if self.memory_manager.is_prop_used_today(prop):
                logger.info(f"[NO-DUP] Skipping already used prop: {prop.get('player_name')} {prop.get('prop_type')}")
                continue
            conf = self._score_single_prop(prop)
            bucket = self._bucket_confidence(conf)
            prop['confidence'] = conf
            prop['confidence_bucket'] = bucket
            scored.append(prop)
        logger.info(f"📈 Scored {len(scored)} props (no dups)")
        return scored

    def _score_single_prop(self, prop: Dict[str, Any]) -> float:
        """
        Calculate confidence for a single prop using all available data.
        """
        # Odds value
        odds = prop.get('odds', 0)
        base_conf = 0.5
        if odds > 0:
            base_conf += min(odds / 1000, 0.2)
        elif odds < 0:
            base_conf -= min(abs(odds) / 1000, 0.2)
        # Reverse engineering
        if self.reverse_engine:
            hist = self.reverse_engine.get_historical_analysis(
                prop.get('player_name', ''),
                prop.get('prop_type', ''),
                prop.get('sport', '')
            )
            if hist:
                hit_rate = hist.get('hit_rate', 0.5)
                base_conf += (hit_rate - 0.5) * 0.5
        # Player trend, tag memory, prop history
        # (Assume memory_manager has player history)
        player = prop.get('player_name', '')
        prop_type = prop.get('prop_type', '')
        player_hist = self.memory_manager.memory.get('player_history', {}).get(player, {}).get(prop_type, {})
        if player_hist:
            streak = player_hist.get('current_streak', 0)
            if streak > 2:
                base_conf += 0.05
            elif streak < -2:
                base_conf -= 0.05
            base_conf += player_hist.get('confidence_adjustment', 0.0)
        # Clamp
        base_conf = max(0.01, min(0.99, base_conf))
        return base_conf

    def _bucket_confidence(self, conf: float) -> str:
        for bucket, threshold in CONFIDENCE_BUCKETS:
            if conf >= threshold:
                return bucket
        return 'Fade'

    def adjust_scoring_weights(self, tier, up=False, down=False):
        """
        Adjust scoring weights for a confidence tier based on calibration feedback.
        TODO: Implement logic to adjust internal weights or thresholds for the given tier.
        """
        print(f"[ConfidenceScorer] Adjusting weights for tier {tier}: up={up}, down={down}")
        # TODO: Actually adjust weights
        pass 