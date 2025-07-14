import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import os

logger = logging.getLogger(__name__)

@dataclass
class OddsAnalysis:
    player_name: str
    prop_type: str
    opening_line: float
    opening_odds: int
    closing_line: float
    closing_odds: int
    market_movement: str  # 'sharp', 'public', 'balanced'
    confidence: float
    analysis_reason: str
    timestamp: str

@dataclass
class PickRecord:
    player_name: str
    prop_type: str
    line: float
    odds: int
    confidence: float
    pick_side: str  # 'over' or 'under'
    timestamp: str
    closing_line: Optional[float] = None
    closing_odds: Optional[int] = None
    result: Optional[str] = None  # 'win', 'loss', 'push'
    market_agreement: Optional[str] = None  # 'alpha', 'trap', 'neutral'

class OddsEngine:
    def __init__(self, memory_file: str = "odds_memory.json"):
        self.memory_file = memory_file
        self.odds_history = self._load_memory()
        self.picks_history = []
        
    def _load_memory(self) -> Dict:
        """Load odds history from memory file."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading odds memory: {e}")
        return {}
    
    def _save_memory(self):
        """Save odds history to memory file."""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.odds_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving odds memory: {e}")
    
    def analyze_props_for_player(self, player_name: str, props: List[Dict]) -> List[Dict]:
        """
        Analyze props for a specific player and return ALL props the AI believes will hit.
        
        Args:
            player_name: Name of the player to analyze
            props: List of all props for this player
            
        Returns:
            List of props the AI believes will hit (can be multiple per player)
        """
        if not props:
            return []
            
        # Analyze all props and select those the AI believes will hit
        selected_props = []
        
        for prop in props:
            try:
                # Get player's historical performance for this prop type
                prop_type = prop.get('prop_type', '')
                line = prop.get('line', 0)
                odds = prop.get('odds', 0)
                
                # Analyze this specific prop
                analysis = self._analyze_single_prop(player_name, prop_type, line, odds)
                
                # Calculate a score for this prop (confidence + odds value)
                confidence = analysis.get('confidence', 0.5)
                odds_value = self._calculate_odds_value(odds)
                score = confidence * 0.7 + odds_value * 0.3
                
                # Select this prop if AI believes it will hit (high confidence)
                if confidence >= 0.65:  # AI believes this prop will hit
                    selected_prop = prop.copy()
                    selected_prop.update(analysis)
                    selected_prop['player_score'] = score
                    selected_props.append(selected_prop)
                    
                    logger.debug(f"AI believes {player_name} {prop_type} {line} will hit - Confidence: {confidence:.2f}, Score: {score:.2f}")
                
            except Exception as e:
                logger.error(f"Error analyzing prop for {player_name}: {e}")
                continue
        
        # Sort by score (best first)
        selected_props.sort(key=lambda x: x.get('player_score', 0), reverse=True)
        
        logger.info(f"AI selected {len(selected_props)} props for {player_name} (believes they will hit)")
        return selected_props

    def _calculate_odds_value(self, odds: int) -> float:
        """Calculate odds value score (0-1)."""
        if -200 <= odds <= 200:  # Good value range
            return 0.8
        elif -300 <= odds <= 300:  # Decent value
            return 0.6
        elif -500 <= odds <= 500:  # Acceptable value
            return 0.4
        else:  # Poor value
            return 0.2

    def process_all_players_props(self, all_props: List[Dict]) -> List[Dict]:
        """
        Process ALL props for ALL players and return ALL props the AI believes will hit.
        Group by player, analyze every prop for each player, select ALL props AI believes will hit, then move to next player.
        
        Args:
            all_props: List of all props from all players
            
        Returns:
            List of all props the AI believes will hit (can be multiple per player)
        """
        # Group props by player
        player_props = {}
        for prop in all_props:
            player_name = prop.get('player_name', '')
            if player_name not in player_props:
                player_props[player_name] = []
            player_props[player_name].append(prop)
        
        all_selected_props = []
        processed_players = 0
        
        # Process each player systematically
        for player_name, props in player_props.items():
            logger.info(f"Processing player {processed_players + 1}/{len(player_props)}: {player_name} ({len(props)} props)")
            
            # Analyze EVERY prop for this player and select ALL props AI believes will hit
            selected_props = self.analyze_props_for_player(player_name, props)
            
            if selected_props:
                all_selected_props.extend(selected_props)
                logger.info(f"AI selected {len(selected_props)} props for {player_name}: {[f'{p.get('prop_type', '')} {p.get('line', 0)}' for p in selected_props]}")
            else:
                logger.warning(f"AI found no suitable props for {player_name}")
            
            processed_players += 1
            
            # Log progress
            if processed_players % 10 == 0:
                logger.info(f"Processed {processed_players}/{len(player_props)} players, {len(all_selected_props)} total props selected")
        
        logger.info(f"Completed analysis: AI selected {len(all_selected_props)} props from {len(player_props)} players")
        return all_selected_props

    def _analyze_single_prop(self, player_name: str, prop_type: str, line: float, odds: int) -> Dict:
        """Analyze a single prop for market movement and confidence."""
        # Get historical odds for this player/prop combination
        key = f"{player_name}_{prop_type}"
        historical_data = self.odds_history.get(key, [])
        
        if not historical_data:
            return {
                'confidence': 0.5,
                'analysis_reason': 'No historical data available',
                'odds_analysis': 'unknown'
            }
        
        # Find most recent opening and closing odds
        recent_data = sorted(historical_data, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        
        if not recent_data:
            return {
                'confidence': 0.5,
                'analysis_reason': 'No recent historical data',
                'odds_analysis': 'unknown'
            }
        
        # Calculate average movement patterns
        total_movement = 0
        sharp_moves = 0
        
        for data in recent_data:
            opening_line = data.get('opening_line', line)
            closing_line = data.get('closing_line', line)
            movement = closing_line - opening_line
            total_movement += movement
            
            # Detect sharp moves (significant line movement)
            if abs(movement) > 0.5:  # Adjust threshold as needed
                sharp_moves += 1
        
        avg_movement = total_movement / len(recent_data)
        sharp_move_ratio = sharp_moves / len(recent_data)
        
        # Determine market movement type
        if sharp_move_ratio > 0.6:
            market_movement = 'sharp'
            confidence = min(0.8, 0.5 + sharp_move_ratio * 0.3)
        elif sharp_move_ratio > 0.3:
            market_movement = 'balanced'
            confidence = 0.6
        else:
            market_movement = 'public'
            confidence = 0.4
        
        # Adjust confidence based on odds value
        if -200 <= odds <= 200:  # Good value range
            confidence += 0.1
        elif odds < -300 or odds > 300:  # Poor value
            confidence -= 0.1
        
        confidence = max(0.1, min(0.9, confidence))
        
        return {
            'confidence': confidence,
            'analysis_reason': f"Market movement: {market_movement}, Sharp moves: {sharp_move_ratio:.2f}",
            'odds_analysis': market_movement
        }
    
    def record_pick(self, player_name: str, prop_type: str, line: float, odds: int, 
                   confidence: float, pick_side: str):
        """Record a pick for later analysis."""
        pick = PickRecord(
            player_name=player_name,
            prop_type=prop_type,
            line=line,
            odds=odds,
            confidence=confidence,
            pick_side=pick_side,
            timestamp=datetime.now().isoformat()
        )
        self.picks_history.append(pick)
        logger.info(f"Recorded pick: {player_name} {prop_type} {pick_side} {line}")
    
    def update_closing_odds(self, player_name: str, prop_type: str, closing_line: float, closing_odds: int):
        """Update closing odds for a recorded pick."""
        for pick in self.picks_history:
            if (pick.player_name == player_name and 
                pick.prop_type == prop_type and 
                pick.closing_line is None):
                pick.closing_line = closing_line
                pick.closing_odds = closing_odds
                logger.info(f"Updated closing odds for {player_name} {prop_type}")
                break
    
    def grade_result(self, player_name: str, prop_type: str, actual_result: float):
        """Grade a pick result and analyze market agreement."""
        for pick in self.picks_history:
            if (pick.player_name == player_name and 
                pick.prop_type == prop_type and 
                pick.result is None):
                
                # Determine result
                if pick.pick_side == 'over':
                    if actual_result > pick.line:
                        pick.result = 'win'
                    elif actual_result < pick.line:
                        pick.result = 'loss'
                    else:
                        pick.result = 'push'
                else:  # under
                    if actual_result < pick.line:
                        pick.result = 'win'
                    elif actual_result > pick.line:
                        pick.result = 'loss'
                    else:
                        pick.result = 'push'
                
                # Analyze market agreement
                if pick.closing_line is not None:
                    line_movement = pick.closing_line - pick.line
                    if pick.pick_side == 'over' and line_movement > 0.5:
                        pick.market_agreement = 'alpha'  # Market moved our way
                    elif pick.pick_side == 'under' and line_movement < -0.5:
                        pick.market_agreement = 'alpha'
                    elif abs(line_movement) > 0.5:
                        pick.market_agreement = 'trap'  # Market moved against us
                    else:
                        pick.market_agreement = 'neutral'
                
                logger.info(f"Graded {player_name} {prop_type}: {pick.result} (market: {pick.market_agreement})")
                break
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary of all picks."""
        if not self.picks_history:
            return {"message": "No picks recorded yet"}
        
        total_picks = len(self.picks_history)
        wins = sum(1 for pick in self.picks_history if pick.result == 'win')
        losses = sum(1 for pick in self.picks_history if pick.result == 'loss')
        pushes = sum(1 for pick in self.picks_history if pick.result == 'push')
        
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        # Market agreement analysis
        alpha_picks = [p for p in self.picks_history if p.market_agreement == 'alpha']
        trap_picks = [p for p in self.picks_history if p.market_agreement == 'trap']
        neutral_picks = [p for p in self.picks_history if p.market_agreement == 'neutral']
        
        alpha_wins = sum(1 for p in alpha_picks if p.result == 'win')
        trap_wins = sum(1 for p in trap_picks if p.result == 'win')
        
        alpha_win_rate = alpha_wins / len(alpha_picks) if alpha_picks else 0
        trap_win_rate = trap_wins / len(trap_picks) if trap_picks else 0
        
        return {
            "total_picks": total_picks,
            "wins": wins,
            "losses": losses,
            "pushes": pushes,
            "win_rate": f"{win_rate:.3f}",
            "alpha_picks": len(alpha_picks),
            "alpha_win_rate": f"{alpha_win_rate:.3f}",
            "trap_picks": len(trap_picks),
            "trap_win_rate": f"{trap_win_rate:.3f}",
            "neutral_picks": len(neutral_picks)
        }
    
    def save_picks_history(self, filename: str = "picks_history.json"):
        """Save picks history to file."""
        try:
            picks_data = [asdict(pick) for pick in self.picks_history]
            with open(filename, 'w') as f:
                json.dump(picks_data, f, indent=2)
            logger.info(f"Saved picks history to {filename}")
        except Exception as e:
            logger.error(f"Error saving picks history: {e}")
    
    def load_picks_history(self, filename: str = "picks_history.json"):
        """Load picks history from file."""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    picks_data = json.load(f)
                self.picks_history = [PickRecord(**pick) for pick in picks_data]
                logger.info(f"Loaded {len(self.picks_history)} picks from {filename}")
        except Exception as e:
            logger.error(f"Error loading picks history: {e}") 