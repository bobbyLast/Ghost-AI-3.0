#!/usr/bin/env python3
"""
run_ai_forever.py - Ghost AI 4.0 Forever Runner
AI decides when to sleep and wake based on its own intelligence.
"""

import time
import logging
import subprocess
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ai_forever')

def ai_decide_sleep_wake():
    """AI decides whether to sleep or wake based on its own intelligence."""
    logger.info("🧠 AI: Analyzing whether to sleep or wake...")
    
    try:
        from ai_brain.ai_brain import AIBrain
        ai_brain = AIBrain()
        
        # AI analyzes current conditions to decide
        current_time = datetime.now()
        hour = current_time.hour
        
        # Get recent performance for AI decision making
        recent_performance = ai_brain.ghost_brain.get_recent_performance()
        
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
        
        # Factor 2: Recent performance (AI considers its performance)
        win_rate = recent_performance.get('win_rate', 0.5)
        if win_rate > 0.7:
            should_sleep = False
            reasoning += " - High performance, staying awake"
        elif win_rate < 0.3:
            should_sleep = True
            reasoning += " - Poor performance, need rest"
        
        # Factor 3: Tickets posted today (if AI has been busy, consider rest)
        tickets_today = recent_performance.get('tickets_posted_today', 0)
        if tickets_today > 10:
            should_sleep = True
            reasoning += f" - Busy day ({tickets_today} tickets), need rest"
        
        # AI makes final decision
        if should_sleep:
            logger.info(f"🧠 AI: Decided to SLEEP - {reasoning}")
            ai_brain.ghost_brain.think(f"Decided to sleep: {reasoning}")
            return {'action': 'sleep', 'reasoning': reasoning, 'duration_hours': 4}
        else:
            logger.info(f"🧠 AI: Decided to WAKE - {reasoning}")
            ai_brain.ghost_brain.think(f"Decided to wake: {reasoning}")
            return {'action': 'wake', 'reasoning': reasoning, 'duration_hours': 2}
            
    except Exception as e:
        logger.error(f"🧠 AI: Sleep/wake decision failed - {e}")
        # Default to wake if decision fails
        return {'action': 'wake', 'reasoning': 'Decision failed, defaulting to wake', 'duration_hours': 2}

def run_ai_cycle():
    """Run one complete AI cycle."""
    logger.info(f"🧠 AI: Starting AI cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)
        logger.info(f"🧠 AI: Cycle output:\n{result.stdout}")
        if result.stderr:
            logger.error(f"🧠 AI: Cycle errors:\n{result.stderr}")
        return True
    except Exception as e:
        logger.error(f"🧠 AI: Cycle failed: {e}")
        return False

def main():
    logger.info("🧠 AI: Ghost AI 4.0 Forever Runner Started")
    logger.info("🧠 AI: AI will decide when to sleep and wake based on its own intelligence!")
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            logger.info(f"🧠 AI: Starting cycle #{cycle_count}")
            
            # AI decides whether to sleep or wake
            decision = ai_decide_sleep_wake()
            
            if decision['action'] == 'sleep':
                duration = decision['duration_hours']
                logger.info(f"🧠 AI: Going to sleep for {duration} hours...")
                logger.info(f"🧠 AI: Sleep reason: {decision['reasoning']}")
                
                # Sleep for the decided duration
                time.sleep(duration * 3600)  # Convert hours to seconds
                
                logger.info(f"🧠 AI: Woke up after {duration} hours of sleep")
            
            # Run AI cycle
            success = run_ai_cycle()
            
            if success:
                logger.info(f"🧠 AI: Cycle #{cycle_count} completed successfully")
            else:
                logger.error(f"🧠 AI: Cycle #{cycle_count} failed")
            
            logger.info("🧠 AI: Cycle complete. AI will decide when to sleep next...")
            
        except KeyboardInterrupt:
            logger.info("🧠 AI: Forever runner stopped by user")
            break
        except Exception as e:
            logger.error(f"🧠 AI: Error in forever runner: {e}")
            logger.info("🧠 AI: Restarting in 5 minutes...")
            time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main() 