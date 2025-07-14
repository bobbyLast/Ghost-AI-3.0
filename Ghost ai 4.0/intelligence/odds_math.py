#!/usr/bin/env python3
"""
Odds Mathematics Module
Provides mathematical functions for odds analysis and calculations.
"""

import math
from typing import Dict, List, Optional, Tuple

class OddsMath:
    """Mathematical utilities for odds analysis and calculations"""
    
    @staticmethod
    def american_to_decimal(american_odds: int) -> float:
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    @staticmethod
    def decimal_to_american(decimal_odds: float) -> int:
        """Convert decimal odds to American odds"""
        if decimal_odds >= 2:
            return int((decimal_odds - 1) * 100)
        else:
            return int(-100 / (decimal_odds - 1))
    
    @staticmethod
    def implied_probability(american_odds: int) -> float:
        """Calculate implied probability from American odds"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    @staticmethod
    def calculate_ev(probability: float, american_odds: int) -> float:
        """Calculate expected value"""
        decimal_odds = OddsMath.american_to_decimal(american_odds)
        return (probability * (decimal_odds - 1)) - (1 - probability)
    
    @staticmethod
    def kelly_criterion(probability: float, american_odds: int) -> float:
        """Calculate Kelly Criterion bet size"""
        decimal_odds = OddsMath.american_to_decimal(american_odds)
        return (probability * decimal_odds - 1) / (decimal_odds - 1)
    
    @staticmethod
    def calculate_parlay_odds(odds_list: List[int]) -> int:
        """Calculate parlay odds from a list of American odds"""
        decimal_odds = 1.0
        for odds in odds_list:
            decimal_odds *= OddsMath.american_to_decimal(odds)
        return OddsMath.decimal_to_american(decimal_odds)
    
    @staticmethod
    def calculate_hedge_bet(original_odds: int, hedge_odds: int, original_bet: float) -> float:
        """Calculate hedge bet size for guaranteed profit"""
        original_decimal = OddsMath.american_to_decimal(original_odds)
        hedge_decimal = OddsMath.american_to_decimal(hedge_odds)
        
        hedge_bet = (original_bet * original_decimal) / hedge_decimal
        return hedge_bet
    
    @staticmethod
    def calculate_arbitrage(odds1: int, odds2: int) -> Optional[Dict[str, float]]:
        """Calculate arbitrage opportunity between two odds"""
        prob1 = OddsMath.implied_probability(odds1)
        prob2 = OddsMath.implied_probability(odds2)
        
        total_prob = prob1 + prob2
        
        if total_prob < 1.0:
            # Arbitrage opportunity exists
            stake1 = 100 / total_prob
            stake2 = stake1 * (prob1 / prob2)
            
            return {
                'stake1': stake1,
                'stake2': stake2,
                'profit': stake1 - 100,
                'roi': ((stake1 - 100) / 100) * 100
            }
        return None
    
    @staticmethod
    def calculate_confidence_score(historical_data: List[Dict]) -> float:
        """Calculate confidence score based on historical performance"""
        if not historical_data:
            return 0.0
        
        wins = sum(1 for result in historical_data if result.get('result') == 'win')
        total = len(historical_data)
        
        if total == 0:
            return 0.0
        
        win_rate = wins / total
        
        # Adjust confidence based on sample size
        confidence = win_rate * min(total / 10, 1.0)  # Cap at 10 samples
        
        return min(confidence, 1.0)  # Cap at 100%
    
    @staticmethod
    def calculate_value_rating(implied_prob: float, our_prob: float) -> float:
        """Calculate value rating for a bet"""
        if our_prob <= implied_prob:
            return 0.0
        
        # Value = (Our Probability - Implied Probability) / Implied Probability
        value = (our_prob - implied_prob) / implied_prob
        return min(value, 1.0)  # Cap at 100% value
    
    @staticmethod
    def calculate_optimal_bet_size(bankroll: float, confidence: float, odds: int) -> float:
        """Calculate optimal bet size using Kelly Criterion with confidence adjustment"""
        implied_prob = OddsMath.implied_probability(odds)
        kelly_fraction = OddsMath.kelly_criterion(confidence, odds)
        
        # Conservative approach: use 1/4 Kelly
        conservative_fraction = kelly_fraction * 0.25
        
        # Ensure bet size doesn't exceed bankroll
        max_bet = bankroll * 0.05  # Max 5% of bankroll
        kelly_bet = bankroll * conservative_fraction
        
        return min(kelly_bet, max_bet)

# Convenience functions
def american_to_decimal(american_odds: int) -> float:
    """Convert American odds to decimal odds"""
    return OddsMath.american_to_decimal(american_odds)

def implied_probability(american_odds: int) -> float:
    """Calculate implied probability from American odds"""
    return OddsMath.implied_probability(american_odds)

def calculate_ev(probability: float, american_odds: int) -> float:
    """Calculate expected value"""
    return OddsMath.calculate_ev(probability, american_odds)

def calculate_confidence_score(historical_data: List[Dict]) -> float:
    """Calculate confidence score based on historical performance"""
    return OddsMath.calculate_confidence_score(historical_data) 