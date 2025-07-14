#!/usr/bin/env python3
"""
streak_manager.py - Ghost AI 3.0 Streak Manager (3 Streaks: 2 Normal, 1 Risky)
Manages 3 streaks ($10 entry): 2 normal, 1 risky. Caps payout and cashes out with normal props.
"""

import logging
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import random

from ghost_teaching_loop import ghost_openai_wrapper

logger = logging.getLogger('streak_manager')

STREAK_PAYOUT_CAP = 50000  # $50k cap for all streaks
MAX_STREAKS = 3

class StreakManager:
    """Streak manager: 2 normal + 1 risky streak, all $10 entry, with payout cap and cash out."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.streaks_file = base_dir / 'data' / 'streaks' / 'active_streaks.json'
        self.streak_history_file = base_dir / 'data' / 'streaks' / 'streak_history.json'
        self.streaks_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Only 3 streaks: 2 normal, 1 risky
        self.streak_types = {
            'normal_streak_1': {
                'name': 'Normal Streak 1',
                'type': 'normal',
                'entry_amount': 10,
                'target_amount': STREAK_PAYOUT_CAP,
                'max_legs': 12,
                'base_multiplier': 1.5,
                'risk_level': 'normal'
            },
            'normal_streak_2': {
                'name': 'Normal Streak 2',
                'type': 'normal',
                'entry_amount': 10,
                'target_amount': STREAK_PAYOUT_CAP,
                'max_legs': 12,
                'base_multiplier': 1.5,
                'risk_level': 'normal'
            },
            'risky_streak': {
                'name': 'Risky Streak',
                'type': 'risky',
                'entry_amount': 10,
                'target_amount': STREAK_PAYOUT_CAP,
                'max_legs': 15,
                'base_multiplier': 1.8,
                'risk_level': 'risky'
            }
        }
        
        # Load existing streaks
        self.active_streaks = self._load_active_streaks()
        self.streak_history = self._load_streak_history()
        
        logger.info("🔥 3-Streak System Initialized: 2 Normal, 1 Risky, $10 Entry Each")
    
    def _load_active_streaks(self) -> Dict:
        try:
            if self.streaks_file.exists():
                with open(self.streaks_file, 'r') as f:
                    return json.load(f)
            else:
                default_streaks = {}
                for streak_type in self.streak_types.keys():
                    streak_info = self.streak_types[streak_type]
                    default_streaks[streak_type] = {
                        'current_streak': 0,
                        'best_streak': 0,
                        'current_leg': 0,
                        'max_legs': streak_info['max_legs'],
                        'entry_amount': streak_info['entry_amount'],
                        'target_amount': streak_info['target_amount'],
                        'current_multiplier': 1.0,
                        'total_multiplier': 1.0,
                        'last_win': None,
                        'last_loss': None,
                        'total_wins': 0,
                        'total_losses': 0,
                        'current_pick': None,
                        'next_pick_ready': None,
                        'status': 'inactive',
                        'legs': [],
                        'status_line': '',
                        'potential_payout': 0,
                        'risk_level': streak_info['risk_level']
                    }
                self._save_active_streaks(default_streaks)
                return default_streaks
        except Exception as e:
            logger.error(f"Failed to load active streaks: {e}")
            return {}
    
    def _load_streak_history(self) -> List[Dict]:
        try:
            if self.streak_history_file.exists():
                with open(self.streak_history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Failed to load streak history: {e}")
            return []
    
    def _save_active_streaks(self, streaks: Dict):
        try:
            with open(self.streaks_file, 'w') as f:
                json.dump(streaks, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save active streaks: {e}")
    
    def _save_streak_history(self):
        try:
            with open(self.streak_history_file, 'w') as f:
                json.dump(self.streak_history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save streak history: {e}")
    
    def _calculate_multiplier(self, streak_type: str, current_leg: int) -> float:
        streak_info = self.streak_types[streak_type]
        base_multiplier = streak_info['base_multiplier']
        risk_level = streak_info['risk_level']
        if risk_level == 'risky':
            risk_factor = 1.0 + (current_leg * 0.08)
        else:
            risk_factor = 1.0 + (current_leg * 0.05)
        calculated_multiplier = round(base_multiplier * risk_factor, 2)
        if calculated_multiplier > 3.0:
            calculated_multiplier = 3.0
        return calculated_multiplier
    
    def _calculate_total_multiplier(self, legs: List[Dict]) -> float:
        total_multiplier = 1.0
        for leg in legs:
            if leg.get('result') == 'win':
                total_multiplier *= leg.get('multiplier', 1.0)
        return round(total_multiplier, 2)
    
    def _generate_status_line(self, legs: List[Dict], max_legs: int) -> str:
        status_emojis = []
        for i in range(max_legs):
            if i < len(legs):
                leg = legs[i]
                if leg.get('result') == 'win':
                    status_emojis.append('✅')
                elif leg.get('result') == 'loss':
                    status_emojis.append('❌')
                else:
                    status_emojis.append('🔒')
            else:
                status_emojis.append('🔒')
        return ''.join(status_emojis)
    
    def generate_streak_picks(self) -> Dict:
        logger.info("🔥 Generating 3 streak picks (2 normal, 1 risky)...")
        streak_picks = {}
        for streak_type, streak_info in self.streak_types.items():
            if self.active_streaks[streak_type]['status'] == 'inactive':
                pick = self._generate_streak_pick(streak_type, streak_info)
                if pick:
                    streak_picks[streak_type] = pick
                    self.active_streaks[streak_type]['current_pick'] = pick
                    self.active_streaks[streak_type]['status'] = 'active'
                    self.active_streaks[streak_type]['current_leg'] = 1
                    self.active_streaks[streak_type]['current_multiplier'] = self._calculate_multiplier(streak_type, 1)
                    self.active_streaks[streak_type]['next_pick_ready'] = self._generate_next_pick(streak_type, streak_info)
        self._save_active_streaks(self.active_streaks)
        logger.info(f"✅ Generated {len(streak_picks)} streak picks")
        return streak_picks
    
    def _generate_streak_pick(self, streak_type: str, streak_info: Dict) -> Optional[Dict]:
        pick_type = streak_info['type']
        name = streak_info['name']
        entry_amount = streak_info['entry_amount']
        target_amount = streak_info['target_amount']
        max_legs = streak_info['max_legs']
        base_multiplier = streak_info['base_multiplier']
        risk_level = streak_info['risk_level']
        risk_description = "RISKY" if risk_level == 'risky' else "NORMAL"
        # --- Gather props from all sports ---
        from ai_brain.tennis_api_client import get_fixtures as tennis_fixtures, get_odds as tennis_odds
        from datetime import datetime
        today = datetime.now().strftime('%Y-%m-%d')
        all_props = []
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
        # (Add similar logic for MLB/WNBA props if not already present)
        # all_props.extend(mlb_props)
        # all_props.extend(wnba_props)
        if not all_props:
            logger.warning("No props found for any sport today.")
            return None
        prompt = f"""
        Here is a list of props from MLB, WNBA, and Tennis:
        {all_props}
        Select the single best prop for a streak leg (maximum value, confidence, and payout). Return as JSON with all fields from the selected prop, plus a 'reasoning' field explaining why it is the best pick for this streak leg.
        """
        try:
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'streak_pick', 'streak_type': streak_type, 'risk_level': risk_level, 'sport': 'MIXED'},
                model='gpt-4',
                max_tokens=500
            )
            pick_data = self._extract_json_from_response(response)
            if pick_data:
                pick_data['timestamp'] = datetime.now().isoformat()
                pick_data['multiplier'] = self._calculate_multiplier(streak_type, 1)
                return pick_data
            else:
                help_prompt = f"""
                Ghost AI 3.0 attempted to generate a {risk_description} streak pick for {name} but failed. Please provide advice or a step-by-step solution for how to proceed, or suggest a fallback prop or strategy."
                """
                help_response = ghost_openai_wrapper(
                    help_prompt,
                    tags={'type': 'streak_help', 'streak_type': streak_type, 'risk_level': risk_level},
                    model='gpt-4',
                    max_tokens=300
                )
                logger.warning(f"[OpenAI Help] {help_response}")
                return None
        except Exception as e:
            help_prompt = f"""
            Ghost AI 3.0 encountered an error while generating a {risk_description} streak pick for {name}: {e}. Please provide advice or a step-by-step solution for how to proceed, or suggest a fallback prop or strategy."
            """
            help_response = ghost_openai_wrapper(
                help_prompt,
                tags={'type': 'streak_help', 'streak_type': streak_type, 'risk_level': risk_level},
                model='gpt-4',
                max_tokens=300
            )
            logger.error(f"[OpenAI Help/Error] {help_response}")
            return None
    
    def _generate_next_pick(self, streak_type: str, streak_info: Dict) -> Optional[Dict]:
        current_leg = self.active_streaks[streak_type].get('current_leg', 1) + 1
        multiplier = self._calculate_multiplier(streak_type, current_leg)
        risk_level = streak_info['risk_level']
        risk_description = "RISKY" if risk_level == 'risky' else "NORMAL"
        prompt = f"""
        You are Ghost AI 3.0's next streak pick generator. Generate the next {risk_description} streak pick for {streak_info['name']}.
        This is leg {current_leg} with a {multiplier}x multiplier.
        If the potential payout would exceed ${STREAK_PAYOUT_CAP:,}, stop and generate a normal prop to cash out.
        Return a JSON object with:
        {{
            "streak_type": "{streak_type}",
            "pick_type": "{streak_info['type']}",
            "name": "{streak_info['name']}",
            "sport": "MLB/WNBA",
            "game": "Team A vs Team B",
            "player": "Player Name",
            "prop": "Prop Type",
            "line": "X.X",
            "pick": "Over/Under",
            "confidence": 0.XX,
            "odds": "X.XX",
            "multiplier": {multiplier},
            "current_leg": {current_leg},
            "risk_level": "{risk_level}",
            "reasoning": "Detailed explanation",
            "timestamp": "ISO timestamp",
            "ready_to_post": true
        }}
        """
        response = ghost_openai_wrapper(
            prompt,
            tags={'type': 'next_streak_pick', 'streak_type': streak_type, 'current_leg': current_leg, 'risk_level': risk_level},
            model='gpt-4',
            max_tokens=500
        )
        pick_data = self._extract_json_from_response(response)
        if pick_data:
            pick_data['timestamp'] = datetime.now().isoformat()
            pick_data['ready_to_post'] = True
            return pick_data
        return None
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        import re
        json_pattern = r'```json\s*\n(.*?)\n```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        if matches:
            return json.loads(matches[0])
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        return None
    
    def record_streak_result(self, streak_type: str, result: str):
        if streak_type not in self.active_streaks:
            logger.error(f"Streak type {streak_type} not found")
            return
        streak_data = self.active_streaks[streak_type]
        current_leg = streak_data.get('current_leg', 1)
        current_pick = streak_data.get('current_pick', {})
        leg_data = {
            'leg_number': current_leg,
            'player': current_pick.get('player', ''),
            'prop': current_pick.get('prop', ''),
            'line': current_pick.get('line', ''),
            'pick': current_pick.get('pick', ''),
            'multiplier': current_pick.get('multiplier', 1.0),
            'result': result.lower(),
            'timestamp': datetime.now().isoformat()
        }
        streak_data.setdefault('legs', []).append(leg_data)
        if result.lower() == 'win':
            streak_data['current_streak'] += 1
            streak_data['total_wins'] += 1
            streak_data['last_win'] = datetime.now().isoformat()
            if streak_data['current_streak'] > streak_data['best_streak']:
                streak_data['best_streak'] = streak_data['current_streak']
            streak_data['current_leg'] += 1
            streak_data['total_multiplier'] = self._calculate_total_multiplier(streak_data['legs'])
            # If payout cap reached, stop and generate a normal prop to cash out
            potential_payout = streak_data['entry_amount'] * streak_data['total_multiplier']
            if potential_payout >= STREAK_PAYOUT_CAP:
                streak_data['status'] = 'cashout'
                streak_data['potential_payout'] = STREAK_PAYOUT_CAP
                logger.info(f"💰 Streak {streak_type} reached payout cap! Cashing out with normal prop.")
                self._post_cashout_ticket(streak_type, STREAK_PAYOUT_CAP)
            elif streak_data['current_leg'] > streak_data['max_legs']:
                streak_data['status'] = 'completed'
                logger.info(f"🎉 Streak {streak_type} completed successfully!")
            else:
                self._post_next_pick(streak_type)
        elif result.lower() == 'loss':
            streak_data['current_streak'] = 0
            streak_data['total_losses'] += 1
            streak_data['last_loss'] = datetime.now().isoformat()
            streak_data['status'] = 'inactive'
            streak_data['current_pick'] = None
            streak_data['next_pick_ready'] = None
            streak_data['current_leg'] = 0
            streak_data['total_multiplier'] = 1.0
            streak_data['legs'] = []
        streak_data['status_line'] = self._generate_status_line(streak_data['legs'], streak_data['max_legs'])
        if streak_data['status'] == 'active':
            potential_payout = streak_data['entry_amount'] * streak_data['total_multiplier']
            streak_data['potential_payout'] = round(potential_payout, 2)
        history_entry = {
            'streak_type': streak_type,
            'result': result,
            'current_leg': current_leg,
            'total_multiplier': streak_data.get('total_multiplier', 1.0),
            'timestamp': datetime.now().isoformat(),
            'current_streak': streak_data['current_streak'],
            'best_streak': streak_data['best_streak']
        }
        self.streak_history.append(history_entry)
        self._save_active_streaks(self.active_streaks)
        self._save_streak_history()
        logger.info(f"✅ Recorded {result} for {streak_type} (Leg {current_leg})")
    
    def _post_next_pick(self, streak_type: str):
        streak_data = self.active_streaks[streak_type]
        next_pick = streak_data.get('next_pick_ready')
        if next_pick:
            from discord_integration.discord_bot import create_discord_bot
            discord_bot = create_discord_bot(self.base_dir)
            message = self._format_underdog_streak_message(streak_type, next_pick, 'immediate')
            discord_bot._post_message(message)
            streak_data['current_pick'] = next_pick
            streak_data['current_multiplier'] = next_pick.get('multiplier', 1.0)
            streak_info = self.streak_types[streak_type]
            streak_data['next_pick_ready'] = self._generate_next_pick(streak_type, streak_info)
            logger.info(f"🚀 Posted immediate next pick for {streak_type} (Leg {streak_data['current_leg']})")
    
    def _post_cashout_ticket(self, streak_type: str, payout: float):
        from discord_integration.discord_bot import create_discord_bot
        discord_bot = create_discord_bot(self.base_dir)
        message = f"💰 **CASH OUT!** {self.streak_types[streak_type]['name']} hit the payout cap (${payout:,.2f})! Posting a normal prop to secure the win."
        discord_bot._post_message(message)
        # Optionally, generate and post a normal prop ticket here
    
    def _format_underdog_streak_message(self, streak_type: str, pick_data: Dict, message_type: str = 'normal') -> str:
        streak_info = self.streak_types[streak_type]
        name = streak_info['name']
        entry_amount = streak_info['entry_amount']
        target_amount = streak_info['target_amount']
        risk_level = streak_info['risk_level']
        streak_data = self.active_streaks[streak_type]
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
        risk_emoji = "💀" if risk_level == 'risky' else "🔥"
        if message_type == 'immediate':
            header = f"🚀 **IMMEDIATE NEXT PICK - {name}** {risk_emoji}"
        else:
            header = f"{risk_emoji} **{name}** {risk_emoji}"
        message = f"""
{header}

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
    
    def post_streak_summary(self):
        from discord_integration.discord_bot import create_discord_bot
        discord_bot = create_discord_bot(self.base_dir)
        message = "🔥 **Active Streaks Summary (2 Normal, 1 Risky, $10 Entry Each)**\n\n"
        for streak_type, streak_data in self.active_streaks.items():
            if streak_data['status'] == 'active':
                streak_info = self.streak_types[streak_type]
                name = streak_info['name']
                current_leg = streak_data.get('current_leg', 1)
                max_legs = streak_data.get('max_legs', 11)
                total_multiplier = streak_data.get('total_multiplier', 1.0)
                potential_payout = streak_data.get('potential_payout', 0)
                status_line = streak_data.get('status_line', '')
                risk_level = streak_data.get('risk_level', 'normal')
                total_wins = streak_data.get('total_wins', 0)
                total_losses = streak_data.get('total_losses', 0)
                win_rate = 0
                if total_wins + total_losses > 0:
                    win_rate = (total_wins / (total_wins + total_losses)) * 100
                risk_emoji = "💀" if risk_level == 'risky' else "🔥"
                message += f"{risk_emoji} **{name}:** Leg {current_leg}/{max_legs} | {total_multiplier}x | ${potential_payout:,.2f}\n"
                message += f"Status: {status_line} | Win Rate: {win_rate:.1f}%\n\n"
        message += "---"
        discord_bot._post_message(message)
        logger.info("📢 Posted streak summary to Discord")
    
    def get_active_streaks(self) -> Dict:
        return self.active_streaks.copy()
    
    def get_streak_history(self) -> List[Dict]:
        return self.streak_history.copy()

def create_streak_manager(base_dir: Path) -> StreakManager:
    return StreakManager(base_dir) 