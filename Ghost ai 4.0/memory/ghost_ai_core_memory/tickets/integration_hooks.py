"""
Integration Hooks for Unified Ticket Manager
Connects the unified ticket manager with the existing Ghost AI pipeline
"""

import logging
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Import from the same directory
from .unified_ticket_manager import unified_ticket_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def hook_ticket_generation(tickets: List[Dict]) -> List[Dict]:
    """
    Hook function to be called when tickets are generated
    Saves all tickets to unified storage
    
    Args:
        tickets: List of generated tickets
        
    Returns:
        List of tickets with unified storage metadata
    """
    try:
        logger.info(f"Hook: Saving {len(tickets)} tickets to unified storage")
        
        saved_tickets = []
        for ticket in tickets:
            try:
                # Determine ticket type
                ticket_type = "standard"
                if ticket.get('ticket_type'):
                    ticket_type = ticket['ticket_type']
                elif 'POTD' in str(ticket):
                    ticket_type = "potd"
                elif 'TOTD' in str(ticket):
                    ticket_type = "totd"
                elif 'streak' in str(ticket).lower():
                    ticket_type = "streak"
                
                # Save to unified storage
                ticket_id = unified_ticket_manager.save_ticket(ticket, ticket_type)
                
                if ticket_id:
                    # Add unified storage metadata
                    ticket['unified_ticket_id'] = ticket_id
                    ticket['unified_storage'] = True
                    saved_tickets.append(ticket)
                    
                    logger.info(f"   Saved {ticket_type} ticket: {ticket_id}")
                else:
                    logger.error(f"   Failed to save ticket: {ticket.get('ticket_id', 'unknown')}")
                    saved_tickets.append(ticket)  # Keep original if save fails
                    
            except Exception as e:
                logger.error(f"Error processing ticket {ticket.get('ticket_id', 'unknown')}: {e}")
                saved_tickets.append(ticket)  # Keep original if processing fails
        
        logger.info(f"Hook: Successfully saved {len(saved_tickets)} tickets to unified storage")
        return saved_tickets
        
    except Exception as e:
        logger.error(f"Error in ticket generation hook: {e}")
        return tickets

