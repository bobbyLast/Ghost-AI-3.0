"""
Quick Integration for Ghost AI Reverse Engine
Simple functions to integrate reverse engine into existing pipeline
"""

import logging
import asyncio
import requests
import json
import os
from typing import Dict, List, Any
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load update webhook from config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')
def get_update_webhook_url():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config['discord'].get('update_webhook_url')
    except Exception:
        return None

# Discord webhook URL (for updates/reports)
DISCORD_WEBHOOK_URL = get_update_webhook_url()

def send_discord_webhook(content: str, username: str = "Ghost AI Reverse Engine") -> bool:
    """
    Send message to Discord webhook (updates only)
    """
    try:
        if not DISCORD_WEBHOOK_URL:
            logger.error("No update webhook URL configured!")
            return False
        payload = {
            "content": content,
            "username": username
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code in [200, 204]:
            logger.info("✅ Discord webhook sent successfully")
            return True
        else:
            logger.error(f"❌ Discord webhook failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Error sending Discord webhook: {e}")
        return False

def integrate_into_ticket_generation(tickets: List[Dict]) -> List[Dict]:
    """
    Integrate reverse engine analysis into ticket generation
    
    Args:
        tickets: List of generated tickets
        
    Returns:
        List of enhanced tickets with reverse engine analysis
    """
    try:
        from auto_integration import auto_integration
        
        enhanced_tickets = []
        for ticket in tickets:
            try:
                # Record picks for tracking
                picks = auto_integration.record_ticket_picks(ticket)
                
                # Enhance with reverse engine analysis
                enhanced_ticket = auto_integration.integration.enhance_ticket_with_reverse_analysis(ticket)
                
                enhanced_tickets.append(enhanced_ticket)
                logger.info(f"🎯 Enhanced ticket {ticket.get('ticket_id', 'unknown')} with {len(picks)} picks")
                
            except Exception as e:
                logger.error(f"Error enhancing ticket {ticket.get('ticket_id', 'unknown')}: {e}")
                enhanced_tickets.append(ticket)  # Use original if enhancement fails
        
        logger.info(f"✅ Enhanced {len(enhanced_tickets)} tickets with reverse engine analysis")
        return enhanced_tickets
        
    except Exception as e:
        logger.error(f"Error in ticket generation integration: {e}")
        return tickets

async def integrate_into_results_processing(game_id: str, results: List[Dict]):
    """
    Integrate reverse engine analysis into results processing
    
    Args:
        game_id: ID of the game
        results: List of game results
    """
    try:
        from auto_integration import auto_integration
        
        # Update closing odds
        await auto_integration.update_closing_odds(game_id)
        
        # Record results
        auto_integration.record_game_results(game_id, results)
        
        logger.info(f"🏁 Integrated results processing for game {game_id}")
        
    except Exception as e:
        logger.error(f"Error in results processing integration: {e}")

def get_daily_report() -> str:
    """
    Get daily performance report with reverse engine insights
    
    Returns:
        Formatted report string
    """
    try:
        from auto_integration import get_daily_performance_report
        return get_daily_performance_report()
    except Exception as e:
        return f"Error generating daily report: {e}"

def send_daily_report_to_discord() -> bool:
    """
    Generate and send daily report to Discord webhook
    Also appends a summary entry to ghost_diary.json
    Returns:
        True if successful, False otherwise
    """
    try:
        # --- Config override for force_post_summary ---
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        force_post = False
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            force_post = config.get('force_post_summary', False)
        # --- End config override ---
        report = get_daily_report()
        from odds_reverse_engineering.auto_integration import auto_integration
        daily_stats = auto_integration.get_daily_summary()
        date = daily_stats.get('date')
        # --- Check if already posted unless force_post is True ---
        diary_path = os.path.join(os.path.dirname(__file__), '../ghost_diary.json')
        already_posted = False
        if not force_post and os.path.exists(diary_path):
            with open(diary_path, 'r', encoding='utf-8') as f:
                diary = json.load(f)
            if any(entry.get('date') == date for entry in diary):
                already_posted = True
        if already_posted:
            logger.info(f"Daily summary for {date} already posted. Skipping (force_post_summary is False).")
            return True
        # Split long reports if needed
        if len(report) > 2000:
            chunks = [report[i:i+1900] for i in range(0, len(report), 1900)]
            for i, chunk in enumerate(chunks):
                success = send_discord_webhook(f"📊 Daily Report (Part {i+1}):\n```{chunk}```")
                if not success:
                    return False
        else:
            success = send_discord_webhook(f"📊 Daily Report:\n```{report}```")
            if not success:
                return False
        # --- Append to ghost_diary.json ---
        diary_entry = {
            'date': date,
            'summary': report,
            'stats': daily_stats
        }
        try:
            if os.path.exists(diary_path):
                with open(diary_path, 'r', encoding='utf-8') as f:
                    diary = json.load(f)
            else:
                diary = []
            diary.append(diary_entry)
            with open(diary_path, 'w', encoding='utf-8') as f:
                json.dump(diary, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing to ghost_diary.json: {e}")
        logger.info("✅ Daily report sent to Discord webhook and logged in ghost_diary.json")
        return True
    except Exception as e:
        logger.error(f"Error sending daily report to Discord: {e}")
        return False

def get_reverse_engine_status() -> Dict[str, Any]:
    """
    Get reverse engine analysis status
    
    Returns:
        Status dictionary
    """
    try:
        from auto_integration import auto_integration
        return auto_integration.get_reverse_engine_insights()
    except Exception as e:
        return {"error": str(e)}

def record_ticket_manually(ticket: Dict) -> bool:
    """
    Manually record a ticket for tracking
    
    Args:
        ticket: Ticket to record
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from auto_integration import auto_integration
        picks = auto_integration.record_ticket_picks(ticket)
        logger.info(f"📝 Manually recorded ticket {ticket.get('ticket_id', 'unknown')} with {len(picks)} picks")
        return True
    except Exception as e:
        logger.error(f"Error manually recording ticket: {e}")
        return False

def record_result_manually(game_id: str, player_name: str, prop_type: str, 
                          actual_value: float, line: float, pick_side: str) -> bool:
    """
    Manually record a single result
    
    Args:
        game_id: ID of the game
        player_name: Name of the player
        prop_type: Type of prop
        actual_value: Actual result value
        line: Prop line
        pick_side: 'over' or 'under'
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from auto_integration import auto_integration
        
        # Create result dictionary
        result = {
            'player_name': player_name,
            'prop_type': prop_type,
            'actual_value': actual_value
        }
        
        # Record the result
        auto_integration.record_game_results(game_id, [result])
        
        logger.info(f"📊 Manually recorded result: {player_name} {prop_type} = {actual_value}")
        return True
        
    except Exception as e:
        logger.error(f"Error manually recording result: {e}")
        return False

def get_tracking_summary() -> Dict[str, Any]:
    """
    Get summary of tracked picks and results
    
    Returns:
        Summary dictionary
    """
    try:
        from auto_integration import auto_integration
        
        # Get today's summary
        today_summary = auto_integration.get_daily_summary()
        
        # Get overall performance
        if auto_integration.performance_file.exists():
            with open(auto_integration.performance_file, 'r') as f:
                performance = json.load(f)
        else:
            performance = {}
        
        return {
            "today": today_summary,
            "overall": performance,
            "tracking_active": True
        }
        
    except Exception as e:
        logger.error(f"Error getting tracking summary: {e}")
        return {"error": str(e)}

def send_tracking_summary_to_discord() -> bool:
    """
    Send tracking summary to Discord webhook
    
    Returns:
        True if successful, False otherwise
    """
    try:
        summary = get_tracking_summary()
        
        today = summary.get('today', {})
        overall = summary.get('overall', {})
        
        message = f"""
📈 Tracking Summary:
Today: {today.get('total_picks', 0)} picks, {today.get('wins', 0)}W-{today.get('losses', 0)}L
Overall: {overall.get('total_picks', 0)} picks, {overall.get('win_rate', 0):.1f}% win rate
"""
        
        return send_discord_webhook(message)
        
    except Exception as e:
        logger.error(f"Error sending tracking summary to Discord: {e}")
        return False

def send_reverse_engine_status_to_discord() -> bool:
    """
    Send reverse engine status to Discord webhook
    
    Returns:
        True if successful, False otherwise
    """
    try:
        status = get_reverse_engine_status()
        
        if status.get('analysis_available'):
            message = "🔬 Reverse Engine Analysis: ✅ Available and Active"
        else:
            message = "🔬 Reverse Engine Analysis: ❌ Not Available"
        
        return send_discord_webhook(message)
        
    except Exception as e:
        logger.error(f"Error sending reverse engine status to Discord: {e}")
        return False

# Example usage functions
def example_ticket_integration():
    """Example of how to integrate into ticket generation"""
    print("🎟️ Example: Ticket Generation Integration")
    print("="*50)
    
    # Mock ticket
    mock_ticket = {
        'ticket_id': 'EXAMPLE_001',
        'game_id': 'example_game_1',
        'commence_time': datetime.now(timezone.utc).isoformat(),
        'selections': [
            {
                'player_name': 'Example Player',
                'prop_type': 'hits',
                'line': 1.5,
                'odds': -110,
                'confidence': 0.75
            }
        ]
    }
    
    # Integrate reverse engine
    enhanced_tickets = integrate_into_ticket_generation([mock_ticket])
    
    print(f"Enhanced {len(enhanced_tickets)} tickets")
    for ticket in enhanced_tickets:
        print(f"  Ticket {ticket.get('ticket_id')}: Enhanced confidence = {ticket.get('enhanced_confidence_score', 'N/A')}")

async def example_results_integration():
    """Example of how to integrate into results processing"""
    print("\n🏁 Example: Results Processing Integration")
    print("="*50)
    
    # Mock results
    mock_results = [
        {
            'player_name': 'Example Player',
            'prop_type': 'hits',
            'actual_value': 2.0
        }
    ]
    
    # Integrate reverse engine
    await integrate_into_results_processing('example_game_1', mock_results)
    
    print("Results processed with reverse engine integration")

def example_daily_report():
    """Example of daily report generation and Discord sending"""
    print("\n📊 Example: Daily Report with Discord")
    print("="*50)
    
    # Generate and send report
    success = send_daily_report_to_discord()
    if success:
        print("✅ Daily report sent to Discord webhook")
    else:
        print("❌ Failed to send daily report to Discord")

if __name__ == "__main__":
    # Run examples
    print("🧪 Quick Integration Examples")
    print("="*50)
    
    # Test ticket integration
    example_ticket_integration()
    
    # Test results integration
    asyncio.run(example_results_integration())
    
    # Test daily report with Discord
    example_daily_report()
    
    # Test status
    status = get_reverse_engine_status()
    print(f"\n🔬 Reverse Engine Status: {status}")
    
    # Test tracking summary
    summary = get_tracking_summary()
    print(f"\n📈 Tracking Summary: {summary}")
    
    # Test Discord webhook
    print("\n🔗 Testing Discord webhook...")
    webhook_success = send_discord_webhook("🧪 Test message from Ghost AI Reverse Engine Integration")
    if webhook_success:
        print("✅ Discord webhook test successful")
    else:
        print("❌ Discord webhook test failed") 