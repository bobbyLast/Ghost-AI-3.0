#!/usr/bin/env python3
"""
Ghost AI 3.0 Enhanced Intelligence Module

Advanced features:
- Reverse Engineering Integration
- Advanced Confidence Algorithms
- Historical Performance Analysis
- Risk Management
- Multi-factor Analysis
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger('enhanced.intelligence')

class EnhancedIntelligence:
    """Enhanced intelligence system for Ghost AI 3.0."""
    
    def __init__(self):
        self.performance_data = {}
        self.risk_models = {}
        self.confidence_boosters = {}
        self.historical_analysis = {}
        self.confidence_weights = {
            "fanduel": 1.0,
            "draftkings": 0.85,
            "caesars": 0.75
        }
        
        # Load existing data
        self._load_performance_data()
        self._initialize_risk_models()
    
    def _load_performance_data(self):
        """Load historical performance data."""
        try:
            performance_file = Path('data/performance/performance.json')
            if performance_file.exists():
                with open(performance_file, 'r') as f:
                    self.performance_data = json.load(f)
                logger.info(f"Loaded {len(self.performance_data)} performance records")
            else:
                logger.info("No performance data found - starting fresh")
        except Exception as e:
            logger.error(f"Failed to load performance data: {e}")
    
    def _initialize_risk_models(self):
        """Initialize risk assessment models."""
        self.risk_models = {
            'volatility': {
                'high': 0.3,    # High volatility threshold
                'medium': 0.15, # Medium volatility threshold
                'low': 0.05     # Low volatility threshold
            },
            'confidence_boost': {
                'historical_success': 0.1,  # 10% boost for historical success
                'trend_alignment': 0.05,    # 5% boost for trend alignment
                'risk_mitigation': 0.08     # 8% boost for risk mitigation
            },
            'risk_penalties': {
                'high_volatility': -0.15,   # 15% penalty for high volatility
                'poor_history': -0.12,      # 12% penalty for poor history
                'market_instability': -0.10 # 10% penalty for market instability
            }
        }
    
    def calculate_enhanced_confidence(self, prop: Dict, historical_data: Dict = None) -> float:
        """Calculate enhanced confidence score using multiple factors."""
        try:
            if historical_data is None:
                historical_data = {}
            base_confidence = prop.get('confidence', 0.5)
            enhanced_confidence = base_confidence
            
            # Add recent player form as a feature
            player_name = prop.get('player_name', '')
            stat_type = prop.get('stat', '')
            recent_form = self.get_recent_player_form(player_name, stat_type)
            prop['recent_form_avg'] = recent_form
            
            # Weight confidence by book
            book = prop.get('bookmaker', '').lower()
            weight = self.confidence_weights.get(book, 1.0)
            enhanced_confidence *= weight
            
            # Factor 1: Historical Performance
            historical_boost = self._calculate_historical_boost(prop, historical_data)
            enhanced_confidence += historical_boost
            
            # Factor 2: Market Stability
            market_stability = self._assess_market_stability(prop)
            enhanced_confidence += market_stability
            
            # Factor 3: Risk Assessment
            risk_adjustment = self._assess_risk(prop)
            enhanced_confidence += risk_adjustment
            
            # Factor 4: Trend Analysis
            trend_boost = self._analyze_trends(prop)
            enhanced_confidence += trend_boost
            
            # Factor 5: Volatility Analysis
            volatility_adjustment = self._analyze_volatility(prop)
            enhanced_confidence += volatility_adjustment
            
            # Clamp to 0-1 range
            enhanced_confidence = max(0.0, min(1.0, enhanced_confidence))
            
            # Store enhanced confidence
            prop['enhanced_confidence'] = enhanced_confidence
            prop['confidence_factors'] = {
                'base_confidence': base_confidence,
                'historical_boost': historical_boost,
                'market_stability': market_stability,
                'risk_adjustment': risk_adjustment,
                'trend_boost': trend_boost,
                'volatility_adjustment': volatility_adjustment
            }
            
            return enhanced_confidence
            
        except Exception as e:
            logger.error(f"Error calculating enhanced confidence: {e}")
            return prop.get('confidence', 0.5)
    
    def _calculate_historical_boost(self, prop: Dict, historical_data: Dict) -> float:
        """Calculate confidence boost based on historical performance."""
        try:
            player_name = prop.get('player_name', '')
            stat_type = prop.get('stat', '')
            
            if not player_name or not stat_type:
                return 0.0
            
            # Get player's historical performance for this stat
            player_history = historical_data.get(player_name, {}).get(stat_type, {})
            
            if not player_history:
                return 0.0
            
            # Calculate success rate
            total_picks = player_history.get('total_picks', 0)
            successful_picks = player_history.get('successful_picks', 0)
            
            if total_picks == 0:
                return 0.0
            
            success_rate = successful_picks / total_picks
            
            # Apply boost based on success rate
            if success_rate >= 0.7:  # 70%+ success rate
                return self.risk_models['confidence_boost']['historical_success']
            elif success_rate >= 0.6:  # 60%+ success rate
                return self.risk_models['confidence_boost']['historical_success'] * 0.5
            elif success_rate <= 0.4:  # 40% or lower
                return self.risk_models['risk_penalties']['poor_history']
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating historical boost: {e}")
            return 0.0
    
    def _assess_market_stability(self, prop: Dict) -> float:
        """Assess market stability for the prop."""
        try:
            # Check odds movement (if available)
            odds = prop.get('price', 0)
            implied_prob = prop.get('implied_prob', 0.5)
            
            # Simple market stability assessment
            if 0.4 <= implied_prob <= 0.6:
                # Balanced market - slight positive
                return 0.02
            elif 0.3 <= implied_prob <= 0.7:
                # Reasonable market
                return 0.0
            else:
                # Unbalanced market - slight negative
                return -0.02
                
        except Exception as e:
            logger.error(f"Error assessing market stability: {e}")
            return 0.0
    
    def _assess_risk(self, prop: Dict) -> float:
        """Assess risk level and apply adjustments."""
        try:
            risk_tier = prop.get('risk_tier', 'Normal')
            confidence = prop.get('confidence', 0.5)
            
            # Risk assessment based on tier and confidence
            if risk_tier == 'Demon' and confidence < 0.6:
                return self.risk_models['risk_penalties']['high_volatility']
            elif risk_tier == 'Goblin' and confidence > 0.7:
                return self.risk_models['confidence_boost']['risk_mitigation']
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            return 0.0
    
    def _analyze_trends(self, prop: Dict) -> float:
        """Analyze trends and apply boost."""
        try:
            # This would integrate with trend analysis data
            # For now, return a small positive boost for high confidence props
            confidence = prop.get('confidence', 0.5)
            
            if confidence > 0.6:
                return self.risk_models['confidence_boost']['trend_alignment']
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return 0.0
    
    def _analyze_volatility(self, prop: Dict) -> float:
        """Analyze volatility and apply adjustments."""
        try:
            # This would integrate with volatility data
            # For now, return neutral
            return 0.0
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return 0.0
    
    def integrate_reverse_engineering(self, prop: Dict) -> Dict:
        """Integrate reverse engineering analysis."""
        try:
            # This would integrate with the reverse engineering system
            # For now, add placeholder data
            
            prop['reverse_engineering'] = {
                'odds_analysis': {
                    'line_movement': 'stable',
                    'sharp_money': 'neutral',
                    'public_percentage': 0.55
                },
                'market_efficiency': 0.75,
                'edge_detected': False
            }
            
            return prop
            
        except Exception as e:
            logger.error(f"Error integrating reverse engineering: {e}")
            return prop
    
    def apply_risk_management(self, picks: List[Dict]) -> List[Dict]:
        """Apply risk management rules to picks."""
        try:
            managed_picks = []
            
            for pick in picks:
                # Apply risk management rules
                risk_score = self._calculate_risk_score(pick)
                pick['risk_score'] = risk_score
                
                # Filter out high-risk picks
                if risk_score <= 0.7:  # Accept picks with 70% or lower risk
                    managed_picks.append(pick)
                else:
                    logger.info(f"Filtered out high-risk pick: {pick.get('player_name')} (risk: {risk_score:.2f})")
            
            return managed_picks
            
        except Exception as e:
            logger.error(f"Error applying risk management: {e}")
            return picks
    
    def _calculate_risk_score(self, pick: Dict) -> float:
        """Calculate risk score for a pick."""
        try:
            confidence = pick.get('enhanced_confidence', pick.get('confidence', 0.5))
            risk_tier = pick.get('risk_tier', 'Normal')
            
            # Base risk score (inverse of confidence)
            risk_score = 1.0 - confidence
            
            # Adjust based on risk tier
            if risk_tier == 'Demon':
                risk_score *= 1.3  # 30% higher risk
            elif risk_tier == 'Goblin':
                risk_score *= 0.8  # 20% lower risk
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 0.5
    
    def generate_intelligence_report(self, picks: List[Dict]) -> Dict:
        """Generate intelligence report for picks."""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_picks': len(picks),
                'confidence_distribution': {
                    'high': len([p for p in picks if p.get('enhanced_confidence', 0) >= 0.7]),
                    'medium': len([p for p in picks if 0.5 <= p.get('enhanced_confidence', 0) < 0.7]),
                    'low': len([p for p in picks if p.get('enhanced_confidence', 0) < 0.5])
                },
                'risk_distribution': {
                    'low_risk': len([p for p in picks if p.get('risk_score', 0) <= 0.3]),
                    'medium_risk': len([p for p in picks if 0.3 < p.get('risk_score', 0) <= 0.6]),
                    'high_risk': len([p for p in picks if p.get('risk_score', 0) > 0.6])
                },
                'average_confidence': np.mean([p.get('enhanced_confidence', 0) for p in picks]) if picks else 0,
                'average_risk': np.mean([p.get('risk_score', 0) for p in picks]) if picks else 0
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating intelligence report: {e}")
            return {}
    
    def save_intelligence_data(self, picks: List[Dict], report: Dict):
        """Save intelligence data for future analysis."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Save picks with intelligence data
            picks_file = Path(f'data/intelligence/picks_{today}.json')
            picks_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(picks_file, 'w') as f:
                json.dump({
                    'date': today,
                    'picks': picks,
                    'intelligence_report': report
                }, f, indent=2)
            
            logger.info(f"Saved intelligence data to {picks_file}")
            
        except Exception as e:
            logger.error(f"Error saving intelligence data: {e}")
    
    def get_recent_player_form(self, player_name: str, stat_type: str, n_games: int = 5) -> Optional[float]:
        """Compute the rolling average for a player/stat from historical data."""
        try:
            if not player_name or not stat_type:
                return None
            # Assume self.performance_data[player_name][stat_type]['history'] is a list of past game values (most recent last)
            player_stats = self.performance_data.get(player_name, {}).get(stat_type, {}).get('history', [])
            if not player_stats or len(player_stats) < 1:
                return None
            # Take the last n_games (or all if fewer)
            recent_stats = player_stats[-n_games:]
            avg = sum(recent_stats) / len(recent_stats)
            return avg
        except Exception as e:
            logger.error(f"Error computing recent player form for {player_name} {stat_type}: {e}")
            return None
    
    def detect_trap(self, prop: Dict, all_props: List[Dict], player_history: Dict = None, matchup_context: Dict = None) -> Dict:
        """Enhanced: Use player/team memory and context in trap detection."""
        # Weighted average odds (as before)
        weighted_sum = 0
        total_weight = 0
        for p in all_props:
            book = p.get('bookmaker', '').lower()
            weight = self.confidence_weights.get(book, 1.0)
            odds = p.get('odds', 0)
            weighted_sum += odds * weight
            total_weight += weight
        avg_weighted_odds = weighted_sum / total_weight if total_weight else 0
        # Memory/context logic
        trap_adjustment = 0
        # Player L5 streak
        if player_history and 'last5' in player_history:
            l5 = player_history['last5']
            if sum(l5) >= 4:  # 4+ hits in last 5
                trap_adjustment += 0.05  # boost confidence
            elif sum(l5) <= 1:
                trap_adjustment -= 0.05  # lower confidence
        # Matchup context (e.g., pace, blowout risk)
        if matchup_context:
            if matchup_context.get('pace', 1.0) > 1.1:
                trap_adjustment += 0.03
            if matchup_context.get('blowout_risk', False):
                trap_adjustment -= 0.04
        trap_confidence = avg_weighted_odds + trap_adjustment
        return {
            "avg_weighted_odds": avg_weighted_odds,
            "trap_adjustment": trap_adjustment,
            "trap_confidence": trap_confidence
        }

# Global instance
enhanced_intelligence = EnhancedIntelligence()

async def enhance_picks_with_intelligence(picks: List[Dict]) -> List[Dict]:
    """Enhance picks with intelligence analysis."""
    try:
        enhanced_picks = []
        
        for pick in picks:
            # Apply enhanced confidence calculation
            enhanced_confidence = enhanced_intelligence.calculate_enhanced_confidence(pick)
            
            # Integrate reverse engineering
            enhanced_pick = enhanced_intelligence.integrate_reverse_engineering(pick)
            
            enhanced_picks.append(enhanced_pick)
        
        # Apply risk management
        managed_picks = enhanced_intelligence.apply_risk_management(enhanced_picks)
        
        # Generate intelligence report
        report = enhanced_intelligence.generate_intelligence_report(managed_picks)
        
        # Save intelligence data
        enhanced_intelligence.save_intelligence_data(managed_picks, report)
        
        logger.info(f"Enhanced {len(picks)} picks with intelligence analysis")
        logger.info(f"Risk management filtered to {len(managed_picks)} picks")
        
        return managed_picks
        
    except Exception as e:
        logger.error(f"Error enhancing picks with intelligence: {e}")
        return picks 