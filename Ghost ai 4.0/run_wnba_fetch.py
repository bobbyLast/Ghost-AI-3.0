#!/usr/bin/env python3
"""
Ghost AI 4.0 WNBA Fetch Script
Runs WNBA player props fetch with AI integration.
"""

import asyncio
import sys
import os
from datetime import datetime

# Dynamically add parent directory to sys.path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

async def main():
    """Run WNBA fetch with AI integration."""
    try:
        # Import the function directly
        from sports.wnba.wnba_props import fetch_wnba_player_props
        from ai_brain.ai_brain import AIBrain
        
        # Initialize AI Brain
        ai_brain = AIBrain()
        
        # Use command line argument for date, or default to tomorrow
        if len(sys.argv) > 1:
            target_date = sys.argv[1]
        else:
            from datetime import timedelta
            target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🤖 Ghost AI 4.0 WNBA Fetch System")
        print(f"🔄 Starting WNBA fetch for {target_date}...")
        
        # Log the action with AI
        ai_brain.log_action('fetch_props', {
            'sport': 'WNBA',
            'date': target_date,
            'type': 'player_props'
        })
        
        # Run the fetch
        await fetch_wnba_player_props(target_date)
        
        # AI analysis of fetched data
        print("🤖 AI analyzing WNBA data...")
        ai_brain.ghost_brain.think(f"WNBA player props fetched for {target_date}")
        
        print("✅ WNBA fetch completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during WNBA fetch: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 