#!/usr/bin/env python3
"""
ghost_ai_orchestrator.py - Ghost AI 3.0 Enhanced Orchestrator
Orchestrates daily picks, streaks, and tickets with proper separation.
"""

import logging
from core.ai_brain import AIBrain

logger = logging.getLogger('ghost_ai_orchestrator')

def main():
    ai_brain = AIBrain()
    next_actions = ai_brain.get_next_actions()
    for action in next_actions:
        if not ai_brain.has_done_action(action['action_type'], action['details'].get('date')):
            ai_brain.handle_action(action)

if __name__ == '__main__':
    main() 