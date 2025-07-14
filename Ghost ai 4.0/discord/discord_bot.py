#!/usr/bin/env python3
"""
discord_bot.py - Ghost AI 3.0 Enhanced Discord Bot (Underdog Style)
Handles posting daily picks, Underdog-style streaks, and tickets.
"""

import logging
import json
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import discord
from discord.ext import commands, tasks

from ghost_teaching_loop import ghost_openai_wrapper

logger = logging.getLogger('discord_bot')

class GhostAIDiscordIntegration:
    """Discord integration for Ghost AI 3.0 (not a bot)"""
    
    def __init__(self, base_dir: Path, webhook_url: str):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True
        
        # Initialize webhook
        self.base_dir = base_dir
        self.webhook_url = webhook_url
        self.webhook = None
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.daily_pick_manager = None
        self.streak_manager = None
        self.ticket_generator = None
        
        logger.info("Discord integration for Ghost AI initialized")
    
    def _load_config(self) -> Dict:
        """Load bot configuration."""
        try:
            config_file = self.base_dir / 'config' / 'discord_config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    async def setup_hook(self):
        """Setup bot components."""
        try:
            # Initialize webhook
            self.webhook = discord.Webhook.from_url(self.webhook_url, session=self.session)
            
            # Initialize managers
            from ai_brain.daily_pick_manager import create_daily_pick_manager
            from ai_brain.streak_manager import create_streak_manager
            from ai_brain.ticket_generator import create_ticket_generator
            
            self.daily_pick_manager = create_daily_pick_manager(self.base_dir)
            self.streak_manager = create_streak_manager(self.base_dir)
            self.ticket_generator = create_ticket_generator(self.base_dir)
            
            logger.info("✅ Bot components initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup bot: {e}")
    
    async def on_ready(self):
        """Bot ready event."""
        logger.info(f"🤖 {self.user} is ready!")
        
        # Start background tasks
        self.post_daily_picks.start()
        self.post_streak_picks.start()
        self.post_tickets.start()
    
    @tasks.loop(hours=24)
    async def post_daily_picks(self):
        """Post daily picks every 24 hours."""
        try:
            logger.info("📅 Posting daily picks...")
            
            # Generate daily picks
            daily_picks = self.daily_pick_manager.generate_daily_picks()
            
            if daily_picks:
                # Post each daily pick
                for pick_type, pick_data in daily_picks.items():
                    message = self._format_daily_pick_message(pick_type, pick_data)
                    await self._post_message(message)
                    await asyncio.sleep(2)  # Small delay between posts
                
                logger.info("✅ Posted all daily picks")
            else:
                logger.warning("No daily picks to post")
                
        except Exception as e:
            logger.error(f"Failed to post daily picks: {e}")
    
    @tasks.loop(hours=6)
    async def post_streak_picks(self):
        """Post streak picks every 6 hours."""
        try:
            logger.info("🔥 Posting Underdog-style streak picks...")
            
            # Generate streak picks
            streak_picks = self.streak_manager.generate_streak_picks()
            
            if streak_picks:
                for streak_type, pick_data in streak_picks.items():
                    message = self._format_underdog_streak_message(streak_type, pick_data)
                    await self._post_message(message)
                    await asyncio.sleep(2)
                
                logger.info("✅ Posted all streak picks")
            else:
                logger.info("No new streak picks to post")
                
        except Exception as e:
            logger.error(f"Failed to post streak picks: {e}")
    
    @tasks.loop(hours=4)
    async def post_tickets(self):
        """Post tickets every 4 hours."""
        try:
            logger.info("🎫 Posting tickets...")
            
            # Generate tickets
            tickets = self.ticket_generator.generate_tickets(num_tickets=3)
            
            if tickets:
                for ticket in tickets:
                    message = self._format_ticket_message(ticket)
                    await self._post_message(message)
                    await asyncio.sleep(3)
                
                logger.info("✅ Posted all tickets")
            else:
                logger.warning("No tickets to post")
                
        except Exception as e:
            logger.error(f"Failed to post tickets: {e}")
    
    def _format_daily_pick_message(self, pick_type: str, pick_data: Dict) -> str:
        """Format daily pick message."""
        try:
            name = pick_data.get('name', 'N/A')
            game = pick_data.get('game', 'N/A')
            player = pick_data.get('player', 'N/A')
            prop = pick_data.get('prop', 'N/A')
            line = pick_data.get('line', 'N/A')
            pick = pick_data.get('pick', 'N/A')
            confidence = pick_data.get('confidence', 0)
            odds = pick_data.get('odds', 'N/A')
            reasoning = pick_data.get('reasoning', 'N/A')
            
            # Daily pick emoji
            emoji_map = {
                'RPOTD': '🌟',
                'TOTD': '🎯',
                'POTD': '⭐',
                'RTOTD': '🔥',
                'HRH': '💣'
            }
            
            emoji = emoji_map.get(pick_type, '📅')
            
            message = f"""
{emoji} **{name}** {emoji}

**Game:** {game}
**Player:** {player}
**Prop:** {prop}
**Line:** {line}
**Pick:** {pick}
**Confidence:** {confidence * 100:.0f}%
**Odds:** {odds}

**Reasoning:** {reasoning}

---
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Failed to format daily pick message: {e}")
            return f"Error formatting {pick_type} message"
    
    def _format_underdog_streak_message(self, streak_type: str, pick_data: Dict) -> str:
        """Format Underdog-style streak message."""
        try:
            streak_info = self.streak_manager.streak_types[streak_type]
            name = streak_info['name']
            entry_amount = streak_info['entry_amount']
            target_amount = streak_info['target_amount']
            risk_level = streak_info['risk_level']
            
            streak_data = self.streak_manager.active_streaks[streak_type]
            current_leg = streak_data.get('current_leg', 1)
            max_legs = streak_data.get('max_legs', 11)
            total_multiplier = streak_data.get('total_multiplier', 1.0)
            status_line = streak_data.get('status_line', '')
            potential_payout = streak_data.get('potential_payout', 0)
            
            game = pick_data.get('game', 'N/A')
            player = pick_data.get('player', 'N/A')
            prop = pick_data.get('prop', 'N/A')
            line = pick_data.get('line', 'N/A')
            pick = pick_data.get('pick', 'N/A')
            confidence = pick_data.get('confidence', 0)
            odds = pick_data.get('odds', 'N/A')
            multiplier = pick_data.get('multiplier', 1.0)
            reasoning = pick_data.get('reasoning', 'N/A')
            
            # Add risk level emoji
            risk_emoji = "💀" if risk_level == 'risky' else "🔥"
            
            message = f"""
{risk_emoji} **{name}** {risk_emoji}

