"""
Unified Ticket Manager for Ghost AI
Handles all ticket storage, results checking, and archiving in one place
"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnifiedTicketManager:
    """
    Unified ticket management system for efficient storage and results checking
    """
    
    def __init__(self):
        # Load config
        self.config = self._load_config()
        
        # Set up directories
        self.tickets_dir = Path(self.config['tickets']['unified_storage']['tickets_dir'])
        self.results_dir = Path(self.config['tickets']['unified_storage']['results_dir'])
        self.archive_dir = Path(self.config['tickets']['unified_storage']['archive_dir'])
        
        # Create directories if they don't exist
        self.tickets_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Unified Ticket Manager initialized")
        logger.info(f"   Tickets: {self.tickets_dir}")
        logger.info(f"   Results: {self.results_dir}")
        logger.info(f"   Archive: {self.archive_dir}")
    
    def _load_config(self) -> Dict:
        """Load configuration from config file"""
        try:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {
                "tickets": {
                    "unified_storage": {
                        "tickets_dir": "ghost_ai_core_memory/tickets/unified",
                        "results_dir": "ghost_ai_core_memory/tickets/results",
                        "archive_dir": "ghost_ai_core_memory/tickets/archive",
                        "auto_archive_days": 7,
                        "efficient_results_checking": True
                    }
                }
            }
    
    def save_ticket(self, ticket: Dict, ticket_type: str = "standard") -> Optional[str]:
        """
        Save a ticket to unified storage
        
        Args:
            ticket: Ticket data to save
            ticket_type: Type of ticket (standard, potd, totd, etc.)
            
        Returns:
            Ticket ID
        """
        try:
            # Generate ticket ID if not present
            if 'ticket_id' not in ticket:
                ticket['ticket_id'] = f"{ticket_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(list(self.tickets_dir.glob('*.json')))}"
            
            # Add metadata
            ticket['saved_at'] = datetime.now(timezone.utc).isoformat()
            ticket['ticket_type'] = ticket_type
            
            # Save to unified directory
            filename = f"{ticket['ticket_id']}.json"
            filepath = self.tickets_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(ticket, f, indent=2)
            
            logger.info(f"💾 Saved ticket {ticket['ticket_id']} to unified storage")
            return ticket['ticket_id']
            
        except Exception as e:
            logger.error(f"Error saving ticket: {e}")
            return None
    
    def get_all_tickets(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get all tickets from unified storage
        
        Args:
            date: Optional date filter (YYYY-MM-DD)
            
        Returns:
            List of tickets
        """
        try:
            tickets = []
            
            for filepath in self.tickets_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        ticket = json.load(f)
                    
                    # Apply date filter if specified
                    if date:
                        saved_date = ticket.get('saved_at', '')[:10]  # Extract YYYY-MM-DD
                        if saved_date != date:
                            continue
                    
                    tickets.append(ticket)
                    
                except Exception as e:
                    logger.error(f"Error loading ticket {filepath}: {e}")
            
            # Sort by saved_at timestamp
            tickets.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
            
            logger.info(f"📋 Retrieved {len(tickets)} tickets from unified storage")
            return tickets
            
        except Exception as e:
            logger.error(f"Error getting tickets: {e}")
            return []
    
    def get_ticket(self, ticket_id: str) -> Optional[Dict]:
        """
        Get a specific ticket by ID
        
        Args:
            ticket_id: ID of the ticket to retrieve
            
        Returns:
            Ticket data or None if not found
        """
        try:
            filepath = self.tickets_dir / f"{ticket_id}.json"
            
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Ticket {ticket_id} not found")
                return None
                
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            return None
    
    def save_results(self, ticket_id: str, results: List[Dict]) -> bool:
        """
        Save results for a ticket
        
        Args:
            ticket_id: ID of the ticket
            results: List of result data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create results data
            results_data = {
                'ticket_id': ticket_id,
                'results': results,
                'processed_at': datetime.now(timezone.utc).isoformat(),
                'total_picks': len(results),
                'wins': len([r for r in results if r.get('result') == 'W']),
                'losses': len([r for r in results if r.get('result') == 'L']),
                'pushes': len([r for r in results if r.get('result') == 'P'])
            }
            
            # Save to results directory
            filename = f"{ticket_id}_results.json"
            filepath = self.results_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"🏁 Saved results for ticket {ticket_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving results for ticket {ticket_id}: {e}")
            return False
    
    def get_results(self, ticket_id: str) -> Optional[Dict]:
        """
        Get results for a specific ticket
        
        Args:
            ticket_id: ID of the ticket
            
        Returns:
            Results data or None if not found
        """
        try:
            filepath = self.results_dir / f"{ticket_id}_results.json"
            
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting results for ticket {ticket_id}: {e}")
            return None
    
    def get_all_results(self, date: Optional[str] = None) -> List[Dict]:
        """
        Get all results from unified storage
        
        Args:
            date: Optional date filter (YYYY-MM-DD)
            
        Returns:
            List of results
        """
        try:
            results = []
            
            for filepath in self.results_dir.glob('*_results.json'):
                try:
                    with open(filepath, 'r') as f:
                        result_data = json.load(f)
                    
                    # Handle different result formats
                    if isinstance(result_data, list):
                        # Old format: list of individual results
                        # Convert to new format
                        if result_data:
                            # Group by ticket_id
                            ticket_groups = {}
                            for item in result_data:
                                ticket_id = item.get('ticket_id', 'unknown')
                                if ticket_id not in ticket_groups:
                                    ticket_groups[ticket_id] = []
                                ticket_groups[ticket_id].append(item)
                            
                            # Convert each group to new format
                            for ticket_id, items in ticket_groups.items():
                                new_result = {
                                    'ticket_id': ticket_id,
                                    'results': items,
                                    'processed_at': items[0].get('game_date', datetime.now().isoformat()),
                                    'total_picks': len(items),
                                    'wins': len([i for i in items if i.get('result') == 'W']),
                                    'losses': len([i for i in items if i.get('result') == 'L']),
                                    'pushes': len([i for i in items if i.get('result') == 'P'])
                                }
                                results.append(new_result)
                    else:
                        # New format: single result object
                        results.append(result_data)
                    
                except Exception as e:
                    logger.error(f"Error loading results {filepath}: {e}")
            
            # Apply date filter if specified
            if date:
                filtered_results = []
                for result in results:
                    processed_date = result.get('processed_at', '')[:10]  # Extract YYYY-MM-DD
                    if processed_date == date:
                        filtered_results.append(result)
                results = filtered_results
            
            # Sort by processed_at timestamp
            results.sort(key=lambda x: x.get('processed_at', ''), reverse=True)
            
            logger.info(f"📊 Retrieved {len(results)} result sets from unified storage")
            return results
            
        except Exception as e:
            logger.error(f"Error getting results: {e}")
            return []
    
    def check_pending_results(self) -> List[str]:
        """
        Check for tickets that need results processing
        
        Returns:
            List of ticket IDs that need results
        """
        try:
            pending_tickets = []
            
            # Get all tickets
            tickets = self.get_all_tickets()
            
            for ticket in tickets:
                ticket_id = ticket.get('ticket_id')
                
                # Check if results exist
                results_file = self.results_dir / f"{ticket_id}_results.json"
                
                if not results_file.exists():
                    # Check if game time has passed
                    game_time = ticket.get('commence_time')
                    if game_time:
                        try:
                            game_dt = datetime.fromisoformat(game_time.replace('Z', '+00:00'))
                            if game_dt < datetime.now(timezone.utc):
                                pending_tickets.append(ticket_id)
                        except:
                            # If we can't parse the time, assume it needs results
                            pending_tickets.append(ticket_id)
            
            logger.info(f"⏳ Found {len(pending_tickets)} tickets pending results")
            return pending_tickets
            
        except Exception as e:
            logger.error(f"Error checking pending results: {e}")
            return []
    
    def archive_old_tickets(self, days: Optional[int] = None) -> int:
        """
        Archive tickets older than specified days
        
        Args:
            days: Number of days (uses config default if None)
            
        Returns:
            Number of tickets archived
        """
        try:
            if days is None:
                days = int(self.config['tickets']['unified_storage']['auto_archive_days'])
            else:
                days = int(days)
            
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            archived_count = 0
            
            # Archive old tickets
            for filepath in self.tickets_dir.glob('*.json'):
                try:
                    with open(filepath, 'r') as f:
                        ticket = json.load(f)
                    
                    saved_at = ticket.get('saved_at')
                    if saved_at:
                        saved_dt = datetime.fromisoformat(saved_at.replace('Z', '+00:00'))
                        if saved_dt < cutoff_date:
                            # Move to archive
                            archive_path = self.archive_dir / filepath.name
                            shutil.move(str(filepath), str(archive_path))
                            archived_count += 1
                            
                except Exception as e:
                    logger.error(f"Error archiving {filepath}: {e}")
            
            # Archive old results
            for filepath in self.results_dir.glob('*_results.json'):
                try:
                    with open(filepath, 'r') as f:
                        result_data = json.load(f)
                    
                    processed_at = result_data.get('processed_at')
                    if processed_at:
                        processed_dt = datetime.fromisoformat(processed_at.replace('Z', '+00:00'))
                        if processed_dt < cutoff_date:
                            # Move to archive
                            archive_path = self.archive_dir / filepath.name
                            shutil.move(str(filepath), str(archive_path))
                            
                except Exception as e:
                    logger.error(f"Error archiving results {filepath}: {e}")
            
            logger.info(f"📦 Archived {archived_count} old tickets")
            return archived_count
            
        except Exception as e:
            logger.error(f"Error archiving old tickets: {e}")
            return 0
    
    def get_daily_summary(self, date: Optional[str] = None) -> Dict:
        """
        Get daily summary of tickets and results
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Summary dictionary
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            tickets = self.get_all_tickets(date)
            results = self.get_all_results(date)
            
            # Calculate summary
            total_tickets = len(tickets)
            total_results = len(results)
            
            total_picks = 0
            total_wins = 0
            total_losses = 0
            total_pushes = 0
            
            for result in results:
                total_picks += result.get('total_picks', 0)
                total_wins += result.get('wins', 0)
                total_losses += result.get('losses', 0)
                total_pushes += result.get('pushes', 0)
            
            win_rate = (total_wins / total_picks * 100) if total_picks > 0 else 0
            
            summary = {
                'date': date,
                'total_tickets': total_tickets,
                'total_results': total_results,
                'total_picks': total_picks,
                'wins': total_wins,
                'losses': total_losses,
                'pushes': total_pushes,
                'win_rate': win_rate,
                'pending_tickets': len(self.check_pending_results())
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {
                'date': date,
                'total_tickets': 0,
                'total_results': 0,
                'total_picks': 0,
                'wins': 0,
                'losses': 0,
                'pushes': 0,
                'win_rate': 0,
                'pending_tickets': 0
            }

    def get_tickets_for_date(self, date_str):
        """
        Stub method for compatibility. Returns all tickets for the given date using get_all_tickets.
        """
        return self.get_all_tickets(date_str)

    def save_tickets(self, tickets, date_str):
        """
        Save a list of tickets for a given date to a single file.
        """
        filename = f"{date_str}_filtered_tickets.json"
        filepath = self.tickets_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=2)
        logger.info(f"Saved {len(tickets)} filtered tickets to {filepath}")

# Global instance for easy access
unified_ticket_manager = UnifiedTicketManager() 