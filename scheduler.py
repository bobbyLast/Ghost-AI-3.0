import schedule
import time
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ghost_scheduler')

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