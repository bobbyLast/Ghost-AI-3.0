#!/usr/bin/env python3
"""
Production Discord Integration

Automated posting of daily picks, alerts, and system status to Discord.
"""

import asyncio
import datetime
import logging
import os
import aiohttp
from typing import Dict, List, Optional
import discord
from discord.ext import commands
from datetime import datetime, timezone

logger = logging.getLogger('production.discord')

class ProductionDiscordBot:
    """Production Discord bot for automated posting."""
    
    def __init__(self):
        self.bot = None
        self.channels = {
            'picks': None,
            'tickets': None,
            'alerts': None,
            'system': None
        }
        self.webhooks = {
            'tickets': os.getenv('DISCORD_TICKETS_WEBHOOK', '')
        }
        self.is_connected = False
        
    async def initialize(self, token: str):
        """Initialize the Discord bot."""
        try:
            logger.info("🤖 Initializing Discord bot...")
            
            # Create bot instance
            intents = discord.Intents.default()
            intents.message_content = True
            
            self.bot = commands.Bot(command_prefix='!', intents=intents)
            
            # Set up event handlers
            self.bot.event(self.on_ready)
            
            # Start the bot
            await self.bot.start(token)
            
        except Exception as e:
            logger.error(f"❌ Discord bot initialization failed: {e}")
            self.is_connected = False
    
    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f"✅ Discord bot ready: {self.bot.user}")
        self.is_connected = True
        
        # Find channels
        await self.find_channels()
    
    async def find_channels(self):
        """Find Discord channels by name."""
        try:
            for guild in self.bot.guilds:
                for channel in guild.channels:
                    if isinstance(channel, discord.TextChannel):
                        if 'picks' in channel.name.lower():
                            self.channels['picks'] = channel
                        elif 'tickets' in channel.name.lower():
                            self.channels['tickets'] = channel
                        elif 'alerts' in channel.name.lower():
                            self.channels['alerts'] = channel
                        elif 'system' in channel.name.lower():
                            self.channels['system'] = channel
            
            logger.info(f"📢 Found channels: {list(self.channels.keys())}")
            
        except Exception as e:
            logger.error(f"❌ Failed to find channels: {e}")
    
    async def post_daily_picks(self, picks: Dict):
        """Post daily picks to Discord."""
        if not self.is_connected:
            logger.warning("⚠️ Discord not connected - skipping post")
            return
        
        try:
            logger.info("📢 Posting daily picks to Discord...")
            
            for pick_type, pick_data in picks.items():
                if not pick_data:
                    continue
                
                if pick_type == 'potd':
                    await self.post_pick(pick_data, "🏆 **PICK OF THE DAY**")
                elif pick_type == 'rpotd':
                    await self.post_pick(pick_data, "🔥 **RISKY PICK OF THE DAY**")
                elif pick_type == 'totd':
                    await self.post_ticket(pick_data, "🎯 **TICKET OF THE DAY**")
                elif pick_type == 'rtotd':
                    await self.post_ticket(pick_data, "💎 **RISKY TICKET OF THE DAY**")
                elif pick_type == 'streaks':
                    await self.post_streaks(pick_data, "🔥 **STREAKS**")
            
            logger.info("✅ Daily picks posted to Discord")
            
        except Exception as e:
            logger.error(f"❌ Failed to post daily picks: {e}")
    
    async def post_pick(self, pick: Dict, title: str):
        """Post a single pick."""
        try:
            channel = self.channels['picks']
            if not channel:
                logger.warning("⚠️ Picks channel not found")
                return
            
            # Format the pick
            player_name = pick.get('player_name', 'Unknown')
            stat = pick.get('stat', 'Unknown')
            line = pick.get('line', 'Unknown')
            confidence = pick.get('confidence', 0)
            team = pick.get('team', 'Unknown')
            
            embed = discord.Embed(
                title=title,
                description=f"**{player_name}** ({team})",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(timezone.utc)
            )
            
            embed.add_field(name="Prop", value=f"{stat} {line}", inline=True)
            embed.add_field(name="Confidence", value=f"{confidence:.1%}", inline=True)
            embed.add_field(name="Pick", value=pick.get('side', 'Over'), inline=True)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ Failed to post pick: {e}")
    
    async def post_ticket(self, picks: List[Dict], title: str):
        """Post a ticket (multiple picks) using webhook."""
        try:
            # Use webhook for tickets if available
            if self.webhooks.get('tickets'):
                await self.post_ticket_webhook(picks, title)
            else:
                # Fallback to channel posting
                channel = self.channels['tickets'] or self.channels['picks']
                if not channel:
                    logger.warning("⚠️ Neither tickets webhook nor picks channel found")
                    return
                
                embed = discord.Embed(
                    title=title,
                    description=f"**{len(picks)}-Leg Ticket**",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now(timezone.utc)
                )
                
                for i, pick in enumerate(picks, 1):
                    player_name = pick.get('player_name', 'Unknown')
                    stat = pick.get('stat', 'Unknown')
                    line = pick.get('line', 'Unknown')
                    confidence = pick.get('confidence', 0)
                    
                    embed.add_field(
                        name=f"Leg {i}",
                        value=f"**{player_name}**\n{stat} {line}\nConfidence: {confidence:.1%}",
                        inline=True
                    )
                
                await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ Failed to post ticket: {e}")
    
    async def post_ticket_webhook(self, picks: List[Dict], title: str):
        """Post ticket using Discord webhook."""
        try:
            webhook_url = self.webhooks['tickets']
            
            # Create embed for webhook
            embed = {
                "title": title,
                "description": f"**{len(picks)}-Leg Ticket**",
                "color": 0x00ff00,  # Green color
                "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
                "fields": []
            }
            
            for i, pick in enumerate(picks, 1):
                player_name = pick.get('player_name', 'Unknown')
                stat = pick.get('stat', 'Unknown')
                line = pick.get('line', 'Unknown')
                confidence = pick.get('confidence', 0)
                
                embed["fields"].append({
                    "name": f"Leg {i}",
                    "value": f"**{player_name}**\n{stat} {line}\nConfidence: {confidence:.1%}",
                    "inline": True
                })
            
            # Prepare webhook payload
            payload = {
                "embeds": [embed],
                "username": "Ghost AI 3.0",
                "avatar_url": "https://cdn.discordapp.com/avatars/123456789/abcdef.png"  # Optional: add your bot avatar
            }
            
            # Send webhook
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 204:
                        logger.info(f"✅ Ticket posted to webhook: {title}")
                    else:
                        logger.error(f"❌ Webhook failed: {response.status}")
            
        except Exception as e:
            logger.error(f"❌ Failed to post ticket webhook: {e}")
    
    async def post_streaks(self, picks: List[Dict], title: str):
        """Post streaks."""
        try:
            channel = self.channels['picks']
            if not channel:
                logger.warning("⚠️ Picks channel not found")
                return
            
            embed = discord.Embed(
                title=title,
                color=discord.Color.orange(),
                timestamp=datetime.datetime.now(timezone.utc)
            )
            
            for pick in picks:
                player_name = pick.get('player_name', 'Unknown')
                stat = pick.get('stat', 'Unknown')
                line = pick.get('line', 'Unknown')
                streak_info = pick.get('streak_info', {})
                current_streak = streak_info.get('current_streak', 0)
                next_legs = streak_info.get('next_legs', 2)
                
                embed.add_field(
                    name=f"🔥 {player_name}",
                    value=f"{stat} {line}\nStreak: {current_streak}\nNext: {next_legs}-leg",
                    inline=True
                )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ Failed to post streaks: {e}")
    
    async def send_alert(self, message: str, level: str = "info"):
        """Send an alert to Discord."""
        try:
            channel = self.channels['alerts']
            if not channel:
                logger.warning("⚠️ Alerts channel not found")
                return
            
            # Choose color based on level
            colors = {
                'info': discord.Color.blue(),
                'warning': discord.Color.orange(),
                'error': discord.Color.red(),
                'success': discord.Color.green()
            }
            
            color = colors.get(level, discord.Color.blue())
            
            embed = discord.Embed(
                title=f"🚨 System Alert",
                description=message,
                color=color,
                timestamp=datetime.datetime.now(timezone.utc)
            )
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert: {e}")
    
    async def send_system_status(self, status: Dict):
        """Send system status to Discord."""
        try:
            channel = self.channels['system']
            if not channel:
                logger.warning("⚠️ System channel not found")
                return
            
            embed = discord.Embed(
                title="📊 System Status",
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now(timezone.utc)
            )
            
            embed.add_field(name="Status", value="🟢 Online", inline=True)
            embed.add_field(name="Last Daily Picks", value=status.get('last_daily_picks', 'Never'), inline=True)
            embed.add_field(name="Successful Runs", value=status.get('successful_runs', 0), inline=True)
            embed.add_field(name="Errors", value=status.get('errors_count', 0), inline=True)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"❌ Failed to send system status: {e}")
    
    async def close(self):
        """Close the Discord bot."""
        if self.bot:
            await self.bot.close()
        self.is_connected = False

# Global instance
discord_bot = ProductionDiscordBot()

async def initialize_discord():
    """Initialize Discord bot."""
    token = os.getenv('DISCORD_TOKEN')
    if token:
        await discord_bot.initialize(token)
    else:
        logger.warning("⚠️ No Discord token found - Discord features disabled")

async def post_daily_picks(picks: Dict):
    """Post daily picks to Discord."""
    await discord_bot.post_daily_picks(picks)

async def send_alert(message: str, level: str = "info"):
    """Send alert to Discord."""
    await discord_bot.send_alert(message, level)

async def send_system_status(status: Dict):
    """Send system status to Discord."""
    await discord_bot.send_system_status(status) 