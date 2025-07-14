#!/usr/bin/env python3
"""
Discord Channel Finder for Ghost AI

This script helps find the correct Discord channel IDs for your Ghost AI.
Run this script to see all available channels and their IDs.
"""

import discord
import os
import asyncio
from discord.ext import commands

class ChannelFinder(commands.AutoAI):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(command_prefix='!', intents=intents)
    
    async def setup_hook(self):
        print("🔍 Channel Finder AI is ready!")
        print("=" * 50)
        
        if not self.guilds:
            print("❌ AI is not connected to any Discord servers!")
            print("Make sure your Discord token is correct and the AI is invited to your server.")
            return
        
        print(f"✅ Connected to {len(self.guilds)} server(s):")
        print()
        
        for guild in self.guilds:
            print(f"🏠 Server: {guild.name} (ID: {guild.id})")
            print(f"   Owner: {guild.owner.name if guild.owner else 'Unknown'}")
            print(f"   Member Count: {guild.member_count}")
            print()
            
            # Get all text channels
            text_channels = [c for c in guild.text_channels if c.permissions_for(guild.me).send_messages]
            
            if not text_channels:
                print("   ❌ No text channels where AI can send messages!")
                print("   Make sure the AI has 'Send Messages' permission in at least one channel.")
                print()
                continue
            
            print("   📝 Available Text Channels:")
            for channel in text_channels:
                # Check if this is one of the preferred channels
                preferred_names = ['tickets', 'betting', 'ghost-ai', 'ai-commands', 'general', 'chat']
                is_preferred = channel.name.lower() in preferred_names
                
                status = "⭐ PREFERRED" if is_preferred else "   "
                print(f"   {status} #{channel.name} (ID: {channel.id})")
            
            print()
            
            # Show recommended configuration
            print("   💡 Recommended Configuration:")
            preferred_channel = None
            for channel in text_channels:
                if channel.name.lower() in ['tickets', 'betting', 'ghost-ai']:
                    preferred_channel = channel
                    break
            
            if not preferred_channel:
                for channel in text_channels:
                    if channel.name.lower() in ['ai-commands', 'general']:
                        preferred_channel = channel
                        break
            
            if preferred_channel:
                print(f"   Use channel ID: {preferred_channel.id}")
                print(f"   Channel name: #{preferred_channel.name}")
            else:
                print(f"   Use channel ID: {text_channels[0].id}")
                print(f"   Channel name: #{text_channels[0].name}")
            
            print("=" * 50)
        
        # Show current config
        print("\n📋 Current Configuration:")
        print(f"   Config file channel ID: 1386168703221108856")
        print(f"   Environment webhook: {'Set' if os.getenv('DISCORD_WEBHOOK') else 'Not set'}")
        
        await self.close()

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ DISCORD_TOKEN environment variable not set!")
        print("Please set your Discord AI token as an environment variable.")
        return
    
    ai = ChannelFinder()
    try:
        await ai.start(token)
    except discord.LoginFailure:
        print("❌ Invalid Discord AI token!")
        print("Please check your DISCORD_TOKEN environment variable.")
    except Exception as e:
        print(f"❌ Error connecting to Discord: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 