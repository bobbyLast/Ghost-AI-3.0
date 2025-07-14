#!/usr/bin/env python3
"""
run_ai_forever.py - Ghost AI 4.0 Forever Runner
AI decides when to sleep and wake based on its own intelligence.
"""

import time
import logging
import subprocess
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ai_forever')

def ai_decide_sleep_wake():
    """AI decides whether to sleep or wake based on its own intelligence."""
    logger.info("🧠 AI: Analyzing whether to sleep or wake...")
    
    # AI analyzes current conditions to decide
    current_time = datetime.now()
    hour = current_time.hour
    
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
    
    # Factor 2: Recent performance (placeholder - would check actual performance)
    # For now, assume good performance during active hours
    if hour >= 5 and hour <= 23:
        should_sleep = False
        reasoning += " - Active hours, staying awake"
    
    # AI makes final decision
    if should_sleep:
        logger.info(f"🧠 AI: Decided to SLEEP - {reasoning}")
        return {'action': 'sleep', 'reasoning': reasoning, 'duration_hours': 4}
    else:
        logger.info(f"🧠 AI: Decided to WAKE - {reasoning}")
        return {'action': 'wake', 'reasoning': reasoning, 'duration_hours': 2}

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