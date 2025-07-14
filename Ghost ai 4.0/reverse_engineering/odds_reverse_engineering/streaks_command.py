"""
Streaks Command System for Ghost AI
Allows tracking of up to 3 concurrent streaks with full management
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone
import argparse

logger = logging.getLogger(__name__)

class StreaksCommand:
    """
    Manages up to 3 concurrent streaks with full tracking
    """
    
    STREAKS_FILE = "odds_reverse_engineering_test/active_streaks.json"
    STREAK_HISTORY_FILE = "odds_reverse_engineering_test/streak_history.json"
    
    def __init__(self):
        self.active_streaks = self.load_active_streaks()
        self.streak_history = self.load_streak_history()
        self.max_concurrent_streaks = 3
        
    def load_active_streaks(self) -> Dict:
        """Load active streaks from file"""
        try:
            with open(self.STREAKS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'streaks': [],
                'total_streaks_created': 0,
                'best_streak_ever': 0
            }
    
    def save_active_streaks(self):
        """Save active streaks to file"""
        with open(self.STREAKS_FILE, 'w') as f:
            json.dump(self.active_streaks, f, indent=2)
    
    def load_streak_history(self) -> List[Dict]:
        """Load streak history from file"""
        try:
            with open(self.STREAK_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    
    def save_streak_history(self):
        """Save streak history to file"""
        with open(self.STREAK_HISTORY_FILE, 'w') as f:
            json.dump(self.streak_history, f, indent=2)
    
    def create_streak(self, name: str, description: str = "") -> bool:
        """
        Create a new streak
        
        Args:
            name: Name of the streak
            description: Optional description
            
        Returns:
            True if created successfully, False if at limit
        """
        if len(self.active_streaks['streaks']) >= self.max_concurrent_streaks:
            logger.error(f"❌ Cannot create streak '{name}' - already at maximum of {self.max_concurrent_streaks} active streaks")
            return False
        
        streak_id = f"streak_{self.active_streaks['total_streaks_created'] + 1}"
        
        new_streak = {
            'id': streak_id,
            'name': name,
            'description': description,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'current_length': 0,
            'wins': 0,
            'losses': 0,
            'pushes': 0,
            'status': 'active',  # active, completed, abandoned
            'tickets': [],
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
        
        self.active_streaks['streaks'].append(new_streak)
        self.active_streaks['total_streaks_created'] += 1
        self.save_active_streaks()
        
        logger.info(f"✅ Created new streak: {name} (ID: {streak_id})")
        logger.info(f"📊 Active streaks: {len(self.active_streaks['streaks'])}/{self.max_concurrent_streaks}")
        
        return True
    
    def add_ticket_to_streak(self, streak_id: str, ticket_id: str, ticket_data: Dict) -> bool:
        """
        Add a ticket to a streak
        
        Args:
            streak_id: ID of the streak
            ticket_id: ID of the ticket
            ticket_data: Full ticket data
            
        Returns:
            True if added successfully
        """
        streak = self.find_streak_by_id(streak_id)
        if not streak:
            logger.error(f"❌ Streak {streak_id} not found")
            return False
        
        if streak['status'] != 'active':
            logger.error(f"❌ Cannot add ticket to {streak_id} - streak is {streak['status']}")
            return False
        
        # Add ticket to streak
        ticket_entry = {
            'ticket_id': ticket_id,
            'added_at': datetime.now(timezone.utc).isoformat(),
            'ticket_data': ticket_data,
            'result': None,
            'result_updated_at': None
        }
        
        streak['tickets'].append(ticket_entry)
        streak['last_updated'] = datetime.now(timezone.utc).isoformat()
        self.save_active_streaks()
        
        logger.info(f"✅ Added ticket {ticket_id} to streak {streak['name']}")
        return True
    
    def update_streak_result(self, streak_id: str, ticket_id: str, result: str) -> bool:
        """
        Update result for a ticket in a streak
        
        Args:
            streak_id: ID of the streak
            ticket_id: ID of the ticket
            result: 'W', 'L', or 'P'
            
        Returns:
            True if updated successfully
        """
        streak = self.find_streak_by_id(streak_id)
        if not streak:
            logger.error(f"❌ Streak {streak_id} not found")
            return False
        
        # Find the ticket
        ticket_found = False
        for ticket in streak['tickets']:
            if ticket['ticket_id'] == ticket_id:
                ticket['result'] = result
                ticket['result_updated_at'] = datetime.now(timezone.utc).isoformat()
                ticket_found = True
                break
        
        if not ticket_found:
            logger.error(f"❌ Ticket {ticket_id} not found in streak {streak_id}")
            return False
        
        # Update streak statistics
        if result == 'W':
            streak['wins'] += 1
            streak['current_length'] += 1
        elif result == 'L':
            streak['losses'] += 1
            # End the streak
            self.end_streak(streak_id, 'completed')
        elif result == 'P':
            streak['pushes'] += 1
            # Push doesn't affect streak length
        
        streak['last_updated'] = datetime.now(timezone.utc).isoformat()
        self.save_active_streaks()
        
        logger.info(f"✅ Updated streak {streak['name']} - Ticket {ticket_id}: {result}")
        if result == 'W':
            logger.info(f"🔥 Streak continues: {streak['current_length']} wins!")
        elif result == 'L':
            logger.info(f"💔 Streak ended at {streak['current_length']} wins")
        
        return True
    
    def end_streak(self, streak_id: str, reason: str = 'completed'):
        """
        End a streak
        
        Args:
            streak_id: ID of the streak
            reason: 'completed', 'abandoned', etc.
        """
        streak = self.find_streak_by_id(streak_id)
        if not streak:
            return
        
        streak['status'] = reason
        streak['ended_at'] = datetime.now(timezone.utc).isoformat()
        
        # Update best streak ever
        if streak['current_length'] > self.active_streaks['best_streak_ever']:
            self.active_streaks['best_streak_ever'] = streak['current_length']
            logger.info(f"🏆 NEW BEST STREAK EVER: {streak['current_length']} wins!")
        
        # Move to history
        self.streak_history.append(streak.copy())
        self.save_streak_history()
        
        # Remove from active streaks
        self.active_streaks['streaks'] = [s for s in self.active_streaks['streaks'] if s['id'] != streak_id]
        self.save_active_streaks()
        
        logger.info(f"📊 Streak {streak['name']} ended: {streak['current_length']} wins")
    
    def find_streak_by_id(self, streak_id: str) -> Optional[Dict]:
        """Find a streak by ID"""
        for streak in self.active_streaks['streaks']:
            if streak['id'] == streak_id:
                return streak
        return None
    
    def find_streak_by_name(self, name: str) -> Optional[Dict]:
        """Find a streak by name"""
        for streak in self.active_streaks['streaks']:
            if streak['name'].lower() == name.lower():
                return streak
        return None
    
    def get_active_streaks(self) -> List[Dict]:
        """Get all active streaks"""
        return self.active_streaks['streaks']
    
    def get_streak_summary(self) -> Dict:
        """Get comprehensive streak summary"""
        active_streaks = self.get_active_streaks()
        
        return {
            'active_streaks_count': len(active_streaks),
            'max_concurrent_streaks': self.max_concurrent_streaks,
            'total_streaks_created': self.active_streaks['total_streaks_created'],
            'best_streak_ever': self.active_streaks['best_streak_ever'],
            'total_completed_streaks': len(self.streak_history),
            'active_streaks': active_streaks
        }
    
    def display_active_streaks(self):
        """Display all active streaks"""
        active_streaks = self.get_active_streaks()
        
        if not active_streaks:
            print("📊 No active streaks")
            return
        
        print(f"🔥 ACTIVE STREAKS ({len(active_streaks)}/{self.max_concurrent_streaks})")
        print("=" * 60)
        
        for streak in active_streaks:
            print(f"🎯 {streak['name']} (ID: {streak['id']})")
            print(f"   Length: {streak['current_length']} wins")
            print(f"   Record: {streak['wins']}W-{streak['losses']}L-{streak['pushes']}P")
            print(f"   Tickets: {len(streak['tickets'])}")
            print(f"   Created: {streak['created_at'][:10]}")
            print(f"   Last Updated: {streak['last_updated'][:10]}")
            if streak['description']:
                print(f"   Description: {streak['description']}")
            print()
    
    def display_streak_history(self, limit: int = 10):
        """Display recent streak history"""
        if not self.streak_history:
            print("📊 No completed streaks")
            return
        
        print(f"📈 RECENT STREAK HISTORY (Last {limit})")
        print("=" * 60)
        
        recent_streaks = sorted(self.streak_history, key=lambda x: x.get('ended_at', ''), reverse=True)[:limit]
        
        for streak in recent_streaks:
            print(f"🏆 {streak['name']} - {streak['current_length']} wins")
            print(f"   Record: {streak['wins']}W-{streak['losses']}L-{streak['pushes']}P")
            print(f"   Ended: {streak.get('ended_at', 'Unknown')[:10]}")
            print(f"   Status: {streak['status']}")
            print()

def main():
    """Command line interface for streaks management"""
    parser = argparse.ArgumentParser(description='Ghost AI Streaks Management')
    parser.add_argument('command', choices=['list', 'create', 'add', 'update', 'history', 'summary'])
    parser.add_argument('--name', help='Streak name')
    parser.add_argument('--id', help='Streak ID')
    parser.add_argument('--ticket', help='Ticket ID')
    parser.add_argument('--result', choices=['W', 'L', 'P'], help='Result (W/L/P)')
    parser.add_argument('--description', help='Streak description')
    
    args = parser.parse_args()
    
    streaks_cmd = StreaksCommand()
    
    if args.command == 'list':
        streaks_cmd.display_active_streaks()
        
    elif args.command == 'create':
        if not args.name:
            print("❌ Error: --name required for create command")
            return
        success = streaks_cmd.create_streak(args.name, args.description or "")
        if success:
            print(f"✅ Created streak: {args.name}")
        else:
            print("❌ Failed to create streak")
            
    elif args.command == 'add':
        if not all([args.id, args.ticket]):
            print("❌ Error: --id and --ticket required for add command")
            return
        # For now, create dummy ticket data
        ticket_data = {'ticket_id': args.ticket, 'selections': []}
        success = streaks_cmd.add_ticket_to_streak(args.id, args.ticket, ticket_data)
        if success:
            print(f"✅ Added ticket {args.ticket} to streak {args.id}")
        else:
            print("❌ Failed to add ticket")
            
    elif args.command == 'update':
        if not all([args.id, args.ticket, args.result]):
            print("❌ Error: --id, --ticket, and --result required for update command")
            return
        success = streaks_cmd.update_streak_result(args.id, args.ticket, args.result)
        if success:
            print(f"✅ Updated streak {args.id} - Ticket {args.ticket}: {args.result}")
        else:
            print("❌ Failed to update result")
            
    elif args.command == 'history':
        streaks_cmd.display_streak_history()
        
    elif args.command == 'summary':
        summary = streaks_cmd.get_streak_summary()
        print("📊 STREAK SUMMARY")
        print("=" * 40)
        print(f"Active Streaks: {summary['active_streaks_count']}/{summary['max_concurrent_streaks']}")
        print(f"Total Created: {summary['total_streaks_created']}")
        print(f"Best Streak Ever: {summary['best_streak_ever']} wins")
        print(f"Completed Streaks: {summary['total_completed_streaks']}")

if __name__ == "__main__":
    main() 