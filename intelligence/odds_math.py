#!/usr/bin/env python3
"""
Odds Math Utilities for Ghost AI

This module provides mathematical utilities for odds analysis:
- Implied probability calculations
- Closing Line Value (CLV) analysis
- Volatility calculations
- Expected value computations
"""

import logging
import math
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class OddsMath:
    """Mathematical utilities for odds analysis."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def implied_probability(self, odds: int) -> float:
        """
        Convert American odds to implied probability.
        
        Args:
            odds: American odds (e.g., -150, +125)
            
        Returns:
            float: Implied probability (0.0 to 1.0)
        """
        try:
            odds = int(odds)
            
            if odds > 0:
                return 100 / (odds + 100)
            else:
                return abs(odds) / (abs(odds) + 100)
                
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid odds format: {odds}")
            return 0.5
    
    def american_odds(self, probability: float) -> int:
        """
        Convert probability to American odds.
        
        Args:
            probability: Probability (0.0 to 1.0)
            
        Returns:
            int: American odds
        """
        try:
            if probability <= 0 or probability >= 1:
                raise ValueError("Probability must be between 0 and 1")
            
            if probability > 0.5:
                return int(-100 * probability / (1 - probability))
            else:
                return int(100 * (1 - probability) / probability)
                
        except Exception as e:
            self.logger.error(f"Error converting probability to odds: {e}")
            return 0
    
    def calculate_clv(self, posted_odds: int, closing_odds: int) -> float:
        """
        Calculate Closing Line Value (CLV).
        
        Args:
            posted_odds: Odds when we posted the pick
            closing_odds: Odds at game time
            
        Returns:
            float: CLV percentage (positive = good, negative = bad)
        """
        try:
            posted_prob = self.implied_probability(posted_odds)
            closing_prob = self.implied_probability(closing_odds)
            
            # CLV = (posted_prob - closing_prob) / closing_prob
            if closing_prob > 0:
                clv = (posted_prob - closing_prob) / closing_prob
                return clv * 100  # Convert to percentage
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error calculating CLV: {e}")
            return 0.0
    
    def calculate_expected_value(self, probability: float, odds: int, 
                               stake: float = 100) -> float:
        """
        Calculate expected value of a bet.
        
        Args:
            probability: Our estimated probability
            odds: American odds
            stake: Bet amount (default $100)
            
        Returns:
            float: Expected value
        """
        try:
            implied_prob = self.implied_probability(odds)
            
            if odds > 0:
                win_amount = stake * (odds / 100)
            else:
                win_amount = stake * (100 / abs(odds))
            
            # EV = (probability * win_amount) - (stake * (1 - probability))
            ev = (probability * win_amount) - (stake * (1 - probability))
            return ev
            
        except Exception as e:
            self.logger.error(f"Error calculating expected value: {e}")
            return 0.0
    
    def calculate_volatility(self, odds_history: List[int]) -> float:
        """
        Calculate volatility from odds history.
        
        Args:
            odds_history: List of odds over time
            
        Returns:
            float: Volatility score (0.0 to 1.0)
        """
        try:
            if len(odds_history) < 2:
                return 0.0
            
            # Convert odds to probabilities
            probs = [self.implied_probability(odds) for odds in odds_history]
            
            # Calculate standard deviation
            mean_prob = sum(probs) / len(probs)
            variance = sum((p - mean_prob) ** 2 for p in probs) / len(probs)
            std_dev = math.sqrt(variance)
            
            # Normalize to 0-1 scale (assuming max reasonable volatility is 0.3)
            volatility = min(std_dev / 0.3, 1.0)
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {e}")
            return 0.0
    
    def calculate_kelly_criterion(self, probability: float, odds: int) -> float:
        """
        Calculate Kelly Criterion for optimal bet sizing.
        
        Args:
            probability: Our estimated probability
            odds: American odds
            
        Returns:
            float: Kelly percentage (0.0 to 1.0)
        """
        try:
            implied_prob = self.implied_probability(odds)
            
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
            
            # Kelly = (bp - q) / b
            # where b = decimal_odds - 1, p = our_prob, q = 1 - our_prob
            b = decimal_odds - 1
            p = probability
            q = 1 - probability
            
            kelly = (b * p - q) / b
            
            # Cap at reasonable levels
            return max(0.0, min(kelly, 0.25))
            
        except Exception as e:
            self.logger.error(f"Error calculating Kelly Criterion: {e}")
            return 0.0
    
    def calculate_confidence_boost(self, clv: float, volatility: float, 
                                 trend_strength: float) -> float:
        """
        Calculate confidence boost from various factors.
        
        Args:
            clv: Closing Line Value percentage
            volatility: Market volatility (0.0 to 1.0)
            trend_strength: Trend strength (0.0 to 1.0)
            
        Returns:
            float: Confidence boost (-0.2 to 0.2)
        """
        try:
            # CLV boost (positive CLV is good)
            clv_boost = min(clv / 10, 0.1)  # Max 10% boost
            
            # Volatility penalty (high volatility is bad)
            volatility_penalty = -volatility * 0.1  # Max 10% penalty
            
            # Trend boost
            trend_boost = trend_strength * 0.05  # Max 5% boost
            
            total_boost = clv_boost + volatility_penalty + trend_boost
            
            # Cap at reasonable levels
            return max(-0.2, min(total_boost, 0.2))
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence boost: {e}")
            return 0.0
    
    def analyze_odds_movement(self, odds_history: List[Dict]) -> Dict[str, Any]:
        """
        Analyze odds movement patterns.
        
        Args:
            odds_history: List of odds snapshots with timestamps
            
        Returns:
            Dict: Analysis results
        """
        try:
            if len(odds_history) < 2:
                return {
                    'movement': 'stable',
                    'direction': 'none',
                    'speed': 0.0,
                    'volatility': 0.0
                }
            
            # Extract odds and timestamps
            odds_values = [entry['odds'] for entry in odds_history]
            timestamps = [entry['timestamp'] for entry in odds_history]
            
            # Calculate movement direction
            first_odds = odds_values[0]
            last_odds = odds_values[-1]
            
            if last_odds > first_odds:
                direction = 'rising'
            elif last_odds < first_odds:
                direction = 'falling'
            else:
                direction = 'stable'
            
            # Calculate movement speed (odds change per hour)
            time_diff = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
            odds_change = abs(last_odds - first_odds)
            speed = odds_change / time_diff if time_diff > 0 else 0
            
            # Calculate volatility
            volatility = self.calculate_volatility(odds_values)
            
            # Determine movement type
            if speed > 50:  # High speed
                movement = 'rapid'
            elif speed > 20:  # Medium speed
                movement = 'moderate'
            else:  # Low speed
                movement = 'slow'
            
            return {
                'movement': movement,
                'direction': direction,
                'speed': speed,
                'volatility': volatility,
                'odds_change': last_odds - first_odds
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing odds movement: {e}")
            return {
                'movement': 'unknown',
                'direction': 'unknown',
                'speed': 0.0,
                'volatility': 0.0
            }

    def detect_hrr_trap(self, hr_line: float, components: Dict[str, float]) -> Dict[str, Any]:
        """
        Detect if an HRR (Hits + Runs + RBIs) line is a trap.
        
        Args:
            hr_line: The total HRR line (e.g., 2.5)
            components: Dict with individual component lines (e.g., {'hits': 0.5, 'runs': 0.5, 'rbis': 0.5})
            
        Returns:
            Dict with trap analysis
        """
        try:
            # Check if this looks like a trap (all components are 0.5)
            is_trap_like = False
            trap_components = []
            
            for stat, line in components.items():
                if line == 0.5:
                    trap_components.append(stat)
            
            # If all components are 0.5, it's likely a trap
            if len(trap_components) >= 2 and len(trap_components) == len(components):
                is_trap_like = True
            
            # Calculate expected total from components
            expected_total = sum(components.values())
            
            # Check if the HRR line matches the sum of components
            line_matches_components = abs(hr_line - expected_total) < 0.1
            
            # Determine trap risk level
            if is_trap_like and line_matches_components:
                risk_level = "high"
                recommendation = "avoid_hrr"
                confidence_penalty = -0.15
                trap_reason = f"HRR {hr_line} = {trap_components[0]} {components[trap_components[0]]} + {trap_components[1]} {components[trap_components[1]]} + {trap_components[2]} {components[trap_components[2]]} - likely trap"
            elif is_trap_like:
                risk_level = "medium"
                recommendation = "caution"
                confidence_penalty = -0.10
                trap_reason = f"HRR {hr_line} has suspicious 0.5 components"
            else:
                risk_level = "low"
                recommendation = "safe"
                confidence_penalty = 0.0
                trap_reason = "HRR line appears normal"
            
            return {
                'is_trap_like': is_trap_like,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'confidence_penalty': confidence_penalty,
                'trap_reason': trap_reason,
                'components': components,
                'expected_total': expected_total,
                'line_matches_components': line_matches_components,
                'trap_components': trap_components
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting HRR trap: {e}")
            return {
                'is_trap_like': False,
                'risk_level': 'unknown',
                'recommendation': 'unknown',
                'confidence_penalty': 0.0,
                'trap_reason': 'Error in analysis',
                'components': components,
                'expected_total': 0.0,
                'line_matches_components': False,
                'trap_components': []
            }

    def analyze_hrr_breakdown(self, player_name: str, hr_line: float, 
                            individual_props: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Analyze HRR breakdown to determine if individual props are better than HRR.
        
        Args:
            player_name: Player name
            hr_line: HRR line
            individual_props: Dict of individual prop data {'hits': {...}, 'runs': {...}, 'rbis': {...}}
            
        Returns:
            Dict with breakdown analysis
        """
        try:
            # Extract component lines
            components = {}
            for stat, prop_data in individual_props.items():
                if stat in ['hits', 'runs', 'rbis']:
                    components[stat] = prop_data.get('line', 0)
            
            # Detect trap
            trap_analysis = self.detect_hrr_trap(hr_line, components)
            
            # Analyze individual prop confidence
            individual_confidence = {}
            best_individual = None
            best_confidence = 0.0
            
            for stat, prop_data in individual_props.items():
                if stat in ['hits', 'runs', 'rbis']:
                    confidence = prop_data.get('confidence', 0.5)
                    individual_confidence[stat] = confidence
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_individual = stat
            
            # Determine recommendation
            if trap_analysis['is_trap_like']:
                if best_confidence > 0.6:
                    recommendation = f"play_individual_{best_individual}"
                    reasoning = f"HRR is trap ({trap_analysis['trap_reason']}), but {best_individual} has {best_confidence:.1%} confidence"
                else:
                    recommendation = "avoid_all"
                    reasoning = f"HRR is trap and no individual prop has sufficient confidence"
            else:
                recommendation = "play_hrr"
                reasoning = "HRR line appears normal and safe"
            
            return {
                'trap_analysis': trap_analysis,
                'individual_confidence': individual_confidence,
                'best_individual': best_individual,
                'best_confidence': best_confidence,
                'recommendation': recommendation,
                'reasoning': reasoning,
                'hr_line': hr_line,
                'components': components
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing HRR breakdown: {e}")
            return {
                'trap_analysis': {'is_trap_like': False, 'confidence_penalty': 0.0},
                'individual_confidence': {},
                'best_individual': None,
                'best_confidence': 0.0,
                'recommendation': 'unknown',
                'reasoning': 'Error in analysis',
                'hr_line': hr_line,
                'components': {}
            } 