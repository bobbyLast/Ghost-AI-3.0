#!/usr/bin/env python3
"""
Reverse Engine Integration for Ghost AI 3.0 Sportsbook Edition
Integrates with existing reverse engineering system for enhanced analysis
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger('reverse_engine_integration')

class ReverseEngineIntegration:
    """Integration with reverse engineering system for enhanced analysis."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.reverse_engine_dir = base_dir / 'odds_reverse_engineering'
        self.ai_data_file = self.reverse_engine_dir / 'data' / 'ai_analysis.json'
        
        # Import reverse engine modules
        self.reverse_engine = None
        self.ai_analyzer = None
        
        try:
            # Add reverse engine to path
            sys.path.append(str(self.reverse_engine_dir))
            
            # Import modules (optional)
            try:
                from auto_odds_analyzer import AutoOddsAnalyzer
                self.ai_analyzer = AutoOddsAnalyzer()
            except ImportError:
                logger.warning("AutoOddsAnalyzer not available")
            
            logger.info("🔬 Reverse Engine Integration initialized")
            
        except Exception as e:
            logger.error(f"Error initializing reverse engine: {e}")
    
    def analyze_props_with_ai(self, props: List[Dict], sport: str) -> List[Dict]:
        """
        Analyze props using reverse engineering AI.
        
        Args:
            props: List of props to analyze
            sport: Sport type
            
        Returns:
            Props with enhanced analysis
        """
        try:
            if not self.ai_analyzer:
                logger.warning("Reverse engine not available, returning original props")
                return props
            
            # Prepare data for analysis
            analysis_data = {
                'props': props,
                'sport': sport,
                'timestamp': datetime.now().isoformat()
            }
            
            # Run AI analysis
            enhanced_props = self.ai_analyzer.enhance_props_with_ai(analysis_data)
            
            if enhanced_props:
                logger.info(f"🔬 Enhanced {len(enhanced_props)} props with AI analysis")
                return enhanced_props
            
            return props
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return props
    
    def get_historical_analysis(self, player_name: str, prop_type: str, sport: str) -> Optional[Dict]:
        """
        Get historical analysis for a player/prop combination.
        
        Args:
            player_name: Player name
            prop_type: Prop type
            sport: Sport type
            
        Returns:
            Historical analysis data or None
        """
        try:
            if not self.ai_analyzer:
                return None
            
            # Get historical data
            historical_data = self.ai_analyzer.get_player_prop_history(
                player_name, prop_type, sport
            )
            
            if historical_data:
                logger.info(f"🔬 Found historical data for {player_name} {prop_type}")
                return historical_data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting historical analysis: {e}")
            return None
    
    def calculate_confidence_score(self, prop: Dict, historical_data: Optional[Dict] = None) -> float:
        """
        Calculate confidence score using reverse engineering analysis.
        
        Args:
            prop: Prop data
            historical_data: Historical analysis data
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        try:
            base_confidence = prop.get('confidence', 0.5)
            
            if not historical_data:
                return base_confidence
            
            # Extract key metrics from historical data
            hit_rate = historical_data.get('hit_rate', 0.5)
            avg_performance = historical_data.get('avg_performance', 0)
            line_accuracy = historical_data.get('line_accuracy', 0.5)
            
            # Calculate enhanced confidence
            enhanced_confidence = base_confidence
            
            # Adjust based on hit rate
            if hit_rate > 0.6:
                enhanced_confidence += 0.1
            elif hit_rate < 0.4:
                enhanced_confidence -= 0.1
            
            # Adjust based on line accuracy
            if line_accuracy > 0.7:
                enhanced_confidence += 0.05
            elif line_accuracy < 0.3:
                enhanced_confidence -= 0.05
            
            # Clamp to valid range
            enhanced_confidence = max(0.1, min(0.95, enhanced_confidence))
            
            logger.info(f"🔬 Enhanced confidence: {base_confidence:.2f} -> {enhanced_confidence:.2f}")
            return enhanced_confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return prop.get('confidence', 0.5)
    
    def detect_value_opportunities(self, props: List[Dict], sport: str) -> List[Dict]:
        """
        Detect value opportunities using reverse engineering analysis.
        
        Args:
            props: List of props
            sport: Sport type
            
        Returns:
            Props with value opportunities highlighted
        """
        try:
            if not self.ai_analyzer:
                return props
            
            value_props = []
            
            for prop in props:
                player_name = prop.get('player_name', '')
                prop_type = prop.get('prop_type', '')
                
                # Get historical analysis
                historical_data = self.get_historical_analysis(player_name, prop_type, sport)
                
                if historical_data:
                    # Check for value opportunities
                    line = prop.get('line', 0)
                    historical_avg = historical_data.get('avg_performance', 0)
                    
                    # Value opportunity: historical average significantly higher than line
                    if historical_avg > line * 1.2:
                        prop['value_opportunity'] = True
                        prop['historical_avg'] = historical_avg
                        prop['value_margin'] = (historical_avg - line) / line
                        
                        logger.info(f"🔬 Value opportunity: {player_name} {prop_type}")
                        logger.info(f"   Line: {line}, Historical Avg: {historical_avg:.2f}")
                    
                    # Enhanced confidence
                    prop['confidence'] = self.calculate_confidence_score(prop, historical_data)
                
                value_props.append(prop)
            
            return value_props
            
        except Exception as e:
            logger.error(f"Error detecting value opportunities: {e}")
            return props
    
    def get_market_movements(self, props: List[Dict]) -> Dict[str, Dict]:
        """
        Get market movement analysis for props.
        
        Args:
            props: List of props
            
        Returns:
            Market movement data by player
        """
        try:
            if not self.ai_analyzer:
                return {}
            
            market_data = {}
            
            for prop in props:
                player_name = prop.get('player_name', '')
                prop_type = prop.get('prop_type', '')
                
                if player_name not in market_data:
                    market_data[player_name] = {}
                
                # Get market movement data
                movement_data = self.ai_analyzer.get_market_movement(
                    player_name, prop_type
                )
                
                if movement_data:
                    market_data[player_name][prop_type] = movement_data
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market movements: {e}")
            return {}
    
    def enhance_prop_with_analysis(self, prop: Dict, sport: str) -> Dict:
        """
        Enhance a single prop with reverse engineering analysis.
        
        Args:
            prop: Prop data
            sport: Sport type
            
        Returns:
            Enhanced prop data
        """
        try:
            enhanced_prop = prop.copy()
            
            # Get historical analysis
            historical_data = self.get_historical_analysis(
                prop.get('player_name', ''),
                prop.get('prop_type', ''),
                sport
            )
            
            if historical_data:
                # Add historical insights
                enhanced_prop['historical_data'] = historical_data
                
                # Calculate enhanced confidence
                enhanced_prop['confidence'] = self.calculate_confidence_score(prop, historical_data)
                
                # Add value indicators
                line = prop.get('line', 0)
                historical_avg = historical_data.get('avg_performance', 0)
                
                if historical_avg > line * 1.15:
                    enhanced_prop['value_play'] = True
                    enhanced_prop['value_margin'] = (historical_avg - line) / line
                
                logger.info(f"🔬 Enhanced prop: {prop.get('player_name')} {prop.get('prop_type')}")
            
            return enhanced_prop
            
        except Exception as e:
            logger.error(f"Error enhancing prop: {e}")
            return prop
    
    def get_ai_recommendations(self, props: List[Dict], sport: str) -> List[Dict]:
        """
        Get AI recommendations for props.
        
        Args:
            props: List of props
            sport: Sport type
            
        Returns:
            Props with AI recommendations
        """
        try:
            if not self.ai_analyzer:
                return props
            
            # Run AI analysis
            enhanced_props = self.analyze_props_with_ai(props, sport)
            
            # Detect value opportunities
            value_props = self.detect_value_opportunities(enhanced_props, sport)
            
            # Sort by confidence and value
            value_props.sort(key=lambda p: (
                p.get('value_play', False),
                p.get('confidence', 0)
            ), reverse=True)
            
            logger.info(f"🔬 Generated AI recommendations for {len(value_props)} props")
            return value_props
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")
            return props 