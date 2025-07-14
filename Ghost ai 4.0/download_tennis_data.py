#!/usr/bin/env python3
"""
Download Comprehensive Tennis Data
Downloads and stores all tennis data locally for reliable access
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path.cwd()))

from tennis_local_data_manager import TennisLocalDataManager
from tennis_local_engine import TennisLocalEngine

def download_tennis_data():
    """Download comprehensive tennis data."""
    print("🎾 Downloading Comprehensive Tennis Data")
    print("=" * 50)
    
    # Initialize data manager
    manager = TennisLocalDataManager()
    
    # Check if API key is available
    if not manager.api_key:
        print("❌ No tennis API key found!")
        print("Please set TENNIS_API_KEY environment variable")
        return False
    
    print("✅ API key found, starting download...")
    
    # Download data for next 30 days
    try:
        manager.download_all_tennis_data(days_ahead=30)
        
        # Show summary
        summary = manager.get_data_summary()
        print("\n📊 Download Summary:")
        print(f"   Players: {summary['players']}")
        print(f"   Matches: {summary['matches']}")
        print(f"   H2H Records: {summary['h2h']}")
        print(f"   Odds Data: {summary['odds']}")
        print(f"   Tournaments: {summary['tournaments']}")
        print(f"   Total Size: {summary['total_size_mb']} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

def test_local_engine():
    """Test the local tennis engine."""
    print("\n🧪 Testing Local Tennis Engine")
    print("=" * 40)
    
    try:
        engine = TennisLocalEngine()
        
        # Get engine status
        status = engine.get_engine_status()
        print(f"Status: {status['status']}")
        print(f"Star Players: {status['star_players_loaded']}")
        print(f"Data Size: {status['data_summary']['total_size_mb']} MB")
        
        # Generate picks for today
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        picks = engine.generate_daily_tennis_picks(today)
        
        print(f"\n🎯 Generated {len(picks)} picks for {today}:")
        for i, pick in enumerate(picks[:5], 1):  # Show first 5 picks
            print(f"{i}. {pick['player']} - {pick['prop']} {pick['line']} {pick['pick']} ({pick['confidence']:.0%})")
        
        return True
        
    except Exception as e:
        print(f"❌ Engine test failed: {e}")
        return False

def main():
    """Main function."""
    print("🎾 Tennis Data Download & Local Engine Setup")
    print("=" * 60)
    
    # Step 1: Download data
    print("\n📥 Step 1: Downloading Tennis Data")
    download_success = download_tennis_data()
    
    if not download_success:
        print("❌ Data download failed, cannot proceed")
        return
    
    # Step 2: Test local engine
    print("\n🧪 Step 2: Testing Local Engine")
    engine_success = test_local_engine()
    
    if engine_success:
        print("\n✅ Setup Complete!")
        print("🎾 Your tennis data is now stored locally")
        print("🎯 The local engine can generate picks without API calls")
        print("📊 Data will be automatically updated when you run this script again")
    else:
        print("\n❌ Engine test failed")
        print("Please check the data download and try again")

if __name__ == "__main__":
    main() 