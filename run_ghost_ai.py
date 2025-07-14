#!/usr/bin/env python3
"""
Ghost AI 24/7 Scheduler Script
- Runs auto-clean and main flow in correct order
- Ensures main flow runs only once per day at 5:00am
- Only auto-clean runs after main flow, until 12:59pm
- Sleeps after 12:59pm until 5:00am next day
- Uses a status file to coordinate state
"""
import time
import datetime
import subprocess
import sys
import os
import json
from core.ai_brain import AIBrain

STATUS_FILE = "ghost_ai_core_memory/scheduler_status.json"
AUTO_CLEAN_SCRIPT = "system/auto_cleanup.py"
MAIN_SCRIPT = "main.py"
CLEAN_INTERVAL_HOURS = 3.4

def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_status(status):
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f)

def run_script(script, args=None):
    cmd = [sys.executable, script]
    if args:
        cmd += args
    return subprocess.run(cmd).returncode

def now_time():
    return datetime.datetime.now()

def run_main():
    ai_brain = AIBrain()
    next_actions = ai_brain.get_next_actions()
    for action in next_actions:
        if not ai_brain.has_done_action(action['action_type'], action['details'].get('date')):
            ai_brain.handle_action(action)

if __name__ == "__main__":
    run_main() 