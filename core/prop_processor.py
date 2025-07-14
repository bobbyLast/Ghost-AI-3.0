"""
Prop Processor Module

Handles the organization and processing of prop data from various sources.
Includes functionality for testing and creating combo props.
"""
import json
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timedelta
import os
import sys
from typing import Dict, List, Any, Optional
import logging
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import the MLB players data
# try:
#     from config.mlb_teams import MLB_PLAYERS, get_team_abbreviation
# except ImportError:
MLB_PLAYERS = {}
def get_team_abbreviation(player_name: str) -> str:
    return "Unknown"

# Import system utilities
from system.logging_config import get_logger

# Set up logger
logger = get_logger("PropProcessor")

class PropProcessor:
    """Handles processing and organization of prop data."""
    
    def _load_player_teams(self) -> None:
        """Load player-team mappings from MLB_PLAYERS."""
        try:
            if 'MLB_PLAYERS' in globals() and MLB_PLAYERS:
                self.player_teams = {}
                for team, players in MLB_PLAYERS.items():
                    if isinstance(players, dict):
                        for player_name in players.keys():
                            self.player_teams[player_name.lower()] = team
                logger.info(f"Loaded {len(self.player_teams)} player-team mappings")
            else:
                logger.warning("MLB_PLAYERS not available, player-team mappings will be empty")
        except Exception as e:
            logger.error(f"Error loading player teams: {e}")
            self.player_teams = {}

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the PropProcessor with base directory and buffered writing."""
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.processed_files: Set[str] = set()
        self.last_processed_time: Dict[str, float] = {}
        self.processing_lock = asyncio.Lock()
        self.player_teams: Dict[str, str] = {}
        self._load_player_teams()
        
        # Buffered writing
        self.write_buffer = []
        self.buffer_size = 50  # Number of props to buffer before writing
        self.last_write_time = time.time()
        self.write_interval = 60  # Max seconds between writes
        
        # Track skipped props for logging
        self.skipped_props = {
            'odds_api_null': [],
            'confidence_too_low': [],
            'validation_failed': []
        }

    def tag_by_odds(self, odds: float) -> str:
        if odds <= -200:
            return "goblin"
        elif odds >= 200:
            return "demon"
        elif odds >= 100:
            return "risky"
        elif odds >= -125:
            return "neutral"
        else:
            return "safe"

    def set_cold_players(self, cold_players: set):
        self.cold_players = cold_players

    def evaluate_confidence(self, prop: dict) -> float:
        base = 0.5
        tag = prop.get("tag", "")
        prop_type = prop.get("prop_type", "").lower() or prop.get("stat_type", "").lower()
        player = prop.get("player_name") or prop.get("player")
        # Volatility nerf
        high_volatility = any(x in prop_type for x in ["hr", "home run", "walk", "sb", "steal", "combo"])
        if high_volatility and tag != "goblin":
            base -= 0.15
        # Tag logic
        if tag == "goblin":
            base += 0.25
        elif tag == "demon":
            base -= 0.2
        # Cold player nerf
        if hasattr(self, 'cold_players') and player and player.lower() in self.cold_players:
            base -= 0.2
        # Clamp
        return round(min(max(base, 0), 1), 2)

    def choose_side(self, odds_higher: Optional[float] = None, odds_lower: Optional[float] = None) -> str:
        if odds_higher is not None and odds_lower is not None:
            return "higher" if odds_higher < odds_lower else "lower"
        return "higher"  # Default

    def detect_platform_from_prop(self, prop: Dict[str, Any]) -> str:
        """
        Detect which platform a prop is from based on its characteristics.
        Returns: 'underdog' or 'fanduel'
        """
        if self._is_underdog_prop(prop):
            return 'underdog'
        else:
            return 'fanduel'

    def _is_underdog_prop(self, prop: Dict[str, Any]) -> bool:
        odds = prop.get('odds', 0)
        multiplier = prop.get('multiplier', 0)
        prop_type = prop.get('prop_type', '').lower()
        tag = prop.get('tag', '').lower()
        if multiplier > 0:
            return True
        if 1.5 <= abs(odds) <= 8.0 and odds > 0:
            return True
        if 'goblin' in prop_type or 'goblin' in tag:
            return False
        if 'demon' in prop_type or 'demon' in tag:
            return False
        ud_prop_types = ['fantasy_points', 'combo_props', 'efficiency', 'multiplier']
        if any(pt in prop_type for pt in ud_prop_types):
            return True
        return False

    def _is_prizepicks_prop(self, prop: Dict[str, Any]) -> bool:
        odds = prop.get('odds', 0)
        multiplier = prop.get('multiplier', 0)
        prop_type = prop.get('prop_type', '').lower()
        tag = prop.get('tag', '').lower()
        if multiplier > 0:
            return False
        if 'goblin' in prop_type or 'goblin' in tag:
            return True
        if 'demon' in prop_type or 'demon' in tag:
            return True
        if 2 <= abs(odds) <= 6:
            return True
        pp_prop_types = ['points', 'rebounds', 'assists', 'steals', 'blocks', 'turnovers']
        if any(pt in prop_type for pt in pp_prop_types):
            return True
        return False

    def process_prop_by_detected_platform(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        platform = self.detect_platform_from_prop(prop)
        prop['detected_platform'] = platform
        if platform == 'underdog':
            return self._process_underdog_prop(prop)
        else:
            return self._process_fanduel_prop(prop)

    def _process_underdog_prop(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        multiplier = prop.get('multiplier', 0)
        odds = prop.get('odds', 0)
        if multiplier == 0 and odds != 0:
            multiplier = self._convert_odds_to_multiplier(odds)
            prop['multiplier'] = multiplier
        if multiplier <= 1.5:
            prop['tag'] = 'safe'
            prop['confidence'] = self.evaluate_confidence(prop) + 0.2
        elif multiplier >= 5.0:
            prop['tag'] = 'risky'
            prop['confidence'] = self.evaluate_confidence(prop) - 0.3
        elif multiplier >= 3.0:
            prop['tag'] = 'moderate'
            prop['confidence'] = self.evaluate_confidence(prop) - 0.1
        else:
            prop['tag'] = 'neutral'
            prop['confidence'] = self.evaluate_confidence(prop)
        prop['confidence'] = self._adjust_confidence_for_multiplier(prop['confidence'], multiplier)
        prop['pick'] = self.choose_side()
        return prop

    def _convert_odds_to_multiplier(self, odds: float) -> float:
        if odds > 0:
            return (odds / 100) + 1
        else:
            return (100 / abs(odds)) + 1

    def _adjust_confidence_for_multiplier(self, base_confidence: float, multiplier: float) -> float:
        if multiplier <= 1.5:
            return base_confidence + 0.1
        elif multiplier >= 6.0:
            return base_confidence - 0.2
        elif multiplier >= 4.0:
            return base_confidence - 0.1
        else:
            return base_confidence

    def _convert_multiplier_to_implied_probability(self, multiplier: float) -> float:
        return 1.0 / multiplier

    def _process_fanduel_prop(self, prop: Dict[str, Any]) -> Dict[str, Any]:
        odds = prop.get('odds', 0)
        if odds <= -200:
            prop['tag'] = 'safe'
        elif odds >= 200:
            prop['tag'] = 'risky'
        else:
            prop['tag'] = 'neutral'
        prop['confidence'] = self.evaluate_confidence(prop)
        prop['pick'] = self.choose_side()
        return prop

    async def process_prop_file(
        self, 
        file_path: Path, 
        platform: str, 
        sport: str,
        min_confidence: float = 0.4
    ) -> Dict[str, Any]:
        """
        Process a single prop file with buffered writes and confidence filtering.
        
        Args:
            file_path: Path to the prop file
            platform: Platform name (e.g., 'prizepicks', 'underdog')
            sport: Sport name (e.g., 'nba', 'nfl')
            min_confidence: Minimum confidence score to process a prop
            
        Returns:
            Dictionary with processing results and stats
        """
        file_str = str(file_path.absolute())
        processed_count = 0
        skipped_count = 0
        
        # Log file processing start
        logger.info(f"Processing {platform.upper()} props from {file_path.name} for {sport.upper()}")
        
        # Skip if already processed
        if file_str in self.processed_files:
            logger.debug(f"Skipping already processed file: {file_path}")
            return {}
            
        try:
            async with self.processing_lock:
                # Read and parse the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        prop_data = json.load(f)
                    
                    # Convert single prop dict to list if needed
                    if isinstance(prop_data, dict):
                        prop_data = [prop_data]
                        logger.info(f"Converted single prop dict to list in {file_path}")
                    
                    if not isinstance(prop_data, list):
                        logger.warning(f"Invalid prop data format in {file_path}, got {type(prop_data)}")
                        return {'file': file_str, 'processed': 0, 'skipped': 0, 'error': 'invalid_format'}
                    
                    # Process props with buffered writes
                    for prop in prop_data:
                        try:
                            # Skip if OddsAPI returned null
                            if prop.get('odds') is None:
                                self._log_skipped_prop(prop, 'odds_api_null')
                                skipped_count += 1
                                continue
                            
                            processed_prop = self.process_prop_by_detected_platform(prop)
                            
                            # STEP 4: Only add to buffer if confidence >= min_confidence
                            if processed_prop['confidence'] < min_confidence:
                                self._log_skipped_prop(processed_prop, 'confidence_too_low')
                                skipped_count += 1
                                continue
                            
                            # Add to buffer
                            self.write_buffer.append(processed_prop)
                            processed_count += 1
                            
                            # Write buffer if it reaches the threshold
                            if len(self.write_buffer) >= self.buffer_size:
                                await self._flush_buffer()
                        
                        except Exception as e:
                            logger.error(f"Error processing prop {prop.get('id', 'unknown')}: {e}")
                            self._log_skipped_prop(prop, 'processing_error')
                            skipped_count += 1
                    
                    # Final buffer flush if needed
                    if self.write_buffer:
                        await self._flush_buffer()
                    
                                # Log skipped props summary
                    self._log_skipped_summary()
                    
                    # Clean up old processed files
                    self._cleanup_processed_files()
                    
                    # Mark file as processed
                    self.processed_files.add(file_str)
                    self.last_processed_time[file_str] = time.time()
                    
                    return {
                        'file': file_str,
                        'processed': processed_count,
                        'skipped': skipped_count,
                        'success': True
                    }
                    
                except Exception as e:
                    logger.error(f"Error reading {file_path}: {e}")
                    return {'file': file_str, 'error': str(e)}
                    
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}", exc_info=True)
            return {'file': file_str, 'error': 'unexpected_error', 'message': str(e)}

    def calc_fantasy_score(self, player_stats: dict, sport: str, platform: str = "prizepicks") -> float:
        """
        Calculate fantasy score for NBA/MLB/WNBA using accurate scoring systems.
        Args:
            player_stats: dict of stat values (e.g., {"points": 25, ...})
            sport: "nba", "mlb", or "wnba"
            platform: "prizepicks" or "underdog"
        Returns:
            float: fantasy score
        """
        sport = sport.lower()
        platform = platform.lower()
        
        if sport == "nba" or sport == "wnba":
            # Basketball scoring (same for both platforms)
            return (
                player_stats.get("points", 0) * 1 +
                player_stats.get("rebounds", 0) * 1.2 +
                player_stats.get("assists", 0) * 1.5 +
                player_stats.get("steals", 0) * 3 +
                player_stats.get("blocks", 0) * 3 +
                player_stats.get("turnovers", 0) * -1
            )
        elif sport == "mlb":
            if platform == "prizepicks":
                # PrizePicks MLB scoring
                return (
                    player_stats.get("singles", 0) * 3 +
                    player_stats.get("doubles", 0) * 5 +
                    player_stats.get("triples", 0) * 8 +
                    player_stats.get("home_runs", 0) * 10 +
                    player_stats.get("runs", 0) * 2 +
                    player_stats.get("rbi", 0) * 2 +
                    player_stats.get("walks", 0) * 2 +
                    player_stats.get("hit_by_pitch", 0) * 2 +
                    player_stats.get("stolen_bases", 0) * 5
                )
            else:  # underdog
                # Underdog MLB scoring
                return (
                    player_stats.get("singles", 0) * 3 +
                    player_stats.get("doubles", 0) * 6 +
                    player_stats.get("triples", 0) * 8 +
                    player_stats.get("home_runs", 0) * 10 +
                    player_stats.get("runs", 0) * 2 +
                    player_stats.get("rbi", 0) * 2 +
                    player_stats.get("walks", 0) * 3 +
                    player_stats.get("hit_by_pitch", 0) * 3 +
                    player_stats.get("stolen_bases", 0) * 4
                )
        return 0.0

    def calc_combo_props(self, player_stats: dict, combo_type: str, sport: str) -> float:
        """
        Calculate combo props (PRA, PA, RA, H+R+RBI, Hits+Walks, etc) for NBA/MLB/WNBA.
        Args:
            player_stats: dict of stat values
            combo_type: e.g., "PRA", "PA", "RA", "H+R+RBI", "Hits+Walks"
            sport: "nba", "mlb", or "wnba"
        Returns:
            float: combo value
        """
        # Ensure combo_type is a string before calling upper()
        if not isinstance(combo_type, str):
            logger.error(f"combo_type is not a string: {combo_type} ({type(combo_type)})")
            return 0.0
        ctype = combo_type.upper()
        if sport.lower() in ["nba", "wnba"]:
            if ctype == "PRA":
                return (
                    player_stats.get("points", 0) +
                    player_stats.get("rebounds", 0) +
                    player_stats.get("assists", 0)
                )
            elif ctype == "PA":
                return (
                    player_stats.get("points", 0) +
                    player_stats.get("assists", 0)
                )
            elif ctype == "RA":
                return (
                    player_stats.get("rebounds", 0) +
                    player_stats.get("assists", 0)
                )
            elif ctype == "PR":
                return (
                    player_stats.get("points", 0) +
                    player_stats.get("rebounds", 0)
                )
        elif sport.lower() == "mlb":
            if ctype in ("H+R+RBI", "HITS+RUNS+RBIS"):
                return (
                    player_stats.get("hits", 0) +
                    player_stats.get("runs", 0) +
                    player_stats.get("rbi", 0)
                )
            elif ctype in ("HITS+WALKS", "H+BB"):
                return (
                    player_stats.get("hits", 0) +
                    player_stats.get("walks", 0)
                )
        return 0.0

    def fantasy_delta(self, player_stats: dict, fantasy_line: float, sport: str, platform: str = 'prizepicks') -> float:
        """
        Calculate the difference between projected fantasy score and the prop line.
        Args:
            player_stats: dict of stat values
            fantasy_line: the prop line to compare against
            sport: 'nba', 'mlb', or 'wnba'
            platform: 'prizepicks' or 'underdog'
        Returns:
            float: projected fantasy score minus line
        """
        proj = self.calc_fantasy_score(player_stats, sport, platform)
        return proj - fantasy_line

    def _log_skipped_prop(self, prop, reason):
        pass

    async def _flush_buffer(self):
        pass

    def _log_skipped_summary(self):
        pass

    def _cleanup_processed_files(self):
        pass

class ComboPropTester:
    """Handles testing and creation of combo props."""
    
    def __init__(self):
        self.test_results = {
            'efficiency_combo_created': False,
            'should_use_combo': False,
            'fantasy_combo_identified': False,
            'prop_count': 0,
            'errors': []
        }
    
    def test_combo_creation(self, prop_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test creation of combo props from the given prop data.
        
        Args:
            prop_data: List of prop dictionaries
            
        Returns:
            Dict with test results including success status and combo details
        """
        self.test_results = {
            'efficiency_combo_created': False,
            'should_use_combo': False,
            'fantasy_combo_identified': False,
            'prop_count': len(prop_data),
            'errors': []
        }
        
        try:
            # Test efficiency combo
            efficiency_result = self.test_efficiency_combo(prop_data)
            self.test_results.update(efficiency_result)
            
            # Test fantasy combo
            fantasy_result = self.test_fantasy_combo(prop_data)
            self.test_results.update(fantasy_result)
            
        except Exception as e:
            self.test_results['errors'].append(f"Error in combo testing: {str(e)}")
            logger.error(f"Error in combo testing: {e}", exc_info=True)
        
        return self.test_results
    
    def test_efficiency_combo(self, prop_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test if we can create an efficiency combo from the props.
        
        Args:
            prop_data: List of prop dictionaries
            
        Returns:
            Dict with test results including success status and combo details
        """
        result = {
            'efficiency_combo_created': False,
            'efficiency_combo_details': None,
            'errors': []
        }
        
        try:
            # Look for points + assists + rebounds combo
            player_stats = {}
            
            for prop in prop_data:
                player = prop.get('player_name')
                if not player:
                    continue
                    
                if player not in player_stats:
                    player_stats[player] = {}
                
                prop_type = prop.get('prop_type', '').lower()
                if 'points' in prop_type:
                    player_stats[player]['points'] = prop
                elif 'assists' in prop_type:
                    player_stats[player]['assists'] = prop
                elif 'rebounds' in prop_type:
                    player_stats[player]['rebounds'] = prop
            
            # Check for players with all three stats
            for player, stats in player_stats.items():
                if all(k in stats for k in ['points', 'assists', 'rebounds']):
                    result['efficiency_combo_created'] = True
                    result['efficiency_combo_details'] = {
                        'player': player,
                        'points': stats['points'].get('line_value'),
                        'assists': stats['assists'].get('line_value'),
                        'rebounds': stats['rebounds'].get('line_value')
                    }
                    break
                    
        except Exception as e:
            error_msg = f"Error in efficiency combo test: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg, exc_info=True)
            
        return result
        
    def test_fantasy_combo(self, prop_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Test if we can identify fantasy score combos.
        
        Args:
            prop_data: List of prop dictionaries
            
        Returns:
            Dict with test results including success status and combo details
        """
        result = {
            'fantasy_combo_identified': False,
            'fantasy_combo_details': None,
            'errors': []
        }
        
        try:
            # Look for fantasy score props
            fantasy_props = [p for p in prop_data 
                          if 'fantasy' in p.get('prop_type', '').lower() 
                          or 'fpts' in p.get('prop_type', '').lower()]
            
            if fantasy_props:
                result['fantasy_combo_identified'] = True
                result['fantasy_combo_details'] = [
                    {
                        'player': p.get('player_name'),
                        'prop_type': p.get('prop_type'),
                        'line_value': p.get('line_value')
                    } 
                    for p in fantasy_props[:3]  # Return first 3 for brevity
                ]
                
        except Exception as e:
            error_msg = f"Error in fantasy combo test: {str(e)}"
            result['errors'].append(error_msg)
            logger.error(error_msg, exc_info=True)
            
        return result

if __name__ == "__main__":
    import sys
    import json
    from pathlib import Path

    # Simple test: load a WNBA props file and print detected platform for each prop
    if len(sys.argv) < 2:
        print("Usage: python prop_processor.py <wnba_props_file.json>")
        sys.exit(1)

    props_file = Path(sys.argv[1])
    if not props_file.exists():
        print(f"File not found: {props_file}")
        sys.exit(1)

    with open(props_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processor = PropProcessor()
    count = 0
    for bookmaker in data.get('bookmakers', []):
        for market in bookmaker.get('markets', []):
            for outcome in market.get('outcomes', []):
                # Build a prop dict similar to what process_prop_by_detected_platform expects
                prop = {
                    'player': outcome.get('description', outcome.get('name', '')),
                    'team': outcome.get('team', ''),
                    'stat_type': market.get('key', ''),
                    'prop_type': market.get('key', ''),
                    'line': outcome.get('point', None),
                    'odds': outcome.get('price', None),
                }
                detected = processor.detect_platform_from_prop(prop)
                print(f"Player: {prop['player']}, Stat: {prop['stat_type']}, Line: {prop['line']}, Odds: {prop['odds']} -> Platform: {detected}")
                count += 1
                if count >= 30:
                    break
            if count >= 30:
                break
        if count >= 30:
            break
