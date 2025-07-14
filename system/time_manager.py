#!/usr/bin/env python3
"""
Time Manager for Ghost AI 3.0

Handles:
- 3.4-hour cleanup intervals during active hours
- Game completion tracking
- System state management
"""

import json
import logging
from datetime import datetime, time, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger('ghost_ai.time_manager')

class TimeManager:
    """Time management for Ghost AI (no sleep/wake cycles, always active)."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.state_file = base_dir / 'data' / 'time_state.json'
        # Remove sleep/wake schedule
        self.cleanup_interval_hours = 3.4  # 3 hours 24 minutes
        self.state = self._load_state()
        self._initialize_state()
        logger.info(f"Time Manager initialized at {self.get_current_time()}")
        logger.info(f"AI is always active, no sleep schedule.")
    
    def _load_state(self) -> Dict[str, Any]:
        """Load time state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    logger.info("Loaded existing time state")
                    return state
        except Exception as e:
            logger.error(f"Error loading time state: {e}")
        
        # Default state
        return {
            'last_cleanup': None,
            'last_wake': None,
            'last_sleep': None,
            'cleanup_count': 0,
            'is_sleeping': False,
            'next_cleanup': None,
            'created_at': self.get_current_time().isoformat()
        }
    
    def _save_state(self):
        """Save current state to file."""
        try:
            self.state_file.parent.mkdir(exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving time state: {e}")
    
    def _initialize_state(self):
        """Initialize state if needed."""
        current_time = self.get_current_time()
        
        if not self.state.get('last_wake'):
            self.state['last_wake'] = current_time.isoformat()
        
        if not self.state.get('next_cleanup'):
            self._schedule_next_cleanup()
        
        self._save_state()
    
    def get_current_time(self) -> datetime:
        """Get current time in UTC."""
        return datetime.now(timezone.utc)
    
    def get_eastern_time(self) -> datetime:
        """Get current time in Eastern Time."""
        eastern = timezone(timedelta(hours=-4))  # EDT
        return self.get_current_time().astimezone(eastern)
    
    def is_wake_time(self) -> bool:
        """Check if it's wake time (1:00 AM)."""
        eastern_time = self.get_eastern_time()
        current_time = eastern_time.time()
        
        # Wake time is 1:00 AM
        return current_time.hour == 1 and current_time.minute == 0
    
    def _schedule_next_cleanup(self):
        """Schedule the next cleanup time."""
        current_time = self.get_current_time()
        next_cleanup = current_time + timedelta(hours=self.cleanup_interval_hours)
        self.state['next_cleanup'] = next_cleanup.isoformat()
        self._save_state()
        
        logger.info(f"📅 Next cleanup scheduled for {next_cleanup}")
    
    def is_time_for_cleanup(self) -> bool:
        """Check if it's time for the next cleanup."""
        if self.state.get('is_sleeping'):
            return False  # Don't cleanup while sleeping
        
        if not self.state.get('next_cleanup'):
            return True  # No cleanup scheduled, do it now
        
        try:
            next_cleanup = datetime.fromisoformat(self.state['next_cleanup'].replace('Z', '+00:00'))
            current_time = self.get_current_time()
            
            return current_time >= next_cleanup
        except Exception as e:
            logger.error(f"Error checking cleanup time: {e}")
            return True
    
    def mark_cleanup_completed(self):
        """Mark cleanup as completed and schedule next one."""
        current_time = self.get_current_time()
        self.state['last_cleanup'] = current_time.isoformat()
        self.state['cleanup_count'] = self.state.get('cleanup_count', 0) + 1
        self._schedule_next_cleanup()
        self._save_state()
        
        logger.info(f"✅ Cleanup #{self.state['cleanup_count']} completed at {current_time}")
    
    def get_sleep_status(self) -> Dict[str, Any]:
        """Get current sleep/wake status."""
        eastern_time = self.get_eastern_time()
        current_time = eastern_time.time()
        
        return {
            'is_sleeping': self.state.get('is_sleeping', False),
            'current_time_eastern': eastern_time.isoformat(),
            'cleanup_interval_hours': self.cleanup_interval_hours,
            'last_cleanup': self.state.get('last_cleanup'),
            'next_cleanup': self.state.get('next_cleanup'),
            'cleanup_count': self.state.get('cleanup_count', 0),
            'is_time_for_cleanup': self.is_time_for_cleanup()
        }
    
    def get_cleanup_schedule(self) -> Dict[str, Any]:
        """Get cleanup schedule information."""
        eastern_time = self.get_eastern_time()
        
        return {
            'current_time_eastern': eastern_time.isoformat(),
            'cleanup_interval_hours': self.cleanup_interval_hours,
            'last_cleanup': self.state.get('last_cleanup'),
            'next_cleanup': self.state.get('next_cleanup'),
            'cleanup_count': self.state.get('cleanup_count', 0),
            'is_sleeping': self.state.get('is_sleeping', False),
            'is_time_for_cleanup': self.is_time_for_cleanup()
        }
    
    def force_cleanup(self):
        """Force immediate cleanup."""
        logger.info("🔄 Forcing immediate cleanup...")
        self.mark_cleanup_completed()
    
    def reset_schedule(self):
        """Reset the schedule and start fresh."""
        logger.info("🔄 Resetting AI schedule...")
        self.state = {
            'last_cleanup': None,
            'last_wake': None,
            'last_sleep': None,
            'cleanup_count': 0,
            'is_sleeping': False,
            'next_cleanup': None,
            'created_at': self.get_current_time().isoformat()
        }
        self._initialize_state()
        logger.info("✅ AI schedule reset complete")

def create_time_manager(base_dir: Path) -> TimeManager:
    """Create and return a TimeManager instance."""
    return TimeManager(base_dir) 