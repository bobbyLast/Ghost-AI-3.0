"""
Ghost AI Reverse Engineering Integration

This module provides integration between the main Ghost AI system and the reverse engineering engine.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import the reverse engineering engine
try:
    from ghost_ai_core_memory.reverse_engine_oddsapi import ReverseEngineOddsAPI, PropOutcome
except ImportError:
    # Fallback if the module is not available
    ReverseEngineOddsAPI = None
    PropOutcome = None

logger = logging.getLogger(__name__)

class GhostAIReverseIntegration:
    """Integration class for reverse engineering with Ghost AI"""
    
    def __init__(self):
        if ReverseEngineOddsAPI is None:
            logger.warning("ReverseEngineOddsAPI not available - reverse engineering disabled")
            self.reverse_engine = None
        else:
            self.reverse_engine = ReverseEngineOddsAPI()
            logger.info("Ghost AI Reverse Integration initialized")
    
    async def run_daily_integration(self, sport: str) -> Optional[Dict]:
        """
        Run daily reverse engineering analysis for a sport.
        
        Args:
            sport: Sport key (e.g., 'baseball_mlb', 'basketball_wnba')
            
        Returns:
            Analysis results or None if failed
        """
        if self.reverse_engine is None:
            logger.warning("Reverse engineering not available")
            return None
            
        try:
            logger.info(f"Starting daily reverse engineering analysis for {sport}")
            
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Run daily analysis
            results = await self.reverse_engine.run_daily_analysis(sport, today)
                
            if results:
                logger.info(f"Daily analysis completed for {sport}: {len(results)} results")
                return {
                    'sport': sport,
                    'date': today,
                    'total_games': len(results),
                    'analysis_results': results
                }
            else:
                logger.warning(f"No analysis results for {sport} on {today}")
                return None
            
        except Exception as e:
            logger.error(f"Error in daily integration for {sport}: {e}")
            return None
    
    def enhance_prop_confidence(self, prop: Dict) -> Dict:
        """
        Enhance a prop with historical confidence data.
        
        Args:
            prop: Prop dictionary to enhance
            
        Returns:
            Enhanced prop dictionary
        """
        if self.reverse_engine is None:
            return prop
            
        try:
            player_name = prop.get('player_name', '')
            prop_type = prop.get('prop_type', '')
            sport = prop.get('sport', 'mlb')
            
            if not player_name or not prop_type:
                return prop
            
            # Get historical performance for this player/prop combination
            historical_data = self.reverse_engine.analyze_historical_performance(
                player=player_name, 
                market=prop_type, 
                sport=sport
            )
            
            # Apply confidence adjustments based on historical data
            base_confidence = prop.get('confidence', 0.5)
            enhanced_confidence = base_confidence
            
            if historical_data:
                # Boost confidence for historically successful combinations
                success_rate = historical_data.get('success_rate', 0.5)
                if success_rate > 0.6:
                    enhanced_confidence += 0.1
                elif success_rate < 0.4:
                    enhanced_confidence -= 0.1
                
                # Add historical data to prop
                prop['historical_analysis'] = historical_data
                prop['enhanced_confidence'] = min(0.95, max(0.05, enhanced_confidence))
            
            return prop
                
        except Exception as e:
            logger.error(f"Error enhancing prop confidence: {e}")
            return prop
    
    def learn_and_save_prop_result(self, prop: Dict, result: str, final_stat: float):
        """
        Learn from a prop result and save it for future analysis.
        
        Args:
            prop: Prop dictionary
            result: Result ('hit' or 'miss')
            final_stat: Final statistical value
        """
        if self.reverse_engine is None or PropOutcome is None:
            logger.warning("Reverse engineering not available - cannot save prop result")
            return
            
        try:
            # Create prop outcome
            outcome = PropOutcome(
                event_id=prop.get('game_info', {}).get('id', ''),
                player=prop.get('player_name', ''),
                market=prop.get('prop_type', ''),
                line=prop.get('line', 0),
                side=prop.get('pick_side', '').lower(),
                odds=prop.get('odds', 0),
                bookmaker=prop.get('bookmaker', ''),
                closing_time=prop.get('game_info', {}).get('commence_time', ''),
                result=result,
                final_stat=final_stat,
                tags=[],
                confidence_predicted=prop.get('confidence', 0),
                ghost_pick=prop.get('pick_side', '').lower()
            )
            
            # Save the outcome
            sport = 'mlb' if 'batter_' in prop.get('prop_type', '') or 'pitcher_' in prop.get('prop_type', '') else 'wnba'
            self.reverse_engine.save_prop_outcome(outcome, sport)
            
            logger.info(f"Saved prop result for {prop.get('player_name', '')} - {result}")
            
        except Exception as e:
            logger.error(f"Error saving prop result: {e}")
        else:
            pass 