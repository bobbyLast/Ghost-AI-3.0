#!/usr/bin/env python3
"""
Direct MLB Fetch Script
Runs MLB player props fetch without circular import issues.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Run MLB fetch directly."""
    try:
        # Import the function directly
        from sports.mlb.mlb_props import fetch_mlb_player_props
        
        # Use command line argument for date, or default to tomorrow
        if len(sys.argv) > 1:
            target_date = sys.argv[1]
        else:
            from datetime import timedelta
            target_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        print(f"🔄 Starting MLB fetch for {target_date}...")
        
        # Run the fetch
        await fetch_mlb_player_props(target_date)
        
        print("✅ MLB fetch completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during MLB fetch: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 