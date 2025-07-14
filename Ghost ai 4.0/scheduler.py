import schedule
import time
import subprocess
import logging
from datetime import datetime
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ghost_scheduler')

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

def run_main_job():
    logger.info(f"[SCHEDULER] 🧠 AI: Running main AI job at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # AI decides whether to sleep or wake
    decision = ai_decide_sleep_wake()
    
    if decision['action'] == 'sleep':
        duration = decision['duration_hours']
        logger.info(f"[SCHEDULER] 🧠 AI: Going to sleep for {duration} hours...")
        logger.info(f"[SCHEDULER] 🧠 AI: Sleep reason: {decision['reasoning']}")
        
        # Sleep for the decided duration
        time.sleep(duration * 3600)  # Convert hours to seconds
        
        logger.info(f"[SCHEDULER] 🧠 AI: Woke up after {duration} hours of sleep")
        return
    
    try:
        result = subprocess.run(['python', 'main.py'], capture_output=True, text=True)
        logger.info(f"[SCHEDULER] 🧠 AI: main.py output:\n{result.stdout}")
        if result.stderr:
            logger.error(f"[SCHEDULER] 🧠 AI: main.py errors:\n{result.stderr}")
    except Exception as e:
        logger.error(f"[SCHEDULER] 🧠 AI: Failed to run main.py: {e}")

# Schedule the job every 2 hours - AI will decide whether to sleep or wake
schedule.every(2).hours.do(run_main_job)

logger.info("[SCHEDULER] 🧠 AI: Ghost AI 4.0 scheduler started. AI will decide when to sleep and wake!")
logger.info("[SCHEDULER] 🧠 AI: AI has its own mind and makes intelligent decisions!")
run_main_job()  # Run once at startup

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute 