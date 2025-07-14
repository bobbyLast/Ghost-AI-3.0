"""
Elite Discord Layout for Ghost AI Tickets

This file contains the updated webhook posting functions with elite Discord formatting.
Copy these functions into your ghost_ai.py file to replace the existing _post_tickets_to_webhook function.
"""

import aiohttp
import logging
import asyncio
from datetime import datetime, timezone
from typing import List, Dict

logger = logging.getLogger(__name__)

# Rate limiting constants
WEBHOOK_DELAY = 10.0  # 10 seconds between webhook posts (increased to slow down AI)
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # 5 seconds before retry

def clean_stat_name(stat_type: str) -> str:
    """Clean stat name for display."""
    return stat_type.replace('_', ' ').title()

def get_clean_prop_display(prop_type: str, line: float) -> str:
    """
    Convert raw prop type to clean, readable display format.
    
    Args:
        prop_type: Raw prop type from API
        line: The line value for the prop
        
    Returns:
        Clean display string like "0.5 Runs" or "8.5 Points"
    """
    prop_type_lower = prop_type.lower()
    
    # MLB Props
    if 'batter_hits' in prop_type_lower:
        return f"{line} Hit{'s' if line != 1 else ''}"
    elif 'batter_runs_scored' in prop_type_lower:
        return f"{line} Run{'s' if line != 1 else ''}"
    elif 'batter_rbis' in prop_type_lower:
        return f"{line} RBI{'s' if line != 1 else ''}"
    elif 'batter_home_runs' in prop_type_lower:
        return f"{line} Home Run{'s' if line != 1 else ''}"
    elif 'batter_doubles' in prop_type_lower:
        return f"{line} Double{'s' if line != 1 else ''}"
    elif 'batter_singles' in prop_type_lower:
        return f"{line} Single{'s' if line != 1 else ''}"
    elif 'batter_walks' in prop_type_lower:
        return f"{line} Walk{'s' if line != 1 else ''}"
    elif 'batter_stolen_bases' in prop_type_lower:
        return f"{line} Stolen Base{'s' if line != 1 else ''}"
    elif 'batter_strikeouts' in prop_type_lower:
        return f"{line} Strikeout{'s' if line != 1 else ''}"
    elif 'batter_total_bases' in prop_type_lower:
        return f"{line} Total Base{'s' if line != 1 else ''}"
    elif 'batter_hits_runs_rbis' in prop_type_lower or 'hrr' in prop_type_lower:
        return f"{line} Hits + Runs + RBIs"
    elif 'batter_fantasy_score' in prop_type_lower:
        return f"{line} Fantasy Score"
    
    # Pitcher Props
    elif 'pitcher_strikeouts' in prop_type_lower:
        return f"{line} Strikeout{'s' if line != 1 else ''}"
    elif 'pitcher_hits_allowed' in prop_type_lower:
        return f"{line} Hits Allowed"
    elif 'pitcher_walks' in prop_type_lower:
        return f"{line} Walk{'s' if line != 1 else ''}"
    elif 'pitcher_earned_runs' in prop_type_lower:
        return f"{line} Earned Run{'s' if line != 1 else ''}"
    elif 'pitcher_outs' in prop_type_lower:
        return f"{line} Out{'s' if line != 1 else ''}"
    
    # WNBA Props
    elif 'player_points' in prop_type_lower:
        return f"{line} Point{'s' if line != 1 else ''}"
    elif 'player_rebounds' in prop_type_lower:
        return f"{line} Rebound{'s' if line != 1 else ''}"
    elif 'player_assists' in prop_type_lower:
        return f"{line} Assist{'s' if line != 1 else ''}"
    elif 'player_threes' in prop_type_lower:
        return f"{line} Three{'s' if line != 1 else ''}"
    elif 'player_steals' in prop_type_lower:
        return f"{line} Steal{'s' if line != 1 else ''}"
    elif 'player_blocks' in prop_type_lower:
        return f"{line} Block{'s' if line != 1 else ''}"
    elif 'player_turnovers' in prop_type_lower:
        return f"{line} Turnover{'s' if line != 1 else ''}"
    elif 'player_points_rebounds_assists' in prop_type_lower:
        return f"{line} Points + Rebounds + Assists"
    elif 'player_points_rebounds' in prop_type_lower:
        return f"{line} Points + Rebounds"
    elif 'player_points_assists' in prop_type_lower:
        return f"{line} Points + Assists"
    elif 'player_rebounds_assists' in prop_type_lower:
        return f"{line} Rebounds + Assists"
    elif 'player_fantasy_score' in prop_type_lower:
        return f"{line} Fantasy Score"
    
    # Default fallback
    else:
        return f"{line} {clean_stat_name(prop_type)}"

def determine_pick_side(pick: Dict) -> str:
    """Determine if the pick is Over or Under based on odds and confidence."""
    odds = pick.get('odds', 0)
    confidence = pick.get('confidence', 0)
    over_under = pick.get('over_under', '')
    
    # If over_under is already set to Over or Under, use it
    if over_under.upper() in ['OVER', 'UNDER']:
        return over_under.upper()
    
    # Determine based on odds (negative odds typically mean Over, positive mean Under)
    # But this can vary by sportsbook, so we'll use a more reliable method
    
    # Check if there's a pick_side field
    pick_side = pick.get('pick_side', '')
    if pick_side.upper() in ['OVER', 'UNDER']:
        return pick_side.upper()
    
    # Check if there's a selection field that indicates the side
    selection = pick.get('selection', '')
    if 'over' in selection.lower():
        return 'OVER'
    elif 'under' in selection.lower():
        return 'UNDER'
    
    # Default logic based on odds (this is a fallback)
    if odds < 0:
        return 'OVER'  # Negative odds often indicate Over
    elif odds > 0:
        return 'UNDER'  # Positive odds often indicate Under
    else:
        return 'OVER'  # Default to Over if we can't determine

async def _post_tickets_to_webhook(self, tickets: List[Dict], sport_key: str, webhook_url: str):
    """
    Post tickets to Discord webhook with elite layout and rate limiting.
    
    Args:
        tickets: List of ticket dictionaries
        sport_key: Sport key
        webhook_url: Discord webhook URL
    """
    try:
        async with aiohttp.ClientSession() as session:
            for i, ticket in enumerate(tickets):
                # Get confidence from the correct field
                ticket_confidence = ticket.get('confidence_score', ticket.get('confidence', ticket.get('total_confidence', 0)))
                
                # Skip tickets with very low confidence
                if ticket_confidence < 0.3:
                    logger.info(f"Skipping webhook ticket with low confidence: {ticket_confidence:.2%}")
                    continue
                
                # Get selections/picks from the correct field
                selections = ticket.get('selections', ticket.get('picks', []))
                if not selections:
                    logger.warning(f"No selections found in webhook ticket: {ticket.get('ticket_id', 'Unknown')}")
                    continue
                
                # Check if this is a streak ticket
                is_streak = ticket.get('streak_id') is not None or ticket.get('ticket_type') == 'streak' or 'streak' in ticket.get('title', '').lower()
                
                # Additional streak detection logic
                if not is_streak:
                    # Check if this is a 2-leg ticket that should be a streak
                    if len(selections) == 2:
                        # Check if both props have high confidence (>50%) and are from different teams
                        high_confidence_count = sum(1 for pick in selections if pick.get('confidence', 0) > 0.5)
                        teams = set(pick.get('team', '') for pick in selections if pick.get('team'))
                        
                        if high_confidence_count == 2 and len(teams) == 2:
                            is_streak = True
                            logger.info(f"🔍 Detected 2-leg streak ticket: {ticket.get('ticket_id', 'Unknown')}")
                
                # RATE LIMITING: Add delay between webhook posts
                if i > 0:  # Don't delay for the first ticket
                    logger.info(f"Rate limiting: Waiting {WEBHOOK_DELAY}s before next webhook post...")
                    await asyncio.sleep(WEBHOOK_DELAY)
                
                if is_streak:
                    # STREAK TICKET LAYOUT
                    success = await _post_streak_webhook_with_retry(session, webhook_url, ticket, selections, sport_key)
                else:
                    # NORMAL TICKET LAYOUT
                    success = await _post_normal_ticket_webhook_with_retry(session, webhook_url, ticket, selections, sport_key, ticket_confidence)
                
                if not success:
                    logger.error(f"Failed to post ticket {ticket.get('ticket_id', 'Unknown')} after all retries")
                        
    except Exception as e:
        logger.error(f"Error in _post_tickets_to_webhook: {e}", exc_info=True)

