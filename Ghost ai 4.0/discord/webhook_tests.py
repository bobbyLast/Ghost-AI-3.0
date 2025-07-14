#!/usr/bin/env python3
"""
Discord Webhook Tests - Consolidated testing module for Discord integration
"""

import requests
import json
import datetime
import asyncio
import aiohttp
from typing import Dict, List
from datetime import timezone
import os

# Webhook URL (should be moved to config)
WEBHOOK_URL = os.getenv('DISCORD_TICKETS_WEBHOOK', '')

def clean_stat_name(stat_type: str) -> str:
    """Clean stat name for display."""
    return stat_type.replace('_', ' ').title()

def test_simple_webhook():
    """Test the webhook with a simple message."""
    print("🎯 Testing Simple Webhook...")
    
    payload = {
        "content": "🧪 **TEST MESSAGE** - Ghost AI 3.0 Tickets Webhook is working!",
        "username": "Ghost AI 3.0"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print("✅ Simple webhook test successful!")
            print("   Check your Discord tickets channel for the test message")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")

def test_ticket_webhook():
    """Test the webhook with a sample ticket."""
    print("🎯 Testing Ticket Webhook...")
    
    # Sample ticket data
    selections = [
        {
            "player_name": "Paige Bueckers",
            "prop_type": "Player Threes",
            "line": 1.5,
            "confidence": 0.688
        },
        {
            "player_name": "Marina Mabrey", 
            "prop_type": "Player Threes",
            "line": 1.5,
            "confidence": 0.667
        },
        {
            "player_name": "Jewell Loyd",
            "prop_type": "Player Threes", 
            "line": 1.5,
            "confidence": 0.658
        },
        {
            "player_name": "Caitlin Clark",
            "prop_type": "Player Threes",
            "line": 3.5,
            "confidence": 0.658
        }
    ]
    
    # Create embed
    embed = {
        "title": "🎯 **TEST TICKET**",
        "description": "**4-Leg Test Ticket**",
        "color": 0x00ff00,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "fields": []
    }
    
    for i, pick in enumerate(selections, 1):
        embed["fields"].append({
            "name": f"Leg {i}",
            "value": f"**{pick['player_name']}**\n{pick['prop_type']} {pick['line']}\nConfidence: {pick['confidence']:.1%}",
            "inline": True
        })
    
    payload = {
        "content": "🧪 **TEST MESSAGE** - Tickets webhook is working!",
        "username": "Ghost AI 3.0",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print("✅ Ticket webhook test successful!")
            print("   Check your Discord tickets channel for the test ticket")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")

def test_streak_webhook():
    """Test the webhook with a sample Underdog-style streak."""
    print("🔥 Testing Streak Webhook...")
    
    # Create a sample streak with progress
    current_step = 3
    max_steps = 11
    entry_amount = 1
    target_amount = 1000
    multiplier = 100
    
    # Create streak status line with emojis
    status_emojis = []
    for i in range(max_steps):
        if i < current_step - 1:
            # First 2 legs won, 3rd leg pending
            if i < 2:
                status_emojis.append('✅')
            else:
                status_emojis.append('🔒')
        else:
            status_emojis.append('🔒')
    
    status_line = ''.join(status_emojis)
    
    # Sample picks for the streak
    selections = [
        {
            "player_name": "Aaron Judge",
            "prop_type": "batter_home_runs",
            "line": 0.5,
            "over_under": "O/U"
        },
        {
            "player_name": "Shohei Ohtani", 
            "prop_type": "pitcher_strikeouts",
            "line": 6.5,
            "over_under": "O/U"
        },
        {
            "player_name": "Ronald Acuna Jr.",
            "prop_type": "hits",
            "line": 1.5,
            "over_under": "O/U"
        }
    ]
    
    # Create props text
    props_text = ""
    for pick in selections:
        player_name = pick["player_name"]
        stat_type = clean_stat_name(pick["prop_type"])
        line = pick["line"]
        over_under = pick["over_under"]
        
        props_text += f"• **{player_name}** – {stat_type} {line} {over_under}\n"
    
    # Create embed for streak
    embed = {
        "title": f"🎯 Streak to ${target_amount:,}   |   {multiplier}x",
        "description": f"**Entry:** ${entry_amount} | **Result:** {status_line}",
        "color": 0x00ff00,  # Green for active streaks
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "fields": [
            {
                "name": "Props:",
                "value": props_text,
                "inline": False
            },
            {
                "name": "Progress",
                "value": f"**Current Leg:** {current_step}/{max_steps}\n**Status:** 🔥 Active Streak",
                "inline": True
            },
            {
                "name": "Potential Payout",
                "value": f"**Target:** ${target_amount:,}\n**Multiplier:** {multiplier}x",
                "inline": True
            }
        ],
        "footer": {
            "text": "Streak ID: test_streak_001"
        }
    }
    
    payload = {
        "content": "🧪 **TEST STREAK** - Ghost AI 3.0 Underdog-style Streak",
        "username": "Ghost AI 3.0",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print("✅ Streak webhook test successful!")
            print("   Check your Discord tickets channel for the streak message")
            print(f"   Status Line: {status_line}")
            print(f"   Progress: {current_step}/{max_steps} legs")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_async_webhook():
    """Test async webhook functionality."""
    print("🔄 Testing Async Webhook...")
    
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "content": "🧪 **ASYNC TEST** - Ghost AI 3.0 Async Webhook Test",
                "username": "Ghost AI 3.0"
            }
            
            async with session.post(WEBHOOK_URL, json=payload) as response:
                if response.status == 204:
                    print("✅ Async webhook test successful!")
                else:
                    print(f"❌ Async webhook failed: {response.status}")
                    
    except Exception as e:
        print(f"❌ Async webhook test failed: {e}")

def run_all_tests():
    """Run all webhook tests."""
    print("🚀 Ghost AI 3.0 Discord Webhook Tests")
    print("=" * 50)
    
    # Run simple test
    test_simple_webhook()
    print()
    
    # Run ticket test
    test_ticket_webhook()
    print()
    
    # Run streak test
    test_streak_webhook()
    print()
    
    # Run async test
    asyncio.run(test_async_webhook())
    print()
    
    print("🎉 All webhook tests completed!")
    print("Check your Discord tickets channel for the test messages")

if __name__ == "__main__":
    run_all_tests() 