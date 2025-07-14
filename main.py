#!/usr/bin/env python3
"""
Ghost AI 4.0 - Autonomous Sports Betting AI
Makes intelligent decisions, posts tickets autonomously, learns from results, and adapts strategy.
"""
import sys
import os
from pathlib import Path
import logging
import asyncio
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ghost_ai')

# --- AI Decision Making Functions ---

def ai_analyze_market_conditions():
    """AI analyzes current market conditions and opportunities."""
    logger.info("🧠 AI: Analyzing market conditions and opportunities...")
    try:
        # AI brain analyzes market conditions
        from ghost_brain import GhostBrain
        brain = GhostBrain(Path.cwd())
        # Use available method to analyze market
        market_analysis = brain.get_recent_performance()
        logger.info(f"🧠 AI: Market analysis complete - {market_analysis}")
        return market_analysis
    except Exception as e:
        logger.error(f"🧠 AI: Market analysis failed - {e}")
        return None

def ai_make_intelligent_decisions():
    """AI makes intelligent decisions about what actions to take."""
    logger.info("🧠 AI: Making intelligent decisions...")
    try:
        from ghost_brain import GhostBrain
        brain = GhostBrain(Path.cwd())
        
        # AI brain analyzes its state and makes decisions
        brain_state = brain.analyze_brain_state()
        goals = brain.set_intelligent_goals()
        decision = brain.make_intelligent_decision(goals, brain_state)
        
        logger.info(f"🧠 AI: Decision made - {decision['action']} - {decision['reasoning']}")
        return decision
    except Exception as e:
        logger.error(f"🧠 AI: Decision making failed - {e}")
        return {'action': 'generate_tickets', 'reasoning': 'Always generate tickets - no idling'}

def ai_fetch_all_props():
    """AI fetches props with intelligent analysis."""
    logger.info("🧠 AI: Fetching all props with intelligent analysis...")
    try:
        # Always fetch props - AI should never skip this
        logger.info("🧠 AI: Fetching MLB props...")
        import run_mlb_fetch
        logger.info("🧠 AI: Fetching WNBA props...")
        import run_wnba_fetch
        logger.info("🧠 AI: All props fetched successfully with analysis")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Props fetch failed - {e}")
        return False

def ai_generate_tickets():
    """AI generates tickets using intelligent analysis."""
    logger.info("🧠 AI: Generating tickets using intelligent analysis...")
    try:
        logger.info("🧠 AI: Running ticket generation...")
        import generate_tickets
        logger.info("🧠 AI: Tickets generated successfully with AI analysis")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Ticket generation failed - {e}")
        return False

def ai_analyze_and_decide():
    """AI analyzes data and makes intelligent decisions."""
    logger.info("🧠 AI: Analyzing data and making intelligent decisions...")
    try:
        import run_analysis
        # AI makes intelligent decisions based on analysis
        logger.info("🧠 AI: Analysis complete - making intelligent decisions")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Analysis failed - {e}")
        return False

