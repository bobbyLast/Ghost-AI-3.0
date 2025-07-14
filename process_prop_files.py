#!/usr/bin/env python3
"""
Process raw prop files into the expected format
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('process_props')

def extract_prop_data(game_data: Dict) -> List[Dict]:
    """Extract prop data from game odds"""
    props = []
    
    # Market mappings for prop types
    market_mappings = {
        'batter_hits': 'Hits',
        'batter_runs': 'Runs', 
        'batter_rbis': 'RBIs',
        'batter_home_runs': 'Home Runs',
        'batter_strikeouts': 'Strikeouts',
        'batter_walks': 'Walks',
        'batter_doubles': 'Doubles',
        'batter_triples': 'Triples',
        'batter_total_bases': 'Total Bases',
        'pitcher_strikeouts': 'Strikeouts',
        'pitcher_walks': 'Walks',
        'pitcher_hits_allowed': 'Hits Allowed',
        'pitcher_earned_runs': 'Earned Runs',
        'pitcher_innings_pitched': 'Innings Pitched',
        'player_points': 'Points',
        'player_rebounds': 'Rebounds',
        'player_assists': 'Assists',
        'player_fantasy_score': 'Fantasy Score'
    }
    
    for bookmaker in game_data.get('bookmakers', []):
        if bookmaker.get('key') != 'fanduel':  # Focus on FanDuel
            continue
            
        for market in bookmaker.get('markets', []):
            market_key = market.get('key', '')
            
            # Only process player prop markets
            if market_key not in market_mappings:
                continue
            
            for outcome in market.get('outcomes', []):
                # Calculate confidence based on odds - FIXED CALCULATION
                odds = outcome.get('price', 0)
                if odds > 0:
                    # For positive odds, use a more reasonable calculation
                    confidence = min(0.8, max(0.3, 100 / (odds + 100)))
                else:
                    # For negative odds, use a more reasonable calculation
                    confidence = min(0.8, max(0.3, abs(odds) / (abs(odds) + 100)))
                
                prop_data = {
                    'player_name': outcome.get('description', ''),
                    'prop_type': market_mappings.get(market_key, market_key),
                    'line': outcome.get('point', 0),
                    'pick_side': outcome.get('name', '').lower(),  # 'over' or 'under'
                    'odds': outcome.get('price', 0),
                    'confidence': confidence,
                    'sport': 'MLB' if 'batter_' in market_key or 'pitcher_' in market_key else 'WNBA',
                    'game_key': game_data.get('id', ''),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'timestamp': datetime.now().isoformat()
                }
                props.append(prop_data)
    
    return props

def process_mlb_props():
    """Process MLB prop files."""
    logger.info("Processing MLB prop files...")
    
    mlb_props_dir = Path('mlb_game_props')
    if not mlb_props_dir.exists():
        logger.warning("MLB props directory not found")
        return
    
    prop_files = list(mlb_props_dir.glob('*.json'))
    logger.info(f"Found {len(prop_files)} MLB prop files")
    
    total_props = 0
    for prop_file in prop_files:
        try:
            with open(prop_file, 'r') as f:
                game_data = json.load(f)
            
            # Extract props from raw data
            props = extract_prop_data(game_data)
            
            # Update the file with processed props
            game_data['props'] = props
            
            # Save back to file
            with open(prop_file, 'w') as f:
                json.dump(game_data, f, indent=2)
            
            total_props += len(props)
            logger.info(f"  {prop_file.name}: {len(props)} props processed")
            
        except Exception as e:
            logger.error(f"Error processing {prop_file}: {e}")
    
    logger.info(f"Total MLB props processed: {total_props}")

def process_wnba_props():
    """Process WNBA prop files."""
    logger.info("Processing WNBA prop files...")
    
    wnba_props_dir = Path('wnba_game_props')
    if not wnba_props_dir.exists():
        logger.warning("WNBA props directory not found")
        return
    
    prop_files = list(wnba_props_dir.glob('*.json'))
    logger.info(f"Found {len(prop_files)} WNBA prop files")
    
    total_props = 0
    for prop_file in prop_files:
        try:
            with open(prop_file, 'r') as f:
                game_data = json.load(f)
            
            # Extract props from raw data
            props = extract_prop_data(game_data)
            
            # Update the file with processed props
            game_data['props'] = props
            
            # Save back to file
            with open(prop_file, 'w') as f:
                json.dump(game_data, f, indent=2)
            
            total_props += len(props)
            logger.info(f"  {prop_file.name}: {len(props)} props processed")
            
        except Exception as e:
            logger.error(f"Error processing {prop_file}: {e}")
    
    logger.info(f"Total WNBA props processed: {total_props}")

def main():
    """Process all prop files."""
    logger.info("Starting prop file processing...")
    
    process_mlb_props()
    process_wnba_props()
    
    logger.info("Prop file processing complete!")

if __name__ == "__main__":
    main() 