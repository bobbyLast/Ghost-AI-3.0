#!/usr/bin/env python3
"""
Simple script to generate and post tickets directly
"""

import json
import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime
import discord
from discord_integration.elite_webhook_layout import _post_tickets_to_webhook

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple_post')

def calculate_real_confidence(selections):
    """Calculate real confidence based on odds and historical factors."""
    total_confidence = 0.0
    
    for selection in selections:
        odds = selection.get('odds', 0)
        prop_type = selection.get('prop_type', '')
        
        # Calculate implied probability from odds
        if odds > 0:
            implied_prob = 100 / (odds + 100)
        else:
            implied_prob = abs(odds) / (abs(odds) + 100)
        
        # Adjust confidence based on prop type difficulty
        if prop_type == 'HRR':
            # HRR is harder to hit, so adjust down
            adjusted_prob = implied_prob * 0.85
        elif prop_type == 'Home Runs':
            # Home runs are very hard, adjust down more
            adjusted_prob = implied_prob * 0.70
        elif prop_type == 'Strikeouts':
            # Strikeouts are more predictable
            adjusted_prob = implied_prob * 1.1
        else:
            adjusted_prob = implied_prob
        
        # Cap at reasonable levels
        adjusted_prob = min(0.85, max(0.15, adjusted_prob))
        total_confidence += adjusted_prob
    
    # Average confidence across all selections
    avg_confidence = total_confidence / len(selections)
    
    # Apply multi-leg penalty (more legs = harder to hit)
    leg_penalty = (len(selections) - 2) * 0.05
    final_confidence = max(0.20, avg_confidence - leg_penalty)
    
    return final_confidence

def calculate_ticket_odds(selections):
    """Calculate real betting odds and potential winnings for a ticket."""
    bet_amount = 5  # $5 bet
    
    # Calculate total odds (multiply all individual odds)
    total_odds = 1.0
    for selection in selections:
        odds = selection.get('odds', 0)
        if odds > 0:
            # Convert American odds to decimal
            decimal_odds = (odds + 100) / 100
        else:
            # Convert negative American odds to decimal
            decimal_odds = (abs(odds) + 100) / abs(odds)
        
        total_odds *= decimal_odds
    
    # Calculate potential winnings
    potential_win = bet_amount * total_odds
    
    return bet_amount, potential_win, total_odds

def generate_simple_tickets():
    """Generate simple tickets from props."""
    logger.info("Generating simple tickets...")
    
    # Load props
    mlb_props_dir = Path('mlb_game_props')
    if not mlb_props_dir.exists():
        logger.error("MLB props directory not found")
        return []
    
    prop_files = list(mlb_props_dir.glob('*.json'))[:3]  # Use first 3 files
    logger.info(f"Loading props from {len(prop_files)} files...")
    
    all_props = []
    for prop_file in prop_files:
        try:
            with open(prop_file, 'r') as f:
                data = json.load(f)
            props = data.get('props', [])
            all_props.extend(props)
            logger.info(f"Loaded {len(props)} props from {prop_file.name}")
        except Exception as e:
            logger.error(f"Error loading {prop_file}: {e}")
    
    logger.info(f"Total props loaded: {len(all_props)}")
    
    # Convert "Hits" to "HRR" and filter by confidence
    confident_props = []
    for prop in all_props:
        # Convert Hits to HRR
        if prop.get('prop_type') == 'Hits':
            prop['prop_type'] = 'HRR'
        
        # Calculate real confidence based on odds
        odds = prop.get('odds', 0)
        if odds > 0:
            implied_prob = 100 / (odds + 100)
        else:
            implied_prob = abs(odds) / (abs(odds) + 100)
        
        # Use real confidence instead of the stored confidence
        prop['confidence'] = implied_prob
        
        if implied_prob >= 0.35:  # 35% implied probability threshold
            confident_props.append(prop)
    
    logger.info(f"Props with real confidence >= 0.35: {len(confident_props)}")
    
    # Generate multi-leg tickets
    tickets = []
    used_players = set()
    
    # Create 3-leg tickets
    for i in range(0, len(confident_props) - 2, 3):
        if len(tickets) >= 5:  # Limit to 5 tickets
            break
        
        # Get 3 props for this ticket
        ticket_props = confident_props[i:i+3]
        
        # Check for duplicate players
        players = [prop.get('player_name', '') for prop in ticket_props]
        if len(players) != len(set(players)):  # Has duplicates
            continue
        
        # Check if any player already used
        if any(player in used_players for player in players):
            continue
        
        # Calculate real confidence based on odds and prop types
        real_confidence = calculate_real_confidence(ticket_props)
        
        # Calculate real betting odds and winnings
        bet_amount, potential_win, total_odds = calculate_ticket_odds(ticket_props)
        
        # Create ticket
        ticket = {
            'ticket_id': f"s_{int(datetime.now().timestamp())}_{len(tickets)+1}",
            'selections': ticket_props,
            'confidence': real_confidence,
            'created_at': datetime.now().isoformat(),
            'legs': len(ticket_props),
            'bet_amount': bet_amount,
            'potential_win': potential_win,
            'total_odds': total_odds
        }
        
        tickets.append(ticket)
        
        # Mark players as used
        for player in players:
            used_players.add(player)
    
    logger.info(f"Generated {len(tickets)} multi-leg tickets")
    return tickets

def get_underdog_payout(legs, bet_amount=5):
    payout_table = {2: 3, 3: 6, 4: 10, 5: 20}
    multiplier = payout_table.get(legs, 0)
    return bet_amount * multiplier if multiplier else 0

async def post_tickets_to_discord(tickets):
    """Post tickets to the tickets Discord webhook using elite layout."""
    webhook_url = os.getenv('DISCORD_TICKETS_WEBHOOK')
    if not webhook_url:
        print("No tickets webhook URL found - skipping posting")
        return
    # Use MLB as sport_key for now; adjust as needed
    sport_key = 'MLB'
    await _post_tickets_to_webhook(None, tickets, sport_key, webhook_url)
    print("✅ All tickets posted to Discord!")

async def main():
    """Main function."""
    logger.info("=== SIMPLE TICKET POSTING ===")
    
    # Generate tickets
    tickets = generate_simple_tickets()
    
    if len(tickets) == 0:
        logger.error("No tickets generated - stopping")
        return
    
    # Show tickets
    for i, ticket in enumerate(tickets):
        selections = ticket.get('selections', [])
        logger.info(f"Ticket {i+1}: {len(selections)} legs, confidence: {ticket.get('confidence', 0):.2f}")
        for j, selection in enumerate(selections):
            logger.info(f"  Leg {j+1}: {selection.get('player_name')} {selection.get('prop_type')}")
    
    # Post to Discord
    await post_tickets_to_discord(tickets)

if __name__ == "__main__":
    asyncio.run(main()) 