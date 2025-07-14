#!/usr/bin/env python3
"""
Test file to debug ticket generation issues
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_tickets')

def test_prop_loading():
    """Test if props are being loaded correctly."""
    logger.info("=== TESTING PROP LOADING ===")
    
    # Check MLB props
    mlb_props_dir = Path('mlb_game_props')
    if mlb_props_dir.exists():
        prop_files = list(mlb_props_dir.glob('*.json'))
        logger.info(f"Found {len(prop_files)} MLB prop files")
        
        total_props = 0
        for prop_file in prop_files:
            try:
                with open(prop_file, 'r') as f:
                    data = json.load(f)
                props = data.get('props', [])
                total_props += len(props)
                logger.info(f"  {prop_file.name}: {len(props)} props")
                
                # Show first few props
                for i, prop in enumerate(props[:3]):
                    logger.info(f"    Prop {i+1}: {prop.get('player_name', 'Unknown')} - {prop.get('prop_type', 'Unknown')} - Confidence: {prop.get('confidence', 0):.2f}")
                    
            except Exception as e:
                logger.error(f"Error loading {prop_file}: {e}")
        
        logger.info(f"Total MLB props: {total_props}")
    else:
        logger.warning("MLB props directory not found")
    
    # Check WNBA props
    wnba_props_dir = Path('wnba_game_props')
    if wnba_props_dir.exists():
        prop_files = list(wnba_props_dir.glob('*.json'))
        logger.info(f"Found {len(prop_files)} WNBA prop files")
        
        total_props = 0
        for prop_file in prop_files:
            try:
                with open(prop_file, 'r') as f:
                    data = json.load(f)
                props = data.get('props', [])
                total_props += len(props)
                logger.info(f"  {prop_file.name}: {len(props)} props")
                
                # Show first few props
                for i, prop in enumerate(props[:3]):
                    logger.info(f"    Prop {i+1}: {prop.get('player_name', 'Unknown')} - {prop.get('prop_type', 'Unknown')} - Confidence: {prop.get('confidence', 0):.2f}")
                    
            except Exception as e:
                logger.error(f"Error loading {prop_file}: {e}")
        
        logger.info(f"Total WNBA props: {total_props}")
    else:
        logger.warning("WNBA props directory not found")

def test_confidence_filtering():
    """Test confidence filtering logic."""
    logger.info("\n=== TESTING CONFIDENCE FILTERING ===")
    
    # Create test props with different confidence levels
    test_props = [
        {'player_name': 'Test Player 1', 'prop_type': 'Hits', 'confidence': 0.05, 'odds': 100},
        {'player_name': 'Test Player 2', 'prop_type': 'Runs', 'confidence': 0.15, 'odds': 150},
        {'player_name': 'Test Player 3', 'prop_type': 'RBIs', 'confidence': 0.25, 'odds': 200},
        {'player_name': 'Test Player 4', 'prop_type': 'Home Runs', 'confidence': 0.35, 'odds': 250},
        {'player_name': 'Test Player 5', 'prop_type': 'Strikeouts', 'confidence': 0.45, 'odds': 300},
    ]
    
    confidence_thresholds = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
    
    for threshold in confidence_thresholds:
        filtered_props = []
        for prop in test_props:
            confidence = prop.get('confidence', 0)
            if confidence >= threshold:
                filtered_props.append(prop)
        
        logger.info(f"Threshold {threshold:.2f}: {len(filtered_props)} props pass")

def test_ticket_generation():
    """Test basic ticket generation logic."""
    logger.info("\n=== TESTING TICKET GENERATION ===")
    
    # Create test props
    test_props = [
        {'player_name': 'Player A', 'prop_type': 'Hits', 'confidence': 0.25, 'odds': 100, 'line': 1.5, 'pick_side': 'OVER'},
        {'player_name': 'Player B', 'prop_type': 'Runs', 'confidence': 0.30, 'odds': 150, 'line': 0.5, 'pick_side': 'OVER'},
        {'player_name': 'Player C', 'prop_type': 'RBIs', 'confidence': 0.35, 'odds': 200, 'line': 0.5, 'pick_side': 'OVER'},
        {'player_name': 'Player D', 'prop_type': 'Home Runs', 'confidence': 0.40, 'odds': 250, 'line': 0.5, 'pick_side': 'OVER'},
        {'player_name': 'Player E', 'prop_type': 'Strikeouts', 'confidence': 0.45, 'odds': 300, 'line': 5.5, 'pick_side': 'OVER'},
    ]
    
    # Test different batch sizes
    batch_sizes = [2, 3, 4, 5]
    
    for batch_size in batch_sizes:
        logger.info(f"\nTesting batch size {batch_size}:")
        
        # Simple combination generation
        if len(test_props) >= batch_size:
            # Create one combination
            combo = test_props[:batch_size]
            
            # Calculate ticket confidence
            confidences = [prop.get('confidence', 0) for prop in combo]
            avg_confidence = sum(confidences) / len(confidences)
            
            # Apply leg penalty
            leg_penalty = (batch_size - 2) * 0.05
            final_confidence = max(0.1, avg_confidence - leg_penalty)
            
            logger.info(f"  Combination: {[prop['player_name'] for prop in combo]}")
            logger.info(f"  Individual confidences: {[f'{c:.2f}' for c in confidences]}")
            logger.info(f"  Average confidence: {avg_confidence:.2f}")
            logger.info(f"  Leg penalty: {leg_penalty:.2f}")
            logger.info(f"  Final confidence: {final_confidence:.2f}")
            
            # Check if it passes basic validation
            if final_confidence >= 0.25:
                logger.info(f"  ✅ PASSES validation")
            else:
                logger.info(f"  ❌ FAILS validation (confidence too low)")

def test_ai_brain_integration():
    """Test AI brain integration."""
    logger.info("\n=== TESTING AI BRAIN INTEGRATION ===")
    
    try:
        from ghost_ai_core_memory.ghost_brain import create_ghost_brain
        
        base_dir = Path('.')
        ghost_brain = create_ghost_brain(base_dir)
        
        # Test AI objectives
        objectives = ghost_brain.get_ai_objectives()
        logger.info(f"AI Objectives: {objectives}")
        
        # Test strategy
        strategy = ghost_brain.get_strategy_engine()
        logger.info(f"Strategy: {strategy}")
        
        # Test with sample props
        sample_props = [
            {'player_name': 'Test Player', 'prop_type': 'Hits', 'confidence': 0.25, 'odds': 100},
            {'player_name': 'Test Player 2', 'prop_type': 'Runs', 'confidence': 0.30, 'odds': 150},
        ]
        
        # Test intelligent analysis
        intelligent_props = ghost_brain.analyze_props_intelligently(sample_props)
        logger.info(f"Intelligent analysis result: {len(intelligent_props)} props")
        
        for i, prop in enumerate(intelligent_props):
            logger.info(f"  Prop {i+1}: {prop.get('player_name')} - Confidence: {prop.get('confidence', 0):.2f}")
        
    except Exception as e:
        logger.error(f"Error testing AI brain: {e}")

def main():
    """Run all tests."""
    logger.info("Starting ticket generation debugging tests...")
    
    test_prop_loading()
    test_confidence_filtering()
    test_ticket_generation()
    test_ai_brain_integration()
    
    logger.info("\n=== DEBUGGING COMPLETE ===")

if __name__ == "__main__":
    main() 