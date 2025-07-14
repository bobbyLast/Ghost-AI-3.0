#!/usr/bin/env python3
"""
Ghost AI 4.0 Discord Bot
Handles bot token authentication and slash commands.
"""

import discord
from discord.ext import commands
import os
import logging
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger('ghost_ai_bot')

class GhostAIBot:
    def __init__(self):
        self.bot = None
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.webhooks = {
            'main': os.getenv('DISCORD_WEBHOOK_URL'),
            'ticket': os.getenv('TICKET_WEBHOOK'),
            'moneyline': os.getenv('MONEYLINE_WEBHOOK'),
            'update': os.getenv('UPDATE_WEBHOOK')
        }
        
    async def initialize(self):
        """Initialize the Discord bot."""
        if not self.token:
            logger.error("❌ DISCORD_BOT_TOKEN not found in environment variables")
            return False
            
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.guilds = True
            
            self.bot = commands.Bot(command_prefix='!', intents=intents)
            
            # Set up event handlers
            self.bot.event(self.on_ready)
            self.bot.event(self.on_message)
            
            # Add slash commands
            await self.setup_commands()
            
            logger.info("🧠 AI: Discord bot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Discord bot: {e}")
            return False
    
    async def setup_commands(self):
        """Set up slash commands for the AI."""
        if not self.bot:
            return
            
        @self.bot.tree.command(name="status", description="Check Ghost AI status")
        async def status(interaction: discord.Interaction):
            await interaction.response.send_message("🧠 Ghost AI 4.0 is running and analyzing markets!")
        
        @self.bot.tree.command(name="generate", description="Force ticket generation")
        async def generate(interaction: discord.Interaction):
            await interaction.response.send_message("🧠 AI: Generating tickets now...")
            # Here you would trigger ticket generation
        
        @self.bot.tree.command(name="sleep", description="Tell AI to sleep")
        async def sleep(interaction: discord.Interaction):
            await interaction.response.send_message("🧠 AI: Going to sleep... Good night!")
            # Here you would trigger sleep mode
        
        @self.bot.tree.command(name="wake", description="Wake up the AI")
        async def wake(interaction: discord.Interaction):
            await interaction.response.send_message("🧠 AI: Waking up! Ready to work!")
            # Here you would trigger wake mode
    
    async def on_ready(self):
        """Called when bot is ready."""
        if not self.bot:
            return
        logger.info(f"🧠 AI: Discord bot ready: {self.bot.user}")
        logger.info(f"🧠 AI: Connected to {len(self.bot.guilds)} servers")
        
        # Sync commands
        try:
            synced = await self.bot.tree.sync()
            logger.info(f"🧠 AI: Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"❌ Failed to sync commands: {e}")
    
    async def on_message(self, message):
        """Handle incoming messages."""
        if not self.bot or message.author == self.bot.user:
            return
        
        # Process commands
        await self.bot.process_commands(message)
    
    async def post_to_webhook(self, webhook_type, content, embed=None):
        """Post message to specific webhook."""
        webhook_url = self.webhooks.get(webhook_type)
        if not webhook_url:
            logger.warning(f"⚠️ No webhook URL for type: {webhook_type}")
            return False
        
        try:
            import requests
            
            payload = {}
            if content:
                payload['content'] = content
            if embed:
                payload['embeds'] = [embed]
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 204:
                logger.info(f"✅ Posted to {webhook_type} webhook")
                return True
            else:
                logger.error(f"❌ Failed to post to {webhook_type} webhook: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error posting to {webhook_type} webhook: {e}")
            return False
    
    async def post_ticket(self, ticket_data, webhook_type='ticket'):
        """Post ticket to Discord."""
        try:
            embed = self.format_ticket_embed(ticket_data)
            return await self.post_to_webhook(webhook_type, None, embed)
        except Exception as e:
            logger.error(f"❌ Error posting ticket: {e}")
            return False
    
    def format_ticket_embed(self, ticket_data):
        """Format ticket data for Discord embed."""
        try:
            ticket_id = ticket_data.get('ticket_id', 'N/A')
            ticket_type = ticket_data.get('ticket_type', 'AI-Powered Selection')
            confidence = ticket_data.get('total_confidence', 0)
            props = ticket_data.get('props', [])
            
            embed = discord.Embed(
                title=f"🧠 {ticket_type}",
                color=0x23272A,
                timestamp=datetime.now()
            )
            
            # Add AI analysis
            ai_reasoning = ticket_data.get('ai_reasoning', 'AI analysis indicates strong value opportunity')
            embed.add_field(name="AI Analysis", value=ai_reasoning, inline=False)
            
            # Add selections
            selections_text = ""
            for i, prop in enumerate(props, 1):
                player = prop.get('player', 'Unknown')
                line = prop.get('line', '')
                prop_type = prop.get('prop', '')
                pick = prop.get('pick', '')
                prop_confidence = prop.get('confidence', 0)
                
                selections_text += f"**{i}. {player} {line} {prop_type} {pick.upper()}** (AI Confidence: {int(prop_confidence*100)}%)\n"
            
            if selections_text:
                embed.add_field(name="AI Selections", value=selections_text, inline=False)
            
            # Add ticket info
            info_text = f"AI Confidence: {int(confidence*100)}% | Legs: {len(props)} | Ticket ID: {ticket_id}"
            embed.add_field(name="Ticket Info", value=info_text, inline=False)
            
            embed.set_footer(text="Ghost AI 4.0")
            
            return embed
            
        except Exception as e:
            logger.error(f"❌ Error formatting ticket embed: {e}")
            return None
    
    async def start(self):
        """Start the Discord bot."""
        if not self.bot or not self.token:
            logger.error("❌ Bot not initialized or token missing")
            return False
        
        try:
            await self.bot.start(self.token)
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False
    
    async def stop(self):
        """Stop the Discord bot."""
        if self.bot:
            await self.bot.close()

# Global bot instance
ghost_ai_bot = GhostAIBot()

async def start_bot():
    """Start the Ghost AI Discord bot."""
    success = await ghost_ai_bot.initialize()
    if success:
        await ghost_ai_bot.start()
    else:
        logger.error("❌ Failed to start Discord bot")

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot()) 