async def _post_streak_webhook_with_retry(session, webhook_url: str, ticket: Dict, selections: List[Dict], sport_key: str) -> bool:
    """Post streak ticket with retry logic for rate limiting."""
    for attempt in range(MAX_RETRIES):
        try:
            await _post_streak_webhook(session, webhook_url, ticket, selections, sport_key)
            return True
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Rate limited (429) on attempt {attempt + 1}/{MAX_RETRIES}. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Error posting streak webhook (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES - 1:
                    return False
    return False

async def _post_normal_ticket_webhook_with_retry(session, webhook_url: str, ticket: Dict, selections: List[Dict], sport_key: str, confidence: float) -> bool:
    """Post normal ticket with retry logic for rate limiting."""
    for attempt in range(MAX_RETRIES):
        try:
            await _post_normal_ticket_webhook(session, webhook_url, ticket, selections, sport_key, confidence)
            return True
        except Exception as e:
            if "429" in str(e) or "rate limit" in str(e).lower():
                wait_time = RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.warning(f"Rate limited (429) on attempt {attempt + 1}/{MAX_RETRIES}. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Error posting normal ticket webhook (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES - 1:
                    return False
    return False

async def _post_streak_webhook(session, webhook_url: str, ticket: Dict, selections: List[Dict], sport_key: str):
    """Post streak ticket with elite layout."""
    try:
        streak_id = ticket.get('streak_id', 'Unknown')
        current_step = ticket.get('current_step', 1)
        max_steps = ticket.get('max_steps', 10)
        entry_amount = ticket.get('entry_amount', 1)
        target_amount = ticket.get('target_amount', 1000)
        multiplier = ticket.get('multiplier', 1)
        
        # Create streak status line with emojis
        status_emojis = []
        for i in range(max_steps):
            if i < current_step - 1:
                result = ticket.get('results', {}).get(str(i + 1))
                if result == 'win':
                    status_emojis.append('✅')
                elif result == 'loss':
                    status_emojis.append('❌')
                else:
                    status_emojis.append('🔒')
            else:
                status_emojis.append('🔒')
        
        status_line = ''.join(status_emojis)
        
        # Create embed for streak
        embed_data = {
            "title": f"🎯 Streak to ${target_amount:,}   |   {multiplier}x",
            "description": f"**Entry:** ${entry_amount} | **Result:** {status_line}",
            "color": 0x00ff00,  # Green for streaks
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fields": []
        }
        
        # Add props field
        props_text = ""
        for pick in selections:
            player_name = pick.get('player_name', pick.get('player', 'Unknown'))
            stat_type = pick.get('prop_type', pick.get('stat', 'Unknown'))
            line = pick.get('line', 'N/A')
            clean_stat = get_clean_prop_display(stat_type, line)
            pick_side = determine_pick_side(pick)
            
            props_text += f"• **{player_name}** – {clean_stat} **{pick_side}**\n"
        
        if props_text:
            embed_data["fields"].append({
                "name": "Props:",
                "value": props_text,
                "inline": False
            })
        
        embed_data["footer"] = {
            "text": f"Streak ID: {streak_id}"
        }
        
        # Prepare webhook payload
        payload = {
            "embeds": [embed_data]
        }
        
        async with session.post(webhook_url, json=payload) as response:
            if response.status == 204:
                logger.info(f"Posted streak ticket to webhook successfully")
            elif response.status == 429:
                # Rate limited - raise exception to trigger retry
                retry_after = response.headers.get('Retry-After', RETRY_DELAY)
                logger.warning(f"Rate limited (429) by Discord. Retry-After: {retry_after}s")
                raise Exception(f"Rate limited (429) - Retry after {retry_after}s")
            else:
                logger.error(f"Streak webhook posting failed with status {response.status}")
                raise Exception(f"Webhook failed with status {response.status}")
                
    except Exception as e:
        logger.error(f"Error in _post_streak_webhook: {e}", exc_info=True)

async def _post_normal_ticket_webhook(session, webhook_url: str, ticket: Dict, selections: List[Dict], sport_key: str, confidence: float):
    """Post normal ticket with Power Play layout for 2-8 legs."""
    try:
        leg_count = len(selections)
        entry_amount = ticket.get('entry_amount', 5)
        total_odds = ticket.get('total_odds', 23.5)  # Default to 23.5x for 5-leg, adjust as needed
        potential_win = entry_amount * total_odds
        ticket_id = ticket.get('ticket_id', 'unknown')

        # Title: 🎯 [Legs]-Pick Power Play
        title = f"🎯 {leg_count}-Pick Power Play"
        
        # Description: $[entry] to win $[payout]
        description = f"${entry_amount} to win {potential_win:.2f}"

        # Numbered prop list with Over/Under in yellow
        picks_text = ""
        for i, pick in enumerate(selections, 1):
            player_name = pick.get('player_name', pick.get('player', 'Unknown'))
            stat_type = pick.get('prop_type', pick.get('stat', 'Unknown'))
            line = pick.get('line', 'N/A')
            clean_stat = get_clean_prop_display(stat_type, line)
            pick_side = determine_pick_side(pick)
            ou_text = f"**{pick_side}**"
            picks_text += f"{i}. {player_name} {clean_stat} {ou_text}\n"

        # Embed
        embed_fields = [
            {
                "name": "Picks",
                "value": picks_text,
                "inline": False
            },
            {
                "name": "Ticket Info",
                "value": f"Confidence {confidence:.0%} | Legs: {leg_count}",
                "inline": True
            },
            {
                "name": "Ticket ID",
                "value": ticket_id,
                "inline": True
            }
        ]
        # Add no-duplicate-team rule announcement if set
        if ticket.get('no_duplicate_team_rule'):
            embed_fields.append({
                "name": "",
                "value": "✅ No duplicate players from the same team in this ticket.",
                "inline": False
            })
        embed_data = {
            "title": title,
            "description": description,
            "color": 0xFFD700,  # Gold for Power Play
            "fields": embed_fields,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Send webhook
        payload = {
            "embeds": [embed_data],
            "username": "Ghost AI"
        }
        async with session.post(webhook_url, json=payload) as response:
            if response.status == 204:
                print(f"✅ Ticket posted: {title}")
                logger.info(f"Posted normal ticket to webhook successfully")
            elif response.status == 429:
                # Rate limited - raise exception to trigger retry
                retry_after = response.headers.get('Retry-After', RETRY_DELAY)
                logger.warning(f"Rate limited (429) by Discord. Retry-After: {retry_after}s")
                raise Exception(f"Rate limited (429) - Retry after {retry_after}s")
            else:
                print(f"❌ Webhook failed: {response.status}")
                logger.error(f"Normal ticket webhook posting failed with status {response.status}")
                raise Exception(f"Webhook failed with status {response.status}")
    except Exception as e:
        print(f"❌ Error posting normal ticket: {e}") 