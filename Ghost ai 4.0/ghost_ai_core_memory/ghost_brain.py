#!/usr/bin/env python3
"""
Ghost AI Brain System

This is the real AI - not a bot. It:
- Remembers every ticket posted
- Uses historical data intelligently  
- Eliminates duplicates completely
- Learns from wins/losses
- Makes smart decisions based on data
- Prevents re-posting the same tickets
"""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import os
import sys
from intelligence.odds_math import OddsMath
from ai_brain.brain_modules.moneyline_sentiment import MoneylineSentimentAnalyzer
from ai_brain.brain_modules.prop_context_filter import PropContextFilter
from ai_brain.brain_modules.ev_evaluator import EVEvaluator
from ai_brain.brain_modules.ml_ticket_trigger import MLTicketTrigger
from ai_brain.brain_modules.public_fade_guard import PublicFadeGuard
from ai_brain.learning_engine import LearningEngine

logger = logging.getLogger('ghost_brain')

class GhostBrain:
    """The real AI brain that remembers, learns, and makes intelligent decisions."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.memory_dir = base_dir / 'ghost_ai_core_memory'
        
        # Memory files
        self.ticket_memory_file = self.memory_dir / 'tickets' / 'posted_tickets_tracking.json'
        self.prop_cache_file = self.memory_dir / 'prop_cache.json'
        self.confidence_cache_file = self.memory_dir / 'confidence_cache.json'
        self.player_history_file = self.memory_dir / 'player_tags' / 'player_history.json'
        self.daily_learning_file = self.memory_dir / 'daily_learning.json'
        
        # Ensure directories exist
        self.ticket_memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.prop_cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.player_history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load memory
        self.ticket_memory = self._load_ticket_memory()
        self.prop_cache = self._load_prop_cache()
        self.confidence_cache = self._load_confidence_cache()
        self.player_history = self._load_player_history()
        self.daily_learning = self._load_daily_learning()
        
        # Today's date
        self.today = datetime.now().strftime('%Y-%m-%d')
        
        self.odds_math = OddsMath()
        # New moneyline intelligence modules
        self.moneyline_sentiment = MoneylineSentimentAnalyzer()
        self.prop_context_filter = PropContextFilter()
        self.ev_evaluator = EVEvaluator()
        self.ml_ticket_trigger = MLTicketTrigger()
        self.public_fade_guard = PublicFadeGuard()
        self.learning_engine = LearningEngine()
        
        logger.info("🧠 Ghost Brain initialized - AI mode activated")
        logger.info(f"   Memory: {len(self.ticket_memory)} tickets tracked")
        logger.info(f"   Cache: {len(self.prop_cache)} props cached")
        logger.info(f"   Players: {len(self.player_history)} players tracked")
    
    def _load_ticket_memory(self) -> Dict:
        """Load ticket memory to prevent duplicates."""
        try:
            if self.ticket_memory_file.exists():
                with open(self.ticket_memory_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading ticket memory: {e}")
        
        return {'tickets': {}, 'daily_tickets': {}, 'last_updated': datetime.now().isoformat()}
    
    def _load_prop_cache(self) -> Dict:
        """Load prop cache to prevent re-processing same props."""
        try:
            if self.prop_cache_file.exists():
                with open(self.prop_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading prop cache: {e}")
        
        return {'props': {}, 'last_updated': datetime.now().isoformat()}
    
    def _load_confidence_cache(self) -> Dict:
        """Load confidence cache to ensure consistent scoring."""
        try:
            if self.confidence_cache_file.exists():
                with open(self.confidence_cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading confidence cache: {e}")
        
        return {'combinations': {}, 'last_updated': datetime.now().isoformat()}
    
    def _load_player_history(self) -> Dict:
        """Load player history for intelligent decision making."""
        try:
            if self.player_history_file.exists():
                with open(self.player_history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading player history: {e}")
        
        return {'players': {}, 'last_updated': datetime.now().isoformat()}
    
    def _load_daily_learning(self) -> Dict:
        """Load daily learning data."""
        try:
            if self.daily_learning_file.exists():
                with open(self.daily_learning_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading daily learning: {e}")
        
        return {'days': {}, 'last_updated': datetime.now().isoformat()}
    
    def _save_ticket_memory(self):
        """Save ticket memory."""
        try:
            self.ticket_memory['last_updated'] = datetime.now().isoformat()
            with open(self.ticket_memory_file, 'w') as f:
                json.dump(self.ticket_memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving ticket memory: {e}")
    
    def _save_prop_cache(self):
        """Save prop cache."""
        try:
            self.prop_cache['last_updated'] = datetime.now().isoformat()
            with open(self.prop_cache_file, 'w') as f:
                json.dump(self.prop_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving prop cache: {e}")
    
    def _save_confidence_cache(self):
        """Save confidence cache."""
        try:
            self.confidence_cache['last_updated'] = datetime.now().isoformat()
            with open(self.confidence_cache_file, 'w') as f:
                json.dump(self.confidence_cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving confidence cache: {e}")
    
    def _save_player_history(self):
        """Save player history."""
        try:
            self.player_history['last_updated'] = datetime.now().isoformat()
            with open(self.player_history_file, 'w') as f:
                json.dump(self.player_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving player history: {e}")
    
    def _save_daily_learning(self):
        """Save daily learning."""
        try:
            self.daily_learning['last_updated'] = datetime.now().isoformat()
            with open(self.daily_learning_file, 'w') as f:
                json.dump(self.daily_learning, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving daily learning: {e}")
    
    def hash_prop(self, prop: Dict) -> str:
        """Create unique hash for a prop."""
        key_parts = [
            prop.get('player_name', ''),
            prop.get('prop_type', ''),
            str(prop.get('line', 0)),
            prop.get('pick_side', ''),
            prop.get('sport', ''),
            self.today
        ]
        return hashlib.md5('_'.join(key_parts).encode()).hexdigest()
    
    def hash_ticket(self, ticket: Dict) -> str:
        """Create unique hash for a ticket combination."""
        selections = ticket.get('selections', [])
        if not selections:
            return ""
        
        # Sort selections for consistent hashing
        sorted_selections = sorted(selections, key=lambda x: (
            x.get('player_name', ''),
            x.get('prop_type', ''),
            x.get('line', 0)
        ))
        
        # Create hash from sorted selections
        hash_parts = []
        for selection in sorted_selections:
            hash_parts.extend([
                selection.get('player_name', ''),
                selection.get('prop_type', ''),
                str(selection.get('line', 0)),
                selection.get('pick_side', ''),
                selection.get('sport', '')
            ])
        
        return hashlib.md5('_'.join(hash_parts).encode()).hexdigest()
    
    def is_prop_already_processed(self, prop: Dict) -> bool:
        """Check if prop has already been processed today."""
        prop_hash = self.hash_prop(prop)
        return prop_hash in self.prop_cache.get('props', {})
    
    def cache_prop(self, prop: Dict, confidence: float):
        """Cache a processed prop."""
        prop_hash = self.hash_prop(prop)
        self.prop_cache.setdefault('props', {})[prop_hash] = {
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'prop': prop
        }
        self._save_prop_cache()
    
    def get_cached_confidence(self, prop: Dict) -> Optional[float]:
        """Get cached confidence for a prop."""
        prop_hash = self.hash_prop(prop)
        cached = self.prop_cache.get('props', {}).get(prop_hash)
        return cached.get('confidence') if cached else None
    
    def is_ticket_already_posted(self, ticket: Dict) -> bool:
        """Check if this exact ticket combination was already posted today."""
        ticket_hash = self.hash_ticket(ticket)
        today_tickets = self.ticket_memory.get('daily_tickets', {}).get(self.today, {})
        return ticket_hash in today_tickets
    
    def mark_ticket_posted(self, ticket: Dict, ticket_id: str):
        """Mark a ticket as posted to prevent duplicates."""
        ticket_hash = self.hash_ticket(ticket)
        
        # Add to daily tickets
        if self.today not in self.ticket_memory.get('daily_tickets', {}):
            self.ticket_memory.setdefault('daily_tickets', {})[self.today] = {}
        
        self.ticket_memory['daily_tickets'][self.today][ticket_hash] = {
            'ticket_id': ticket_id,
            'posted_at': datetime.now().isoformat(),
            'selections': ticket.get('selections', []),
            'confidence': ticket.get('confidence', 0)
        }
        
        # Add to all tickets
        self.ticket_memory.setdefault('tickets', {})[ticket_hash] = {
            'ticket_id': ticket_id,
            'posted_at': datetime.now().isoformat(),
            'date': self.today,
            'selections': ticket.get('selections', []),
            'confidence': ticket.get('confidence', 0)
        }
        
        self._save_ticket_memory()
        logger.info(f"🎫 Marked ticket {ticket_id} as posted (hash: {ticket_hash[:8]})")
    
    def get_cached_combination_confidence(self, selections: List[Dict]) -> Optional[float]:
        """Get cached confidence for a combination of selections."""
        if not selections:
            return None
        
        # Sort selections for consistent hashing
        sorted_selections = sorted(selections, key=lambda x: (
            x.get('player_name', ''),
            x.get('prop_type', ''),
            x.get('line', 0)
        ))
        
        # Create combination hash
        hash_parts = []
        for selection in sorted_selections:
            hash_parts.extend([
                selection.get('player_name', ''),
                selection.get('prop_type', ''),
                str(selection.get('line', 0)),
                selection.get('pick_side', ''),
                selection.get('sport', '')
            ])
        
        combination_hash = hashlib.md5('_'.join(hash_parts).encode()).hexdigest()
        
        cached = self.confidence_cache.get('combinations', {}).get(combination_hash)
        return cached.get('confidence') if cached else None
    
    def cache_combination_confidence(self, selections: List[Dict], confidence: float):
        """Cache confidence for a combination of selections."""
        if not selections:
            return
        
        # Sort selections for consistent hashing
        sorted_selections = sorted(selections, key=lambda x: (
            x.get('player_name', ''),
            x.get('prop_type', ''),
            x.get('line', 0)
        ))
        
        # Create combination hash
        hash_parts = []
        for selection in sorted_selections:
            hash_parts.extend([
                selection.get('player_name', ''),
                selection.get('prop_type', ''),
                str(selection.get('line', 0)),
                selection.get('pick_side', ''),
                selection.get('sport', '')
            ])
        
        combination_hash = hashlib.md5('_'.join(hash_parts).encode()).hexdigest()
        
        self.confidence_cache.setdefault('combinations', {})[combination_hash] = {
            'confidence': confidence,
            'timestamp': datetime.now().isoformat(),
            'selections': sorted_selections
        }
        
        self._save_confidence_cache()
    
    def filter_duplicate_props(self, props: List[Dict]) -> List[Dict]:
        """Remove duplicate props intelligently."""
        seen_props = set()
        filtered_props = []
        
        for prop in props:
            prop_hash = self.hash_prop(prop)
            
            if prop_hash not in seen_props:
                seen_props.add(prop_hash)
                filtered_props.append(prop)
            else:
                logger.info(f"🧠 Filtered duplicate prop: {prop.get('player_name', 'Unknown')} {prop.get('prop_type', 'Unknown')}")
        
        logger.info(f"🧠 Filtered {len(props) - len(filtered_props)} duplicate props")
        return filtered_props
    
    def get_player_performance_history(self, player_name: str, prop_type: str) -> Dict:
        """Get player's historical performance for intelligent decisions."""
        player_data = self.player_history.get('players', {}).get(player_name, {})
        prop_history = player_data.get(prop_type, {})
        
        return {
            'hit_rate': prop_history.get('hit_rate', 0.5),
            'total_picks': prop_history.get('total_picks', 0),
            'last_5_results': prop_history.get('last_5_results', []),
            'streak': prop_history.get('current_streak', 0),
            'confidence_adjustment': prop_history.get('confidence_adjustment', 0.0)
        }
    
    def update_player_performance(self, player_name: str, prop_type: str, result: str, confidence: float):
        """Update player performance after a game."""
        if player_name not in self.player_history.get('players', {}):
            self.player_history.setdefault('players', {})[player_name] = {}
        
        if prop_type not in self.player_history['players'][player_name]:
            self.player_history['players'][player_name][prop_type] = {
                'hit_rate': 0.5,
                'total_picks': 0,
                'last_5_results': [],
                'current_streak': 0,
                'confidence_adjustment': 0.0
            }
        
        player_prop = self.player_history['players'][player_name][prop_type]
        
        # Update hit rate
        if result == 'WIN':
            player_prop['current_streak'] = max(0, player_prop.get('current_streak', 0) + 1)
        elif result == 'LOSS':
            player_prop['current_streak'] = min(0, player_prop.get('current_streak', 0) - 1)
        
        # Update last 5 results
        last_5 = player_prop.get('last_5_results', [])
        last_5.append(result)
        if len(last_5) > 5:
            last_5.pop(0)
        player_prop['last_5_results'] = last_5
        
        # Calculate new hit rate
        wins = last_5.count('WIN')
        player_prop['hit_rate'] = wins / len(last_5) if last_5 else 0.5
        player_prop['total_picks'] = player_prop.get('total_picks', 0) + 1
        
        # Adjust confidence based on performance
        if player_prop['hit_rate'] < 0.4:
            player_prop['confidence_adjustment'] = -0.1
        elif player_prop['hit_rate'] > 0.7:
            player_prop['confidence_adjustment'] = 0.1
        else:
            player_prop['confidence_adjustment'] = 0.0
        
        self._save_player_history()
        logger.info(f"🧠 Updated {player_name} {prop_type}: hit_rate={player_prop['hit_rate']:.2f}, streak={player_prop['current_streak']}")
    
    def should_post_today(self) -> bool:
        """Determine if AI should post tickets today based on learning."""
        # TEMPORARILY DISABLED - Always allow posting
        return True
        
        # today_learning = self.daily_learning.get('days', {}).get(self.today, {})
        
        # # Check if we already processed today's props
        # if today_learning.get('props_processed', False):
        #     self.think(f"Already processed props for {self.today} - skipping")
        #     return False
        
        # # Check recent performance
        # recent_days = list(self.daily_learning.get('days', {}).keys())[-7:]
        # if len(recent_days) >= 3:
        #     recent_performance = []
        #     for day in recent_days[-3:]:
        #         day_data = self.daily_learning['days'].get(day, {})
        #         if day_data.get('tickets_posted', 0) > 0:
        #             win_rate = day_data.get('win_rate', 0.0)
        #             recent_performance.append(win_rate)
            
        #     avg_recent_performance = sum(recent_performance) / len(recent_performance) if recent_performance else 0.5
            
        #     # If recent performance is poor, reduce posting
        #     if avg_recent_performance < 0.3:
        #         self.think(f"Recent performance poor ({avg_recent_performance:.2f}), reducing ticket volume")
        #         return False
        
        # return True
    
    def mark_props_processed(self):
        """Mark that props have been processed for today."""
        if self.today not in self.daily_learning.get('days', {}):
            self.daily_learning.setdefault('days', {})[self.today] = {}
        
        self.daily_learning['days'][self.today]['props_processed'] = True
        self.daily_learning['days'][self.today]['processed_at'] = datetime.now().isoformat()
        self._save_daily_learning()
        self.think(f"Marked props as processed for {self.today}")
    
    def is_props_already_processed_today(self) -> bool:
        """Check if props have already been processed today."""
        today_learning = self.daily_learning.get('days', {}).get(self.today, {})
        return today_learning.get('props_processed', False)
    
    def get_optimal_ticket_count(self) -> int:
        """Get optimal number of tickets to post based on learning."""
        recent_days = list(self.daily_learning.get('days', {}).keys())[-5:]
        if not recent_days:
            return 5  # Default
        
        recent_performance = []
        for day in recent_days:
            day_data = self.daily_learning['days'].get(day, {})
            if day_data.get('tickets_posted', 0) > 0:
                win_rate = day_data.get('win_rate', 0.0)
                recent_performance.append(win_rate)
        
        if not recent_performance:
            return 5
        
        avg_performance = sum(recent_performance) / len(recent_performance)
        
        if avg_performance > 0.7:
            return 8  # Hot streak - post more
        elif avg_performance < 0.3:
            return 2  # Cold streak - post less
        else:
            return 5  # Normal
    
    def log_daily_performance(self, tickets_posted: int, wins: int, losses: int, pushes: int):
        """Log daily performance for learning."""
        total_tickets = wins + losses + pushes
        win_rate = wins / total_tickets if total_tickets > 0 else 0.0
        
        self.daily_learning.setdefault('days', {})[self.today] = {
            'tickets_posted': tickets_posted,
            'wins': wins,
            'losses': losses,
            'pushes': pushes,
            'win_rate': win_rate,
            'timestamp': datetime.now().isoformat()
        }
        
        self._save_daily_learning()
        logger.info(f"🧠 Logged daily performance: {wins}W-{losses}L-{pushes}P ({win_rate:.2f} win rate)")
    
    def think(self, message: str):
        """Ghost thinks out loud."""
        logger.info(f"🧠 GHOST THOUGHT: {message}")
    
    def is_realistic_prop(self, prop: dict) -> bool:
        """Return True if the prop matches real sportsbook/Underdog/PrizePicks lines and odds."""
        prop_type = prop.get('prop_type', '')
        line = prop.get('line', None)
        odds = prop.get('odds', 0)
        sport = prop.get('sport', '').upper()
        # MLB rules
        if sport == 'MLB':
            if prop_type == 'Hits':
                return False
            if prop_type == 'HRR' and line not in [1.5, 2.5]:
                return False
            if prop_type in ['Runs', 'RBIs', 'Home Runs'] and line != 0.5:
                return False
            if prop_type == 'Fantasy Score' and (line is None or line < 6 or line > 25):
                return False
            if prop_type == 'Strikeouts' and line not in [0.5, 1.5]:
                return False
            if odds < -170 or odds > 400:
                return False
            return True
        # WNBA rules
        if sport == 'WNBA':
            if prop_type == 'Points' and (line is None or line < 8.5 or line > 35.5):
                return False
            if prop_type == 'Rebounds' and (line is None or line < 2.5 or line > 15.5):
                return False
            if prop_type == 'Assists' and (line is None or line < 1.5 or line > 10.5):
                return False
            if prop_type == 'Fantasy Score' and (line is None or line < 10 or line > 60):
                return False
            if odds < -170 or odds > 400:
                return False
            return True
        # Default: reject unknowns
        return False

    def _prop_is_odds_eligible(self, prop: Dict) -> Tuple[bool, str]:
        """Return (True, reason) if prop is eligible by odds intelligence."""
        odds = prop.get('odds', 0)
        implied_prob = self.odds_math.implied_probability(odds)
        if implied_prob < 0.30 or implied_prob > 0.80:
            return False, f"Implied probability {implied_prob:.2f} out of range"
        # Add more sharp signal checks here as needed
        return True, "Eligible by odds"

    def analyze_props_intelligently(self, props: List[Dict]) -> List[Dict]:
        """Analyze props using odds intelligence, memory, and sharp signals."""
        eligible_props = []
        for prop in props:
            eligible, reason = self._prop_is_odds_eligible(prop)
            if not eligible:
                logger.info(f"⛔ Skipped {prop.get('player_name','?')} {prop.get('prop_type','?')} @ {prop.get('odds','?')}: {reason}")
                continue
            # Odds-driven confidence
            prop['implied_prob'] = self.odds_math.implied_probability(prop.get('odds', 0))
            prop['confidence'] = prop['implied_prob']
            eligible_props.append(prop)
        return eligible_props

    def build_combo_if_strong(self, combo_components: List[Dict]) -> Optional[Dict]:
        """Only build combo if all components are strong by odds/trend/memory."""
        for comp in combo_components:
            eligible, reason = self._prop_is_odds_eligible(comp)
            if not eligible:
                logger.info(f"⛔ Combo suppressed: {comp.get('player_name','?')} {comp.get('prop_type','?')} weak: {reason}")
                return None
        # If all components are strong, build combo
        combo_odds = sum(c.get('odds', 0) for c in combo_components) / len(combo_components)
        combo = {
            'player_name': combo_components[0].get('player_name', ''),
            'prop_type': '+'.join([c.get('prop_type','') for c in combo_components]),
            'odds': combo_odds,
            'confidence': min(c.get('confidence', 0.5) for c in combo_components),
            'components': combo_components,
            'reason': 'All components strong by odds intelligence'
        }
        logger.info(f"✅ Combo built: {combo['player_name']} {combo['prop_type']} @ {combo['odds']}")
        return combo
    
    def validate_ticket_before_posting(self, ticket: Dict) -> bool:
        """Validate ticket before posting to prevent bad decisions."""
        selections = ticket.get('selections', [])
        
        if not selections:
            self.think("Rejecting ticket - no selections")
            return False
        
        # Check if already posted
        if self.is_ticket_already_posted(ticket):
            self.think("Rejecting ticket - already posted today")
            return False
        
        # Check for duplicate players
        players = [s.get('player_name', '') for s in selections]
        if len(players) != len(set(players)):
            self.think("Rejecting ticket - duplicate players")
            return False
        
        # Check for duplicate games - CRITICAL VALIDATION
        games = set()
        for selection in selections:
            game_key = selection.get('game_key', '')
            if game_key:
                games.add(game_key)
            else:
                # Try to extract from team info for moneyline tickets
                team = selection.get('team', '')
                opponent = selection.get('opponent', '')
                if team and opponent:
                    game_id = f"{team}_vs_{opponent}"
                    games.add(game_id)
        
        # If all selections are from the same game, reject
        if len(games) == 1:
            self.think(f"Rejecting ticket - all selections from same game: {list(games)[0]}")
            return False
        
        # Check confidence - very low threshold
        ticket_confidence = ticket.get('confidence', 0)
        if ticket_confidence < 0.15:  # Very low threshold
            self.think(f"Rejecting ticket - extremely low confidence ({ticket_confidence:.2f})")
            return False
        
        # REMOVED HISTORICAL PERFORMANCE CHECKS - Let all tickets through
        # Only check for basic issues
        
        self.think(f"Ticket validated - {len(selections)} legs from {len(games)} different games, confidence {ticket_confidence:.2f}")
        return True
    
    def create_combo_hash(self, selections: List[Dict]) -> str:
        """Create unique hash for a combination of selections."""
        if not selections:
            return ""
        
        # Sort selections for consistent hashing
        sorted_selections = sorted(selections, key=lambda x: (
            x.get('player_name', ''),
            x.get('prop_type', ''),
            x.get('line', 0),
            x.get('pick_side', '')
        ))
        
        # Create hash from sorted selections
        hash_parts = []
        for selection in sorted_selections:
            hash_parts.extend([
                selection.get('player_name', ''),
                selection.get('prop_type', ''),
                str(selection.get('line', 0)),
                selection.get('pick_side', ''),
                selection.get('sport', '')
            ])
        
        return hashlib.md5('_'.join(hash_parts).encode()).hexdigest()
    
    def is_combo_already_scored(self, selections: List[Dict]) -> bool:
        """Check if this combination has already been scored."""
        combo_hash = self.create_combo_hash(selections)
        return combo_hash in self.confidence_cache.get('combinations', {})
    
    def get_ai_objectives(self) -> Dict:
        """Get AI objectives for today's session."""
        recent_performance = self.get_recent_performance()
        
        objectives = {
            'target_tickets': 15,  # Increased from 8
            'min_confidence': 0.10,  # TEMPORARILY LOWERED from 0.20
            'max_risk': 'high',  # Changed from medium
            'focus_areas': ['MLB', 'WNBA'],
            'avoid_players': [],
            'target_players': []
        }
        
        # Adjust based on recent performance
        if recent_performance.get('win_rate', 0.5) > 0.7:
            objectives['target_tickets'] = 20  # Increased
            objectives['max_risk'] = 'high'
            objectives['min_confidence'] = 0.05  # Even lower for hot streaks
            self.think("Hot streak detected - increasing ticket volume and lowering confidence threshold")
        elif recent_performance.get('win_rate', 0.5) < 0.3:
            objectives['target_tickets'] = 8  # Still reasonable
            objectives['max_risk'] = 'medium'
            objectives['min_confidence'] = 0.15  # Lowered from 0.25
            self.think("Cold streak detected - reducing ticket volume but keeping reasonable confidence")
        
        return objectives
    
    def get_recent_performance(self) -> Dict:
        """Get recent performance metrics."""
        recent_days = list(self.daily_learning.get('days', {}).keys())[-5:]
        if not recent_days:
            return {'win_rate': 0.5, 'total_tickets': 0}
        
        total_wins = 0
        total_tickets = 0
        
        for day in recent_days:
            day_data = self.daily_learning['days'].get(day, {})
            wins = day_data.get('wins', 0)
            losses = day_data.get('losses', 0)
            pushes = day_data.get('pushes', 0)
            
            total_wins += wins
            total_tickets += wins + losses + pushes
        
        win_rate = total_wins / total_tickets if total_tickets > 0 else 0.5
        
        return {
            'win_rate': win_rate,
            'total_tickets': total_tickets,
            'recent_days': len(recent_days)
        }
    
    def get_strategy_engine(self) -> Dict:
        """Get strategy engine recommendations."""
        recent_performance = self.get_recent_performance()
        objectives = self.get_ai_objectives()
        
        strategy = {
            'aggression_level': 'medium',
            'confidence_threshold': objectives['min_confidence'],
            'max_tickets': objectives['target_tickets'],
            'focus_sports': objectives['focus_areas'],
            'risk_tolerance': objectives['max_risk']
        }
        
        # Adjust strategy based on performance
        if recent_performance['win_rate'] > 0.7:
            strategy['aggression_level'] = 'high'
            strategy['confidence_threshold'] = max(0.45, strategy['confidence_threshold'] - 0.05)
        elif recent_performance['win_rate'] < 0.3:
            strategy['aggression_level'] = 'low'
            strategy['confidence_threshold'] = min(0.65, strategy['confidence_threshold'] + 0.05)
        
        self.think(f"Strategy: {strategy['aggression_level']} aggression, {strategy['confidence_threshold']:.2f} confidence threshold")
        return strategy
    
    def check_for_red_flags(self, ticket: Dict) -> List[str]:
        """Check for red flags in a ticket."""
        red_flags = []
        selections = ticket.get('selections', [])
        
        # Check for too many legs
        if len(selections) > 8:
            red_flags.append("Too many legs (>8)")
        
        # Check for duplicate players
        players = [s.get('player_name', '') for s in selections]
        if len(players) != len(set(players)):
            red_flags.append("Duplicate players")
        
        # Check for impossible odds
        for selection in selections:
            odds = selection.get('odds', 0)
            if odds < -500 or odds > 1000:
                red_flags.append(f"Impossible odds: {odds}")
        
        # Check for poor player history
        for selection in selections:
            player_name = selection.get('player_name', '')
            prop_type = selection.get('prop_type', '')
            history = self.get_player_performance_history(player_name, prop_type)
            
            if history.get('hit_rate', 0.5) < 0.2 and history.get('total_picks', 0) > 5:
                red_flags.append(f"Poor player history: {player_name} ({history['hit_rate']:.2f} hit rate)")
        
        return red_flags
    
    def enforce_no_duplicates_policy(self, new_tickets: List[Dict]) -> List[Dict]:
        """Enforce strict no-duplicates policy including different games requirement."""
        filtered_tickets = []
        seen_combinations = set()
        
        for ticket in new_tickets:
            combo_hash = self.create_combo_hash(ticket.get('selections', []))
            
            # Check for duplicate combinations
            if combo_hash in seen_combinations:
                self.think(f"Ticket rejected - duplicate combination")
                continue
            
            # Check if already posted
            if self.is_ticket_already_posted(ticket):
                self.think(f"Ticket rejected - already posted today")
                continue
            
            # Check for different games requirement
            if not self._has_different_games(ticket):
                self.think(f"Ticket rejected - all selections from same game")
                continue
            
            # All checks passed
            seen_combinations.add(combo_hash)
            filtered_tickets.append(ticket)
            self.think(f"Ticket approved - unique combination from different games")
        
        self.think(f"Filtered {len(new_tickets) - len(filtered_tickets)} duplicate/invalid tickets")
        return filtered_tickets
    
    def _has_different_games(self, ticket: Dict) -> bool:
        """Check if ticket has selections from different games."""
        selections = ticket.get('selections', [])
        if len(selections) <= 1:
            return True  # Single selection is always valid
        
        games = set()
        for selection in selections:
            # For prop tickets
            game_key = selection.get('game_key', '')
            if game_key:
                games.add(game_key)
            else:
                # For moneyline tickets
                team = selection.get('team', '')
                opponent = selection.get('opponent', '')
                if team and opponent:
                    game_id = f"{team}_vs_{opponent}"
                    games.add(game_id)
        
        # Must have at least 2 different games
        return len(games) >= 2
    
    def cleanup_old_memory(self):
        """Clean up old memory entries to prevent bloat."""
        try:
            # Clean up old daily tickets (keep last 30 days)
            daily_tickets = self.ticket_memory.get('daily_tickets', {})
            cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            old_dates = [date for date in daily_tickets.keys() if date < cutoff_date]
            for old_date in old_dates:
                del daily_tickets[old_date]
                logger.info(f"🧠 Cleaned up old tickets from {old_date}")

            # Clean up old prop cache (keep last 7 days)
            props_cache = self.prop_cache.get('props', {})
            cutoff_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            old_props = [prop_hash for prop_hash, prop_data in props_cache.items() 
                         if prop_data.get('date', '') < cutoff_date]
            for old_prop in old_props:
                del props_cache[old_prop]

            self._save_ticket_memory()
            self._save_prop_cache()

            logger.info(f"🧠 Memory cleanup completed")
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
    
    def detect_old_tickets(self) -> List[Dict]:
        """Detect tickets that are old and need to be cleaned up."""
        old_tickets = []
        today = datetime.now()
        
        for ticket_hash, ticket_data in self.ticket_memory.get('tickets', {}).items():
            posted_at = ticket_data.get('posted_at')
            if posted_at:
                try:
                    posted_time = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                    age_hours = (today - posted_time).total_seconds() / 3600
                    
                    # Consider tickets old after 24 hours
                    if age_hours > 24:
                        old_tickets.append({
                            'ticket_hash': ticket_hash,
                            'ticket_id': ticket_data.get('ticket_id'),
                            'posted_at': posted_at,
                            'age_hours': age_hours,
                            'selections': ticket_data.get('selections', [])
                        })
                except Exception as e:
                    logger.error(f"Error parsing ticket date: {e}")
        
        if old_tickets:
            logger.info(f"🧠 Detected {len(old_tickets)} old tickets that need cleanup")
        
        return old_tickets
    
    def identify_ticket_gaps(self) -> Dict:
        """Identify gaps in ticket generation that need to be filled."""
        gaps = {
            'mlb_gaps': [],
            'wnba_gaps': [],
            'total_gaps': 0
        }
        
        today = datetime.now()
        current_hour = today.hour
        
        # Check if we're in active hours (12 PM - 1 AM ET)
        # Active hours: 12 PM (hour 12) to 1 AM (hour 1) = 12 <= hour <= 23 OR hour < 1
        is_active_hours = current_hour >= 12 or current_hour < 1
        
        if not is_active_hours:
            logger.info("🧠 Outside active hours (12 PM - 1 AM ET), no gaps to fill")
            return gaps
        
        # Get today's tickets
        today_tickets = self.ticket_memory.get('daily_tickets', {}).get(self.today, {})
        ticket_count = len(today_tickets)
        
        # Check optimal ticket count
        optimal_count = self.get_optimal_ticket_count()
        
        if ticket_count < optimal_count:
            gap_size = optimal_count - ticket_count
            gaps['total_gaps'] = gap_size
            
            # Determine sport-specific gaps based on available games
            mlb_games = self._get_available_mlb_games()
            wnba_games = self._get_available_wnba_games()
            
            if mlb_games:
                gaps['mlb_gaps'] = mlb_games[:gap_size // 2]
            
            if wnba_games:
                gaps['wnba_gaps'] = wnba_games[:gap_size // 2]
            
            logger.info(f"🧠 Identified {gap_size} ticket gaps: {len(gaps['mlb_gaps'])} MLB, {len(gaps['wnba_gaps'])} WNBA")
        
        return gaps
    
    def _get_available_mlb_games(self) -> List[str]:
        """Get list of available MLB games for today."""
        try:
            mlb_props_dir = Path('mlb_game_props')
            if not mlb_props_dir.exists():
                return []
            
            available_games = []
            for game_file in mlb_props_dir.glob('*.json'):
                if game_file.name.startswith('props_mlb_'):
                    game_key = game_file.stem
                    available_games.append(game_key)
            
            return available_games
        except Exception as e:
            logger.error(f"Error getting available MLB games: {e}")
            return []
    
    def _get_available_wnba_games(self) -> List[str]:
        """Get list of available WNBA games for today."""
        try:
            wnba_props_dir = Path('wnba_game_props')
            if not wnba_props_dir.exists():
                return []
            
            available_games = []
            for game_file in wnba_props_dir.glob('*.json'):
                if game_file.name.startswith('props_wnba_'):
                    game_key = game_file.stem
                    available_games.append(game_key)
            
            return available_games
        except Exception as e:
            logger.error(f"Error getting available WNBA games: {e}")
            return []
    
    def should_generate_new_tickets(self) -> bool:
        """Determine if new tickets should be generated based on gaps and timing."""
        # Check if we're in active hours
        current_hour = datetime.now().hour
        # Active hours: 12 PM (hour 12) to 1 AM (hour 1) = 12 <= hour <= 23 OR hour < 1
        is_active_hours = current_hour >= 12 or current_hour < 1
        
        if not is_active_hours:
            self.think("Outside active hours (12 PM - 1 AM ET) - no new ticket generation")
            return False
        
        # Check for gaps
        gaps = self.identify_ticket_gaps()
        has_gaps = gaps['total_gaps'] > 0
        
        if has_gaps:
            self.think(f"Detected {gaps['total_gaps']} ticket gaps - should generate new tickets")
            return True
        
        # Check if we have recent tickets (within last 4 hours)
        recent_tickets = self._get_recent_tickets(hours=4)
        if len(recent_tickets) == 0:
            self.think("No recent tickets found - should generate new tickets")
            return True
        
        self.think("No gaps detected and recent tickets exist - no new generation needed")
        return False
    
    def _get_recent_tickets(self, hours: int = 4) -> List[Dict]:
        """Get tickets posted within the last N hours."""
        recent_tickets = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for ticket_hash, ticket_data in self.ticket_memory.get('tickets', {}).items():
            posted_at = ticket_data.get('posted_at')
            if posted_at:
                try:
                    posted_time = datetime.fromisoformat(posted_at.replace('Z', '+00:00'))
                    if posted_time > cutoff_time:
                        recent_tickets.append(ticket_data)
                except Exception as e:
                    logger.error(f"Error parsing ticket date: {e}")
        
        return recent_tickets
    
    def trigger_ticket_generation(self) -> Dict:
        """Trigger new ticket generation based on gaps and analysis."""
        analysis = {
            'should_generate': False,
            'reason': '',
            'gaps': {},
            'available_games': {}
        }
        
        # Check if we should generate new tickets
        should_generate = self.should_generate_new_tickets()
        analysis['should_generate'] = should_generate
        
        if should_generate:
            # Get gaps
            gaps = self.identify_ticket_gaps()
            analysis['gaps'] = gaps
            
            # Get available games
            analysis['available_games'] = {
                'mlb': self._get_available_mlb_games(),
                'wnba': self._get_available_wnba_games()
            }
            
            analysis['reason'] = f"Detected {gaps['total_gaps']} ticket gaps"
            
            self.think(f"Triggering ticket generation: {gaps['total_gaps']} gaps, "
                      f"{len(analysis['available_games']['mlb'])} MLB games, "
                      f"{len(analysis['available_games']['wnba'])} WNBA games")
        else:
            analysis['reason'] = "No gaps detected or outside active hours"
        
        return analysis
    
    def is_in_low_power_mode(self) -> bool:
        """Check if AI is in low power listening mode."""
        # AI is always in low power mode, listening for commands
        return True
    
    def wake_up_for_command(self, command: str) -> Dict:
        """Wake up AI for a specific command."""
        self.think(f"🔔 Waking up for command: {command}")
        
        response = {
            'command': command,
            'wake_time': datetime.now().isoformat(),
            'status': 'awake',
            'actions': []
        }
        
        # Handle different commands
        if command.lower() in ['imbow', 'inbox', 'check']:
            response['actions'].append('check_inbox')
            self.think("📬 Checking inbox for new orders")
            
        elif command.lower() in ['generate', 'tickets', 'new']:
            response['actions'].append('generate_tickets')
            self.think("🎫 Generating new tickets on demand")
            
        elif command.lower() in ['cleanup', 'clean']:
            response['actions'].append('run_cleanup')
            self.think("🧹 Running cleanup on demand")
            
        elif command.lower() in ['status', 'report']:
            response['actions'].append('generate_report')
            self.think("📊 Generating status report")
            
        else:
            response['actions'].append('unknown_command')
            self.think(f"❓ Unknown command: {command}")
        
        return response
    
    def should_generate_new_tickets_always_listening(self) -> bool:
        """Determine if new tickets should be generated (always listening mode)."""
        # In low power mode, check for gaps regardless of time
        gaps = self.identify_ticket_gaps()
        has_gaps = gaps['total_gaps'] > 0
        
        if has_gaps:
            self.think(f"Detected {gaps['total_gaps']} ticket gaps - should generate new tickets")
            return True
        
        # Check if we have recent tickets (within last 6 hours instead of 4)
        recent_tickets = self._get_recent_tickets(hours=6)
        if len(recent_tickets) == 0:
            self.think("No recent tickets found - should generate new tickets")
            return True
        
        self.think("No gaps detected and recent tickets exist - no new generation needed")
        return False
    
    def identify_ticket_gaps_always_listening(self) -> Dict:
        """Identify gaps in ticket generation (always listening mode)."""
        gaps = {
            'mlb_gaps': [],
            'wnba_gaps': [],
            'total_gaps': 0
        }
        
        # Get today's tickets
        today_tickets = self.ticket_memory.get('daily_tickets', {}).get(self.today, {})
        ticket_count = len(today_tickets)
        
        # Check optimal ticket count
        optimal_count = self.get_optimal_ticket_count()
        
        if ticket_count < optimal_count:
            gap_size = optimal_count - ticket_count
            gaps['total_gaps'] = gap_size
            
            # Determine sport-specific gaps based on available games
            mlb_games = self._get_available_mlb_games()
            wnba_games = self._get_available_wnba_games()
            
            if mlb_games:
                gaps['mlb_gaps'] = mlb_games[:gap_size // 2]
            
            if wnba_games:
                gaps['wnba_gaps'] = wnba_games[:gap_size // 2]
            
            logger.info(f"🧠 Identified {gap_size} ticket gaps: {len(gaps['mlb_gaps'])} MLB, {len(gaps['wnba_gaps'])} WNBA")
        
        return gaps

    def analyze_market_movement(self, prop):
        """Stub for market movement analysis (future ML/sharp logic)."""
        logger.info("[STUB] analyze_market_movement called")
        pass

    def track_clv(self, posted_prop, closing_prop):
        """Stub for CLV tracking (future ML/sharp logic)."""
        logger.info("[STUB] track_clv called")
        pass

    def detect_trap(self, prop):
        """Stub for trap detection (future ML/sharp logic)."""
        logger.info("[STUB] detect_trap called")
        pass

    def moneyline_pipeline(self, props: List[Dict], moneyline_data: List[Dict], posted_ml_tickets: List[str]) -> Dict:
        """
        Full moneyline-driven pipeline:
        - Runs sentiment/trap analysis
        - Applies prop context filter
        - Evaluates EV for ML bets
        - Triggers ML tickets if enough props align
        - Uses public fade guard to block/penalize traps
        Returns dict with updated props, ML tickets, and logs.
        """
        logs = []
        # 1. Sentiment/trap analysis
        ml_sentiment = self.moneyline_sentiment.aggregate_moneylines(moneyline_data)
        logs.append({'step': 'sentiment', 'result': ml_sentiment})
        # 2. Prop context filter
        props_with_context = self.prop_context_filter.apply_ml_context(props, ml_sentiment)
        logs.append({'step': 'prop_context', 'result': props_with_context})
        # 3. EV evaluation (stub: loop through teams in ml_sentiment)
        ml_ev_results = {}
        for team, team_data in ml_sentiment.items():
            ghost_win_prob = team_data.get('ghost_win_prob', 0.5)
            payout = team_data.get('payout', 1.0)
            ev = self.ev_evaluator.calculate_ev(ghost_win_prob, payout)
            ml_ev_results[team] = ev
            self.ev_evaluator.log_ev_calculation(team, team_data.get('consensus_odds', 0), ghost_win_prob, ev)
        logs.append({'step': 'ev', 'result': ml_ev_results})
        # 4. ML ticket trigger
        ml_tickets = []
        for team, ev in ml_ev_results.items():
            if self.ev_evaluator.is_premium_ev(ev) and not self.ml_ticket_trigger.is_duplicate_ml_ticket(team, posted_ml_tickets):
                team_props = [p for p in props_with_context if p.get('team') == team]
                if self.ml_ticket_trigger.should_post_ml(team_props, ml_sentiment.get(team, {})):
                    ml_tickets.append({'team': team, 'ev': ev, 'props': team_props})
        logs.append({'step': 'ml_ticket_trigger', 'result': ml_tickets})
        # 5. Public fade guard
        for ticket in ml_tickets:
            team = ticket['team']
            team_data = ml_sentiment.get(team, {})
            public_bet_pct = team_data.get('public_bet_pct', 0.5)
            line_movement = team_data.get('line_movement', 0)
            odds = team_data.get('consensus_odds', 0)
            if self.public_fade_guard.is_trap(team, odds, public_bet_pct, line_movement):
                ticket['fade_public'] = True
                ticket['confidence_penalty'] = 0.12
                logs.append({'step': 'public_fade_guard', 'result': f'Faded {team} ML for public trap'})
        return {'props': props_with_context, 'ml_tickets': ml_tickets, 'logs': logs}

    def _auto_tune_from_learning(self, summary):
        # Example: If ChatGPT hit rate < 0.5, reduce escalation; if > 0.7, increase
        hit_rate = summary.get('chatgpt_hit_rate', {}).get('hit_rate')
        if hit_rate is not None:
            if hit_rate < 0.5:
                # Lower ChatGPT usage for tennis/golf
                self.FEATURES['chatgpt_escalation'] = False
            elif hit_rate > 0.7:
                self.FEATURES['chatgpt_escalation'] = True
        # Example: If trap detection accuracy < 0.4, flag for review
        trap_acc = summary.get('trap_detection_accuracy', {}).get('accuracy')
        if trap_acc is not None and trap_acc < 0.4:
            print('[GhostBrain] Trap detection accuracy low—review needed.')
        # Add more auto-tuning as desired

    def get_recent_learning(self, n=7):
        return self.learning_engine.get_recent_learning(n)

def create_ghost_brain(base_dir: Path) -> GhostBrain:
    """Create and return a GhostBrain instance."""
    return GhostBrain(base_dir) 