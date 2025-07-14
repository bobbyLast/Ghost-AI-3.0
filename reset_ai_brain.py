#!/usr/bin/env python3
"""
Reset AI brain memory to allow fresh processing
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('reset_brain')

def reset_ai_brain_memory():
    """Reset AI brain memory files."""
    logger.info("Resetting AI brain memory...")
    
    # Clear daily learning
    daily_learning_file = Path('ghost_ai_core_memory/daily_learning.json')
    if daily_learning_file.exists():
        daily_learning_file.unlink()
        logger.info("Cleared daily learning memory")
    
    # Clear prop cache
    prop_cache_file = Path('ghost_ai_core_memory/prop_cache.json')
    if prop_cache_file.exists():
        prop_cache_file.unlink()
        logger.info("Cleared prop cache")
    
    # Clear confidence cache
    confidence_cache_file = Path('ghost_ai_core_memory/confidence_cache.json')
    if confidence_cache_file.exists():
        confidence_cache_file.unlink()
        logger.info("Cleared confidence cache")
    
    # Clear ticket memory
    ticket_memory_file = Path('ghost_ai_core_memory/ticket_memory.json')
    if ticket_memory_file.exists():
        ticket_memory_file.unlink()
        logger.info("Cleared ticket memory")
    
    # Clear player history
    player_history_file = Path('ghost_ai_core_memory/player_history.json')
    if player_history_file.exists():
        player_history_file.unlink()
        logger.info("Cleared player history")
    
    logger.info("AI brain memory reset complete!")

def main():
    """Reset all AI brain memory."""
    reset_ai_brain_memory()

if __name__ == "__main__":
    main() 