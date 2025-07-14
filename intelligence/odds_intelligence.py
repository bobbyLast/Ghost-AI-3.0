"""
Ghost AI Odds Intelligence System

This module provides odds-aware prop analysis and classification using OddsAPI.
It includes trend tracking, book trap detection, market stability scoring,
and prop classification (DEMON, GOBLIN, HOT HITTER).
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class OddsIntelligence:
    """Odds intelligence system for Ghost AI."""
    
    def __init__(self, ghost_ai_instance):
        self.ghost_ai = ghost_ai_instance
        self.odds_handler = None
        self.odds_tracker = None
        self.odds_memory = {}
        self.prop_meta_memory = {}
        # Ensure odds_memory directory exists
        odds_memory_dir = os.path.join(os.getcwd(), 'odds_memory')
        if not os.path.exists(odds_memory_dir):
            os.makedirs(odds_memory_dir)
    
    async def initialize(self):
        """Initialize the odds intelligence system."""
        try:
            # from core.api.oddsapi_handler import OddsAPIHandler
            # from core.utils.odds_tracker import OddsTracker
            
            self.odds_handler = OddsAPIHandler()
            self.odds_tracker = OddsTracker()
            
            logger.info("✅ Odds intelligence system initialized")
            
        except Exception as e:
            logger.error(f"❌ Error initializing odds intelligence: {e}")
    
    async def pull_fanduel_props(self, sport: str) -> List[Dict]:
        """
        Pull all FanDuel props for the current day.
        
        Args:
            sport: Sport key (e.g., 'baseball_mlb', 'basketball_wnba')
            
        Returns:
            List of FanDuel props with player, prop type, line, odds, game info
        """
        try:
            if not self.odds_handler:
                await self.initialize()
            
            # Get all games for today
            games = await self.odds_handler.get_games(sport)
            
            all_props = []
            for game in games:
                game_id = game.get('id')
                if game_id:
                    # Get player props for this game from FanDuel
                    props = await self.odds_handler.get_player_props(game_id, "fanduel")
                    
                    # Add game context to each prop
                    for prop in props:
                        prop.update({
                            'game_id': game_id,
                            'home_team': game.get('home_team'),
                            'away_team': game.get('away_team'),
                            'commence_time': game.get('commence_time'),
                            'sport': sport
                        })
                    
                    all_props.extend(props)
            
            logger.info(f"✅ Pulled {len(all_props)} FanDuel props for {sport}")
            return all_props
            
        except Exception as e:
            logger.error(f"❌ Error pulling FanDuel props: {e}")
            return []
    
    def track_odds_trend(self, player: str, stat_type: str, sport: str, current_odds: Dict) -> Dict:
        """
        Track odds trend for a player and stat type.
        
        Args:
            player: Player name
            stat_type: Stat type (points, rebounds, hits, etc.)
            sport: Sport (basketball_nba, baseball_mlb, etc.)
            current_odds: Current odds data
            
        Returns:
            Trend analysis with confidence and tags
        """
        try:
            if not self.odds_tracker:
                logger.warning("Odds tracker not initialized")
                return {'trend': 'neutral', 'confidence': 0.5, 'tags': ['⚠️ No Tracker']}
            
            return self.odds_tracker.track_odds_trend(player, stat_type, sport, current_odds)
            
        except Exception as e:
            logger.error(f"❌ Error tracking odds trend: {e}")
            return {'trend': 'neutral', 'confidence': 0.5, 'tags': ['❌ Error']}
    
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
            if not self.odds_tracker:
                logger.warning("Odds tracker not initialized")
                return {'is_trap': False, 'reason': 'no_tracker', 'tags': []}
            
            return self.odds_tracker.detect_book_traps(odds_data, trend_analysis)
            
        except Exception as e:
            logger.error(f"❌ Error detecting book traps: {e}")
            return {'is_trap': False, 'reason': 'error', 'tags': ['❌ Error']}
    
    def score_market_stability(self, player: str, stat_type: str, sport: str) -> Dict:
        """
        Score market stability for a prop type based on historical volatility.
        
        Args:
            player: Player name
            stat_type: Stat type
            sport: Sport
            
        Returns:
            Market stability score and recommendations
        """
        try:
            if not self.odds_tracker:
                logger.warning("Odds tracker not initialized")
                return {'stability': 'unknown', 'score': 0.5, 'tags': ['⚠️ No Tracker']}
            
            return self.odds_tracker.score_market_stability(player, stat_type, sport)
            
        except Exception as e:
            logger.error(f"❌ Error scoring market stability: {e}")
            return {'stability': 'unknown', 'score': 0.5, 'tags': ['❌ Error']}
    
    def log_closing_line_value(self, player: str, stat_type: str, sport: str, 
                              posted_odds: Dict, closing_odds: Dict) -> Dict:
        """
        Log closing line value (CLV) for a prop.
        
        Args:
            player: Player name
            stat_type: Stat type
            sport: Sport
            posted_odds: Odds when we posted the pick
            closing_odds: Odds at game time
            
        Returns:
            CLV analysis
        """
        try:
            if not self.odds_tracker:
                logger.warning("Odds tracker not initialized")
                return {'clv': 0, 'edge': 'none', 'tags': ['⚠️ No Tracker']}
            
            return self.odds_tracker.log_closing_line_value(player, stat_type, sport, posted_odds, closing_odds)
            
        except Exception as e:
            logger.error(f"❌ Error logging CLV: {e}")
            return {'clv': 0, 'edge': 'none', 'tags': ['❌ Error']}
    
    def build_prop_meta_memory(self, player: str, stat_type: str, sport: str) -> Dict:
        """
        Build meta memory for a player/stat combination.
        
        Args:
            player: Player name
            stat_type: Stat type
            sport: Sport
            
        Returns:
            Meta memory data
        """
        try:
            if not self.odds_tracker:
                logger.warning("Odds tracker not initialized")
                return {'meta_memory': {}, 'tags': ['⚠️ No Tracker']}
            
            return self.odds_tracker.build_prop_meta_memory(player, stat_type, sport)
            
        except Exception as e:
            logger.error(f"❌ Error building meta memory: {e}")
            return {'meta_memory': {}, 'tags': ['❌ Error']}
    
    def classify_prop_by_odds(self, odds_data: Dict, trend_analysis: Dict, 
                            market_stability: Dict, sport: str = '') -> Dict:
        """
        Classify a prop as DEMON, GOBLIN, or HOT HITTER based on odds and analysis.
        
        Args:
            odds_data: Current odds data
            trend_analysis: Trend analysis
            market_stability: Market stability analysis
            sport: Sport (for MLB-specific classifications)
            
        Returns:
            Prop classification with tags and rationale
        """
        try:
            over_odds = odds_data.get('over_odds', 0)
            under_odds = odds_data.get('under_odds', 0)
            
            classification = {
                'type': 'unknown',
                'tags': [],
                'rationale': '',
                'confidence': 0.5
            }
            
            # DEMON: Odds ≥ +110, trend/CLV edge
            if over_odds >= 110:
                if trend_analysis.get('trend') == 'over_hitting' or trend_analysis.get('confidence', 0) > 0.6:
                    classification.update({
                        'type': 'DEMON',
                        'tags': ['💀 DEMON', '📈 High Risk', '🎯 Trend Edge'],
                        'rationale': f'High odds ({over_odds}) with trend edge',
                        'confidence': trend_analysis.get('confidence', 0.5)
                    })
            
            # GOBLIN: Odds ≤ -300, stable/rising trend
            elif under_odds <= -300:
                if market_stability.get('stability') == 'stable' or trend_analysis.get('movement') == 'odds_rising':
                    classification.update({
                        'type': 'GOBLIN',
                        'tags': ['👺 GOBLIN', '🛡️ Safe Leg', '📊 Stable'],
                        'rationale': f'Low odds ({under_odds}) with stable trend',
                        'confidence': market_stability.get('score', 0.5)
                    })
            
            # HOT HITTER (MLB only): Odds between -150 and -400, over trend, market stability
            elif sport == 'baseball_mlb' and -400 <= over_odds <= -150:
                if (trend_analysis.get('trend') == 'over_hitting' and 
                    market_stability.get('stability') == 'stable'):
                    classification.update({
                        'type': 'HOT_HITTER',
                        'tags': ['🔥 HOT HITTER', '⚾ MLB Only', '📈 Over Trend'],
                        'rationale': f'MLB hitting prop ({over_odds}) with over trend and stability',
                        'confidence': min(trend_analysis.get('confidence', 0.5), market_stability.get('score', 0.5))
                    })
            
            # Default classification
            if classification['type'] == 'unknown':
                classification.update({
                    'type': 'REGULAR',
                    'tags': ['📊 Regular Prop'],
                    'rationale': 'Standard prop classification',
                    'confidence': 0.5
                })
            
            return classification
            
        except Exception as e:
            logger.error(f"❌ Error classifying prop: {e}")
            return {
                'type': 'ERROR',
                'tags': ['❌ Classification Error'],
                'rationale': 'Error in classification',
                'confidence': 0.0
            }
    
    async def process_prop_with_odds_intelligence(self, prop: Dict) -> Dict:
        """
        Process a prop with full odds intelligence analysis.
        
        Args:
            prop: Raw prop data
            
        Returns:
            Enhanced prop with odds analysis, classification, and tags
        """
        try:
            player = prop.get('player', '')
            stat_type = prop.get('stat_type', '')
            sport = prop.get('sport', '')
            
            # Extract odds data
            odds_data = {
                'over_odds': prop.get('over_odds'),
                'under_odds': prop.get('under_odds'),
                'line': prop.get('line')
            }
            
            # Track odds trend
            trend_analysis = self.track_odds_trend(player, stat_type, sport, odds_data)
            
            # Detect book traps
            trap_analysis = self.detect_book_traps(odds_data, trend_analysis)
            
            # Score market stability
            market_stability = self.score_market_stability(player, stat_type, sport)
            
            # Classify prop
            classification = self.classify_prop_by_odds(odds_data, trend_analysis, market_stability, sport)
            
            # Build meta memory
            meta_memory = self.build_prop_meta_memory(player, stat_type, sport)
            
            # Combine all analysis
            enhanced_prop = prop.copy()
            enhanced_prop.update({
                'odds_analysis': {
                    'trend': trend_analysis,
                    'traps': trap_analysis,
                    'stability': market_stability,
                    'classification': classification,
                    'meta_memory': meta_memory
                },
                'tags': (
                    trend_analysis.get('tags', []) +
                    trap_analysis.get('tags', []) +
                    market_stability.get('tags', []) +
                    classification.get('tags', [])
                ),
                'confidence': classification.get('confidence', 0.5),
                'prop_type': classification.get('type', 'REGULAR')
            })
            
            # Store in odds memory
            key = f"{player}_{stat_type}_{sport}"
            self.odds_memory[key] = enhanced_prop
            
            logger.info(f"✅ Processed {player} {stat_type} as {classification['type']} (confidence: {classification['confidence']:.2f})")
            
            return enhanced_prop
            
        except Exception as e:
            logger.error(f"❌ Error processing prop with odds intelligence: {e}")
            return prop 
    
    async def pull_and_store_odds_snapshots(self, props: List[Dict]):
        """
        Pull and store odds snapshots for all props in the provided list.
        Args:
            props: List of prop dicts with at least player, stat_type, sport, and game_id
        """
        if not self.odds_handler or not self.odds_tracker:
            logger.warning("Odds handler or tracker not initialized")
            return
        for prop in props:
            try:
                player = prop.get('player')
                stat_type = prop.get('stat_type')
                sport = prop.get('sport')
                game_id = prop.get('game_id')
                if not all([player, stat_type, sport, game_id]):
                    continue
                # Fetch current odds for this player/prop
                odds_list = await self.odds_handler.get_player_props(game_id)
                # Find matching odds for this player/stat
                for odds in odds_list:
                    if (odds.get('player') == player and odds.get('stat_type') == stat_type):
                        self.odds_tracker.store_odds_snapshot(player, stat_type, sport, odds)
                        break
            except Exception as e:
                logger.error(f"Error pulling/storing odds snapshot for {prop}: {e}") 