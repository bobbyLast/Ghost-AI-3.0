"""
Odds Tracker for Ghost AI Odds Intelligence System

This module tracks odds movement, trends, and historical patterns
to enable odds-based intelligence without relying on stat feeds.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np

logger = logging.getLogger(__name__)

class OddsTracker:
    """Tracks odds movement and trends for odds intelligence."""
    
    def __init__(self, memory_dir: str = "odds_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
    def track_odds_trend(self, player: str, stat_type: str, sport: str, 
                        current_odds: Dict) -> Dict:
        """
        Track odds trend for a player and stat type.
        
        Args:
            player: Player name
            stat_type: Stat type (points, rebounds, etc.)
            sport: Sport (basketball_nba, baseball_mlb, etc.)
            current_odds: Current odds data
            
        Returns:
            Trend analysis with confidence and tags
        """
        try:
            # Load historical odds
            historical_odds = self._load_historical_odds(player, stat_type, sport)
            
            if not historical_odds:
                return {
                    'trend': 'neutral',
                    'movement': 'stable',
                    'confidence': 0.5,
                    'tags': ['📊 New Prop'],
                    'historical_count': 0
                }
            
            # Get last 3 historical under odds
            recent_odds = historical_odds[-3:] if len(historical_odds) >= 3 else historical_odds
            under_odds_history = [odds['under_odds'] for odds in recent_odds if odds.get('under_odds')]
            
            if len(under_odds_history) < 2:
                return {
                    'trend': 'neutral',
                    'movement': 'stable',
                    'confidence': 0.5,
                    'tags': ['📊 Insufficient History'],
                    'historical_count': len(under_odds_history)
                }
            
            current_under = current_odds.get('under_odds')
            if not current_under:
                return {
                    'trend': 'neutral',
                    'movement': 'stable',
                    'confidence': 0.5,
                    'tags': ['❌ No Current Odds'],
                    'historical_count': len(under_odds_history)
                }
            
            # Calculate trend
            avg_historical = sum(under_odds_history) / len(under_odds_history)
            odds_change = current_under - avg_historical
            
            # Determine trend and movement
            if odds_change < -20:  # Odds getting worse (more negative)
                trend = 'over_hitting'
                movement = 'odds_falling'
                tags = ['📈 Trend Hitter', '⬇️ Odds Falling']
            elif odds_change > 20:  # Odds getting better (less negative)
                trend = 'under_hitting'
                movement = 'odds_rising'
                tags = ['🧊 Cold Prop', '⬆️ Odds Rising']
            else:
                trend = 'neutral'
                movement = 'stable'
                tags = ['📊 Stable Odds']
            
            # Calculate confidence based on trend strength
            trend_strength = abs(odds_change) / 100
            confidence = min(0.9, 0.5 + trend_strength)
            
            # Add confidence-based tags
            if confidence > 0.7:
                tags.append('🎯 High Confidence')
            elif confidence < 0.3:
                tags.append('⚠️ Low Confidence')
            
            return {
                'trend': trend,
                'movement': movement,
                'confidence': confidence,
                'tags': tags,
                'historical_count': len(under_odds_history),
                'odds_change': odds_change,
                'current_under': current_under,
                'avg_historical': avg_historical
            }
            
        except Exception as e:
            logger.error(f"Error tracking odds trend: {e}")
            return {
                'trend': 'neutral',
                'movement': 'stable',
                'confidence': 0.5,
                'tags': ['❌ Error in Analysis'],
                'historical_count': 0
            }
    
    def detect_book_traps(self, odds_data: Dict, trend_analysis: Dict) -> Dict:
        """
        Detect potential book traps and sharp odds setups.
        
        Args:
            odds_data: Current odds data
            trend_analysis: Trend analysis from track_odds_trend
            
        Returns:
            Trap detection results
        """
        try:
            over_odds = odds_data.get('over_odds')
            under_odds = odds_data.get('under_odds')
            
            if not over_odds or not under_odds:
                return {
                    'is_trap': False,
                    'reason': 'insufficient_odds_data',
                    'tags': []
                }
            
            is_trap = False
            reasons = []
            tags = []
            
            # Check for sharp juice imbalance
            juice_imbalance = abs(over_odds) - abs(under_odds)
            if juice_imbalance > 30:
                is_trap = True
                reasons.append('sharp_juice_imbalance')
                tags.append('🧨 Sharp Juice')
            
            # Check for no movement despite trend
            if trend_analysis['movement'] == 'stable' and trend_analysis['trend'] != 'neutral':
                is_trap = True
                reasons.append('no_movement_despite_trend')
                tags.append('🚫 No Movement')
            
            # Check for extreme odds
            if over_odds > 150:
                is_trap = True
                reasons.append('extreme_over_odds')
                tags.append('💀 Extreme Over')
            
            if under_odds < -400:
                is_trap = True
                reasons.append('extreme_under_odds')
                tags.append('👺 Extreme Under')
            
            # Check for suspicious line movement
            if trend_analysis.get('odds_change', 0) > 50:
                is_trap = True
                reasons.append('suspicious_movement')
                tags.append('⚠️ Suspicious Move')
            
            return {
                'is_trap': is_trap,
                'reason': ' | '.join(reasons) if reasons else 'clean_line',
                'tags': tags,
                'juice_imbalance': juice_imbalance
            }
            
        except Exception as e:
            logger.error(f"Error detecting book traps: {e}")
            return {
                'is_trap': False,
                'reason': 'error_in_analysis',
                'tags': ['❌ Analysis Error']
            }
    
    def score_market_stability(self, player: str, stat_type: str, sport: str) -> Dict:
        """
        Score market stability for a prop type based on historical volatility.
        
        Args:
            player: Player name
            stat_type: Stat type
            sport: Sport
            
        Returns:
            Market stability score and analysis
        """
        try:
            historical_odds = self._load_historical_odds(player, stat_type, sport)
            
            if len(historical_odds) < 5:
                return {
                    'stability': 'unknown',
                    'score': 0.5,
                    'volatility': 0,
                    'tags': ['📊 Insufficient Data']
                }
            
            # Calculate volatility of under odds
            under_odds = [odds['under_odds'] for odds in historical_odds if odds.get('under_odds')]
            
            if len(under_odds) < 3:
                return {
                    'stability': 'unknown',
                    'score': 0.5,
                    'volatility': 0,
                    'tags': ['📊 Insufficient Odds Data']
                }
            
            # Calculate variance and standard deviation
            variance = np.var(under_odds)
            std_dev = np.std(under_odds)
            
            # Determine stability
            if variance < 100:  # Low variance = stable
                stability = 'stable'
                score = 0.8
                tags = ['📊 Stable Market']
            elif variance < 500:  # Medium variance = moderate
                stability = 'moderate'
                score = 0.6
                tags = ['⚠️ Moderate Volatility']
            else:  # High variance = volatile
                stability = 'volatile'
                score = 0.3
                tags = ['🚫 Volatile Market']
            
            return {
                'stability': stability,
                'score': score,
                'volatility': variance,
                'std_dev': std_dev,
                'tags': tags,
                'historical_count': len(under_odds)
            }
            
        except Exception as e:
            logger.error(f"Error scoring market stability: {e}")
            return {
                'stability': 'unknown',
                'score': 0.5,
                'volatility': 0,
                'tags': ['❌ Analysis Error']
            }
    
    def log_closing_line_value(self, player: str, stat_type: str, sport: str,
                              posted_odds: Dict, closing_odds: Dict) -> Dict:
        """
        Log closing line value (CLV) to track Ghost's edge.
        
        Args:
            player: Player name
            stat_type: Stat type
            sport: Sport
            posted_odds: Odds when Ghost posted the pick
            closing_odds: Odds at game time
            
        Returns:
            CLV analysis
        """
        try:
            posted_under = posted_odds.get('under_odds')
            closing_under = closing_odds.get('under_odds')
            
            if not posted_under or not closing_under:
                return {
                    'clv': 0,
                    'edge': 'none',
                    'tags': ['❌ Missing Odds Data']
                }
            
            # Calculate CLV (positive = Ghost beat the close)
            clv = posted_under - closing_under
            
            if clv > 20:  # Ghost got better odds
                edge = 'positive'
                tags = ['💰 CLV Winner', '✅ Beat the Close']
            elif clv < -20:  # Ghost got worse odds
                edge = 'negative'
                tags = ['📉 CLV Loser', '❌ Worse than Close']
            else:
                edge = 'neutral'
                tags = ['📊 Neutral CLV']
            
            # Store CLV data
            self._store_clv_data(player, stat_type, sport, {
                'posted_odds': posted_odds,
                'closing_odds': closing_odds,
                'clv': clv,
                'edge': edge,
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'clv': clv,
                'edge': edge,
                'tags': tags,
                'posted_under': posted_under,
                'closing_under': closing_under
            }
            
        except Exception as e:
            logger.error(f"Error logging CLV: {e}")
            return {
                'clv': 0,
                'edge': 'error',
                'tags': ['❌ CLV Error']
            }
    
    def build_prop_meta_memory(self, player: str, stat_type: str, sport: str) -> Dict:
        """
        Build meta memory for prop types based on historical performance.
        
        Args:
            player: Player name
            stat_type: Stat type
            sport: Sport
            
        Returns:
            Meta memory analysis
        """
        try:
            # Load all historical data for this player/stat
            historical_data = self._load_historical_odds(player, stat_type, sport)
            
            if len(historical_data) < 10:
                return {
                    'meta_score': 0.5,
                    'hit_rate': 0.5,
                    'tags': ['📊 Insufficient Meta Data']
                }
            
            # Analyze performance by odds tier
            odds_tiers = {}
            for data in historical_data:
                over_odds = data.get('over_odds', 0)
                under_odds = data.get('under_odds', 0)
                
                # Categorize by odds tier
                if over_odds >= 110:
                    tier = 'demon'
                elif over_odds <= -300:
                    tier = 'goblin'
                elif -150 <= over_odds <= -400:
                    tier = 'hot_hitter'
                else:
                    tier = 'neutral'
                
                if tier not in odds_tiers:
                    odds_tiers[tier] = {'count': 0, 'hits': 0}
                
                odds_tiers[tier]['count'] += 1
                # Note: We'd need result data to calculate actual hits
                # For now, we'll estimate based on trend analysis
            
            # Calculate meta score
            total_props = sum(tier['count'] for tier in odds_tiers.values())
            if total_props == 0:
                return {
                    'meta_score': 0.5,
                    'hit_rate': 0.5,
                    'tags': ['📊 No Props Found']
                }
            
            # Weight by tier performance (estimated)
            tier_weights = {
                'demon': 0.3,      # Demons hit ~30%
                'goblin': 0.8,     # Goblins hit ~80%
                'hot_hitter': 0.6, # Hot hitters hit ~60%
                'neutral': 0.5     # Neutral hit ~50%
            }
            
            weighted_score = 0
            for tier, data in odds_tiers.items():
                weight = tier_weights.get(tier, 0.5)
                weighted_score += (data['count'] / total_props) * weight
            
            # Generate tags based on meta analysis
            tags = []
            if weighted_score > 0.6:
                tags.append('🎯 Strong Meta Profile')
            elif weighted_score < 0.4:
                tags.append('⚠️ Weak Meta Profile')
            
            if odds_tiers.get('demon', {}).get('count', 0) > 5:
                tags.append('💀 Demon History')
            
            if odds_tiers.get('goblin', {}).get('count', 0) > 5:
                tags.append('👺 Goblin History')
            
            return {
                'meta_score': weighted_score,
                'hit_rate': weighted_score,  # Estimated
                'tags': tags,
                'odds_tiers': odds_tiers,
                'total_props': total_props
            }
            
        except Exception as e:
            logger.error(f"Error building prop meta memory: {e}")
            return {
                'meta_score': 0.5,
                'hit_rate': 0.5,
                'tags': ['❌ Meta Analysis Error']
            }
    
    def _load_historical_odds(self, player: str, stat_type: str, sport: str) -> List[Dict]:
        """Load historical odds data for a player/stat combination."""
        try:
            memory_file = self.memory_dir / sport / player / f"{stat_type}.json"
            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading historical odds: {e}")
            return []
    
    def _store_clv_data(self, player: str, stat_type: str, sport: str, clv_data: Dict):
        """Store CLV data for analysis."""
        try:
            clv_dir = self.memory_dir / "clv" / sport / player
            clv_dir.mkdir(parents=True, exist_ok=True)
            
            clv_file = clv_dir / f"{stat_type}_clv.json"
            
            # Load existing CLV data
            existing_data = []
            if clv_file.exists():
                with open(clv_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Add new CLV data
            existing_data.append(clv_data)
            
            # Keep only last 100 CLV records
            if len(existing_data) > 100:
                existing_data = existing_data[-100:]
            
            # Save updated data
            with open(clv_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error storing CLV data: {e}")
    
    def store_odds_snapshot(self, player: str, stat_type: str, sport: str, odds_snapshot: Dict):
        """Store a new odds snapshot for a player/stat/sport."""
        try:
            odds_dir = self.memory_dir / sport / player
            odds_dir.mkdir(parents=True, exist_ok=True)
            odds_file = odds_dir / f"{stat_type}.json"

            # Load existing odds data
            existing_data = []
            if odds_file.exists():
                with open(odds_file, 'r') as f:
                    existing_data = json.load(f)

            # Add new snapshot with timestamp
            odds_snapshot['timestamp'] = datetime.now().isoformat()
            existing_data.append(odds_snapshot)

            # Keep only last 100 snapshots
            if len(existing_data) > 100:
                existing_data = existing_data[-100:]

            # Save updated data
            with open(odds_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error storing odds snapshot: {e}") 