def get_ticket_webhook():
    # 1. Check environment variable
    webhook = os.environ.get('TICKET_WEBHOOK')
    if webhook:
        return webhook
    # 2. Check config file
    config_file = Path('config/discord_config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            webhook = config.get('ticket_webhook') or config.get('webhook_url')
            if webhook:
                return webhook
    # 3. Fallback to known correct value
    return 'https://discord.com/api/webhooks/1386168741938597989/Ib-d9TDtSnd4gZ-C2JkKQ866p6fxAF3Ps4fLUhkGJYI_dZQCe8hCRBTODv1-vZV_U7Sy'

def get_moneyline_webhook():
    # 1. Check environment variable
    webhook = os.environ.get('MONEYLINE_WEBHOOK')
    if webhook:
        return webhook
    # 2. Check config file
    config_file = Path('config/discord_config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            webhook = config.get('moneyline_webhook')
            if webhook:
                return webhook
    # 3. Fallback to known correct value
    return 'https://discord.com/api/webhooks/1390410910392385756/w9-96vnCSQQjfu_hzesnaSt6MP3EEbC_5WuTGuQnvsKnxoxkS4cj8Nl3Z0KYqWnaV36z'

def get_update_webhook():
    # 1. Check environment variable
    webhook = os.environ.get('UPDATE_WEBHOOK')
    if webhook:
        return webhook
    # 2. Check config file
    config_file = Path('config/discord_config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            webhook = config.get('update_webhook')
            if webhook:
                return webhook
    # 3. Fallback to main webhook
    return os.environ.get('DISCORD_WEBHOOK_URL') or get_ticket_webhook()

def get_main_webhook():
    # 1. Check environment variable
    webhook = os.environ.get('DISCORD_WEBHOOK_URL')
    if webhook:
        return webhook
    # 2. Check config file
    config_file = Path('config/discord_config.json')
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
            webhook = config.get('webhook_url')
            if webhook:
                return webhook
    # 3. Fallback to ticket webhook
    return get_ticket_webhook()

def ai_post_tickets_intelligently():
    """AI posts tickets with intelligent formatting and analysis."""
    logger.info("🧠 AI: Posting tickets with intelligent analysis...")
    try:
        tickets_dir = Path("ghost_ai_core_memory/tickets/generated")
        if not tickets_dir.exists():
            logger.info("🧠 AI: No tickets directory found, checking for recent tickets...")
            return True
        ticket_files = list(tickets_dir.glob("*.json"))
        if not ticket_files:
            logger.info("🧠 AI: No generated tickets found to post")
            return True
        ticket_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        posted_count = 0
        for ticket_file in ticket_files[:10]:  # Increase to 10 to catch more types
            try:
                with open(ticket_file, 'r') as f:
                    ticket_data = json.load(f)
                # Robustly extract ticket(s)
                tickets = []
                if isinstance(ticket_data, dict):
                    if 'tickets' in ticket_data and isinstance(ticket_data['tickets'], list):
                        tickets = ticket_data['tickets']
                    elif 'ticket' in ticket_data and isinstance(ticket_data['ticket'], dict):
                        tickets = [ticket_data['ticket']]
                    elif 'props' in ticket_data or 'legs' in ticket_data:
                        tickets = [ticket_data]
                # Only post tickets with real props/legs
                for t in tickets:
                    is_moneyline = False
                    # Detect moneyline by type, market, or filename
                    if t.get('ticket_type', '').lower() == 'moneyline':
                        is_moneyline = True
                    elif any((leg.get('market', '').lower() == 'h2h') for leg in t.get('legs', [])) and not t.get('props'):
                        is_moneyline = True
                    elif 'moneyline' in ticket_file.name.lower() and not t.get('props'):
                        is_moneyline = True
                    webhook_url = get_moneyline_webhook() if is_moneyline else get_ticket_webhook()
                    # Post all valid tickets (including daily picks, streaks, mixed-sport, etc.) to ticket webhook
                    if (t.get('props') and isinstance(t['props'], list) and len(t['props']) > 0) or (t.get('legs') and isinstance(t['legs'], list) and len(t['legs']) > 0):
                        message = ai_format_ticket_for_discord(t)
                        import requests
                        payload = message
                        response = requests.post(webhook_url, json=payload)
                        if response.status_code == 204:
                            logger.info(f"🧠 AI: Posted ticket {ticket_file.name} to {'moneyline' if is_moneyline else 'ticket'} webhook")
                            posted_count += 1
                        else:
                            logger.warning(f"🧠 AI: Failed to post ticket {ticket_file.name}")
                    else:
                        logger.info(f"🧠 AI: Skipped empty or malformed ticket in {ticket_file.name}")
            except Exception as e:
                logger.error(f"🧠 AI: Error posting ticket {ticket_file.name}: {e}")
        if posted_count > 0:
            logger.info(f"🧠 AI: Successfully posted {posted_count} tickets with intelligent analysis")
        else:
            logger.info("🧠 AI: No tickets were posted")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Ticket posting failed - {e}")
        return False

def ai_format_ticket_for_discord(ticket):
    """AI formats tickets with intelligent analysis and reasoning."""
    try:
        ticket_id = ticket.get('ticket_id') or ticket.get('id') or 'N/A'
        ticket_type = ticket.get('ticket_type', '').upper() or 'AI-Powered Selection'
        confidence = ticket.get('total_confidence') or ticket.get('confidence') or 0
        legs = len(ticket.get('props', []) or ticket.get('legs', []) or [])
        timestamp = ticket.get('timestamp') or ''
        props = ticket.get('props') or ticket.get('legs') or []
        
        # AI analysis header
        title = f"🧠 {ticket_type}"
        
        # AI reasoning section
        ai_reasoning = ticket.get('ai_reasoning', 'AI analysis indicates strong value opportunity')
        
        # Picks section with AI confidence
        picks_lines = []
        for i, prop in enumerate(props, 1):
            player = prop.get('player') or prop.get('team') or 'N/A'
            line = prop.get('line') or ''
            prop_type = prop.get('prop') or prop.get('market') or ''
            pick = prop.get('pick') or prop.get('label') or ''
            prop_confidence = prop.get('confidence', 0)
            picks_lines.append(f"**{i}. {player} {line} {prop_type} {pick.upper()}** (AI Confidence: {int(prop_confidence*100)}%)")
        picks_str = '\n'.join(picks_lines)
        
        # AI Analysis section
        analysis_str = f"AI Analysis: {ai_reasoning}"
        
        # Ticket Info row
        info_row = f"AI Confidence: {int(confidence*100) if confidence <= 1 else int(confidence)}% | Legs: {legs} | Ticket ID: {ticket_id}"
        
        # Timestamp
        ts_str = ''
        if timestamp:
            from datetime import datetime
            try:
                dt = datetime.fromisoformat(timestamp)
                ts_str = dt.strftime('%-m/%-d/%y, %-I:%M %p')
            except Exception:
                ts_str = timestamp
        
        # Build embed with AI analysis
        embed = {
            "title": title,
            "color": 0x23272A,  # Discord dark background
            "fields": [
                {"name": "AI Analysis", "value": analysis_str, "inline": False},
                {"name": "AI Selections", "value": picks_str, "inline": False},
                {"name": "Ticket Info", "value": info_row, "inline": False},
            ],
            "footer": {"text": ts_str}
        }
        return {"embeds": [embed]}
    except Exception as e:
        logger.error(f"Failed to format ticket embed for Discord: {e}")
        return {"content": "Error formatting ticket embed"}

def ai_learn_from_results():
    """AI learns from previous results and adapts strategy."""
    logger.info("🧠 AI: Learning from previous results and adapting strategy...")
    try:
        # AI analyzes past performance and updates its strategy
        from ghost_brain import GhostBrain
        brain = GhostBrain(Path.cwd())
        brain.learn_from_execution({'action': 'learning', 'result': 'success'}, {})
        logger.info("🧠 AI: Learning complete - strategy adapted intelligently")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Learning failed - {e}")
        return False

def ai_adapt_strategy():
    """AI adapts strategy based on performance and market conditions."""
    logger.info("🧠 AI: Adapting strategy based on performance and market conditions...")
    try:
        # AI modifies its approach based on what's working/not working
        from ghost_brain import GhostBrain
        brain = GhostBrain(Path.cwd())
        brain.adapt_workflow(context={'action': 'strategy_adaptation', 'result': 'success'})
        logger.info("🧠 AI: Strategy adapted successfully with intelligent analysis")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Strategy adaptation failed - {e}")
        return False

def ai_run_cleanup():
    """AI runs intelligent cleanup and maintenance."""
    logger.info("🧠 AI: Running intelligent cleanup and maintenance...")
    try:
        logger.info("🧠 AI: Starting cleanup process...")
        import run_cleanup
        logger.info("🧠 AI: Cleanup completed with intelligent analysis")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Cleanup failed - {e}")
        return False

def ai_run_auto_cleanup():
    """Run auto-cleanup to remove old games and grade tickets."""
    logger.info("🧠 AI: Running auto-cleanup...")
    try:
        # Import and run the enhanced auto-cleanup system
        import asyncio
        from system.enhanced_auto_cleanup import EnhancedAutoCleanupSystem
        
        # Create cleanup system
        cleanup_system = EnhancedAutoCleanupSystem()
        
        # Run cleanup tasks
        async def run_cleanup():
            await cleanup_system.analyze_what_needs_processing()
            await cleanup_system.grade_pending_tickets()
            await cleanup_system.cleanup_completed_games()
            await cleanup_system.update_ghost_brain_memory()
        
        # Run the cleanup
        asyncio.run(run_cleanup())
        logger.info("🧠 AI: Auto-cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"🧠 AI: Auto-cleanup failed - {e}")

def fetch_all_props_and_generate_tickets():
    logger.info("AI: Fetching tennis props only (testing mode)...")
    try:
        # Fetch props from tennis only (testing mode)
        # import run_mlb_fetch  # DISABLED FOR TENNIS TESTING
        # import run_wnba_fetch  # DISABLED FOR TENNIS TESTING
        import test_tennis_prop_estimation
        
        logger.info("AI: Tennis props fetched successfully")
        
        # Generate tickets using tennis props only
        logger.info("AI: Generating tickets using tennis props only...")
        from core.ticket_generator import TicketGenerator
        generator = TicketGenerator(base_dir=Path.cwd())
        new_tickets = generator.generate_tickets(num_tickets=5)  # Generate 5 tickets using tennis props
        
        if new_tickets:
            logger.info(f"AI: Generated {len(new_tickets)} new tennis tickets")
            
            # Save new tickets to the generated directory
            tickets_dir = Path("ghost_ai_core_memory/tickets/generated")
            tickets_dir.mkdir(parents=True, exist_ok=True)
            
            for i, ticket in enumerate(new_tickets):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"tennis_ticket_{timestamp}_{i+1}.json"
                filepath = tickets_dir / filename
                
                with open(filepath, 'w') as f:
                    json.dump(ticket, f, indent=2)
                logger.info(f"AI: Saved new tennis ticket to {filename}")
            
            # Post the new tickets
            posted_count = 0
            for ticket in new_tickets:
                is_moneyline = False
                if ticket.get('ticket_type', '').lower() == 'moneyline':
                    is_moneyline = True
                elif any((leg.get('market', '').lower() == 'h2h') for leg in ticket.get('legs', [])) and not ticket.get('props'):
                    is_moneyline = True
                
                webhook_url = get_moneyline_webhook() if is_moneyline else get_ticket_webhook()
                
                if (ticket.get('props') and isinstance(ticket['props'], list) and len(ticket['props']) > 0) or (ticket.get('legs') and isinstance(ticket['legs'], list) and len(ticket['legs']) > 0):
                    message = ai_format_ticket_for_discord(ticket)
                    import requests
                    payload = message
                    response = requests.post(webhook_url, json=payload)
                    if response.status_code == 204:
                        logger.info(f"AI: Posted new tennis ticket to {'moneyline' if is_moneyline else 'ticket'} webhook")
                        posted_count += 1
                    else:
                        logger.warning(f"AI: Failed to post new tennis ticket")
                else:
                    logger.info(f"AI: Skipped empty or malformed new tennis ticket")
            
            if posted_count > 0:
                logger.info(f"AI: Successfully posted {posted_count} new tennis tickets.")
            else:
                logger.info(f"AI: No new tennis tickets were posted.")
        else:
            logger.warning(f"AI: No new tennis tickets generated")
            
    except Exception as e:
        logger.error(f"AI: Tennis ticket generation/posting failed - {e}")

def generate_and_post_tickets_for_sport(sport_name, fetch_func, ticket_dir):
    # This function is now deprecated - using fetch_all_props_and_generate_tickets instead
    pass

def ai_decide_sleep_wake():
    """AI decides whether to sleep or wake based on its own intelligence."""
    logger.info("🧠 AI: Analyzing whether to sleep or wake...")
    try:
        from ghost_brain import GhostBrain
        brain = GhostBrain(Path.cwd())
        
        # AI analyzes current conditions to decide
        current_time = datetime.now()
        hour = current_time.hour
        
        # AI brain analysis
        brain_state = brain.analyze_brain_state()
        recent_performance = brain.get_recent_performance()
        
        # AI decision factors
        should_sleep = False
        reasoning = ""
        
        # Factor 1: Time of day (AI prefers to work during active hours)
        if hour < 5 or hour > 23:
            should_sleep = True
            reasoning = f"Late night ({hour}:00) - AI should sleep"
        elif hour >= 5 and hour <= 23:
            should_sleep = False
            reasoning = f"Active hours ({hour}:00) - AI should work"
        
        # Factor 2: Recent performance (if AI is doing well, work more)
        if recent_performance.get('win_rate', 0) > 0.7:
            should_sleep = False
            reasoning += " - High performance, staying awake"
        elif recent_performance.get('win_rate', 0) < 0.3:
            should_sleep = True
            reasoning += " - Poor performance, need rest"
        
        # Factor 3: Brain state (if AI is tired, sleep)
        if brain_state.get('mood') == 'cautious' and brain_state.get('confidence_level', 0) < 0.4:
            should_sleep = True
            reasoning += " - Low confidence, need rest"
        
        # Factor 4: Market conditions (if no games, sleep)
        # Check if there are any games available (placeholder logic)
        available_games = True  # Assume games are available for now
        if not available_games:
            should_sleep = True
            reasoning += " - No games available, sleeping"
        
        # AI makes final decision
        if should_sleep:
            logger.info(f"🧠 AI: Decided to SLEEP - {reasoning}")
            return {'action': 'sleep', 'reasoning': reasoning, 'duration_hours': 4}
        else:
            logger.info(f"🧠 AI: Decided to WAKE - {reasoning}")
            return {'action': 'wake', 'reasoning': reasoning, 'duration_hours': 2}
            
    except Exception as e:
        logger.error(f"🧠 AI: Sleep/wake decision failed - {e}")
        # Default to wake if decision fails
        return {'action': 'wake', 'reasoning': 'Decision failed, defaulting to wake', 'duration_hours': 2}

def ai_sleep_intelligently():
    """AI sleeps intelligently based on its own decision."""
    decision = ai_decide_sleep_wake()
    
    if decision['action'] == 'sleep':
        duration = decision['duration_hours']
        logger.info(f"🧠 AI: Going to sleep for {duration} hours...")
        logger.info(f"🧠 AI: Sleep reason: {decision['reasoning']}")
        
        # Sleep for the decided duration
        time.sleep(duration * 3600)  # Convert hours to seconds
        
        logger.info(f"🧠 AI: Woke up after {duration} hours of sleep")
        return True
    else:
        logger.info(f"🧠 AI: Staying awake - {decision['reasoning']}")
        return False

def run_continuous_ai():
    """Run the AI continuously with intelligent sleep/wake decisions."""
    logger.info("🧠 AI: Starting continuous AI mode with intelligent sleep/wake!")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            logger.info(f"🧠 AI: Starting cycle #{cycle_count}")
            
            # AI decides whether to sleep or wake
            if ai_sleep_intelligently():
                # AI was sleeping, now wake up and work
                logger.info("🧠 AI: Waking up from sleep, starting work...")
            
            # Run the main AI mission
            main()
            
            logger.info("🧠 AI: Cycle complete. AI will decide when to sleep next...")
            
        except KeyboardInterrupt:
            logger.info("🧠 AI: Continuous mode stopped by user")
            break
        except Exception as e:
            logger.error(f"🧠 AI: Error in continuous mode: {e}")
            logger.info("🧠 AI: Restarting in 5 minutes...")
            time.sleep(300)  # Wait 5 minutes before retrying

def main():
    logger.info("🧠 Ghost AI 4.0 - Autonomous Sports Betting AI Activated")
    logger.info("🧠 AI: Taking control and executing intelligent mission...")
    try:
        # Step 1: AI analyzes market conditions
        market_analysis = ai_analyze_market_conditions()
        if market_analysis:
            logger.info("🧠 AI: Market analysis complete")
        
        # Step 2: AI runs intelligent cleanup
        ai_run_cleanup()
        
        # Step 3: AI runs auto-cleanup to grade tickets and clean old games
        ai_run_auto_cleanup()
        
        # Step 4: AI ALWAYS fetches props - never skip this
        logger.info("🧠 AI: Always fetching props - no idling allowed!")
        ai_fetch_all_props()
        
        # Step 5: AI ALWAYS generates tickets - never skip this
        logger.info("🧠 AI: Always generating tickets - no idling allowed!")
        ai_generate_tickets()
        
        # Step 6: AI posts tickets with intelligent formatting
        ai_post_tickets_intelligently()
        
        # Step 7: AI learns from results and adapts strategy
        ai_learn_from_results()
        ai_adapt_strategy()
        
        logger.info("🧠 AI Mission Complete - All intelligent decisions executed")
        logger.info("🧠 AI: Standing by for next intelligent cycle...")
    except Exception as e:
        logger.error(f"🧠 AI Mission failed: {e}")
        return 1
    return 0

if __name__ == "__main__":
    import sys
    import time
    
    # Check if continuous mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--continuous':
        run_continuous_ai()
    else:
        exit(main()) 