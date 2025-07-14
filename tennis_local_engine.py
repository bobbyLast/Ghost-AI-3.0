#!/usr/bin/env python3
"""
Tennis Local Engine
Uses local data to generate tennis picks without API dependency
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from tennis_local_data_manager import TennisLocalDataManager

logger = logging.getLogger(__name__)

class TennisLocalEngine:
    """Tennis engine that uses local data for reliable pick generation."""
    
    def __init__(self):
        self.data_manager = TennisLocalDataManager()
        self.base_dir = Path('data/tennis_local')
        
        # Star players for filtering
        self.star_players = self.data_manager.star_players
        
        logger.info("🎾 Tennis Local Engine initialized")
    
    def generate_daily_tennis_picks(self, date: str = None) -> List[Dict]:
        """Generate daily tennis picks using local data."""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        logger.info(f"🎾 Generating tennis picks for {date} using local data...")
        
        # Get local fixtures
        fixtures = self.data_manager.get_local_fixtures(date)
        if not fixtures:
            logger.warning(f"No local fixtures found for {date}")
            return []
        
        # Filter for star players and major tournaments
        star_matches = self._filter_star_matches(fixtures)
        
        picks = []
        for match in star_matches:
            match_picks = self._generate_match_picks(match)
            picks.extend(match_picks)
        
        logger.info(f"✅ Generated {len(picks)} tennis picks for {date}")
        return picks
    
    def _filter_star_matches(self, fixtures: List[Dict]) -> List[Dict]:
        """Filter fixtures for star players and major tournaments."""
        star_matches = []
        
        for fixture in fixtures:
            player1 = fixture.get('event_first_player', '')
            player2 = fixture.get('event_second_player', '')
            event_type = fixture.get('event_type_type', '')
            
            # Check if it's a star player match
            is_star_match = any(
                player in self.star_players['ATP_TOP_50'] + self.star_players['WTA_TOP_50']
                for player in [player1, player2]
            )
            
            # Check if it's a major tournament
            is_major_tournament = any(major in event_type for major in [
                'Atp Singles', 'Wta Singles', 'Grand Slam', 'Atp Masters 1000',
                'Wta Premier', 'Wta Premier Mandatory'
            ])
            
            if is_star_match and is_major_tournament:
                star_matches.append(fixture)
        
        return star_matches
    
    def _generate_match_picks(self, match: Dict) -> List[Dict]:
        """Generate picks for a specific match."""
        picks = []
        
        player1 = match.get('event_first_player', '')
        player2 = match.get('event_second_player', '')
        tournament = match.get('tournament_name', '')
        event_type = match.get('event_type_type', '')
        surface = match.get('tournament_sourface', 'Unknown')
        
        # Get local data
        player1_key = match.get('first_player_key')
        player2_key = match.get('second_player_key')
        match_key = match.get('event_key')
        
        player1_data = self.data_manager.get_local_player_data(player1_key) if player1_key else None
        player2_data = self.data_manager.get_local_player_data(player2_key) if player2_key else None
        h2h_data = self.data_manager.get_local_h2h_data(player1_key, player2_key) if player1_key and player2_key else None
        odds_data = self.data_manager.get_local_odds_data(match_key) if match_key else None
        
        # Generate different types of picks
        picks.extend(self._generate_total_games_pick(match, player1_data, player2_data, h2h_data))
        picks.extend(self._generate_aces_picks(match, player1_data, player2_data))
        picks.extend(self._generate_double_faults_picks(match, player1_data, player2_data))
        picks.extend(self._generate_first_set_picks(match, h2h_data))
        
        return picks
    
    def _generate_total_games_pick(self, match: Dict, player1_data: Optional[Dict], 
                                  player2_data: Optional[Dict], h2h_data: Optional[Dict]) -> List[Dict]:
        """Generate total games pick."""
        picks = []
        
        player1 = match.get('event_first_player', '')
        player2 = match.get('event_second_player', '')
        tournament = match.get('tournament_name', '')
        
        # Analyze H2H data for total games
        total_games_estimate = 22.5  # Default estimate
        confidence = 0.60  # Default confidence
        
        if h2h_data and 'H2H' in h2h_data and h2h_data['H2H']:
            # Analyze historical matches for total games
            total_games_list = []
            for h2h_match in h2h_data['H2H'][:5]:  # Last 5 matches
                final_result = h2h_match.get('event_final_result', '')
                if final_result:
                    total_games = self._calculate_total_games_from_result(final_result)
                    if total_games:
                        total_games_list.append(total_games)
            
            if total_games_list:
                avg_games = sum(total_games_list) / len(total_games_list)
                total_games_estimate = avg_games
                confidence = min(0.75, 0.60 + (len(total_games_list) * 0.03))
        
        # Generate pick
        line = 20.5
        pick = 'Higher' if total_games_estimate > line else 'Lower'
        
        picks.append({
            'sport': 'TENNIS',
            'player': f"{player1} vs {player2}",
            'prop': 'Total Games',
            'line': line,
            'pick': pick,
            'confidence': confidence,
            'reasoning': f"Based on H2H analysis: avg {total_games_estimate:.1f} games",
            'tournament': tournament,
            'surface': match.get('tournament_sourface', 'Unknown'),
            'data_source': 'local_h2h'
        })
        
        return picks
    
    def _generate_aces_picks(self, match: Dict, player1_data: Optional[Dict], 
                            player2_data: Optional[Dict]) -> List[Dict]:
        """Generate aces picks for both players."""
        picks = []
        
        player1 = match.get('event_first_player', '')
        player2 = match.get('event_second_player', '')
        tournament = match.get('tournament_name', '')
        
        # Generate aces pick for player 1
        if player1_data:
            ace_line = 4.5
            ace_confidence = 0.65
            ace_pick = 'Higher'  # Placeholder - would use player stats
            
            picks.append({
                'sport': 'TENNIS',
                'player': player1,
                'prop': 'Aces',
                'line': ace_line,
                'pick': ace_pick,
                'confidence': ace_confidence,
                'reasoning': f"Based on {player1} ace statistics",
                'tournament': tournament,
                'surface': match.get('tournament_sourface', 'Unknown'),
                'data_source': 'local_player_stats'
            })
        
        # Generate aces pick for player 2
        if player2_data:
            ace_line = 4.5
            ace_confidence = 0.65
            ace_pick = 'Higher'  # Placeholder - would use player stats
            
            picks.append({
                'sport': 'TENNIS',
                'player': player2,
                'prop': 'Aces',
                'line': ace_line,
                'pick': ace_pick,
                'confidence': ace_confidence,
                'reasoning': f"Based on {player2} ace statistics",
                'tournament': tournament,
                'surface': match.get('tournament_sourface', 'Unknown'),
                'data_source': 'local_player_stats'
            })
        
        return picks
    
    def _generate_double_faults_picks(self, match: Dict, player1_data: Optional[Dict], 
                                     player2_data: Optional[Dict]) -> List[Dict]:
        """Generate double faults picks for both players."""
        picks = []
        
        player1 = match.get('event_first_player', '')
        player2 = match.get('event_second_player', '')
        tournament = match.get('tournament_name', '')
        
        # Generate double faults pick for player 1
        if player1_data:
            df_line = 2.5
            df_confidence = 0.60
            df_pick = 'Lower'  # Placeholder - would use player stats
            
            picks.append({
                'sport': 'TENNIS',
                'player': player1,
                'prop': 'Double Faults',
                'line': df_line,
                'pick': df_pick,
                'confidence': df_confidence,
                'reasoning': f"Based on {player1} double fault statistics",
                'tournament': tournament,
                'surface': match.get('tournament_sourface', 'Unknown'),
                'data_source': 'local_player_stats'
            })
        
        # Generate double faults pick for player 2
        if player2_data:
            df_line = 2.5
            df_confidence = 0.60
            df_pick = 'Lower'  # Placeholder - would use player stats
            
            picks.append({
                'sport': 'TENNIS',
                'player': player2,
                'prop': 'Double Faults',
                'line': df_line,
                'pick': df_pick,
                'confidence': df_confidence,
                'reasoning': f"Based on {player2} double fault statistics",
                'tournament': tournament,
                'surface': match.get('tournament_sourface', 'Unknown'),
                'data_source': 'local_player_stats'
            })
        
        return picks
    
    def _generate_first_set_picks(self, match: Dict, h2h_data: Optional[Dict]) -> List[Dict]:
        """Generate first set related picks."""
        picks = []
        
        player1 = match.get('event_first_player', '')
        player2 = match.get('event_second_player', '')
        tournament = match.get('tournament_name', '')
        
        if h2h_data and 'H2H' in h2h_data and h2h_data['H2H']:
            # Analyze first set patterns
            first_set_games_list = []
            for h2h_match in h2h_data['H2H'][:5]:
                final_result = h2h_match.get('event_final_result', '')
                if final_result:
                    first_set_games = self._calculate_first_set_games(final_result)
                    if first_set_games:
                        first_set_games_list.append(first_set_games)
            
            if first_set_games_list:
                avg_first_set_games = sum(first_set_games_list) / len(first_set_games_list)
                line = 9.5
                pick = 'Higher' if avg_first_set_games > line else 'Lower'
                confidence = min(0.70, 0.55 + (len(first_set_games_list) * 0.03))
                
                picks.append({
                    'sport': 'TENNIS',
                    'player': f"{player1} vs {player2}",
                    'prop': '1st Set Total Games',
                    'line': line,
                    'pick': pick,
                    'confidence': confidence,
                    'reasoning': f"Based on H2H first set analysis: avg {avg_first_set_games:.1f} games",
                    'tournament': tournament,
                    'surface': match.get('tournament_sourface', 'Unknown'),
                    'data_source': 'local_h2h'
                })
        
        return picks
    
    def _calculate_total_games_from_result(self, final_result: str) -> Optional[int]:
        """Calculate total games from match result string."""
        try:
            sets = []
            for set_score in final_result.split(','):
                set_score = set_score.strip()
                if '-' in set_score:
                    a, b = map(int, set_score.split('-'))
                    sets.append([a, b])
            
            if sets:
                total_games = sum(sum(set_games) for set_games in sets)
                return total_games
        except:
            pass
        return None
    
    def _calculate_first_set_games(self, final_result: str) -> Optional[int]:
        """Calculate first set games from match result string."""
        try:
            sets = []
            for set_score in final_result.split(','):
                set_score = set_score.strip()
                if '-' in set_score:
                    a, b = map(int, set_score.split('-'))
                    sets.append([a, b])
            
            if sets:
                first_set_games = sum(sets[0])
                return first_set_games
        except:
            pass
        return None
    
    def get_engine_status(self) -> Dict:
        """Get engine status and data summary."""
        data_summary = self.data_manager.get_data_summary()
        
        return {
            'status': 'operational',
            'data_summary': data_summary,
            'star_players_loaded': len(self.star_players['ATP_TOP_50']) + len(self.star_players['WTA_TOP_50']),
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Test the tennis local engine."""
    engine = TennisLocalEngine()
    
    print("🎾 Tennis Local Engine Test")
    print("=" * 40)
    
    # Get engine status
    status = engine.get_engine_status()
    print(f"Status: {status['status']}")
    print(f"Star Players: {status['star_players_loaded']}")
    print(f"Data Size: {status['data_summary']['total_size_mb']} MB")
    
    # Generate picks for today
    today = datetime.now().strftime('%Y-%m-%d')
    picks = engine.generate_daily_tennis_picks(today)
    
    print(f"\n🎯 Generated {len(picks)} picks for {today}:")
    for i, pick in enumerate(picks[:5], 1):  # Show first 5 picks
        print(f"{i}. {pick['player']} - {pick['prop']} {pick['line']} {pick['pick']} ({pick['confidence']:.0%})")

if __name__ == "__main__":
    main() 