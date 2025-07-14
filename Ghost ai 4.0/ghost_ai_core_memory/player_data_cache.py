#!/usr/bin/env python3
"""
Player Data Cache System for Ghost AI
Checks if the AI already has data for a player before making API calls or data pulls.
This prevents wasting resources on duplicate data fetching.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import hashlib

logger = logging.getLogger(__name__)

class PlayerDataCache:
    """Manages player data cache to avoid duplicate API calls and data pulls."""
    
    def __init__(self):
        self.cache_dir = Path('ghost_ai_core_memory/player_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache files
        self.player_stats_cache = self.cache_dir / 'player_stats_cache.json'
        self.player_history_cache = self.cache_dir / 'player_history_cache.json'
        self.player_props_cache = self.cache_dir / 'player_props_cache.json'
        self.cache_metadata = self.cache_dir / 'cache_metadata.json'
        
        # Initialize cache
        self._initialize_cache()
        
        # Track recently checked players to avoid repeated file reads
        self._recent_checks: Set[str] = set()
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _initialize_cache(self):
        """Initialize cache files if they don't exist."""
        cache_files = [
            self.player_stats_cache,
            self.player_history_cache,
            self.player_props_cache,
            self.cache_metadata
        ]
        
        for cache_file in cache_files:
            if not cache_file.exists():
                if cache_file == self.cache_metadata:
                    initial_data = {
                        'last_updated': datetime.now().isoformat(),
                        'cache_hits': 0,
                        'cache_misses': 0,
                        'total_players': 0
                    }
                else:
                    initial_data = {}
                
                with open(cache_file, 'w') as f:
                    json.dump(initial_data, f, indent=2)
                
                logger.info(f"Initialized cache file: {cache_file.name}")
    
    def _get_player_key(self, player_name: str, sport: str = None, prop_type: str = None) -> str:
        """Generate a unique key for a player."""
        key_parts = [player_name.lower().strip()]
        if sport:
            key_parts.append(sport.lower())
        if prop_type:
            key_parts.append(prop_type.lower())
        
        return hashlib.md5('_'.join(key_parts).encode()).hexdigest()
    
    def has_player_stats(self, player_name: str, sport: str = None) -> bool:
        """
        Check if we already have stats data for a player.
        
        Args:
            player_name: Name of the player
            sport: Sport (optional, for sport-specific checks)
            
        Returns:
            True if we have recent stats data, False otherwise
        """
        try:
            player_key = self._get_player_key(player_name, sport)
            
            # Check recent checks first
            if player_key in self._recent_checks:
                self._cache_hits += 1
                return True
            
            # Load cache
            if not self.player_stats_cache.exists():
                return False
            
            with open(self.player_stats_cache, 'r') as f:
                cache_data = json.load(f)
            
            if player_key in cache_data:
                # Check if data is recent (within last 24 hours)
                last_updated = cache_data[player_key].get('last_updated')
                if last_updated:
                    try:
                        last_update = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update < timedelta(hours=24):
                            self._recent_checks.add(player_key)
                            self._cache_hits += 1
                            logger.debug(f"Cache HIT: Found recent stats for {player_name}")
                            return True
                    except ValueError:
                        pass
            
            self._cache_misses += 1
            logger.debug(f"Cache MISS: No recent stats for {player_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking player stats cache for {player_name}: {e}")
            return False
    
    def has_player_history(self, player_name: str, prop_type: str, sport: str = None) -> bool:
        """
        Check if we already have history data for a player and prop type.
        
        Args:
            player_name: Name of the player
            prop_type: Type of prop
            sport: Sport (optional)
            
        Returns:
            True if we have recent history data, False otherwise
        """
        try:
            player_key = self._get_player_key(player_name, sport, prop_type)
            
            # Check recent checks first
            if player_key in self._recent_checks:
                self._cache_hits += 1
                return True
            
            # Load cache
            if not self.player_history_cache.exists():
                return False
            
            with open(self.player_history_cache, 'r') as f:
                cache_data = json.load(f)
            
            if player_key in cache_data:
                # Check if data is recent (within last 7 days for history)
                last_updated = cache_data[player_key].get('last_updated')
                if last_updated:
                    try:
                        last_update = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update < timedelta(days=7):
                            self._recent_checks.add(player_key)
                            self._cache_hits += 1
                            logger.debug(f"Cache HIT: Found recent history for {player_name} {prop_type}")
                            return True
                    except ValueError:
                        pass
            
            self._cache_misses += 1
            logger.debug(f"Cache MISS: No recent history for {player_name} {prop_type}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking player history cache for {player_name}: {e}")
            return False
    
    def has_player_props(self, player_name: str, game_id: str = None) -> bool:
        """
        Check if we already have props data for a player.
        
        Args:
            player_name: Name of the player
            game_id: Game ID (optional, for game-specific checks)
            
        Returns:
            True if we have recent props data, False otherwise
        """
        try:
            player_key = self._get_player_key(player_name, game_id)
            
            # Check recent checks first
            if player_key in self._recent_checks:
                self._cache_hits += 1
                return True
            
            # Load cache
            if not self.player_props_cache.exists():
                return False
            
            with open(self.player_props_cache, 'r') as f:
                cache_data = json.load(f)
            
            if player_key in cache_data:
                # Check if data is recent (within last 2 hours for props)
                last_updated = cache_data[player_key].get('last_updated')
                if last_updated:
                    try:
                        last_update = datetime.fromisoformat(last_updated)
                        if datetime.now() - last_update < timedelta(hours=2):
                            self._recent_checks.add(player_key)
                            self._cache_hits += 1
                            logger.debug(f"Cache HIT: Found recent props for {player_name}")
                            return True
                    except ValueError:
                        pass
            
            self._cache_misses += 1
            logger.debug(f"Cache MISS: No recent props for {player_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error checking player props cache for {player_name}: {e}")
            return False
    
    def should_fetch_player_data(self, player_name: str, data_type: str, **kwargs) -> bool:
        """
        Determine if we should fetch player data based on cache status.
        
        Args:
            player_name: Name of the player
            data_type: Type of data ('stats', 'history', 'props')
            **kwargs: Additional parameters (sport, prop_type, game_id)
            
        Returns:
            True if we should fetch data, False if we have recent cached data
        """
        if data_type == 'stats':
            return not self.has_player_stats(player_name, kwargs.get('sport'))
        elif data_type == 'history':
            return not self.has_player_history(player_name, kwargs.get('prop_type'), kwargs.get('sport'))
        elif data_type == 'props':
            return not self.has_player_props(player_name, kwargs.get('game_id'))
        else:
            return True
    
    def cache_player_stats(self, player_name: str, stats_data: Dict, sport: str = None):
        """Cache player stats data."""
        try:
            player_key = self._get_player_key(player_name, sport)
            
            # Load existing cache
            if self.player_stats_cache.exists():
                with open(self.player_stats_cache, 'r') as f:
                    cache_data = json.load(f)
            else:
                cache_data = {}
            
            # Add/update cache entry
            cache_data[player_key] = {
                'player_name': player_name,
                'sport': sport,
                'data': stats_data,
                'last_updated': datetime.now().isoformat(),
                'cache_type': 'stats'
            }
            
            # Save cache
            with open(self.player_stats_cache, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            self._recent_checks.add(player_key)
            logger.debug(f"Cached stats for {player_name}")
            
        except Exception as e:
            logger.error(f"Error caching player stats for {player_name}: {e}")
    
    def cache_player_history(self, player_name: str, history_data: List[Dict], prop_type: str, sport: str = None):
        """Cache player history data."""
        try:
            player_key = self._get_player_key(player_name, sport, prop_type)
            
            # Load existing cache
            if self.player_history_cache.exists():
                with open(self.player_history_cache, 'r') as f:
                    cache_data = json.load(f)
            else:
                cache_data = {}
            
            # Add/update cache entry
            cache_data[player_key] = {
                'player_name': player_name,
                'prop_type': prop_type,
                'sport': sport,
                'data': history_data,
                'last_updated': datetime.now().isoformat(),
                'cache_type': 'history'
            }
            
            # Save cache
            with open(self.player_history_cache, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            self._recent_checks.add(player_key)
            logger.debug(f"Cached history for {player_name} {prop_type}")
            
        except Exception as e:
            logger.error(f"Error caching player history for {player_name}: {e}")
    
    def cache_player_props(self, player_name: str, props_data: Dict, game_id: str = None):
        """Cache player props data."""
        try:
            player_key = self._get_player_key(player_name, game_id)
            
            # Load existing cache
            if self.player_props_cache.exists():
                with open(self.player_props_cache, 'r') as f:
                    cache_data = json.load(f)
            else:
                cache_data = {}
            
            # Add/update cache entry
            cache_data[player_key] = {
                'player_name': player_name,
                'game_id': game_id,
                'data': props_data,
                'last_updated': datetime.now().isoformat(),
                'cache_type': 'props'
            }
            
            # Save cache
            with open(self.player_props_cache, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            self._recent_checks.add(player_key)
            logger.debug(f"Cached props for {player_name}")
            
        except Exception as e:
            logger.error(f"Error caching player props for {player_name}: {e}")
    
    def get_cached_stats(self, player_name: str, sport: str = None) -> Optional[Dict]:
        """Get cached stats for a player."""
        try:
            player_key = self._get_player_key(player_name, sport)
            
            if not self.player_stats_cache.exists():
                return None
            
            with open(self.player_stats_cache, 'r') as f:
                cache_data = json.load(f)
            
            if player_key in cache_data:
                return cache_data[player_key].get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached stats for {player_name}: {e}")
            return None
    
    def get_cached_history(self, player_name: str, prop_type: str, sport: str = None) -> Optional[List[Dict]]:
        """Get cached history for a player."""
        try:
            player_key = self._get_player_key(player_name, sport, prop_type)
            
            if not self.player_history_cache.exists():
                return None
            
            with open(self.player_history_cache, 'r') as f:
                cache_data = json.load(f)
            
            if player_key in cache_data:
                return cache_data[player_key].get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached history for {player_name}: {e}")
            return None
    
    def get_cached_props(self, player_name: str, game_id: str = None) -> Optional[Dict]:
        """Get cached props for a player."""
        try:
            player_key = self._get_player_key(player_name, game_id)
            
            if not self.player_props_cache.exists():
                return None
            
            with open(self.player_props_cache, 'r') as f:
                cache_data = json.load(f)
            
            if player_key in cache_data:
                return cache_data[player_key].get('data')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached props for {player_name}: {e}")
            return None
    
    def update_cache_metadata(self):
        """Update cache metadata with current statistics."""
        try:
            metadata = {
                'last_updated': datetime.now().isoformat(),
                'cache_hits': self._cache_hits,
                'cache_misses': self._cache_misses,
                'cache_hit_rate': self._cache_hits / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0,
                'total_players': len(self._recent_checks)
            }
            
            with open(self.cache_metadata, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error updating cache metadata: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if self.cache_metadata.exists():
                with open(self.cache_metadata, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'cache_hits': 0,
                    'cache_misses': 0,
                    'cache_hit_rate': 0.0,
                    'total_players': 0
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
    
    def clear_old_cache(self, days_old: int = 30):
        """Clear cache entries older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleared_count = 0
            
            cache_files = [
                self.player_stats_cache,
                self.player_history_cache,
                self.player_props_cache
            ]
            
            for cache_file in cache_files:
                if cache_file.exists():
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    # Remove old entries
                    old_keys = []
                    for key, entry in cache_data.items():
                        last_updated = entry.get('last_updated')
                        if last_updated:
                            try:
                                last_update = datetime.fromisoformat(last_updated)
                                if last_update < cutoff_date:
                                    old_keys.append(key)
                            except ValueError:
                                old_keys.append(key)
                    
                    # Remove old entries
                    for key in old_keys:
                        del cache_data[key]
                        cleared_count += 1
                    
                    # Save updated cache
                    with open(cache_file, 'w') as f:
                        json.dump(cache_data, f, indent=2)
            
            logger.info(f"Cleared {cleared_count} old cache entries")
            
        except Exception as e:
            logger.error(f"Error clearing old cache: {e}")

# Global cache instance
player_cache = PlayerDataCache() 