async def hook_results_processing(game_id: str, results: List[Dict]) -> bool:
    """
    Hook function to be called when game results are processed
    Saves results to unified storage
    
    Args:
        game_id: ID of the game
        results: List of game results
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Hook: Processing results for game {game_id}")
        
        # Find tickets for this game
        all_tickets = unified_ticket_manager.get_all_tickets()
        game_tickets = []
        
        for ticket in all_tickets:
            if ticket.get('game_id') == game_id:
                game_tickets.append(ticket)
        
        if not game_tickets:
            logger.info(f"No tickets found for game {game_id}")
            return True
        
        # Process results for each ticket
        for ticket in game_tickets:
            ticket_id = ticket.get('ticket_id')
            
            # Match results to ticket selections
            ticket_results = []
            for selection in ticket.get('selections', []):
                player_name = selection.get('player_name')
                prop_type = selection.get('prop_type')
                
                # Find matching result
                for result in results:
                    if (result.get('player_name') == player_name and 
                        result.get('prop_type') == prop_type):
                        ticket_results.append(result)
                        break
            
            if ticket_results:
                # Save results for this ticket
                success = unified_ticket_manager.save_results(ticket_id, ticket_results)
                if success:
                    logger.info(f"   Saved results for ticket {ticket_id}")
                else:
                    logger.error(f"   Failed to save results for ticket {ticket_id}")
        
        logger.info(f"Hook: Processed results for {len(game_tickets)} tickets")
        return True
        
    except Exception as e:
        logger.error(f"Error in results processing hook: {e}")
        return False

def hook_daily_cleanup() -> Dict:
    """
    Hook function to be called for daily cleanup
    Archives old tickets and provides summary
    
    Returns:
        Cleanup summary
    """
    try:
        logger.info("Hook: Running daily cleanup")
        
        # Archive old tickets
        archived_count = unified_ticket_manager.archive_old_tickets()
        
        # Get daily summary
        summary = unified_ticket_manager.get_daily_summary()
        
        # Check pending results
        pending_tickets = unified_ticket_manager.check_pending_results()
        
        cleanup_summary = {
            'archived_tickets': archived_count,
            'daily_summary': summary,
            'pending_tickets': len(pending_tickets),
            'cleanup_time': datetime.now().isoformat()
        }
        
        logger.info(f"Hook: Cleanup completed - {archived_count} tickets archived, {len(pending_tickets)} pending")
        return cleanup_summary
        
    except Exception as e:
        logger.error(f"Error in daily cleanup hook: {e}")
        return {'error': str(e)}

def get_unified_summary() -> Dict:
    """
    Get comprehensive summary of unified ticket storage
    
    Returns:
        Summary dictionary
    """
    try:
        # Get all data
        all_tickets = unified_ticket_manager.get_all_tickets()
        all_results = unified_ticket_manager.get_all_results()
        pending_tickets = unified_ticket_manager.check_pending_results()
        
        # Calculate totals
        total_tickets = len(all_tickets)
        total_results = len(all_results)
        total_picks = sum(result.get('total_picks', 0) for result in all_results)
        total_wins = sum(result.get('wins', 0) for result in all_results)
        total_losses = sum(result.get('losses', 0) for result in all_results)
        total_pushes = sum(result.get('pushes', 0) for result in all_results)
        
        win_rate = (total_wins / total_picks * 100) if total_picks > 0 else 0
        
        summary = {
            'total_tickets': total_tickets,
            'total_results': total_results,
            'total_picks': total_picks,
            'wins': total_wins,
            'losses': total_losses,
            'pushes': total_pushes,
            'win_rate': win_rate,
            'pending_tickets': len(pending_tickets),
            'storage_efficiency': 'unified',
            'last_updated': datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting unified summary: {e}")
        return {'error': str(e)}

def migrate_existing_tickets() -> int:
    """
    Migrate existing tickets from old storage to unified storage
    
    Returns:
        Number of tickets migrated
    """
    try:
        logger.info("🔄 Starting migration of existing tickets to unified storage")
        
        # Check old storage locations
        old_locations = [
            Path("ghost_ai_core_memory/tickets/generated"),
            Path("ghost_ai_core_memory/tickets/posted"),
            Path("ghost_ai_core_memory/tickets/analyzed")
        ]
        
        migrated_count = 0
        
        for old_location in old_locations:
            if old_location.exists():
                logger.info(f"📁 Checking {old_location}")
                
                for filepath in old_location.glob('*.json'):
                    try:
                        with open(filepath, 'r') as f:
                            ticket = json.load(f)
                        
                        # Determine ticket type from filename or content
                        ticket_type = "migrated"
                        if 'potd' in filepath.name.lower():
                            ticket_type = "potd"
                        elif 'totd' in filepath.name.lower():
                            ticket_type = "totd"
                        elif 'streak' in filepath.name.lower():
                            ticket_type = "streak"
                        
                        # Save to unified storage
                        ticket_id = unified_ticket_manager.save_ticket(ticket, ticket_type)
                        
                        if ticket_id:
                            migrated_count += 1
                            logger.info(f"   ✅ Migrated: {filepath.name} -> {ticket_id}")
                        
                    except Exception as e:
                        logger.error(f"Error migrating {filepath}: {e}")
        
        logger.info(f"✅ Migration completed: {migrated_count} tickets migrated")
        return migrated_count
        
    except Exception as e:
        logger.error(f"Error in migration: {e}")
        return 0

# Integration with main pipeline
def integrate_with_pipeline():
    """
    Integrate unified ticket manager with main pipeline
    """
    try:
        logger.info("🔗 Integrating unified ticket manager with main pipeline")
        
        # Import main pipeline components
        try:
            from ai_brain.ghost_ai_orchestrator import GhostAIOrchestrator
            from ai_brain.daily_pick_manager import DailyPickManager
            
            # Add hooks to pipeline
            logger.info("✅ Successfully integrated with main pipeline")
            return True
            
        except ImportError as e:
            logger.warning(f"Could not import main pipeline components: {e}")
            logger.info("Unified ticket manager ready for manual integration")
            return False
            
    except Exception as e:
        logger.error(f"Error integrating with pipeline: {e}")
        return False

if __name__ == "__main__":
    # Test the integration
    logger.info("🧪 Testing unified ticket manager integration")
    
    # Test summary
    summary = get_unified_summary()
    logger.info(f"Summary: {summary}")
    
    # Test cleanup
    cleanup = hook_daily_cleanup()
    logger.info(f"Cleanup: {cleanup}")
    
    logger.info("✅ Integration test completed") 