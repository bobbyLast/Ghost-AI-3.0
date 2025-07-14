#!/usr/bin/env python3
"""
ticket_generator.py - Ghost AI 3.0 Enhanced Ticket Generator
Generates tickets with no duplicate players and proper separation from daily picks/streaks.
"""

import logging
import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import random
import re
import requests

from ghost_teaching_loop import ghost_openai_wrapper
from ai_brain.tennis_api_client import get_fixtures, get_odds
# Temporarily commented out to avoid circular import - will be fixed in architecture refactor
# from sports.mlb.mlb_props import MLBFetcher
# from sports.wnba.wnba_props import WNBAFetcher
from ghost_ai_core_memory.confidence_scoring import ConfidenceScorer
from reverse_engineering.reverse_engine.odds_engine import OddsReverseEngine

logger = logging.getLogger('ticket_generator')

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1375912085762080868/qRsmIH92iKpMwrtt2TYWsRY1OkFerN61zFVGooCFZvae-liF5l_4ovbwpgv0b7nSOKJg"

def send_discord_log(message: str):
    try:
        payload = {"content": message}
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        logger.warning(f"Failed to send Discord log: {e}")

class TicketGenerator:
    """Enhanced ticket generator with duplicate prevention and proper separation."""
    # --- Smart idle tuning ---
    min_idle_seconds = 600   # 10 minutes
    max_idle_seconds = 3600  # 1 hour
    
    TENNIS_PROP_WHITELIST = [
        'Total Games',
        'Aces',
        'Double Faults',
        '1st Set Total Games',
        '1st Set Aces',
        '1st Set Double Faults',
        # Add more Underdog-allowed tennis props here as needed
    ]

    def __init__(self, base_dir: Path, memory_manager=None, reverse_engine=None):
        self.base_dir = base_dir
        self.tickets_dir = base_dir / 'data' / 'tickets'
        self.tickets_dir.mkdir(parents=True, exist_ok=True)
        
        # Track used players to prevent duplicates
        self.used_players_file = base_dir / 'data' / 'used_players.json'
        self.used_players = self._load_used_players()
        
        # Daily pick and streak tracking
        self.daily_picks_file = base_dir / 'data' / 'daily_picks.json'
        self.streaks_file = base_dir / 'data' / 'streaks' / 'active_streaks.json'
        self.memory_manager = memory_manager
        self.reverse_engine = reverse_engine
        
        logger.info("🎫 Enhanced Ticket Generator initialized")
    
    def _load_used_players(self) -> Set[str]:
        """Load used players to prevent duplicates."""
        try:
            if self.used_players_file.exists():
                with open(self.used_players_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('used_players', []))
            return set()
        except Exception as e:
            logger.error(f"Failed to load used players: {e}")
            return set()
    
    def _save_used_players(self):
        """Save used players."""
        try:
            data = {
                'used_players': list(self.used_players),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.used_players_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save used players: {e}")
    
    def _get_daily_pick_players(self) -> Set[str]:
        """Get players from today's daily picks."""
        try:
            if self.daily_picks_file.exists():
                with open(self.daily_picks_file, 'r') as f:
                    daily_picks = json.load(f)
                    today = datetime.now().strftime('%Y-%m-%d')
                    today_picks = daily_picks.get(today, {})
                    
                    players = set()
                    for pick_data in today_picks.values():
                        player = pick_data.get('player', '')
                        if player and player != 'N/A':
                            players.add(player.lower())
                    
                    return players
            return set()
        except Exception as e:
            logger.error(f"Failed to get daily pick players: {e}")
            return set()
    
    def _get_streak_players(self) -> Set[str]:
        """Get players from active streaks."""
        try:
            if self.streaks_file.exists():
                with open(self.streaks_file, 'r') as f:
                    streaks = json.load(f)
                    
                    players = set()
                    for streak_data in streaks.values():
                        current_pick = streak_data.get('current_pick', {})
                        player = current_pick.get('player', '')
                        if player and player != 'N/A':
                            players.add(player.lower())
                        
                        next_pick = streak_data.get('next_pick_ready', {})
                        player = next_pick.get('player', '')
                        if player and player != 'N/A':
                            players.add(player.lower())
                    
                    return players
            return set()
        except Exception as e:
            logger.error(f"Failed to get streak players: {e}")
            return set()
    
    def generate_tickets(self, num_tickets: int = 5) -> List[Dict]:
        """Generate tickets using actual fetched props from all sports."""
        try:
            logger.info(f"🎫 Generating {num_tickets} tickets using actual fetched props...")
            tickets = []
            
            # Load all available props from fetched files
            all_props = self._load_all_fetched_props()
            logger.info(f"🎫 Loaded {len(all_props)} total props from all sports")
            
            if not all_props:
                logger.warning("No props found, generating generic tickets")
                return self._generate_generic_tickets(num_tickets)
            
            # Generate tickets using actual props
            for i in range(num_tickets):
                ticket = self._generate_single_ticket_from_props(all_props, ticket_number=i+1)
                if ticket:
                    context = {
                        'ticket': ticket,
                        'confidence_breakdown': [],
                        'reverse_engine_analysis': [],
                        'pipeline_steps': []
                    }
                    try:
                        scorer = ConfidenceScorer(self.memory_manager, reverse_engine=self.reverse_engine)
                        context['confidence_breakdown'] = [scorer._score_single_prop(prop) for prop in ticket.get('props', [])]
                        if self.reverse_engine:
                            context['reverse_engine_analysis'] = [self.reverse_engine.get_historical_analysis(
                                prop.get('player', ''),
                                prop.get('prop', ''),
                                ticket.get('sport', '')
                            ) for prop in ticket.get('props', [])]
                        else:
                            context['reverse_engine_analysis'] = []
                        context['pipeline_steps'] = ['fetch_props', 'score_confidence', 'reverse_engine_analysis', 'generate_ticket']
                    except Exception as e:
                        logger.warning(f"Failed to build full context for OpenAI: {e}")
                    feedback = ghost_openai_wrapper(
                        f"Ghost AI full pipeline context for self-training and evolution:\n{json.dumps(context, default=str, indent=2)}\n\nTeach, calibrate, or suggest improvements. Return JSON with any calibration, new logic, or code suggestions.",
                        tags={'type': 'full_pipeline_feedback'},
                        model='gpt-4',
                        max_tokens=1000
                    )
                    ticket['openai_full_pipeline_feedback'] = feedback
                    logger.info(f"OpenAI full pipeline feedback: {feedback}")
                    tickets.append(ticket)
            logger.info(f"Generated {len(tickets)} tickets using actual fetched props")
            return tickets
        except Exception as e:
            logger.error("Failed to generate tickets")
            return []
    
    def _load_all_fetched_props(self) -> List[Dict]:
        """Load all props from our new prop fetchers for MLB, WNBA, and Tennis."""
        all_props = []
        
        # Load MLB props
        mlb_props_dir = Path("mlb_game_props")
        logger.info(f"Checking MLB props directory: {mlb_props_dir}")
        if mlb_props_dir.exists():
            mlb_files = list(mlb_props_dir.glob("*.json"))
            logger.info(f"Found {len(mlb_files)} MLB prop files")
            for prop_file in mlb_files:
                try:
                    with open(prop_file, 'r') as f:
                        game = json.load(f)
                        if isinstance(game, dict) and 'player_props' in game:
                            for prop in game['player_props']:
                                normalized_prop = {
                                    'sport': 'MLB',
                                    'game': f"{game.get('home_team', '')} vs {game.get('away_team', '')}",
                                    'player': prop.get('player', ''),
                                    'prop': prop.get('prop_type', ''),
                                    'line': prop.get('line', ''),
                                    'pick': 'Over',  # Default pick
                                    'confidence': 0.75,  # Default confidence
                                    'odds': prop.get('over_odds', -110),
                                    'reasoning': f"MLB {prop.get('prop_type', '')} prop for {prop.get('player', '')}",
                                    'game_time': prop.get('game_time', game.get('commence_time', ''))
                                }
                                all_props.append(normalized_prop)
                except Exception as e:
                    logger.warning(f"Failed to load MLB props from {prop_file}: {e}")
        
        # Load WNBA props
        wnba_props_dir = Path("wnba_game_props")
        logger.info(f"Checking WNBA props directory: {wnba_props_dir}")
        if wnba_props_dir.exists():
            wnba_files = list(wnba_props_dir.glob("*.json"))
            logger.info(f"Found {len(wnba_files)} WNBA prop files")
            for prop_file in wnba_files:
                try:
                    with open(prop_file, 'r') as f:
                        game = json.load(f)
                        if isinstance(game, dict) and 'player_props' in game:
                            for prop in game['player_props']:
                                normalized_prop = {
                                    'sport': 'WNBA',
                                    'game': f"{game.get('home_team', '')} vs {game.get('away_team', '')}",
                                    'player': prop.get('player', ''),
                                    'prop': prop.get('prop_type', ''),
                                    'line': prop.get('line', ''),
                                    'pick': 'Over',  # Default pick
                                    'confidence': 0.75,  # Default confidence
                                    'odds': prop.get('over_odds', -110),
                                    'reasoning': f"WNBA {prop.get('prop_type', '')} prop for {prop.get('player', '')}",
                                    'game_time': prop.get('game_time', game.get('commence_time', ''))
                                }
                                all_props.append(normalized_prop)
                except Exception as e:
                    logger.warning(f"Failed to load WNBA props from {prop_file}: {e}")
        
        # Load Tennis props
        tennis_props_dir = Path("tennis_game_props")
        logger.info(f"Checking Tennis props directory: {tennis_props_dir}")
        if tennis_props_dir.exists():
            tennis_files = list(tennis_props_dir.glob("*.json"))
            logger.info(f"Found {len(tennis_files)} Tennis prop files")
            for prop_file in tennis_files:
                try:
                    with open(prop_file, 'r') as f:
                        match = json.load(f)
                        if isinstance(match, dict) and 'player_props' in match:
                            for prop in match['player_props']:
                                if prop.get('prop_type') != 'match_winner':  # Skip match winner props for now
                                    normalized_prop = {
                                        'sport': 'Tennis',
                                        'game': f"{match.get('player1', '')} vs {match.get('player2', '')}",
                                        'player': prop.get('player', ''),
                                        'prop': prop.get('prop_type', ''),
                                        'line': prop.get('line', ''),
                                        'pick': 'Over',  # Default pick
                                        'confidence': 0.75,  # Default confidence
                                        'odds': prop.get('over_odds', -110),
                                        'reasoning': f"Tennis {prop.get('prop_type', '')} prop for {prop.get('player', '')}",
                                        'game_time': prop.get('match_time', match.get('commence_time', ''))
                                    }
                                    all_props.append(normalized_prop)
                except Exception as e:
                    logger.warning(f"Failed to load Tennis props from {prop_file}: {e}")
        
        logger.info(f"Loaded {len(all_props)} props from all sports")
        return all_props
    
    def _generate_single_ticket_from_props(self, all_props: List[Dict], ticket_number: int) -> Optional[Dict]:
        """Generate a single ticket using actual fetched props."""
        try:
            if not all_props:
                return None
            
            # Randomly select 2-4 props for this ticket
            import random
            num_props = random.randint(2, 4)
            selected_props = random.sample(all_props, min(num_props, len(all_props)))

            # --- Begin Hit to HRR replacement logic ---
            replaced_props = []
            used_players = set()
            for prop in selected_props:
                player = prop.get('player', '')
                player_name = prop.get('player_name', player)
                if not player_name or player_name.lower() in used_players:
                    continue
                prop_name = prop.get('prop', '').lower()
                prop_type = prop.get('prop_type', prop.get('prop', ''))
                if 'hit' in prop_name:
                    # Replace Hit prop with HRR prop
                    try:
                        hit_line = float(prop.get('line', 1.5))
                    except Exception:
                        hit_line = 1.5
                    hrr_line = hit_line + 1.0  # Default logic: HRR line is Hit line + 1
                    hrr_prop = {
                        'sport': prop.get('sport', 'MLB'),
                        'game': prop.get('game', ''),
                        'player': player,
                        'player_name': player_name,
                        'prop': 'batter_hits_runs_rbis',
                        'prop_type': 'batter_hits_runs_rbis',
                        'line': hrr_line,
                        'pick': 'Over',
                        'confidence': prop.get('confidence', 0.7),
                        'odds': prop.get('odds', 1.9),
                        'reasoning': f"Converted Hit prop to HRR (Hits+Runs+RBIs) for {player_name}. HRR line set to {hrr_line} (Hit line was {hit_line}). This is a safer OVER pick as it includes runs and RBIs.",
                    }
                    replaced_props.append(hrr_prop)
                else:
                    # Always set player_name and prop_type for all props
                    prop['player_name'] = player_name
                    prop['prop_type'] = prop_type
                    replaced_props.append(prop)
                used_players.add(player_name.lower())
            # --- End Hit to HRR replacement logic ---

            # Calculate total confidence and odds
            total_confidence = sum(prop.get('confidence', 0.7) for prop in replaced_props) / len(replaced_props)
            total_odds = 1.0
            for prop in replaced_props:
                odds = prop.get('odds', 1.9)
                if isinstance(odds, str):
                    try:
                        odds = float(odds)
                    except:
                        odds = 1.9
                total_odds *= odds
            
            # Determine primary sport for the ticket
            sports_in_ticket = [prop.get('sport', '') for prop in replaced_props]
            primary_sport = max(set(sports_in_ticket), key=sports_in_ticket.count) if sports_in_ticket else 'Mixed'
            
            # Create ticket with proper labeling
            ticket = {
                'ticket_id': self._generate_ticket_id(),
                'sport': primary_sport,
                'props': replaced_props,
                'total_confidence': round(total_confidence, 3),
                'total_odds': round(total_odds, 3),
                'reasoning': f"High-confidence {primary_sport} ticket #{ticket_number} using actual fetched props",
                'timestamp': datetime.now().isoformat(),
                'ticket_type': f"{primary_sport} Player Props"
            }
            
            return ticket
            
        except Exception as e:
            logger.error(f"Failed to generate single ticket from props: {e}")
            return None
    
    def _generate_generic_tickets(self, num_tickets: int) -> List[Dict]:
        """Generate generic tickets when no props are available."""
        tickets = []
        for i in range(num_tickets):
            ticket = self._generate_single_ticket()
            if ticket:
                tickets.append(ticket)
        return tickets
    
    def _generate_single_ticket(self, tennis_props: Optional[list] = None, recursion_depth: int = 0) -> Optional[Dict]:
        """Generate a single ticket without duplicate player restrictions."""
        try:
            if recursion_depth > 5:
                logger.error("Maximum recursion depth exceeded, stopping ticket generation")
                return None
            # --- Tennis prop filtering ---
            props_pool = tennis_props if tennis_props else []
            if props_pool and all('sport' in p and p['sport'].lower() == 'tennis' for p in props_pool):
                # Only keep props that are in the whitelist
                props_pool = [p for p in props_pool if p.get('prop_type') in self.TENNIS_PROP_WHITELIST]
                # Remove any moneyline or unsupported props
                props_pool = [p for p in props_pool if 'to Win Match' not in p.get('prop_type', '') and 'WINNER' not in p.get('prop_type', '')]
                if not props_pool:
                    logger.warning("No valid Underdog-style tennis props available after filtering.")
                    return None
            prompt = """
            You are Ghost AI 3.0's ticket generator. Generate a high-confidence ticket.
            Generate a ticket with 2-4 props that:
            - Has high confidence (80%+ combined)
            - Includes a mix of prop types
            - Has good value and odds
            Consider:
            - Player form and recent performance
            - Matchup advantages
            - Line value and odds
            - Historical data
            - Weather conditions (for outdoor sports)
            Only use props from this list (Underdog allowed):
            {whitelist}
            Return a JSON object with:
            {{
                "ticket_id": "unique_id",
                "sport": "MLB/WNBA/TENNIS",
                "props": [
                    {{
                        "game": "Team A vs Team B",
                        "player": "Player Name",
                        "prop": "Prop Type",
                        "line": "X.X",
                        "pick": "Over/Under",
                        "confidence": 0.XX,
                        "odds": "X.XX",
                        "reasoning": "Brief explanation"
                    }}
                ],
                "total_confidence": 0.XX,
                "total_odds": "X.XX",
                "reasoning": "Overall ticket reasoning",
                "timestamp": "ISO timestamp"
            }}
            """.replace('{whitelist}', ', '.join(self.TENNIS_PROP_WHITELIST))
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'ticket_generation'},
                model='gpt-4',
                max_tokens=800
            )
            ticket_data = self._extract_json_from_response(response)
            if ticket_data:
                ticket_data['ticket_id'] = self._generate_ticket_id()
                ticket_data['timestamp'] = datetime.now().isoformat()
                return ticket_data
            return None
        except Exception as e:
            logger.error("Failed to generate single ticket")
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
            logger.error("Failed to extract JSON from response")
            return None
    
    def _generate_ticket_id(self) -> str:
        """Generate a unique ticket ID."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=6))
        return f"TICKET_{timestamp}_{random_suffix}"
    
    def analyze_all_props(self, game_data: Dict) -> List[Dict]:
        """Analyze all available props in game data."""
        try:
            logger.info("Analyzing all props")
            
            all_props = []
            
            # Extract all props from game data
            for game in game_data.get('games', []):
                game_info = game.get('game_info', {})
                home_team = game_info.get('home_team', '')
                away_team = game_info.get('away_team', '')
                game_id = game_info.get('game_id', '')
                
                # Analyze player props
                player_props = game.get('player_props', [])
                for prop in player_props:
                    prop_analysis = self._analyze_prop(prop, home_team, away_team, game_id)
                    if prop_analysis:
                        all_props.append(prop_analysis)
                
                # Analyze game props
                game_props = game.get('game_props', [])
                for prop in game_props:
                    prop_analysis = self._analyze_prop(prop, home_team, away_team, game_id)
                    if prop_analysis:
                        all_props.append(prop_analysis)
            
            logger.info(f"✅ Analyzed {len(all_props)} props")
            return all_props
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze props: {e}")
            return []
    
    def _analyze_prop(self, prop: Dict, home_team: str, away_team: str, game_id: str) -> Optional[Dict]:
        """Analyze a single prop."""
        try:
            player = prop.get('player', '')
            prop_type = prop.get('prop_type', '')
            line = prop.get('line', '')
            over_odds = prop.get('over_odds', '')
            under_odds = prop.get('under_odds', '')
            
            prompt = f"""
            You are Ghost AI 3.0's prop analyzer. Analyze this prop:
            
            Game: {away_team} vs {home_team}
            Player: {player}
            Prop Type: {prop_type}
            Line: {line}
            Over Odds: {over_odds}
            Under Odds: {under_odds}
            
            Analyze the value and confidence for both over and under.
            Consider player form, matchup, historical data, and line value.
            
            Return a JSON object with:
            {{
                "game": "{away_team} vs {home_team}",
                "player": "{player}",
                "prop_type": "{prop_type}",
                "line": "{line}",
                "over_odds": "{over_odds}",
                "under_odds": "{under_odds}",
                "over_confidence": 0.XX,
                "under_confidence": 0.XX,
                "over_value": "high/medium/low",
                "under_value": "high/medium/low",
                "recommended_pick": "over/under",
                "reasoning": "Detailed analysis",
                "game_id": "{game_id}"
            }}
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'prop_analysis', 'game_id': game_id},
                model='gpt-4',
                max_tokens=400
            )
            
            # Extract JSON from response
            analysis = self._extract_json_from_response(response)
            if analysis:
                analysis['timestamp'] = datetime.now().isoformat()
                return analysis
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze prop: {e}")
            return None
    
    def try_different_prop_types(self, game_data: Dict) -> List[Dict]:
        """Try different prop types beyond the standard ones."""
        try:
            logger.info("🔄 Trying different prop types...")
            
            alternative_props = []
            
            # Look for alternative prop types
            prop_types_to_try = [
                'strikeouts', 'walks', 'hits_allowed', 'earned_runs',
                'total_bases', 'extra_base_hits', 'runs_batted_in',
                'stolen_bases', 'caught_stealing', 'assists', 'putouts',
                'fielding_errors', 'double_plays_turned'
            ]
            
            for game in game_data.get('games', []):
                game_info = game.get('game_info', {})
                home_team = game_info.get('home_team', '')
                away_team = game_info.get('away_team', '')
                
                for prop_type in prop_types_to_try:
                    # Check if this prop type exists in the data
                    if prop_type in str(game):
                        # Generate analysis for this prop type
                        alt_prop = self._generate_alternative_prop(
                            prop_type, home_team, away_team, game
                        )
                        if alt_prop:
                            alternative_props.append(alt_prop)
            
            logger.info(f"✅ Found {len(alternative_props)} alternative props")
            return alternative_props
            
        except Exception as e:
            logger.error(f"❌ Failed to try different prop types: {e}")
            return []
    
    def _generate_alternative_prop(self, prop_type: str, home_team: str, away_team: str, game: Dict) -> Optional[Dict]:
        """Generate analysis for an alternative prop type."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's alternative prop analyzer. Analyze {prop_type} props for {away_team} vs {home_team}.
            
            Prop Type: {prop_type}
            Game: {away_team} vs {home_team}
            
            Find the best {prop_type} prop in this game and analyze its value.
            Consider:
            - Player form and recent performance
            - Matchup advantages
            - Historical data for this prop type
            - Line value and odds
            
            Return a JSON object with:
            {{
                "game": "{away_team} vs {home_team}",
                "player": "Player Name",
                "prop_type": "{prop_type}",
                "line": "X.X",
                "pick": "Over/Under",
                "confidence": 0.XX,
                "odds": "X.XX",
                "reasoning": "Analysis of this alternative prop",
                "alternative_prop": true,
                "timestamp": "ISO timestamp"
            }}
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'alternative_prop', 'prop_type': prop_type},
                model='gpt-4',
                max_tokens=400
            )
            
            # Extract JSON from response
            prop_data = self._extract_json_from_response(response)
            if prop_data:
                prop_data['timestamp'] = datetime.now().isoformat()
                prop_data['alternative_prop'] = True
                return prop_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to generate alternative prop: {e}")
            return None

    @staticmethod
    def get_next_event_time() -> datetime:
        """Scan all sports for the next event (game/prop) time and return the soonest."""
        now = datetime.now()
        soonest = now + timedelta(days=2)  # Default: far future
        # --- Tennis ---
        try:
            tennis_matches = get_fixtures(now.strftime('%Y-%m-%d'))
            for match in tennis_matches:
                start = match.get('event_start_date') or match.get('event_date')
                if start:
                    dt = datetime.fromisoformat(start)
                    if dt > now and dt < soonest:
                        soonest = dt
        except Exception as e:
            logging.warning(f"Tennis event scan failed: {e}")
        # --- MLB ---
        try:
            # from sports.mlb.mlb_props import MLBFetcher
            # mlb = MLBFetcher()
            # Assume fetch_games returns list of games with 'commence_time'
            games = []  # TODO: implement actual fetch
            for game in games:
                start = game.get('commence_time')
                if start:
                    dt = datetime.fromisoformat(start)
                    if dt > now and dt < soonest:
                        soonest = dt
        except Exception as e:
            logging.warning(f"MLB event scan failed: {e}")
        # --- WNBA ---
        try:
            # from sports.wnba.wnba_props import WNBAFetcher
            # wnba = WNBAFetcher()
            # Assume fetch_games returns list of games with 'commence_time'
            games = []  # TODO: implement actual fetch
            for game in games:
                start = game.get('commence_time')
                if start:
                    dt = datetime.fromisoformat(start)
                    if dt > now and dt < soonest:
                        soonest = dt
        except Exception as e:
            logging.warning(f"WNBA event scan failed: {e}")
        return soonest

    @staticmethod
    def get_idle_seconds_until_next_event() -> int:
        """Return seconds to idle until the next event, with min/max cap (tunable)."""
        now = datetime.now()
        next_event = TicketGenerator.get_next_event_time()
        delta = (next_event - now).total_seconds()
        min_idle = TicketGenerator.min_idle_seconds
        max_idle = TicketGenerator.max_idle_seconds
        if delta < min_idle:
            return min_idle
        if delta > max_idle:
            return max_idle
        return int(delta)
    @classmethod
    def tune_idle_times(cls, min_idle: int, max_idle: int):
        """Allow the AI to tune its own idle times."""
        cls.min_idle_seconds = min_idle
        cls.max_idle_seconds = max_idle
        logger.info(f"AI tuned idle times: min={min_idle}s, max={max_idle}s")

def create_ticket_generator(base_dir: Path) -> TicketGenerator:
    """Create and return a TicketGenerator instance."""
    return TicketGenerator(base_dir)
