#!/usr/bin/env python3
"""
Prop Filter for Ghost AI 3.0 Sportsbook Edition
Intelligently filters props, handles HRR combinations, and prevents duplicates
"""

import logging
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime

logger = logging.getLogger('prop_filter')

class PropFilter:
    """Advanced prop filtering and combination system."""
    
    def __init__(self):
        # MLB prop priorities (higher = more important)
        self.mlb_priorities = {
            'Hits': 10,
            'Home Runs': 9,
            'RBIs': 8,
            'Runs': 7,
            'Stolen Bases': 6,
            'Walks': 5,
            'Doubles': 4,
            'Triples': 3,
            'Fantasy Score': 2
        }
        
        # WNBA prop priorities
        self.wnba_priorities = {
            'Points': 10,
            'Rebounds': 9,
            'Assists': 8,
            'Threes': 7,
            'Steals': 6,
            'Blocks': 5,
            'Turnovers': 4,
            'Fantasy Score': 3
        }
        
        # HRR (Hits, Runs, RBIs) combinations
        self.hrr_combinations = {
            'Hits + Runs': ['Hits', 'Runs'],
            'Hits + RBIs': ['Hits', 'RBIs'],
            'Runs + RBIs': ['Runs', 'RBIs'],
            'Hits + Runs + RBIs': ['Hits', 'Runs', 'RBIs']
        }
        
        # Avoid these prop types (too volatile or low value)
        self.avoid_props = {
            'MLB': ['Triples', 'Stolen Bases'],  # Too rare
            'WNBA': ['Turnovers']  # Too volatile
        }
        
        logger.info("🔍 Prop Filter initialized")
    
    def filter_props(self, all_props: List[Dict], sport: str, memory_manager=None) -> List[Dict]:
        """
        Filter and prioritize props for a sport.
        
        Args:
            all_props: All available props
            sport: 'MLB' or 'WNBA'
            memory_manager: Memory manager for duplicate checking
            
        Returns:
            Filtered and prioritized props
        """
        try:
            # Group props by player
            player_props = self._group_props_by_player(all_props)
            filtered_props = []
            
            for player_name, player_prop_list in player_props.items():
                # Check if player already used today
                if memory_manager and memory_manager.is_player_used_today(player_name):
                    logger.info(f"🔍 Skipping {player_name} - already used today")
                    continue
                
                # Filter player's props
                filtered_player_props = self._filter_player_props(player_prop_list, sport)
                
                if filtered_player_props:
                    filtered_props.extend(filtered_player_props)
            
            # Sort by priority
            priorities = self.mlb_priorities if sport == 'MLB' else self.wnba_priorities
            filtered_props.sort(key=lambda p: priorities.get(p.get('prop_type', ''), 0), reverse=True)
            
            logger.info(f"🔍 Filtered {len(all_props)} props down to {len(filtered_props)}")
            return filtered_props
            
        except Exception as e:
            logger.error(f"Error filtering props: {e}")
            return []
    
    def _group_props_by_player(self, props: List[Dict]) -> Dict[str, List[Dict]]:
        """Group props by player name."""
        player_props = {}
        
        for prop in props:
            player_name = prop.get('player_name', '')
            if player_name:
                if player_name not in player_props:
                    player_props[player_name] = []
                player_props[player_name].append(prop)
        
        return player_props
    
    def _filter_player_props(self, player_props: List[Dict], sport: str) -> List[Dict]:
        """Filter props for a single player."""
        try:
            # Remove avoided prop types
            avoid_list = self.avoid_props.get(sport, [])
            filtered = [p for p in player_props if p.get('prop_type') not in avoid_list]
            
            # Remove props with extreme odds (avoid -1800)
            filtered = [p for p in filtered if abs(p.get('odds', 0)) < 1800]
            
            # Remove props with very low lines (likely to hit)
            if sport == 'MLB':
                filtered = [p for p in filtered if p.get('line', 0) > 0.5]
            elif sport == 'WNBA':
                filtered = [p for p in filtered if p.get('line', 0) > 2.5]
            
            # Remove props with very high lines (unlikely to hit)
            if sport == 'MLB':
                filtered = [p for p in filtered if p.get('line', 0) < 3.5]
            elif sport == 'WNBA':
                filtered = [p for p in filtered if p.get('line', 0) < 25.5]
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error filtering player props: {e}")
            return player_props
    
    def combine_hrr_props(self, player_props: List[Dict]) -> List[Dict]:
        """
        Intelligently combine HRR (Hits, Runs, RBIs) props.
        
        Args:
            player_props: List of props for a player
            
        Returns:
            Combined HRR props plus individual props
        """
        try:
            combined_props = []
            
            # Find HRR props for this player
            hrr_props = {}
            for prop in player_props:
                prop_type = prop.get('prop_type', '')
                if prop_type in ['Hits', 'Runs', 'RBIs']:
                    hrr_props[prop_type] = prop
            
            # Create HRR combinations
            for combo_name, prop_types in self.hrr_combinations.items():
                combo_props = [hrr_props.get(pt) for pt in prop_types if pt in hrr_props]
                
                if len(combo_props) == len(prop_types):  # All props available
                    # Calculate combined line (sum of individual lines)
                    combined_line = sum(p.get('line', 0) for p in combo_props)
                    
                    # Calculate combined odds (average of individual odds)
                    combined_odds = sum(p.get('odds', 0) for p in combo_props) / len(combo_props)
                    
                    # Create combined prop
                    combined_prop = {
                        'player_name': combo_props[0].get('player_name', ''),
                        'prop_type': combo_name,
                        'line': combined_line,
                        'pick_side': 'Over',  # Default to Over for HRR
                        'sport': 'MLB',
                        'odds': combined_odds,
                        'confidence': 0.7,  # Moderate confidence for combinations
                        'reason': f"HRR combination: {', '.join(prop_types)}",
                        'tag': 'hrr-combination',
                        'individual_props': combo_props
                    }
                    
                    combined_props.append(combined_prop)
                    logger.info(f"🔍 Created HRR combination: {combo_name} = {combined_line}")
            
            # Add individual HRR props (if not in combinations)
            individual_hrr = [p for p in player_props if p.get('prop_type') in ['Hits', 'Runs', 'RBIs']]
            combined_props.extend(individual_hrr)
            
            return combined_props
            
        except Exception as e:
            logger.error(f"Error combining HRR props: {e}")
            return player_props
    
    def create_ticket_selections(self, filtered_props: List[Dict], max_selections: int = 3) -> List[Dict]:
        """
        Create ticket selections from filtered props.
        
        Args:
            filtered_props: Filtered props
            max_selections: Maximum selections per ticket
            
        Returns:
            List of ticket selections
        """
        try:
            selections = []
            used_prop_types = set()
            used_players = set()
            
            for prop in filtered_props:
                if len(selections) >= max_selections:
                    break
                
                player_name = prop.get('player_name', '')
                prop_type = prop.get('prop_type', '')
                
                # Avoid duplicate prop types in same ticket
                if prop_type in used_prop_types:
                    continue
                
                # Avoid duplicate players in same ticket
                if player_name in used_players:
                    continue
                
                # Create selection
                selection = {
                    'player_name': player_name,
                    'prop_type': prop_type,
                    'line': prop.get('line', 0),
                    'pick_side': prop.get('pick_side', 'Over'),
                    'sport': prop.get('sport', 'MLB'),
                    'odds': prop.get('odds', 0),
                    'confidence': prop.get('confidence', 0.5),
                    'reason': prop.get('reason', ''),
                    'tag': prop.get('tag', '')
                }
                
                selections.append(selection)
                used_prop_types.add(prop_type)
                used_players.add(player_name)
                
                logger.info(f"🔍 Added selection: {player_name} {prop_type}")
            
            return selections
            
        except Exception as e:
            logger.error(f"Error creating ticket selections: {e}")
            return []
    
    def validate_ticket(self, selections: List[Dict], sport: str) -> Tuple[bool, str]:
        """
        Validate a ticket for posting.
        
        Args:
            selections: Ticket selections
            sport: Sport type
            
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            if not selections:
                return False, "No selections"
            
            # Check for duplicate players
            players = [s.get('player_name', '') for s in selections]
            if len(players) != len(set(players)):
                return False, "Duplicate players"
            
            # Check for duplicate prop types
            prop_types = [s.get('prop_type', '') for s in selections]
            if len(prop_types) != len(set(prop_types)):
                return False, "Duplicate prop types"
            
            # Check for mixed sports
            sports = [s.get('sport', '') for s in selections]
            if len(set(sports)) > 1:
                return False, "Mixed sports"
            
            # Check for reasonable odds
            total_odds = sum(abs(s.get('odds', 0)) for s in selections)
            if total_odds > 5000:  # Avoid extreme odds
                return False, "Extreme odds"
            
            # Check for reasonable confidence
            avg_confidence = sum(s.get('confidence', 0) for s in selections) / len(selections)
            if avg_confidence < 0.3:
                return False, "Low confidence"
            
            return True, "Valid ticket"
            
        except Exception as e:
            logger.error(f"Error validating ticket: {e}")
            return False, f"Error: {e}"
    
    def get_best_props_for_player(self, player_props: List[Dict], sport: str, max_props: int = 2) -> List[Dict]:
        """
        Get the best props for a player based on priority and value.
        
        Args:
            player_props: All props for a player
            sport: Sport type
            max_props: Maximum props to return
            
        Returns:
            Best props for the player
        """
        try:
            # Filter props
            filtered = self._filter_player_props(player_props, sport)
            
            if not filtered:
                return []
            
            # Sort by priority
            priorities = self.mlb_priorities if sport == 'MLB' else self.wnba_priorities
            filtered.sort(key=lambda p: priorities.get(p.get('prop_type', ''), 0), reverse=True)
            
            # Return top props
            return filtered[:max_props]
            
        except Exception as e:
            logger.error(f"Error getting best props: {e}")
            return [] 