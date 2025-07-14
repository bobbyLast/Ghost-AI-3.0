"""
AI Data Loader for Ghost AI Reverse Engine Integration
Provides access to reverse engine analysis data
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIDataLoader:
    """
    Loads and provides access to reverse engine analysis data
    """
    
    def __init__(self):
        self.data_dir = Path("odds_reverse_engineering/data")
        self.analysis_file = self.data_dir / "ai_analysis.json"
        self.memory_file = self.data_dir / "ghost_confidence" / "prop_memory.json"
        
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "ghost_confidence").mkdir(parents=True, exist_ok=True)
        
        # Load data
        self.analysis_data = self._load_analysis_data()
        self.memory_data = self._load_memory_data()
    
    def _load_analysis_data(self) -> Dict[str, Any]:
        """Load analysis data from file"""
        if self.analysis_file.exists():
            try:
                with open(self.analysis_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading analysis data: {e}")
        return {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "hot_picks": [],
            "trap_risks": [],
            "player_analysis": {},
            "analysis_available": False
        }
    
    def _load_memory_data(self) -> Dict[str, Any]:
        """Load memory data from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading memory data: {e}")
        return {}
    
    def get_enhanced_confidence_score(self, player_name: str, prop_type: str, base_confidence: float) -> float:
        """Get enhanced confidence score for a player/prop combination"""
        try:
            # Check if we have analysis for this player
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                confidence_boost = analysis.get("confidence_boost", 0)
                risk_penalty = analysis.get("risk_penalty", 0)
                
                enhanced_confidence = base_confidence + confidence_boost - risk_penalty
                enhanced_confidence = max(0.1, min(0.95, enhanced_confidence))
                
                return enhanced_confidence
            
            # No analysis available, return base confidence
            return base_confidence
            
        except Exception as e:
            logger.error(f"Error getting enhanced confidence for {player_name} {prop_type}: {e}")
            return base_confidence
    
    def get_player_trend_tag(self, player_name: str, prop_type: str) -> str:
        """Get trend tag for a player/prop combination"""
        try:
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                return analysis.get("trend_tag", "📊 Neutral")
            
            return "📊 Neutral"
            
        except Exception as e:
            logger.error(f"Error getting trend tag for {player_name} {prop_type}: {e}")
            return "📊 Neutral"
    
    def get_player_ghost_read(self, player_name: str, prop_type: str) -> str:
        """Get Ghost AI read for a player/prop combination"""
        try:
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                return analysis.get("ghost_read", "🤖 No read available")
            
            return "🤖 No read available"
            
        except Exception as e:
            logger.error(f"Error getting ghost read for {player_name} {prop_type}: {e}")
            return "🤖 No read available"
    
    def get_player_confidence_trend(self, player_name: str, prop_type: str) -> str:
        """Get confidence trend for a player/prop combination"""
        try:
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                trend = analysis.get("confidence_trend", "stable")
                
                if trend == "rising":
                    return "📈 Rising"
                elif trend == "falling":
                    return "📉 Falling"
                else:
                    return "➡️ Stable"
            
            return "➡️ Stable"
            
        except Exception as e:
            logger.error(f"Error getting confidence trend for {player_name} {prop_type}: {e}")
            return "➡️ Stable"
    
    def get_player_risk_rating(self, player_name: str, prop_type: str) -> str:
        """Get risk rating for a player/prop combination"""
        try:
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                risk_level = analysis.get("risk_level", "medium")
                
                if risk_level == "high":
                    return "⛔ High Risk"
                elif risk_level == "low":
                    return "✅ Low Risk"
                else:
                    return "⚠️ Medium Risk"
            
            return "⚠️ Medium Risk"
            
        except Exception as e:
            logger.error(f"Error getting risk rating for {player_name} {prop_type}: {e}")
            return "⚠️ Medium Risk"
    
    def is_hot_pick(self, player_name: str, prop_type: str) -> bool:
        """Check if a player/prop is a hot pick"""
        try:
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                return analysis.get("is_hot_pick", False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking hot pick for {player_name} {prop_type}: {e}")
            return False
    
    def is_trap_risk(self, player_name: str, prop_type: str) -> bool:
        """Check if a player/prop is a trap risk"""
        try:
            player_key = f"{player_name}_{prop_type}"
            
            if player_key in self.analysis_data.get("player_analysis", {}):
                analysis = self.analysis_data["player_analysis"][player_key]
                return analysis.get("is_trap_risk", False)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking trap risk for {player_name} {prop_type}: {e}")
            return False
    
    def get_hot_picks(self) -> List[Dict]:
        """Get list of hot picks"""
        return self.analysis_data.get("hot_picks", [])
    
    def get_trap_risks(self) -> List[Dict]:
        """Get list of trap risks"""
        return self.analysis_data.get("trap_risks", [])
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """Get analysis status"""
        return {
            "analysis_available": self.analysis_data.get("analysis_available", False),
            "analysis_timestamp": self.analysis_data.get("analysis_timestamp", ""),
            "total_players_analyzed": len(self.analysis_data.get("player_analysis", {})),
            "hot_picks_count": len(self.analysis_data.get("hot_picks", [])),
            "trap_risks_count": len(self.analysis_data.get("trap_risks", []))
        }
    
    def get_analysis_timestamp(self) -> str:
        """Get analysis timestamp"""
        return self.analysis_data.get("analysis_timestamp", datetime.now(timezone.utc).isoformat())
    
    def is_analysis_fresh(self) -> bool:
        """Check if analysis is fresh (less than 24 hours old)"""
        try:
            timestamp_str = self.analysis_data.get("analysis_timestamp", "")
            if not timestamp_str:
                return False
            
            analysis_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            
            # Check if analysis is less than 24 hours old
            time_diff = current_time - analysis_time
            return time_diff.total_seconds() < 24 * 3600
            
        except Exception as e:
            logger.error(f"Error checking analysis freshness: {e}")
            return False
    
    def create_mock_analysis_data(self):
        """Create mock analysis data for testing"""
        mock_data = {
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_available": True,
            "hot_picks": [
                {"player": "Mike Trout", "prop": "hits", "trend_tag": "🔥 Hot"},
                {"player": "Shohei Ohtani", "prop": "strikeouts", "trend_tag": "📈 Rising"}
            ],
            "trap_risks": [
                {"player": "Player X", "prop": "runs", "trend_tag": "❄️ Cold"},
                {"player": "Player Y", "prop": "walks", "trend_tag": "📉 Falling"}
            ],
            "player_analysis": {
                "Mike Trout_hits": {
                    "confidence_boost": 0.1,
                    "risk_penalty": 0.0,
                    "trend_tag": "🔥 Hot",
                    "ghost_read": "🤖 Strong confidence in over",
                    "confidence_trend": "rising",
                    "risk_level": "low",
                    "is_hot_pick": True,
                    "is_trap_risk": False
                },
                "Shohei Ohtani_strikeouts": {
                    "confidence_boost": 0.15,
                    "risk_penalty": 0.0,
                    "trend_tag": "📈 Rising",
                    "ghost_read": "🤖 Excellent recent form",
                    "confidence_trend": "rising",
                    "risk_level": "low",
                    "is_hot_pick": True,
                    "is_trap_risk": False
                }
            }
        }
        
        # Save mock data
        with open(self.analysis_file, 'w') as f:
            json.dump(mock_data, f, indent=2)
        
        self.analysis_data = mock_data
        logger.info("✅ Created mock analysis data")

if __name__ == "__main__":
    # Test the data loader
    print("🧪 Testing AI Data Loader")
    print("="*50)
    
    loader = AIDataLoader()
    
    # Create mock data for testing
    loader.create_mock_analysis_data()
    
    # Test enhanced confidence
    confidence = loader.get_enhanced_confidence_score("Mike Trout", "hits", 0.75)
    print(f"Enhanced confidence for Mike Trout hits: {confidence:.3f}")
    
    # Test trend tag
    trend = loader.get_player_trend_tag("Mike Trout", "hits")
    print(f"Trend tag for Mike Trout hits: {trend}")
    
    # Test hot pick
    is_hot = loader.is_hot_pick("Mike Trout", "hits")
    print(f"Is Mike Trout hits a hot pick: {is_hot}")
    
    # Test analysis status
    status = loader.get_analysis_status()
    print(f"Analysis status: {status}")
    
    # Test hot picks
    hot_picks = loader.get_hot_picks()
    print(f"Hot picks: {hot_picks}") 