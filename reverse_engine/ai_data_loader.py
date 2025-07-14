"""
AI Data Loader for Ghost AI
Allows Ghost AI to pull reverse engine analysis data instead of recalculating
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class AIDataLoader:
    """
    Loads reverse engine analysis data for Ghost AI to use
    Eliminates need to recalculate historical patterns
    """
    
    def __init__(self, data_dir: str = "ghost_ai_core_memory/odds_analysis"):
        self.data_dir = Path(data_dir)
        self.current_summary_file = self.data_dir / "current_analysis_summary.json"
        self.prop_memory_file = Path("odds_reverse_engineering_test/data/prop_memory.json")
        
    def get_player_analysis(self, player_name: str, prop_type: str) -> Optional[Dict]:
        """
        Get analysis data for a specific player/prop combination
        
        Args:
            player_name: Name of the player
            prop_type: Type of prop (e.g., 'hits', 'strikeouts')
            
        Returns:
            Analysis data dict or None if not found
        """
        if not self.current_summary_file.exists():
            logger.warning("No current analysis summary found")
            return None
        
        try:
            with open(self.current_summary_file, 'r') as f:
                summary_data = json.load(f)
            
            key = f"{player_name}_{prop_type}"
            return summary_data.get('players_analyzed', {}).get(key)
            
        except Exception as e:
            logger.error(f"Error loading player analysis: {e}")
            return None
    
    def get_hot_picks(self) -> List[Dict]:
        """Get list of current hot picks"""
        if not self.current_summary_file.exists():
            return []
        
        try:
            with open(self.current_summary_file, 'r') as f:
                summary_data = json.load(f)
            
            return summary_data.get('hot_picks', [])
            
        except Exception as e:
            logger.error(f"Error loading hot picks: {e}")
            return []
    
    def get_trap_risks(self) -> List[Dict]:
        """Get list of current trap risks"""
        if not self.current_summary_file.exists():
            return []
        
        try:
            with open(self.current_summary_file, 'r') as f:
                summary_data = json.load(f)
            
            return summary_data.get('trap_risks', [])
            
        except Exception as e:
            logger.error(f"Error loading trap risks: {e}")
            return []
    
    def get_trend_summary(self) -> Dict:
        """Get overall trend summary"""
        if not self.current_summary_file.exists():
            return {}
        
        try:
            with open(self.current_summary_file, 'r') as f:
                summary_data = json.load(f)
            
            return summary_data.get('trend_summary', {})
            
        except Exception as e:
            logger.error(f"Error loading trend summary: {e}")
            return {}
    
    def get_all_analyzed_players(self) -> List[str]:
        """Get list of all players that have been analyzed"""
        if not self.current_summary_file.exists():
            return []
        
        try:
            with open(self.current_summary_file, 'r') as f:
                summary_data = json.load(f)
            
            return list(summary_data.get('players_analyzed', {}).keys())
            
        except Exception as e:
            logger.error(f"Error loading analyzed players: {e}")
            return []
    
    def get_odds_memory_data(self) -> Dict:
        """Get the full odds memory data for advanced analysis"""
        if not self.prop_memory_file.exists():
            return {}
        
        try:
            with open(self.prop_memory_file, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading odds memory: {e}")
            return {}
    
    def get_player_confidence_trend(self, player_name: str, prop_type: str) -> Optional[str]:
        """Get confidence trend for a player/prop"""
        analysis = self.get_player_analysis(player_name, prop_type)
        if analysis and 'confidence_drift' in analysis:
            return analysis['confidence_drift'].get('trend')
        return None
    
    def get_player_risk_rating(self, player_name: str, prop_type: str) -> Optional[str]:
        """Get risk rating for a player/prop"""
        analysis = self.get_player_analysis(player_name, prop_type)
        if analysis and 'confidence_drift' in analysis:
            return analysis['confidence_drift'].get('risk_rating')
        return None
    
    def get_player_trend_tag(self, player_name: str, prop_type: str) -> Optional[str]:
        """Get trend tag for a player/prop"""
        analysis = self.get_player_analysis(player_name, prop_type)
        if analysis:
            return analysis.get('trend_tag')
        return None
    
    def get_player_ghost_read(self, player_name: str, prop_type: str) -> Optional[str]:
        """Get ghost read for a player/prop"""
        analysis = self.get_player_analysis(player_name, prop_type)
        if analysis:
            return analysis.get('ghost_read')
        return None
    
    def is_hot_pick(self, player_name: str, prop_type: str) -> bool:
        """Check if a player/prop is a hot pick"""
        hot_picks = self.get_hot_picks()
        return any(pick['player'] == player_name and pick['prop'] == prop_type for pick in hot_picks)
    
    def is_trap_risk(self, player_name: str, prop_type: str) -> bool:
        """Check if a player/prop is a trap risk"""
        trap_risks = self.get_trap_risks()
        return any(risk['player'] == player_name and risk['prop'] == prop_type for risk in trap_risks)
    
    def get_enhanced_confidence_score(self, player_name: str, prop_type: str, base_confidence: float) -> float:
        """
        Calculate enhanced confidence score using reverse engine analysis
        
        Args:
            player_name: Name of the player
            prop_type: Type of prop
            base_confidence: Base confidence score from Ghost AI
            
        Returns:
            Enhanced confidence score
        """
        enhanced_confidence = base_confidence
        
        # Boost for hot picks
        if self.is_hot_pick(player_name, prop_type):
            enhanced_confidence += 0.15
            logger.info(f"🔥 Hot pick boost for {player_name} {prop_type}")
        
        # Penalty for trap risks
        if self.is_trap_risk(player_name, prop_type):
            enhanced_confidence -= 0.20
            logger.info(f"⛔ Trap risk penalty for {player_name} {prop_type}")
        
        # Adjust based on confidence trend
        trend = self.get_player_confidence_trend(player_name, prop_type)
        if trend:
            if "🔥" in trend:
                enhanced_confidence += 0.10
            elif "🔻" in trend:
                enhanced_confidence -= 0.10
        
        # Adjust based on risk rating
        risk_rating = self.get_player_risk_rating(player_name, prop_type)
        if risk_rating:
            if "⛔" in risk_rating:
                enhanced_confidence -= 0.15
            elif "✅" in risk_rating:
                enhanced_confidence += 0.10
        
        return max(0.0, min(1.0, enhanced_confidence))
    
    def get_analysis_timestamp(self) -> Optional[str]:
        """Get timestamp of last analysis"""
        if not self.current_summary_file.exists():
            return None
        
        try:
            with open(self.current_summary_file, 'r') as f:
                summary_data = json.load(f)
            
            return summary_data.get('timestamp')
            
        except Exception as e:
            logger.error(f"Error getting analysis timestamp: {e}")
            return None
    
    def is_analysis_fresh(self, max_age_hours: int = 24) -> bool:
        """
        Check if analysis data is fresh (within specified hours)
        
        Args:
            max_age_hours: Maximum age in hours for data to be considered fresh
            
        Returns:
            True if data is fresh, False otherwise
        """
        timestamp_str = self.get_analysis_timestamp()
        if not timestamp_str:
            return False
        
        try:
            analysis_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            age_hours = (current_time - analysis_time).total_seconds() / 3600
            
            return age_hours <= max_age_hours
            
        except Exception as e:
            logger.error(f"Error checking analysis freshness: {e}")
            return False
    
    def get_analysis_status(self) -> Dict:
        """Get comprehensive analysis status"""
        return {
            'has_data': self.current_summary_file.exists(),
            'is_fresh': self.is_analysis_fresh(),
            'timestamp': self.get_analysis_timestamp(),
            'total_players': len(self.get_all_analyzed_players()),
            'hot_picks_count': len(self.get_hot_picks()),
            'trap_risks_count': len(self.get_trap_risks()),
            'trend_summary': self.get_trend_summary()
        }

# Example usage for Ghost AI integration
def integrate_with_ghost_ai():
    """
    Example of how Ghost AI can integrate with the reverse engine data
    """
    loader = AIDataLoader()
    
    # Check if we have fresh analysis data
    if not loader.is_analysis_fresh():
        logger.warning("Analysis data is stale - consider running reverse engine")
        return
    
    # Example: Enhance a player's confidence score
    player_name = "Mike Trout"
    prop_type = "hits"
    base_confidence = 0.75
    
    enhanced_confidence = loader.get_enhanced_confidence_score(
        player_name, prop_type, base_confidence
    )
    
    logger.info(f"Base confidence: {base_confidence}")
    logger.info(f"Enhanced confidence: {enhanced_confidence}")
    
    # Get trend information
    trend_tag = loader.get_player_trend_tag(player_name, prop_type)
    ghost_read = loader.get_player_ghost_read(player_name, prop_type)
    
    logger.info(f"Trend tag: {trend_tag}")
    logger.info(f"Ghost read: {ghost_read}")
    
    # Check if it's a hot pick or trap risk
    if loader.is_hot_pick(player_name, prop_type):
        logger.info("🔥 This is a hot pick!")
    elif loader.is_trap_risk(player_name, prop_type):
        logger.info("⛔ This is a trap risk!")

if __name__ == "__main__":
    # Test the data loader
    integrate_with_ghost_ai() 