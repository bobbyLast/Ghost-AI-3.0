#!/usr/bin/env python3
"""
Ghost AI Pipeline with AI Brain Integration

This pipeline now uses the Ghost Brain AI system to:
- Eliminate duplicate tickets completely
- Use historical data for intelligent decisions
- Prevent re-posting the same tickets
- Make smart confidence adjustments
- Learn from player performance
"""

import logging
from core.ai_brain import AIBrain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/GhostAI.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GhostAI")

def main():
    ai_brain = AIBrain()
    next_actions = ai_brain.get_next_actions()
    for action in next_actions:
        if not ai_brain.has_done_action(action['action_type'], action['details'].get('date')):
            ai_brain.handle_action(action)

if __name__ == '__main__':
    main() 