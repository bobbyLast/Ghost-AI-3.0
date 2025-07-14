#!/usr/bin/env python3
"""
Memory Manager for Ghost AI 3.0 Sportsbook Edition
Tracks every ticket, prop, and player used to prevent duplicates and overload loops
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional
import hashlib

logger = logging.getLogger('memory_manager')

class MemoryManager:
    """Persistent memory manager for tracking all posted content."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_dir = base_dir / 'ghost_ai_core_memory'
        
        # Memory files
        self.memory_file = self.memory_dir / 'memory_manager.json'
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Today's date
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        # Load memory
        self.memory = self._load_memory()
        
        # Initialize today's tracking
        if self.today not in self.memory.get('daily_tracking', {}):
            self.memory.setdefault('daily_tracking', {})[self.today] = {
                'props_used': set(),
                'players_used': set(),
                'tickets_posted': set(),
                'prop_types_used': set(),
                'fades_posted': set(),
                'last_updated': datetime.now().isoformat()
            }
        
        logger.info("🧠 Memory Manager initialized")
        logger.info(f"   Props used today: {len(self.memory['daily_tracking'][self.today]['props_used'])}")
        logger.info(f"   Players used today: {len(self.memory['daily_tracking'][self.today]['players_used'])}")
        logger.info(f"   Tickets posted today: {len(self.memory['daily_tracking'][self.today]['tickets_posted'])}")
    
    def _load_memory(self) -> Dict:
        """Load memory from file."""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Convert sets back from lists
                    for date in data.get('daily_tracking', {}):
                        daily = data['daily_tracking'][date]
                        daily['props_used'] = set(daily.get('props_used', []))
                        daily['players_used'] = set(daily.get('players_used', []))
                        daily['tickets_posted'] = set(daily.get('tickets_posted', []))
                        daily['prop_types_used'] = set(daily.get('prop_types_used', []))
                        daily['fades_posted'] = set(daily.get('fades_posted', []))
                    return data
        except Exception as e:
            logger.error(f"Error loading memory: {e}")
        
        return {
            'daily_tracking': {},
            'historical_data': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_memory(self):
        """Save memory to file."""
        try:
            # Convert sets to lists for JSON serialization
            save_data = self.memory.copy()
            for date in save_data.get('daily_tracking', {}):
                daily = save_data['daily_tracking'][date]
                daily['props_used'] = list(daily.get('props_used', []))
                daily['players_used'] = list(daily.get('players_used', []))
                daily['tickets_posted'] = list(daily.get('tickets_posted', []))
                daily['prop_types_used'] = list(daily.get('prop_types_used', []))
                daily['fades_posted'] = list(daily.get('fades_posted', []))
            
            save_data['last_updated'] = datetime.now().isoformat()
            
            with open(self.memory_file, 'w') as f:
                json.dump(save_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def hash_prop(self, prop: Dict) -> str:
        """Create unique hash for a prop."""
        key_parts = [
            prop.get('player_name', ''),
            prop.get('prop_type', ''),
            str(prop.get('line', 0)),
            prop.get('pick_side', ''),
            prop.get('sport', ''),
            self.today
        ]
        return hashlib.md5('_'.join(key_parts).encode()).hexdigest()
    
    def hash_ticket(self, ticket: Dict) -> str:
        """Create unique hash for a ticket."""
        selections = ticket.get('selections', [])
        if not selections:
            return ""
        
        # Sort selections for consistent hashing
        sorted_selections = sorted(selections, key=lambda x: (
            x.get('player_name', ''),
            x.get('prop_type', ''),
            x.get('line', 0)
        ))
        
        # Create hash from sorted selections
        hash_parts = []
        for selection in sorted_selections:
            hash_parts.extend([
                selection.get('player_name', ''),
                selection.get('prop_type', ''),
                str(selection.get('line', 0)),
                selection.get('pick_side', ''),
                selection.get('sport', '')
            ])
        
        return hashlib.md5('_'.join(hash_parts).encode()).hexdigest()
    
    def is_prop_used_today(self, prop: Dict) -> bool:
        """Check if a prop has been used today."""
        prop_hash = self.hash_prop(prop)
        return prop_hash in self.memory['daily_tracking'][self.today]['props_used']
    
    def is_player_used_today(self, player_name: str) -> bool:
        """Check if a player has been used today."""
        return player_name in self.memory['daily_tracking'][self.today]['players_used']
    
    def is_ticket_posted_today(self, ticket: Dict) -> bool:
        """Check if a ticket has been posted today."""
        ticket_hash = self.hash_ticket(ticket)
        return ticket_hash in self.memory['daily_tracking'][self.today]['tickets_posted']
    
    def is_prop_type_used_in_ticket(self, prop_type: str, ticket_selections: List[Dict]) -> bool:
        """Check if a prop type is already used in a ticket."""
        for selection in ticket_selections:
            if selection.get('prop_type') == prop_type:
                return True
        return False
    
    def is_fade_posted_today(self, player_name: str, prop_type: str) -> bool:
        """Check if a fade has been posted today."""
        fade_key = f"{player_name}_{prop_type}_fade"
        return fade_key in self.memory['daily_tracking'][self.today]['fades_posted']
    
    def mark_prop_used(self, prop: Dict, player_name: str):
        """Mark a prop as used today."""
        prop_hash = self.hash_prop(prop)
        self.memory['daily_tracking'][self.today]['props_used'].add(prop_hash)
        self.memory['daily_tracking'][self.today]['players_used'].add(player_name)
        self._save_memory()
        logger.info(f"🧠 Marked prop as used: {player_name} {prop.get('prop_type', 'Unknown')}")
    
    def mark_ticket_posted(self, ticket: Dict, ticket_id: str):
        """Mark a ticket as posted today."""
        ticket_hash = self.hash_ticket(ticket)
        self.memory['daily_tracking'][self.today]['tickets_posted'].add(ticket_hash)
        
        # Mark all players and props in the ticket
        for selection in ticket.get('selections', []):
            player_name = selection.get('player_name', '')
            if player_name:
                self.memory['daily_tracking'][self.today]['players_used'].add(player_name)
            
            prop_hash = self.hash_prop(selection)
            self.memory['daily_tracking'][self.today]['props_used'].add(prop_hash)
        
        self._save_memory()
        logger.info(f"🧠 Marked ticket as posted: {ticket_id}")
    
    def mark_fade_posted(self, player_name: str, prop_type: str):
        """Mark a fade as posted today."""
        fade_key = f"{player_name}_{prop_type}_fade"
        self.memory['daily_tracking'][self.today]['fades_posted'].add(fade_key)
        self.memory['daily_tracking'][self.today]['players_used'].add(player_name)
        self._save_memory()
        logger.info(f"🧠 Marked fade as posted: {player_name} {prop_type}")
    
    def get_daily_summary(self) -> Dict:
        """Get summary of today's activity."""
        today_data = self.memory['daily_tracking'].get(self.today, {})
        return {
            'date': self.today,
            'props_used': len(today_data.get('props_used', set())),
            'players_used': len(today_data.get('players_used', set())),
            'tickets_posted': len(today_data.get('tickets_posted', set())),
            'fades_posted': len(today_data.get('fades_posted', set())),
            'last_updated': today_data.get('last_updated', '')
        }
    
    def cleanup_old_memory(self, days: int = 30):
        """Clean up old memory entries."""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            old_dates = [date for date in self.memory.get('daily_tracking', {}).keys() 
                        if date < cutoff_date]
            
            for old_date in old_dates:
                del self.memory['daily_tracking'][old_date]
                logger.info(f"🧠 Cleaned up old memory from {old_date}")
            
            self._save_memory()
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
    
    def reset_daily_memory(self):
        """Reset today's memory (for testing or manual reset)."""
        self.memory['daily_tracking'][self.today] = {
            'props_used': set(),
            'players_used': set(),
            'tickets_posted': set(),
            'prop_types_used': set(),
            'fades_posted': set(),
            'last_updated': datetime.now().isoformat()
        }
        self._save_memory()
        logger.info("🧠 Reset daily memory") 