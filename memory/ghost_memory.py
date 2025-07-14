"""
Ghost Memory System

Handles persistent storage and retrieval of pick data, player statistics,
and other information to enable learning and pattern recognition.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import hashlib
import logging

# Import centralized logging
from system.logging_config import get_logger

# Set up logger
logger = get_logger('GhostMemory')

class PickStatus(str, Enum):
    PENDING = "pending"
    HIT = "hit"
    MISS = "miss"
    PUSH = "push"
    NO_ACTION = "no_action"

class PickImpact(str, Enum):
    NORMAL = "normal"
    RED_FLAGGED = "red_flagged"
    TIGHT_MISS = "tight_miss"
    CONSISTENT = "consistent"
    STREAK_BREAKER = "streak_breaker"

@dataclass
class PickRecord:
    """Data class representing a single pick record."""
    id: str
    player_name: str
    team: str
    sport: str
    prop_type: str
    line: float
    actual: Optional[float] = None
    status: PickStatus = PickStatus.PENDING
    impact: PickImpact = PickImpact.NORMAL
    confidence: float = 0.0
    ticket_id: Optional[str] = None
    is_hot_streak: bool = False
    is_cold_streak: bool = False
    red_flags: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['status'] = self.status.value
        data['impact'] = self.impact.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PickRecord':
        """Create from dictionary with proper enum handling."""
        if isinstance(data.get('status'), str):
            data['status'] = PickStatus(data['status'])
        if isinstance(data.get('impact'), str):
            data['impact'] = PickImpact(data['impact'])
        return cls(**data)

class GhostMemory:
    """
    Handles persistent storage and retrieval of pick data, player statistics,
    and other information to enable learning and pattern recognition.
    """
    
    def __init__(self, base_dir: str = "ghost_ai_core_memory"):
        """Initialize the memory system with base directory."""
        self.base_dir = Path(base_dir)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.base_dir.mkdir(exist_ok=True)
        (self.base_dir / "tracked_picks").mkdir(exist_ok=True)
        (self.base_dir / "streaks").mkdir(exist_ok=True)
        (self.base_dir / "player_tags").mkdir(exist_ok=True)
        (self.base_dir / "prop_outcomes").mkdir(exist_ok=True)
    
    def _get_picks_file_path(self, date: datetime = None) -> Path:
        """Get the file path for storing picks for a specific date."""
        if date is None:
            date = datetime.utcnow()
        return self.base_dir / "tracked_picks" / f"{date.strftime('%Y-%m-%d')}.json"
    
    def _generate_id(self, *args) -> str:
        """Generate a unique ID based on input arguments."""
        input_str = "".join(str(arg) for arg in args) + str(datetime.utcnow().timestamp())
        return hashlib.md5(input_str.encode()).hexdigest()
    
    def record_pick(self, pick_data: Dict[str, Any]) -> str:
        """
        Record a new pick in the memory system.
        
        Args:
            pick_data: Dictionary containing pick information
            
        Returns:
            str: The generated pick ID
        """
        # Generate a unique ID for this pick
        pick_id = self._generate_id(
            pick_data.get('player_name'),
            pick_data.get('prop_type'),
            pick_data.get('line'),
            datetime.utcnow().timestamp()
        )
        
        # Create pick record
        pick = PickRecord(
            id=pick_id,
            player_name=pick_data['player_name'],
            team=pick_data.get('team', ''),
            sport=pick_data.get('sport', 'mlb'),
            prop_type=pick_data['prop_type'],
            line=float(pick_data['line']),
            confidence=float(pick_data.get('confidence', 0.0)),
            ticket_id=pick_data.get('ticket_id'),
            red_flags=pick_data.get('red_flags', []),
            is_hot_streak=pick_data.get('is_hot_streak', False),
            is_cold_streak=pick_data.get('is_cold_streak', False)
        )
        
        # Save to daily file
        file_path = self._get_picks_file_path()
        picks = self._load_picks_file(file_path)
        picks[pick_id] = pick.to_dict()
        self._save_picks_file(file_path, picks)
        
        # Update player stats
        self._update_player_stats(pick)
        
        return pick_id
    
    def update_pick_result(self, pick_id: str, actual: float) -> bool:
        """
        Update a pick with its actual result.
        
        Args:
            pick_id: The ID of the pick to update
            actual: The actual result value
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Find the pick in the last 7 days of files
        for days_ago in range(7):
            date = datetime.utcnow() - timedelta(days=days_ago)
            file_path = self._get_picks_file_path(date)
            
            if not file_path.exists():
                continue
                
            picks = self._load_picks_file(file_path)
            
            if pick_id in picks:
                # Update pick status
                pick_data = picks[pick_id]
                pick = PickRecord.from_dict(pick_data)
                pick.actual = float(actual)
                
                # Determine status
                if actual > pick.line:
                    pick.status = PickStatus.HIT
                elif actual < pick.line:
                    pick.status = PickStatus.MISS
                else:
                    pick.status = PickStatus.PUSH
                
                # Update impact based on result
                if abs(actual - pick.line) <= 0.5:  # Consider it a tight miss/hit
                    pick.impact = PickImpact.TIGHT_MISS
                
                pick.updated_at = datetime.utcnow().isoformat()
                picks[pick_id] = pick.to_dict()
                
                # Save updated picks
                self._save_picks_file(file_path, picks)
                
                # Update player stats and streaks
                self._update_player_stats(pick)
                self._update_streaks(pick)
                
                return True
        
        logger.warning(f"Pick {pick_id} not found in recent records")
        return False
    
    def _load_picks_file(self, file_path: Path) -> Dict[str, Any]:
        """Load picks from a JSON file."""
        if not file_path.exists():
            return {}
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading picks file {file_path}: {e}")
            return {}
    
    def _save_picks_file(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Save picks to a JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving picks file {file_path}: {e}")
    
    def _update_player_stats(self, pick: PickRecord) -> None:
        """Update player statistics based on pick result."""
        player_file = self.base_dir / "player_tags" / f"{pick.player_name.replace(' ', '_')}.json"
        
        try:
            if player_file.exists():
                with open(player_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
            else:
                stats = {
                    'player_name': pick.player_name,
                    'team': pick.team,
                    'sport': pick.sport,
                    'total_picks': 0,
                    'hits': 0,
                    'misses': 0,
                    'pushes': 0,
                    'current_streak': 0,
                    'best_streak': 0,
                    'prop_types': {},
                    'last_updated': datetime.utcnow().isoformat()
                }
            
            # Update basic stats
            stats['total_picks'] = stats.get('total_picks', 0) + 1
            
            if pick.status == PickStatus.HIT:
                stats['hits'] = stats.get('hits', 0) + 1
                stats['current_streak'] = stats.get('current_streak', 0) + 1
                if stats['current_streak'] > stats.get('best_streak', 0):
                    stats['best_streak'] = stats['current_streak']
            elif pick.status == PickStatus.MISS:
                stats['misses'] = stats.get('misses', 0) + 1
                stats['current_streak'] = 0
            elif pick.status == PickStatus.PUSH:
                stats['pushes'] = stats.get('pushes', 0) + 1
            
            # Update prop type stats
            prop_type = pick.prop_type
            if prop_type not in stats['prop_types']:
                stats['prop_types'][prop_type] = {'hits': 0, 'attempts': 0}
            
            stats['prop_types'][prop_type]['attempts'] += 1
            if pick.status == PickStatus.HIT:
                stats['prop_types'][prop_type]['hits'] += 1
            
            # Update last updated timestamp
            stats['last_updated'] = datetime.utcnow().isoformat()
            
            # Save updated stats
            with open(player_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error updating player stats for {pick.player_name}: {e}")
    
    def _update_streaks(self, pick: PickRecord) -> None:
        """Update streak information for players and prop types."""
        # This would be implemented to track various streaks
        # (hot streaks, cold streaks, etc.)
        pass
    
    def get_player_streak(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get current streak status for a player."""
        streak_file = self.base_dir / "streaks" / f"{player_name.replace(' ', '_')}.json"
        
        if not streak_file.exists():
            return None
        
        try:
            with open(streak_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading streak data for {player_name}: {e}")
            return None
    
    def update_player_streak(self, player_name: str, streak_data: Dict[str, Any]) -> bool:
        """Update streak status for a player."""
        try:
            streak_file = self.base_dir / "streaks" / f"{player_name.replace(' ', '_')}.json"
            
            # Ensure streaks directory exists
            streak_file.parent.mkdir(exist_ok=True)
            
            # Save streak data
            with open(streak_file, 'w', encoding='utf-8') as f:
                json.dump(streak_data, f, indent=2, default=str)
            
            logger.info(f"Updated streak for {player_name}: {streak_data}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating streak for {player_name}: {e}")
            return False
    
    def get_all_active_streaks(self) -> Dict[str, Dict[str, Any]]:
        """Get all active streaks."""
        active_streaks = {}
        streaks_dir = self.base_dir / "streaks"
        
        if not streaks_dir.exists():
            return active_streaks
        
        try:
            for streak_file in streaks_dir.glob("*.json"):
                with open(streak_file, 'r', encoding='utf-8') as f:
                    streak_data = json.load(f)
                    
                if streak_data.get('is_active', False):
                    player_name = streak_data.get('player_name', '')
                    if player_name:
                        active_streaks[player_name] = streak_data
                        
        except Exception as e:
            logger.error(f"Error loading active streaks: {e}")
        
        return active_streaks
    
    def get_player_stats(self, player_name: str) -> Dict[str, Any]:
        """Get statistics for a specific player."""
        player_file = self.base_dir / "player_tags" / f"{player_name.replace(' ', '_')}.json"
        
        if not player_file.exists():
            return {
                'player_name': player_name,
                'total_picks': 0,
                'hits': 0,
                'misses': 0,
                'pushes': 0,
                'hit_rate': 0.0,
                'prop_types': {}
            }
        
        try:
            with open(player_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                
            # Calculate hit rate
            total = stats.get('hits', 0) + stats.get('misses', 0) + stats.get('pushes', 0)
            if total > 0:
                stats['hit_rate'] = stats.get('hits', 0) / total
            else:
                stats['hit_rate'] = 0.0
                
            return stats
            
        except Exception as e:
            logger.error(f"Error loading player stats for {player_name}: {e}")
            return {
                'player_name': player_name,
                'error': str(e)
            }
    
    def get_prop_type_stats(self, prop_type: str) -> Dict[str, Any]:
        """Get statistics for a specific prop type."""
        stats_file = self.base_dir / "prop_outcomes" / f"{prop_type}_stats.json"
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading prop type stats: {e}")
        
        return {
            'total': 0,
            'hits': 0,
            'misses': 0,
            'success_rate': 0.0,
            'avg_confidence': 0.0
        }
    
    def get_active_props(self) -> Dict[str, Any]:
        """
        Get all active (pending) props from memory.
        
        Returns:
            Dict[str, Any]: Dictionary of active props with prop_id as key
        """
        active_props = {}
        
        # Check the last 7 days for pending props
        for days_ago in range(7):
            date = datetime.utcnow() - timedelta(days=days_ago)
            file_path = self._get_picks_file_path(date)
            
            if not file_path.exists():
                continue
                
            try:
                picks = self._load_picks_file(file_path)
                
                # Filter for pending props
                for pick_id, pick_data in picks.items():
                    pick = PickRecord.from_dict(pick_data)
                    if pick.status == PickStatus.PENDING:
                        # Convert to the format expected by the calling code
                        active_props[pick_id] = {
                            'player': pick.player_name,
                            'sport': pick.sport,
                            'stat_type': pick.prop_type,
                            'line': pick.line,
                            'over_under': 'over',  # Default, could be enhanced to store this
                            'confidence': pick.confidence,
                            'created_at': pick.created_at
                        }
                        
            except Exception as e:
                logger.error(f"Error loading picks from {file_path}: {e}")
                continue
        
        logger.info(f"Found {len(active_props)} active props")
        return active_props
    
    def update_prop_outcome(self, prop_id: str, hit: bool) -> bool:
        """
        Update a prop outcome in the memory system.
        
        Args:
            prop_id: The ID of the prop to update
            hit: Whether the prop hit (True) or missed (False)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Find the prop in the last 7 days of files
        for days_ago in range(7):
            date = datetime.utcnow() - timedelta(days=days_ago)
            file_path = self._get_picks_file_path(date)
            
            if not file_path.exists():
                continue
                
            picks = self._load_picks_file(file_path)
            
            if prop_id in picks:
                # Update pick status
                pick_data = picks[prop_id]
                pick = PickRecord.from_dict(pick_data)
                
                if hit:
                    pick.status = PickStatus.HIT
                else:
                    pick.status = PickStatus.MISS
                
                pick.updated_at = datetime.utcnow().isoformat()
                picks[prop_id] = pick.to_dict()
                
                # Save updated picks
                self._save_picks_file(file_path, picks)
                
                # Update player stats and streaks
                self._update_player_stats(pick)
                self._update_streaks(pick)
                
                logger.info(f"Updated prop {prop_id} outcome: {'HIT' if hit else 'MISS'}")
                return True
        
        logger.warning(f"Prop {prop_id} not found in recent records")
        return False
    
    def get_daily_picks(self, date: str) -> Dict[str, Any]:
        """Get daily picks for a specific date."""
        daily_picks_file = self.base_dir / "daily_picks.json"
        
        if not daily_picks_file.exists():
            return {}
        
        try:
            with open(daily_picks_file, 'r', encoding='utf-8') as f:
                all_daily_picks = json.load(f)
                
            return all_daily_picks.get(date, {})
            
        except Exception as e:
            logger.error(f"Error loading daily picks for {date}: {e}")
            return {}
    
    def record_daily_pick(self, pick_type: str, pick_data: Dict[str, Any]) -> bool:
        """Record a daily pick (POTD, RPOTD, TOTD, RTOTD)."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            daily_picks_file = self.base_dir / "daily_picks.json"
            
            # Load existing daily picks
            if daily_picks_file.exists():
                with open(daily_picks_file, 'r', encoding='utf-8') as f:
                    all_daily_picks = json.load(f)
            else:
                all_daily_picks = {}
            
            # Initialize today's picks if not exists
            if today not in all_daily_picks:
                all_daily_picks[today] = {}
            
            # Record the pick
            all_daily_picks[today][pick_type] = {
                'pick_data': pick_data,
                'posted_at': datetime.now().isoformat()
            }
            
            # Save updated daily picks
            with open(daily_picks_file, 'w', encoding='utf-8') as f:
                json.dump(all_daily_picks, f, indent=2, default=str)
            
            logger.info(f"Recorded {pick_type} for {today}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording daily pick {pick_type}: {e}")
            return False
    
    def get_performance_summary(self, date: str) -> Dict[str, Any]:
        """Get performance summary for a specific date."""
        try:
            file_path = self.base_dir / "tracked_picks" / f"{date}.json"
            
            if not file_path.exists():
                return {
                    'total_picks': 0,
                    'hits': 0,
                    'misses': 0,
                    'pushes': 0,
                    'hit_rate': 0.0,
                    'total_profit': 0.0
                }
            
            picks = self._load_picks_file(file_path)
            
            total_picks = len(picks)
            hits = sum(1 for pick in picks.values() if pick.get('status') == 'hit')
            misses = sum(1 for pick in picks.values() if pick.get('status') == 'miss')
            pushes = sum(1 for pick in picks.values() if pick.get('status') == 'push')
            
            hit_rate = hits / total_picks if total_picks > 0 else 0.0
            
            return {
                'total_picks': total_picks,
                'hits': hits,
                'misses': misses,
                'pushes': pushes,
                'hit_rate': hit_rate,
                'total_profit': 0.0  # TODO: Calculate actual profit
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {
                'total_picks': 0,
                'hits': 0,
                'misses': 0,
                'pushes': 0,
                'hit_rate': 0.0,
                'total_profit': 0.0
            }
    
    async def get_player_history(self, player_name: str, stat_type: str, limit: int = 5) -> List[Dict]:
        """Get recent history for a player and stat type."""
        try:
            history = []
            
            # Look through recent pick files (last 30 days)
            for days_ago in range(30):
                date = datetime.utcnow() - timedelta(days=days_ago)
                file_path = self._get_picks_file_path(date)
                
                if not file_path.exists():
                    continue
                
                picks = self._load_picks_file(file_path)
                
                # Find picks for this player and stat type
                for pick_data in picks.values():
                    if (pick_data.get('player_name') == player_name and 
                        pick_data.get('prop_type') == stat_type):
                        
                        # Add to history if we haven't reached the limit
                        if len(history) < limit:
                            history.append({
                                'date': date.strftime('%Y-%m-%d'),
                                'line': pick_data.get('line', 0),
                                'actual': pick_data.get('actual'),
                                'result': pick_data.get('status', 'pending'),
                                'confidence': pick_data.get('confidence', 0)
                            })
                
                # Stop if we have enough history
                if len(history) >= limit:
                    break
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting player history: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Initialize memory system
    memory = GhostMemory()
    
    # Record a new pick
    pick_id = memory.record_pick({
        'player_name': 'Juan Soto',
        'team': 'nyy',
        'sport': 'mlb',
        'prop_type': 'hits_plus_runs_plus_rbis',
        'line': 2.5,
        'confidence': 0.75,
        'ticket_id': 'ticket_123',
        'red_flags': ['high_wind'],
        'is_hot_streak': True
    })
    
    print(f"Recorded pick with ID: {pick_id}")
    
    # Update pick result (simulating a hit)
    memory.update_pick_result(pick_id, 3.0)
    
    # Get player stats
    stats = memory.get_player_stats('Juan Soto')
    print(f"Juan Soto stats: {stats}")
