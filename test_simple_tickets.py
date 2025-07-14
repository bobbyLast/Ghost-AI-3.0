#!/usr/bin/env python3
"""
Simple test to check ticket generation
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('simple_test')

def test_simple_ticket_generation():
    """Test simple ticket generation without AI brain."""
    logger.info("=== TESTING SIMPLE TICKET GENERATION ===")
    
    # Load some props
    mlb_props_dir = Path('mlb_game_props')
    if not mlb_props_dir.exists():
        logger.error("MLB props directory not found")
        return
    
    prop_files = list(mlb_props_dir.glob('*.json'))[:2]  # Just test first 2 files
    logger.info(f"Testing with {len(prop_files)} prop files")
    
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
    
    # Filter props by confidence
    confident_props = []
    for prop in all_props:
        confidence = prop.get('confidence', 0)
        if confidence >= 0.3:  # 30% confidence threshold
            confident_props.append(prop)
    
    logger.info(f"Props with confidence >= 0.3: {len(confident_props)}")
    
    # Show some sample props
    for i, prop in enumerate(confident_props[:5]):
        logger.info(f"Sample prop {i+1}: {prop.get('player_name')} - {prop.get('prop_type')} - Confidence: {prop.get('confidence', 0):.2f}")
    
    # Generate simple tickets
    tickets = []
    used_players = set()
    
    for prop in confident_props:
        if len(tickets) >= 5:  # Limit to 5 tickets
            break
        
        player_name = prop.get('player_name', '')
        if player_name in used_players:
            continue
        
        # Create a simple 2-leg ticket
        ticket = {
            'ticket_id': f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(tickets)+1}",
            'selections': [prop],
            'confidence': prop.get('confidence', 0),
            'created_at': datetime.now().isoformat()
        }
        
        tickets.append(ticket)
        used_players.add(player_name)
    
    logger.info(f"Generated {len(tickets)} simple tickets")
    
    # Show tickets
    for i, ticket in enumerate(tickets):
        selections = ticket.get('selections', [])
        logger.info(f"Ticket {i+1}: {len(selections)} legs, confidence: {ticket.get('confidence', 0):.2f}")
        for j, selection in enumerate(selections):
            logger.info(f"  Leg {j+1}: {selection.get('player_name')} {selection.get('prop_type')}")

def main():
    """Run the simple test."""
    test_simple_ticket_generation()

if __name__ == "__main__":
    main() 