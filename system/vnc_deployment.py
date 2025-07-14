#!/usr/bin/env python3
"""
Ghost AI VNC Server Deployment Script
Handles complete startup sequence for VNC server deployment
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/vnc_deployment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VNCDeployment:
    """Handles Ghost AI deployment on VNC server"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.logs_dir = self.base_dir / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
    def run_deployment(self):
        """Run the complete deployment sequence"""
        logger.info("Starting Ghost AI VNC Deployment")
        logger.info("=" * 50)
        
        try:
            # Step 1: Environment Check
            self.check_environment()
            
            # Step 2: Auto-Cleanup
            self.run_auto_cleanup()
            
            # Step 3: Fetch Props (if needed)
            self.fetch_props_if_needed()
            
            # Step 4: Start Ghost AI
            self.start_ghost_ai()
            
            logger.info("VNC Deployment Complete!")
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}", exc_info=True)
            sys.exit(1)
    
    def check_environment(self):
        """Check if environment is ready for deployment"""
        logger.info("Checking environment...")
        
        # Check required environment variables
        required_vars = ['DISCORD_TOKEN', 'ODDS_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing environment variables: {missing_vars}")
            raise Exception("Environment not properly configured")
        
        # Check required directories
        required_dirs = [
            'mlb_props', 'wnba_props', 
            'mlb_game_props', 'wnba_game_props',
            'ghost_ai_core_memory', 'data'
        ]
        
        for dir_name in required_dirs:
            dir_path = self.base_dir / dir_name
            if not dir_path.exists():
                logger.info(f"Creating directory: {dir_name}")
                dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Environment check passed")
    
    def run_auto_cleanup(self):
        """Run auto-cleanup system"""
        logger.info("Running auto-cleanup...")
        
        try:
            result = subprocess.run(
                [sys.executable, 'auto_cleanup_system.py'],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                logger.info("Auto-cleanup completed successfully")
            else:
                logger.warning(f"Auto-cleanup had issues: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Auto-cleanup failed: {e}")
            raise
    
    def fetch_props_if_needed(self):
        """Fetch props if directories are empty"""
        logger.info("Checking props directories...")
        
        # Check MLB props
        mlb_props_dir = self.base_dir / 'mlb_props'
        if not any(mlb_props_dir.glob('*.json')):
            logger.info("MLB props directory empty, fetching...")
            self.run_script('mlb_props.py')
        
        # Check WNBA props
        wnba_props_dir = self.base_dir / 'wnba_props'
        if not any(wnba_props_dir.glob('*.json')):
            logger.info("WNBA props directory empty, fetching...")
            self.run_script('wnba_props.py')
        
        logger.info("Props check completed")
    
    def run_script(self, script_name: str):
        """Run a Python script"""
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"{script_name} completed successfully")
            else:
                logger.warning(f"{script_name} had issues: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error(f"{script_name} timed out")
        except Exception as e:
            logger.error(f"{script_name} failed: {e}")
    
    def start_ghost_ai(self):
        """Start the main Ghost AI system"""
        logger.info("Starting Ghost AI...")
        
        try:
            # Use the existing startup script
            result = subprocess.run(
                [sys.executable, 'start_ghost_ai.py'],
                capture_output=True,
                text=True,
                cwd=self.base_dir
            )
            
            if result.returncode == 0:
                logger.info("Ghost AI started successfully")
            else:
                logger.warning(f"Ghost AI startup had issues: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Ghost AI startup failed: {e}")
            raise

def main():
    """Main deployment function"""
    deployment = VNCDeployment()
    deployment.run_deployment()

if __name__ == "__main__":
    main() 