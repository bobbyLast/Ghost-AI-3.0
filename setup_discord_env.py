#!/usr/bin/env python3
"""
Discord Environment Setup Script
Sets up environment variables for Discord integration
"""

import os
import sys

def setup_discord_environment():
    """Set up Discord environment variables."""
    
    print("🔧 Setting up Discord Environment Variables")
    print("=" * 50)
    
    # Discord Bot Token
    os.environ['DISCORD_BOT_TOKEN'] = 'summaries'
    
    # Discord Webhooks
    os.environ['TICKET_WEBHOOK'] = 'https://discord.com/api/webhooks/1386168741938597989/Ib-d9TDtSnd4gZ-C2JkKQ866p6fxAF3Ps4fLUhkGJYI_dZQCe8hCRBTODv1-vZV_U7Sy'
    os.environ['UPDATE_WEBHOOK'] = 'https://discord.com/api/webhooks/1375912085762080868/qRsmIH92iKpMwrtt2TYWsRY1OkFerN61zFVGooCFZvae-liF5l_4ovbwpgv0b7nSOKJg'
    os.environ['MONEYLINE_WEBHOOK'] = 'https://discord.com/api/webhooks/1390410910392385756/w9-96vnCSQQjfu_hzesnaSt6MP3EEbC_5WuTGuQnvsKnxoxkS4cj8Nl3Z0KYqWnaV36z'
    
    # Main webhook (fallback)
    os.environ['DISCORD_WEBHOOK_URL'] = os.environ['TICKET_WEBHOOK']
    
    print("✅ Environment variables set:")
    print(f"   DISCORD_BOT_TOKEN: {os.environ['DISCORD_BOT_TOKEN']}")
    print(f"   TICKET_WEBHOOK: {os.environ['TICKET_WEBHOOK'][:50]}...")
    print(f"   UPDATE_WEBHOOK: {os.environ['UPDATE_WEBHOOK'][:50]}...")
    print(f"   MONEYLINE_WEBHOOK: {os.environ['MONEYLINE_WEBHOOK'][:50]}...")
    
    print("\n🎯 Discord Integration Ready!")
    print("   - Tickets will be posted to ticket webhook")
    print("   - Moneyline bets will be posted to moneyline webhook")
    print("   - Updates and summaries will be posted to update webhook")
    print("   - Bot token is configured for slash commands")
    
    return True

def test_discord_webhooks():
    """Test Discord webhooks to ensure they're working."""
    
    print("\n🧪 Testing Discord Webhooks...")
    
    import requests
    
    webhooks = {
        'Ticket Webhook': os.environ.get('TICKET_WEBHOOK'),
        'Update Webhook': os.environ.get('UPDATE_WEBHOOK'),
        'Moneyline Webhook': os.environ.get('MONEYLINE_WEBHOOK')
    }
    
    for name, webhook in webhooks.items():
        if not webhook:
            print(f"❌ {name}: Not configured")
            continue
            
        try:
            payload = {
                "content": f"🧪 Test message from Ghost AI 4.0 - {name}",
                "username": "Ghost AI 4.0 Test"
            }
            
            response = requests.post(webhook, json=payload, timeout=10)
            
            if response.status_code in [200, 204]:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
    
    print("\n🎉 Discord setup complete!")

if __name__ == "__main__":
    setup_discord_environment()
    test_discord_webhooks() 