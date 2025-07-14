#!/usr/bin/env python3
"""
daily_pick_manager.py - Ghost AI 3.0 Daily Pick Manager
Manages daily picks (RPOTD, TOTD, POTD, RTOTD, HRH) with streak integration.
"""

import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

from ghost_teaching_loop import ghost_openai_wrapper
from ai_brain.streak_manager import create_streak_manager
from ai_brain.tennis_api_client import get_fixtures as tennis_fixtures, get_odds as tennis_odds

logger = logging.getLogger('daily_pick_manager')

class DailyPickManager:
    """Manages daily picks with streak integration and proper separation."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.daily_picks_file = base_dir / 'data' / 'daily_picks.json'
        self.daily_picks_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Daily pick types
        self.daily_pick_types = {
            'RPOTD': {'name': 'Rookie Pick of the Day', 'sport': 'MLB'},
            'TOTD': {'name': 'Total Pick of the Day', 'sport': 'MLB'},
            'POTD': {'name': 'Player Pick of the Day', 'sport': 'MLB'},
            'RTOTD': {'name': 'Rookie Total of the Day', 'sport': 'MLB'},
            'HRH': {'name': 'Homerun Hitter', 'sport': 'MLB'},
            'TTPOTD': {'name': 'Tennis Top Pick of the Day', 'sport': 'TENNIS'}
        }
        
        # Load existing daily picks
        self.daily_picks = self._load_daily_picks()
        
        # Initialize streak manager
        self.streak_manager = create_streak_manager(base_dir)
        
        logger.info("📅 Daily Pick Manager initialized")
    
    def _load_daily_picks(self) -> Dict:
        """Load existing daily picks."""
        try:
            if self.daily_picks_file.exists():
                with open(self.daily_picks_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load daily picks: {e}")
            return {}
    
    def _save_daily_picks(self):
        """Save daily picks."""
        try:
            with open(self.daily_picks_file, 'w') as f:
                json.dump(self.daily_picks, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save daily picks: {e}")
    
    def generate_daily_picks(self) -> Dict:
        """Generate all daily picks for today."""
        try:
            logger.info("📅 Generating daily picks...")
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Check if we already have picks for today
            if today in self.daily_picks:
                logger.info("✅ Daily picks already generated for today")
                return self.daily_picks[today]
            
            daily_picks = {}
            
            # Generate picks for each type
            for pick_type, pick_info in self.daily_pick_types.items():
                pick = self._generate_daily_pick(pick_type, pick_info)
                if pick:
                    daily_picks[pick_type] = pick
            
            # Store today's picks
            self.daily_picks[today] = daily_picks
            self._save_daily_picks()
            
            logger.info(f"✅ Generated {len(daily_picks)} daily picks")
            return daily_picks
            
        except Exception as e:
            logger.error(f"❌ Failed to generate daily picks: {e}")
            return {}
    
    def _generate_daily_pick(self, pick_type: str, pick_info: Dict) -> Optional[Dict]:
        """Generate a specific daily pick."""
        try:
            name = pick_info['name']
            # Instead of picking by sport, always select the best prop from the mixed pool
            today = datetime.now().strftime('%Y-%m-%d')
            all_props = []
            # --- Tennis props ---
            try:
                tennis_matches = tennis_fixtures(today)
                for match in tennis_matches:
                    match_key = match.get('event_key')
                    if not match_key:
                        continue
                    odds = tennis_odds(match_key)
                    if odds and isinstance(odds, dict):
                        for market, market_data in odds.items():
                            if isinstance(market_data, dict):
                                for outcome, price in market_data.items():
                                    all_props.append({
                                        'sport': 'TENNIS',
                                        'game': f"{match.get('event_first_player')} vs {match.get('event_second_player')}",
                                        'player': match.get('event_first_player'),
                                        'prop': market,
                                        'line': outcome,
                                        'pick': 'Over/Under',
                                        'confidence': 0.75,  # Placeholder, can use OpenAI for real confidence
                                        'odds': price,
                                        'reasoning': f"Tennis prop for {market} {outcome}"
                                    })
            except Exception as e:
                logger.warning(f"Tennis API fetch failed: {e}")
            # --- MLB/WNBA props ---
            # (Assume similar logic exists for MLB/WNBA, or add here)
            # all_props.extend(mlb_props)
            # all_props.extend(wnba_props)
            # --- Use OpenAI to select the best prop from the mixed pool ---
            if not all_props:
                logger.warning("No props found for any sport today.")
                return None
            prompt = f"""
            Here is a list of props from MLB, WNBA, and Tennis:
            {all_props}
            Select the single best prop for a daily pick (for sure hitting, maximum value). Return as JSON with all fields from the selected prop, plus a 'reasoning' field explaining why it is the best pick today.
            """
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'daily_pick', 'pick_type': pick_type, 'sport': 'MIXED'},
                model='gpt-4',
                max_tokens=500
            )
            pick_data = self._extract_json_from_response(response)
            if pick_data:
                pick_data['timestamp'] = datetime.now().isoformat()
                pick_data['daily_pick'] = True
                return pick_data
            return None
        except Exception as e:
            logger.error(f"Failed to generate daily pick: {e}")
            return None
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from OpenAI response."""
        try:
            import re
            
            # Look for JSON blocks
            json_pattern = r'```json\s*\n(.*?)\n```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            if matches:
                return json.loads(matches[0])
            
            # Look for JSON without markdown
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract JSON: {e}")
            return None
    
    def post_daily_picks(self):
        """Post all daily picks to Discord."""
        try:
            from discord_integration.discord_bot import create_discord_bot
            
            discord_bot = create_discord_bot(self.base_dir)
            
            today = datetime.now().strftime('%Y-%m-%d')
            daily_picks = self.daily_picks.get(today, {})
            
            if not daily_picks:
                logger.warning("No daily picks found for today")
                return
            
            # Post each daily pick
            for pick_type, pick_data in daily_picks.items():
                message = self._format_daily_pick_message(pick_type, pick_data)
                discord_bot._post_message(message)
            
            # Post streak summary
            self.streak_manager.post_streak_summary()
            
            logger.info("📢 Posted all daily picks to Discord")
            
        except Exception as e:
            logger.error(f"Failed to post daily picks: {e}")
    
    def _format_daily_pick_message(self, pick_type: str, pick_data: Dict) -> str:
        """Format daily pick message for Discord."""
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
    
    def generate_streak_picks(self) -> Dict:
        """Generate streak picks using the streak manager."""
        return self.streak_manager.generate_streak_picks()
    
    def record_streak_result(self, streak_type: str, result: str):
        """Record streak result."""
        self.streak_manager.record_streak_result(streak_type, result)
    
    def get_today_picks(self) -> Dict:
        """Get today's daily picks."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.daily_picks.get(today, {})
    
    def get_active_streaks(self) -> Dict:
        """Get active streaks."""
        return self.streak_manager.get_active_streaks()
    
    def get_streak_history(self) -> List[Dict]:
        """Get streak history."""
        return self.streak_manager.get_streak_history()

def create_daily_pick_manager(base_dir: Path) -> DailyPickManager:
    """Create and return a DailyPickManager instance."""
    return DailyPickManager(base_dir) 