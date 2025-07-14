#!/usr/bin/env python3
"""
Risk Classifier for Ghost AI Odds Intelligence

This module handles prop classification into risk tiers:
- DEMON: High risk, high reward (+110+ odds)
- GOBLIN: Low risk, low reward (-300+ odds) 
- HOT HITTER: MLB-specific hitting props
- REGULAR: Standard props
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class RiskTier(Enum):
    """Risk tier classifications for props."""
    DEMON = "DEMON"
    GOBLIN = "GOBLIN" 
    HOT_HITTER = "HOT_HITTER"
    REGULAR = "REGULAR"
    TRAP = "TRAP"

class RiskClassifier:
    """Classifies props by risk level based on odds and analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Risk thresholds
        self.demon_threshold = 110  # +110 or higher
        self.goblin_threshold = -300  # -300 or lower
        self.hot_hitter_min = -400  # MLB hitting props
        self.hot_hitter_max = -150
        
    def classify_prop(self, odds_data: Dict, trend_analysis: Dict, 
                     market_stability: Dict, sport: str = "") -> Dict[str, Any]:
        """
        Classify a prop by risk tier.
        
        Args:
            odds_data: Current odds data
            trend_analysis: Trend analysis results
            market_stability: Market stability analysis
            sport: Sport (for sport-specific classifications)
            
        Returns:
            Classification with tier, tags, and rationale
        """
        try:
            over_odds = odds_data.get('over_odds', 0)
            under_odds = odds_data.get('under_odds', 0)
            
            classification = {
                'tier': RiskTier.REGULAR,
                'tags': [],
                'rationale': '',
                'confidence': 0.5,
                'risk_level': 'medium'
            }
            
            # DEMON: High odds with trend edge
            if over_odds >= self.demon_threshold:
                if self._has_trend_edge(trend_analysis):
                    classification.update({
                        'tier': RiskTier.DEMON,
                        'tags': ['💀 DEMON', '📈 High Risk', '🎯 Trend Edge'],
                        'rationale': f'High odds ({over_odds}) with trend edge',
                        'confidence': trend_analysis.get('confidence', 0.5),
                        'risk_level': 'high'
                    })
            
            # GOBLIN: Low odds with stability
            elif under_odds <= self.goblin_threshold:
                if self._has_stability(market_stability):
                    classification.update({
                        'tier': RiskTier.GOBLIN,
                        'tags': ['👺 GOBLIN', '🛡️ Safe Leg', '📊 Stable'],
                        'rationale': f'Low odds ({under_odds}) with stable trend',
                        'confidence': market_stability.get('score', 0.5),
                        'risk_level': 'low'
                    })
            
            # HOT HITTER: MLB-specific hitting props
            elif (sport == 'baseball_mlb' and 
                  self.hot_hitter_min <= over_odds <= self.hot_hitter_max):
                if self._is_hot_hitter(over_odds, trend_analysis, market_stability):
                    classification.update({
                        'tier': RiskTier.HOT_HITTER,
                        'tags': ['🔥 HOT HITTER', '⚾ MLB Only', '📈 Over Trend'],
                        'rationale': f'MLB hitting prop ({over_odds}) with over trend and stability',
                        'confidence': min(trend_analysis.get('confidence', 0.5), 
                                        market_stability.get('score', 0.5)),
                        'risk_level': 'medium'
                    })
            
            # TRAP: High variance, low confidence
            elif self._is_trap(odds_data, trend_analysis, market_stability):
                classification.update({
                    'tier': RiskTier.TRAP,
                    'tags': ['🧊 TRAP', '⚠️ High Variance', '🚫 Avoid'],
                    'rationale': 'High variance with low confidence',
                    'confidence': 0.3,
                    'risk_level': 'high'
                })
            
            # Default: REGULAR
            else:
                classification.update({
                    'tier': RiskTier.REGULAR,
                    'tags': ['📊 Regular Prop'],
                    'rationale': 'Standard prop classification',
                    'confidence': 0.5,
                    'risk_level': 'medium'
                })
            
            return classification
            
        except Exception as e:
            self.logger.error(f"❌ Error classifying prop: {e}")
            return {
                'tier': RiskTier.REGULAR,
                'tags': ['❌ Classification Error'],
                'rationale': 'Error in classification',
                'confidence': 0.0,
                'risk_level': 'unknown'
            }
    
    def _has_trend_edge(self, trend_analysis: Dict) -> bool:
        """Check if prop has trend edge for DEMON classification."""
        trend = trend_analysis.get('trend', 'neutral')
        confidence = trend_analysis.get('confidence', 0.5)
        
        return (trend in ['over_hitting', 'rising'] and confidence > 0.6)
    
    def _has_stability(self, market_stability: Dict) -> bool:
        """Check if prop has stability for GOBLIN classification."""
        stability = market_stability.get('stability', 'unknown')
        score = market_stability.get('score', 0.5)
        
        return (stability == 'stable' and score > 0.6)
    
    def _is_hot_hitter(self, odds: int, trend_analysis: Dict, 
                      market_stability: Dict) -> bool:
        """Check if MLB prop qualifies as HOT HITTER."""
        trend = trend_analysis.get('trend', 'neutral')
        stability = market_stability.get('stability', 'unknown')
        
        return (trend == 'over_hitting' and stability == 'stable')
    
    def _is_trap(self, odds_data: Dict, trend_analysis: Dict, 
                market_stability: Dict) -> bool:
        """Check if prop is a trap (high variance, low confidence)."""
        # High variance indicators
        high_variance = market_stability.get('volatility', 0) > 0.8
        low_confidence = trend_analysis.get('confidence', 0.5) < 0.4
        unstable_market = market_stability.get('stability', 'unknown') == 'unstable'
        
        return high_variance or (low_confidence and unstable_market)
    
    def get_risk_score(self, classification: Dict) -> float:
        """Calculate numerical risk score from classification."""
        risk_scores = {
            RiskTier.DEMON: 0.8,
            RiskTier.GOBLIN: 0.2,
            RiskTier.HOT_HITTER: 0.5,
            RiskTier.REGULAR: 0.5,
            RiskTier.TRAP: 0.9
        }
        
        tier = classification.get('tier', RiskTier.REGULAR)
        return risk_scores.get(tier, 0.5)
    
    def should_include_in_ticket(self, classification: Dict, 
                               ticket_type: str = "standard") -> bool:
        """Determine if prop should be included in ticket based on classification."""
        tier = classification.get('tier', RiskTier.REGULAR)
        
        if ticket_type == "power":
            # Power tickets can include all tiers except traps
            return tier != RiskTier.TRAP
        
        elif ticket_type == "flex":
            # Flex tickets prefer regular and goblin props
            return tier in [RiskTier.REGULAR, RiskTier.GOBLIN]
        
        elif ticket_type == "safe":
            # Safe tickets only include goblin props
            return tier == RiskTier.GOBLIN
        
        else:  # standard
            # Standard tickets exclude traps and demons
            return tier not in [RiskTier.TRAP, RiskTier.DEMON] 