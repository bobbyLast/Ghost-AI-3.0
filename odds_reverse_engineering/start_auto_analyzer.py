"""
Startup script for Auto Odds Analyzer
Runs alongside Ghost AI 24/7 system
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_odds_analyzer import AutoOddsAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoAnalyzerService:
    """Service wrapper for the auto odds analyzer"""
    
    def __init__(self):
        self.analyzer = AutoOddsAnalyzer()
        self.running = False
        
    async def start_service(self):
        """Start the auto analyzer service"""
        logger.info("🚀 Starting Auto Odds Analyzer Service")
        self.running = True
        
        try:
            # Start monitoring with 5-minute intervals
            await self.analyzer.start_monitoring(check_interval=300)
        except KeyboardInterrupt:
            logger.info("🛑 Received shutdown signal")
        except Exception as e:
            logger.error(f"❌ Service error: {e}", exc_info=True)
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🔄 Shutting down Auto Odds Analyzer Service")
        self.running = False
        
        # Save final analysis summary
        self.analyzer.save_analysis_summary()
        logger.info("✅ Shutdown complete")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"📡 Received signal {signum}")
    raise KeyboardInterrupt

async def main():
    """Main entry point"""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create service
    service = AutoAnalyzerService()
    
    # Start the service
    await service.start_service()

if __name__ == "__main__":
    # Ensure log directory exists
    Path("logs").mkdir(parents=True, exist_ok=True)
    
    # Run the service
    asyncio.run(main()) 