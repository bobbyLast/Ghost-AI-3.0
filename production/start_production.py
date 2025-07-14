#!/usr/bin/env python3
"""
Ghost AI 3.0 Production Startup Script

Launches the 24/7 autonomous production system with all components.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/production_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('production.startup')

async def main():
    """Main production startup function."""
    try:
        logger.info("Starting Ghost AI 3.0 Production System...")
        
        # Check environment variables
        required_vars = ['ODDS_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.error("Please set these in your .env file")
            return False
        
        # Check Discord token (optional but recommended)
        discord_token = os.getenv('DISCORD_TOKEN')
        if discord_token:
            logger.info("Discord token found - Discord integration enabled")
        else:
            logger.warning("No Discord token found - Discord features will be disabled")
        
        # Import and start production orchestrator (simple version)
        from production_orchestrator_simple import ProductionOrchestrator
        
        orchestrator = ProductionOrchestrator()
        await orchestrator.main_loop()
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Production startup interrupted by user")
        return True
    except Exception as e:
        logger.error(f"Production startup failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        logger.info("Production system shutdown complete")
    else:
        logger.error("Production system failed to start")
        sys.exit(1) 