**Entry:** ${entry_amount} | **Target:** ${target_amount:,} | **Multiplier:** {multiplier}x
**Risk Level:** {risk_level.upper()}

**Game:** {game}
**Player:** {player}
**Prop:** {prop}
**Line:** {line}
**Pick:** {pick}
**Confidence:** {confidence * 100:.0f}%
**Odds:** {odds}

**Progress:** {current_leg}/{max_legs} legs
**Status:** {status_line}
**Total Multiplier:** {total_multiplier}x
**Potential Payout:** ${potential_payout:,.2f}

**Reasoning:** {reasoning}

---
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Failed to format Underdog streak message: {e}")
            return f"Error formatting {streak_type} message"
    
    def _format_ticket_message(self, ticket: Dict) -> str:
        """Format ticket message."""
        try:
            ticket_id = ticket.get('ticket_id', 'N/A')
            sport = ticket.get('sport', 'N/A')
            props = ticket.get('props', [])
            total_confidence = ticket.get('total_confidence', 0)
            total_odds = ticket.get('total_odds', 'N/A')
            reasoning = ticket.get('reasoning', 'N/A')
            
            message = f"""
🎫 **Ticket #{ticket_id}**

**Sport:** {sport}
**Total Confidence:** {total_confidence * 100:.0f}%
**Total Odds:** {total_odds}

**Props:**
"""
            
            for i, prop in enumerate(props, 1):
                game = prop.get('game', 'N/A')
                player = prop.get('player', 'N/A')
                prop_type = prop.get('prop', 'N/A')
                line = prop.get('line', 'N/A')
                pick = prop.get('pick', 'N/A')
                confidence = prop.get('confidence', 0)
                odds = prop.get('odds', 'N/A')
                
                message += f"""
{i}. **{game}**
   **Player:** {player}
   **Prop:** {prop_type}
   **Line:** {line}
   **Pick:** {pick}
   **Confidence:** {confidence * 100:.0f}%
   **Odds:** {odds}
"""
            
            message += f"""
**Reasoning:** {reasoning}

---
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"Failed to format ticket message: {e}")
            return f"Error formatting ticket message"
    
    async def _post_message(self, message: str):
        """Post message to Discord."""
        try:
            if self.webhook:
                await self.webhook.send(content=message)
                logger.info("📢 Message posted to Discord")
            else:
                logger.error("Webhook not initialized")
                
        except Exception as e:
            logger.error(f"Failed to post message: {e}")
    
    @commands.command(name='feedback')
    async def feedback_command(self, ctx, ticket_id: str, *, feedback_text: str):
        """Submit feedback for a ticket."""
        try:
            # Process feedback
            feedback_data = {
                'ticket_id': ticket_id,
                'feedback': feedback_text,
                'user': ctx.author.name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save feedback
            feedback_file = self.base_dir / 'data' / 'feedback.json'
            feedback_file.parent.mkdir(parents=True, exist_ok=True)
            
            feedback_list = []
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    feedback_list = json.load(f)
            
            feedback_list.append(feedback_data)
            
            with open(feedback_file, 'w') as f:
                json.dump(feedback_list, f, indent=2)
            
            # Send confirmation
            await ctx.send(f"✅ Feedback submitted for ticket {ticket_id}")
            
            logger.info(f"Feedback submitted for ticket {ticket_id}")
            
        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            await ctx.send("❌ Failed to submit feedback")
    
    @commands.command(name='streak_result')
    async def streak_result_command(self, ctx, streak_type: str, result: str):
        """Record streak result (win/loss)."""
        try:
            if result.lower() not in ['win', 'loss']:
                await ctx.send("❌ Result must be 'win' or 'loss'")
                return
            
            self.streak_manager.record_streak_result(streak_type, result)
            await ctx.send(f"✅ Recorded {result} for {streak_type}")
            
            logger.info(f"Streak result recorded: {streak_type} - {result}")
            
        except Exception as e:
            logger.error(f"Failed to record streak result: {e}")
            await ctx.send("❌ Failed to record streak result")
    
    @commands.command(name='streak_summary')
    async def streak_summary_command(self, ctx):
        """Show Underdog-style streak summary with separate safe/risky sections."""
        try:
            active_streaks = self.streak_manager.get_active_streaks()
            
            message = "🔥 **Active Underdog-Style Streaks Summary**\n\n"
            
            # Separate safe and risky streaks
            safe_streaks = []
            risky_streaks = []
            
            for streak_type, streak_data in active_streaks.items():
                if streak_data['status'] == 'active':
                    streak_info = self.streak_manager.streak_types[streak_type]
                    name = streak_info['name']
                    current_leg = streak_data.get('current_leg', 1)
                    max_legs = streak_data.get('max_legs', 11)
                    total_multiplier = streak_data.get('total_multiplier', 1.0)
                    potential_payout = streak_data.get('potential_payout', 0)
                    status_line = streak_data.get('status_line', '')
                    risk_level = streak_data.get('risk_level', 'safe')
                    
                    total_wins = streak_data.get('total_wins', 0)
                    total_losses = streak_data.get('total_losses', 0)
                    
                    win_rate = 0
                    if total_wins + total_losses > 0:
                        win_rate = (total_wins / (total_wins + total_losses)) * 100
                    
                    streak_info = {
                        'name': name,
                        'current_leg': current_leg,
                        'max_legs': max_legs,
                        'total_multiplier': total_multiplier,
                        'potential_payout': potential_payout,
                        'status_line': status_line,
                        'win_rate': win_rate,
                        'risk_level': risk_level
                    }
                    
                    if risk_level == 'risky':
                        risky_streaks.append(streak_info)
                    else:
                        safe_streaks.append(streak_info)
            
            # Display safe streaks
            if safe_streaks:
                message += "**Safe Streaks:**\n"
                for streak in safe_streaks:
                    message += f"🔥 **{streak['name']}:** Leg {streak['current_leg']}/{streak['max_legs']} | {streak['total_multiplier']}x | ${streak['potential_payout']:,.2f}\n"
                    message += f"Status: {streak['status_line']} | Win Rate: {streak['win_rate']:.1f}%\n\n"
            
            # Display risky streaks
            if risky_streaks:
                message += "**Risky Streaks:**\n"
                for streak in risky_streaks:
                    message += f"💀 **{streak['name']}:** Leg {streak['current_leg']}/{streak['max_legs']} | {streak['total_multiplier']}x | ${streak['potential_payout']:,.2f}\n"
                    message += f"Status: {streak['status_line']} | Win Rate: {streak['win_rate']:.1f}%\n\n"
            
            if not safe_streaks and not risky_streaks:
                message += "No active streaks at the moment.\n"
            
            await ctx.send(message)
            
        except Exception as e:
            logger.error(f"Failed to show streak summary: {e}")
            await ctx.send("❌ Failed to show streak summary")

def create_discord_bot(base_dir: Path) -> GhostAIDiscordIntegration:
    """Create and return a Discord bot instance."""
    try:
        # Load webhook URL from config
        config_file = base_dir / 'config' / 'discord_config.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                webhook_url = config.get('webhook_url', '')
        else:
            webhook_url = ''
        
        if not webhook_url:
            logger.error("No webhook URL found in config")
            return None
        
        return GhostAIDiscordIntegration(base_dir, webhook_url)
        
    except Exception as e:
        logger.error(f"Failed to create Discord bot: {e}")
        return None 

def create_discord_integration(base_dir: Path):
    """Alias for create_discord_bot for compatibility."""
    return create_discord_bot(base_dir)

def start_discord_integration(base_dir: Path):
    """Stub for starting Discord integration if needed."""
    integration = create_discord_integration(base_dir)
    # Add startup logic if needed
    return integration 