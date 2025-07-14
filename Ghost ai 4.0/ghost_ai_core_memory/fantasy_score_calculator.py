#!/usr/bin/env python3
"""
Fantasy Score Calculator for Ghost AI 3.0 Sportsbook Edition
Calculates fantasy scores from normal props and detects low fantasy for auto-fades
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger('fantasy_score_calculator')

class FantasyScoreCalculator:
    """Advanced fantasy score calculator with auto-fade detection."""
    
    def __init__(self):
        # WNBA Fantasy Score Weights (Underdog Scoring)
        self.wnba_weights = {
            'player_points': 1.0,
            'player_rebounds': 1.2,
            'player_assists': 1.5,
            'player_steals': 3.0,
            'player_blocks': 3.0,
            'player_turnovers': -1.0
        }
        
        # MLB Fantasy Score Weights (Underdog Scoring)
        self.mlb_weights = {
            'batter_singles': 3.0,
            'batter_doubles': 5.0,
            'batter_triples': 8.0,
            'batter_home_runs': 10.0,
            'batter_rbis': 2.0,
            'batter_runs_scored': 2.0,
            'batter_walks': 2.0,
            'batter_stolen_bases': 5.0
        }
        
        # Fantasy score thresholds for auto-fade detection
        self.fantasy_thresholds = {
            'MLB': 7.5,
            'WNBA': 17.0
        }
        
        logger.info("🧮 Fantasy Score Calculator initialized")
    
    def calculate_fantasy_score(self, player_props: List[Dict], sport: str) -> Optional[float]:
        """
        Calculate fantasy score from normal props.
        
        Args:
            player_props: List of props for a player
            sport: 'MLB' or 'WNBA'
            
        Returns:
            Calculated fantasy score or None if insufficient data
        """
        try:
            weights = self.mlb_weights if sport == 'MLB' else self.wnba_weights
            total_fantasy = 0.0
            props_used = 0
            
            for prop in player_props:
                prop_type = prop.get('prop_type', '')
                market_key = self._get_market_key(prop_type, sport)
                
                if market_key in weights:
                    # Get the line value (what the player needs to exceed)
                    line = prop.get('line', 0)
                    weight = weights[market_key]
                    
                    # Calculate expected fantasy contribution
                    # For most props, we assume they'll hit the line (conservative estimate)
                    fantasy_contribution = line * weight
                    total_fantasy += fantasy_contribution
                    props_used += 1
            
            if props_used > 0:
                # Average the fantasy score based on props used
                calculated_fantasy = total_fantasy / props_used
                logger.info(f"🧮 Calculated fantasy score: {calculated_fantasy:.1f} from {props_used} props")
                return calculated_fantasy
            
            return None
            
        except Exception as e:
            logger.error(f"Error calculating fantasy score: {e}")
            return None
    
    def _get_market_key(self, prop_type: str, sport: str) -> str:
        """Convert prop type to market key for weight lookup."""
        if sport == 'MLB':
            # MLB prop type mappings
            mlb_mappings = {
                'Hits': 'batter_singles',  # Assume singles for hits
                'Home Runs': 'batter_home_runs',
                'RBIs': 'batter_rbis',
                'Runs': 'batter_runs_scored',
                'Stolen Bases': 'batter_stolen_bases',
                'Walks': 'batter_walks',
                'Doubles': 'batter_doubles',
                'Triples': 'batter_triples'
            }
            return mlb_mappings.get(prop_type, prop_type.lower())
        
        elif sport == 'WNBA':
            # WNBA prop type mappings
            wnba_mappings = {
                'Points': 'player_points',
                'Rebounds': 'player_rebounds',
                'Assists': 'player_assists',
                'Steals': 'player_steals',
                'Blocks': 'player_blocks',
                'Turnovers': 'player_turnovers',
                'Threes': 'player_points'  # Threes count as points
            }
            return wnba_mappings.get(prop_type, prop_type.lower())
        
        return prop_type.lower()
    
    def is_low_fantasy_player(self, player_props: List[Dict], sport: str) -> Tuple[bool, Optional[float]]:
        """
        Detect if a player has low fantasy score potential.
        
        Args:
            player_props: List of props for a player
            sport: 'MLB' or 'WNBA'
            
        Returns:
            Tuple of (is_low_fantasy, calculated_fantasy_score)
        """
        try:
            # Check if there's already a fantasy score prop
            fantasy_prop = next((p for p in player_props if 'fantasy' in p.get('prop_type', '').lower()), None)
            
            if fantasy_prop:
                fantasy_score = fantasy_prop.get('line', 0)
                threshold = self.fantasy_thresholds.get(sport, 10.0)
                is_low = fantasy_score <= threshold
                
                logger.info(f"🧮 Found fantasy prop: {fantasy_score} (threshold: {threshold})")
                return is_low, fantasy_score
            
            # Calculate fantasy score from normal props
            calculated_fantasy = self.calculate_fantasy_score(player_props, sport)
            
            if calculated_fantasy is not None:
                threshold = self.fantasy_thresholds.get(sport, 10.0)
                is_low = calculated_fantasy <= threshold
                
                logger.info(f"🧮 Calculated fantasy: {calculated_fantasy:.1f} (threshold: {threshold})")
                return is_low, calculated_fantasy
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error detecting low fantasy player: {e}")
            return False, None
    
    def should_auto_fade(self, player_props: List[Dict], sport: str, recent_fantasy_history: Optional[List[float]] = None) -> Tuple[bool, str]:
        """
        Determine if a player should be auto-faded based on fantasy score and history.
        
        Args:
            player_props: List of props for a player
            sport: 'MLB' or 'WNBA'
            recent_fantasy_history: List of recent fantasy scores (optional)
            
        Returns:
            Tuple of (should_fade, reason)
        """
        try:
            is_low_fantasy, fantasy_score = self.is_low_fantasy_player(player_props, sport)
            
            if not is_low_fantasy or fantasy_score is None:
                return False, "Fantasy score above threshold"
            
            # Check for weak prop board (only 0.5 lines)
            has_only_low_lines = self._has_only_low_lines(player_props, sport)
            
            if not has_only_low_lines:
                return False, "Has strong prop lines"
            
            # Check recent history if available
            if recent_fantasy_history:
                recent_avg = sum(recent_fantasy_history[-3:]) / min(len(recent_fantasy_history), 3)
                if recent_avg > fantasy_score * 1.2:  # Recent form is 20% better
                    return False, "Recent form is strong"
            
            # All conditions met - should fade
            reason = f"Low fantasy ({fantasy_score:.1f}), weak prop board, cold history"
            logger.info(f"🧮 Auto-fade detected: {reason}")
            return True, reason
            
        except Exception as e:
            logger.error(f"Error in should_auto_fade: {e}")
            return False, f"Error: {e}"
    
    def _has_only_low_lines(self, player_props: List[Dict], sport: str) -> bool:
        """Check if player only has low-line props (0.5 for MLB, low for WNBA)."""
        try:
            if sport == 'MLB':
                # MLB: Check if all core props are 0.5
                core_props = ['Hits', 'Home Runs', 'RBIs', 'Runs']
                core_lines = [p.get('line', 0) for p in player_props 
                            if p.get('prop_type') in core_props]
                
                if core_lines:
                    return all(line <= 0.5 for line in core_lines)
            
            elif sport == 'WNBA':
                # WNBA: Check if all core props are low (≤ 9.5)
                core_props = ['Points', 'Rebounds', 'Assists', 'Threes']
                core_lines = [p.get('line', 0) for p in player_props 
                            if p.get('prop_type') in core_props]
                
                if core_lines:
                    return all(line <= 9.5 for line in core_lines)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking low lines: {e}")
            return False
    
    def get_fantasy_fade_pick(self, player_props: List[Dict], sport: str) -> Optional[Dict]:
        """
        Generate a fantasy fade pick if conditions are met.
        
        Args:
            player_props: List of props for a player
            sport: 'MLB' or 'WNBA'
            
        Returns:
            Fade pick dict or None
        """
        try:
            should_fade, reason = self.should_auto_fade(player_props, sport)
            
            if not should_fade:
                return None
            
            # Find fantasy score prop or calculate
            fantasy_prop = next((p for p in player_props if 'fantasy' in p.get('prop_type', '').lower()), None)
            
            if fantasy_prop:
                return {
                    'player_name': fantasy_prop.get('player_name', ''),
                    'prop_type': fantasy_prop.get('prop_type', 'Fantasy Score'),
                    'line': fantasy_prop.get('line', 0),
                    'pick_side': 'Under',
                    'sport': sport,
                    'odds': fantasy_prop.get('odds', 0),
                    'confidence': 0.8,  # High confidence for auto-fades
                    'reason': reason,
                    'tag': 'auto-fade-low-fantasy'
                }
            
            # Calculate fantasy score if no fantasy prop exists
            calculated_fantasy = self.calculate_fantasy_score(player_props, sport)
            
            if calculated_fantasy is not None:
                return {
                    'player_name': player_props[0].get('player_name', ''),
                    'prop_type': 'Fantasy Score',
                    'line': calculated_fantasy,
                    'pick_side': 'Under',
                    'sport': sport,
                    'odds': -110,  # Default odds
                    'confidence': 0.8,
                    'reason': reason,
                    'tag': 'auto-fade-calculated-fantasy'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating fantasy fade pick: {e}")
            return None 