from core.tennis_api_client import get_fixtures, get_players, get_h2h, get_odds
from datetime import datetime, timedelta
import json
import os
from typing import List, Dict, Any, Optional

class TennisPropFetcher:
    """Dynamic tennis prop fetcher for AI ticket generation."""
    
    def __init__(self):
        self.cache_dir = "data/tennis_props"
        self.ensure_cache_dir()
        
    def ensure_cache_dir(self):
        """Ensure the cache directory exists."""
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def get_available_matches(self, days_ahead: int = 1) -> List[Dict]:
        """Get available matches for today (default) or next N days."""
        matches = []
        today = datetime.now()
        for i in range(days_ahead):
            date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            fixtures = get_fixtures(date, date_stop=date)
            if fixtures:
                matches.extend(fixtures)
        return matches

    def filter_underdog_quality_matches(self, matches: List[Dict]) -> List[Dict]:
        """Filter matches to only include high-quality matches Underdog would likely cover."""
        filtered_matches = []
        
        # Priority event types (in order of preference)
        priority_events = [
            'Atp Singles', 'Wta Singles',  # Grand Slams, Tour events
            'Challenger Men Singles', 'Challenger Women Singles',  # Challenger main draws
            'Itf Men Singles', 'Itf Women Singles'  # ITF pro circuit
        ]
        
        # Tournament keywords that indicate quality events
        quality_tournaments = [
            'wimbledon', 'us open', 'australian open', 'french open',  # Grand Slams
            'atp', 'wta', 'challenger', 'itf',  # Professional circuits
            'masters', '500', '250', '125k'  # Tour levels
        ]
        
        for match in matches:
            event_type = match.get('event_type_type', '').lower()
            tournament = match.get('tournament_name', '').lower()
            
            # Only include singles matches
            if 'doubles' in event_type or 'mixed' in event_type:
                continue
                
            # Check if it's a priority event type
            is_priority_event = any(priority in event_type for priority in priority_events)
            
            # Check if tournament name suggests quality
            is_quality_tournament = any(keyword in tournament for keyword in quality_tournaments)
            
            # Include if it's a priority event OR quality tournament
            if is_priority_event or is_quality_tournament:
                filtered_matches.append(match)
        
        # Sort by priority (ATP/WTA first, then Challenger, then ITF)
        def get_priority_score(match):
            event_type = match.get('event_type_type', '').lower()
            if 'atp singles' in event_type or 'wta singles' in event_type:
                return 1
            elif 'challenger' in event_type:
                return 2
            elif 'itf' in event_type:
                return 3
            return 4
        
        filtered_matches.sort(key=get_priority_score)
        
        # Limit to top 20-25 matches
        return filtered_matches[:25]

    def get_unique_players_from_matches(self, matches: List[Dict]) -> List[Dict]:
        """Extract unique players from matches, prioritizing by tournament level."""
        unique_players = {}
        
        for match in matches:
            player1 = match.get('event_first_player', '')
            player2 = match.get('event_second_player', '')
            tournament = match.get('tournament_name', '')
            event_type = match.get('event_type_type', '')
            
            # Priority score for tournament level
            def get_tournament_priority(event_type):
                if 'atp singles' in event_type.lower() or 'wta singles' in event_type.lower():
                    return 1
                elif 'challenger' in event_type.lower():
                    return 2
                elif 'itf' in event_type.lower():
                    return 3
                return 4
            
            priority = get_tournament_priority(event_type)
            
            # Add players if not already seen, or if this tournament has higher priority
            for player in [player1, player2]:
                if player and player not in unique_players:
                    unique_players[player] = {
                        'player': player,
                        'tournament': tournament,
                        'event_type': event_type,
                        'priority': priority,
                        'match_data': match
                    }
                elif player in unique_players:
                    # Update if this tournament has higher priority
                    if priority < unique_players[player]['priority']:
                        unique_players[player] = {
                            'player': player,
                            'tournament': tournament,
                            'event_type': event_type,
                            'priority': priority,
                            'match_data': match
                        }
        
        # Sort by priority and limit to ~20 players
        sorted_players = sorted(unique_players.values(), key=lambda x: x['priority'])
        return sorted_players[:20]

    def estimate_stat(self, stats: Optional[List[Dict]], stat_name: str) -> Optional[float]:
        """Extract a specific stat from player stats."""
        if not stats or not isinstance(stats, list):
            return None
        for s in stats[0].get('stats', []):
            if stat_name in s:
                try:
                    return float(s[stat_name])
                except (ValueError, TypeError):
                    return None
        return None
    
    def generate_underdog_props(self, match: Dict) -> List[Dict]:
        """Generate Underdog-style props for a tennis match."""
        player1 = match.get('event_first_player')
        player2 = match.get('event_second_player')
        player1_key = match.get('first_player_key')
        player2_key = match.get('second_player_key')
        
        # Get player data
        p1_stats = get_players(player_key=player1_key) if player1_key else None
        p2_stats = get_players(player_key=player2_key) if player2_key else None
        
        # Get H2H data
        h2h = get_h2h(player1_key, player2_key) if player1_key and player2_key and isinstance(player1_key, str) and isinstance(player2_key, str) else None
        
        props = []
        
        # Games Played (Higher/Lower) - Total games in the match
        avg_games = self.estimate_stat(p1_stats, 'games_played_avg')
        if avg_games:
            props.append({
                'player': f"{player1} vs {player2}",
                'prop': 'Games Played',
                'line': 20.5,
                'pick': 'Higher' if avg_games > 20.5 else 'Lower',
                'confidence': 0.6,
                'reasoning': f"Based on season avg: {avg_games:.1f} games played per match.",
                'match_info': f"{player1} vs {player2}",
                'tournament': match.get('tournament_name', 'Unknown'),
                'event_type': match.get('event_type_type', 'Unknown'),
                'date': match.get('event_date', 'Unknown'),
                'time': match.get('event_time', 'Unknown')
            })
        
        # Games Won (Higher/Lower) for each player
        for player, stats, player_key in [(player1, p1_stats, player1_key), (player2, p2_stats, player2_key)]:
            avg_games_won = self.estimate_stat(stats, 'games_won_avg')
            if avg_games_won:
                props.append({
                    'player': player,
                    'prop': 'Games Won',
                    'line': 10.5,
                    'pick': 'Higher' if avg_games_won > 10.5 else 'Lower',
                    'confidence': 0.6,
                    'reasoning': f"Based on season avg: {avg_games_won:.1f} games won per match.",
                    'match_info': f"{player1} vs {player2}",
                    'tournament': match.get('tournament_name', 'Unknown'),
                    'event_type': match.get('event_type_type', 'Unknown'),
                    'date': match.get('event_date', 'Unknown'),
                    'time': match.get('event_time', 'Unknown')
                })
        
        # Sets won (Higher/Lower) for each player
        for player, stats in [(player1, p1_stats), (player2, p2_stats)]:
            avg_sets = self.estimate_stat(stats, 'sets_won_avg')
            if avg_sets:
                props.append({
                    'player': player,
                    'prop': 'Sets won',
                    'line': 0.5,
                    'pick': 'Higher' if avg_sets > 0.5 else 'Lower',
                    'confidence': 0.6,
                    'reasoning': f"Based on season avg: {avg_sets:.1f} sets won per match.",
                    'match_info': f"{player1} vs {player2}",
                    'tournament': match.get('tournament_name', 'Unknown'),
                    'event_type': match.get('event_type_type', 'Unknown'),
                    'date': match.get('event_date', 'Unknown'),
                    'time': match.get('event_time', 'Unknown')
                })
        
        # 1st Set Games Played (Higher/Lower)
        avg_first_set = self.estimate_stat(p1_stats, 'first_set_games_avg')
        if avg_first_set:
            props.append({
                'player': f"{player1} vs {player2}",
                'prop': '1st Set Games Played',
                'line': 9.5,
                'pick': 'Higher' if avg_first_set > 9.5 else 'Lower',
                'confidence': 0.6,
                'reasoning': f"Based on season avg: {avg_first_set:.1f} games in 1st set.",
                'match_info': f"{player1} vs {player2}",
                'tournament': match.get('tournament_name', 'Unknown'),
                'event_type': match.get('event_type_type', 'Unknown'),
                'date': match.get('event_date', 'Unknown'),
                'time': match.get('event_time', 'Unknown')
            })
        
        # Breakpoints Won (Higher/Lower) for each player
        for player, stats in [(player1, p1_stats), (player2, p2_stats)]:
            bp_won = self.estimate_stat(stats, 'breakpoints_won')
            if bp_won:
                props.append({
                    'player': player,
                    'prop': 'Breakpoints Won',
                    'line': 2.5,
                    'pick': 'Higher' if bp_won > 2.5 else 'Lower',
                    'confidence': 0.6,
                    'reasoning': f"Based on season avg: {bp_won:.1f} breakpoints won per match.",
                    'match_info': f"{player1} vs {player2}",
                    'tournament': match.get('tournament_name', 'Unknown'),
                    'event_type': match.get('event_type_type', 'Unknown'),
                    'date': match.get('event_date', 'Unknown'),
                    'time': match.get('event_time', 'Unknown')
                })
        
        # Aces (Higher/Lower) for each player
        for player, stats in [(player1, p1_stats), (player2, p2_stats)]:
            avg_aces = self.estimate_stat(stats, 'aces')
            if avg_aces:
                props.append({
                    'player': player,
                    'prop': 'Aces',
                    'line': 4.5,
                    'pick': 'Higher' if avg_aces > 4.5 else 'Lower',
                    'confidence': 0.6,
                    'reasoning': f"Based on season/career avg: {avg_aces:.1f} aces per match.",
                    'match_info': f"{player1} vs {player2}",
                    'tournament': match.get('tournament_name', 'Unknown'),
                    'event_type': match.get('event_type_type', 'Unknown'),
                    'date': match.get('event_date', 'Unknown'),
                    'time': match.get('event_time', 'Unknown')
                })
        
        return props
    
    # ATP and WTA Top 50 (as of July 2024, singles only, last names only for matching)
    ATP_TOP_50 = [
        'Carlos Alcaraz', 'Novak Djokovic', 'Jannik Sinner', 'Daniil Medvedev', 'Alexander Zverev',
        'Andrey Rublev', 'Casper Ruud', 'Hubert Hurkacz', 'Alex de Minaur', 'Grigor Dimitrov',
        'Stefanos Tsitsipas', 'Taylor Fritz', 'Holger Rune', 'Tommy Paul', 'Karen Khachanov',
        'Ben Shelton', 'Frances Tiafoe', 'Sebastian Korda', 'Ugo Humbert', 'Adrian Mannarino',
        'Nicolas Jarry', 'Francisco Cerundolo', 'Lorenzo Musetti', 'Alexander Bublik', 'Jan-Lennard Struff',
        'Sebastian Baez', 'Tallon Griekspoor', 'Alejandro Davidovich Fokina', 'Jiri Lehecka', 'Tomas Martin Etcheverry',
        'Arthur Fils', 'Matteo Arnaldi', 'Cameron Norrie', 'Mackenzie McDonald', 'Laslo Djere',
        'Yannick Hanfmann', 'Dominik Koepfer', 'Lorenzo Sonego', 'Miomir Kecmanovic', 'Alexei Popyrin',
        'Daniel Evans', 'Roman Safiullin', 'Christopher Eubanks', 'Marcos Giron', 'Richard Gasquet',
        'Jordan Thompson', 'Emil Ruusuvuori', 'Zhizhen Zhang', 'Borna Coric', 'Jack Draper'
    ]
    WTA_TOP_50 = [
        'Iga Swiatek', 'Aryna Sabalenka', 'Coco Gauff', 'Elena Rybakina', 'Jessica Pegula',
        'Ons Jabeur', 'Marketa Vondrousova', 'Maria Sakkari', 'Jelena Ostapenko', 'Daria Kasatkina',
        'Madison Keys', 'Liudmila Samsonova', 'Danielle Collins', 'Ekaterina Alexandrova', 'Elina Svitolina',
        'Beatriz Haddad Maia', 'Veronika Kudermetova', 'Victoria Azarenka', 'Anastasia Pavlyuchenkova', 'Emma Navarro',
        'Sorana Cirstea', 'Caroline Garcia', 'Petra Kvitova', 'Anna Kalinskaya', 'Linda Noskova',
        'Katerina Siniakova', 'Leylah Fernandez', 'Yulia Putintseva', 'Marie Bouzkova', 'Elise Mertens',
        'Xinyu Wang', 'Zhu Lin', 'Sofia Kenin', 'Tatjana Maria', 'Anna Blinkova',
        'Anhelina Kalinina', 'Martina Trevisan', 'Alycia Parks', 'Magda Linette', 'Sloane Stephens',
        'Camila Giorgi', 'Jasmine Paolini', 'Clara Burel', 'Varvara Gracheva', 'Aliaksandra Sasnovich',
        'Paula Badosa', 'Petra Martic', 'Bernarda Pera', 'Karolina Muchova', 'Donna Vekic'
    ]

    def get_star_name_variants(self, name: str):
        """Generate possible API name variants for a star (full name, initial+last, last name only)."""
        parts = name.split()
        variants = set()
        if len(parts) == 2:
            first, last = parts
            variants.add(name)
            variants.add(f"{first[0]}. {last}")
            variants.add(last)
        else:
            variants.add(name)
        return variants

    def is_star_player(self, player_name: str) -> bool:
        """Check if a player is in the ATP or WTA top 50, matching full name, initial+last, or last name only."""
        player_name_lower = player_name.lower().replace('.', '').replace('  ', ' ').strip()
        for star in self.ATP_TOP_50 + self.WTA_TOP_50:
            for variant in self.get_star_name_variants(star):
                variant_lower = variant.lower().replace('.', '').replace('  ', ' ').strip()
                if variant_lower == player_name_lower:
                    return True
        return False

    def filter_star_matches(self, matches: List[Dict]) -> List[Dict]:
        """Filter matches to only include those with at least one top 50 star player."""
        filtered = []
        for match in matches:
            player1 = match.get('event_first_player', '')
            player2 = match.get('event_second_player', '')
            if self.is_star_player(player1) or self.is_star_player(player2):
                filtered.append(match)
        return filtered

    def fetch_all_props(self, days_ahead: int = 1) -> List[Dict]:
        print(f"Fetching tennis props for next {days_ahead} day(s)... (stars only)")
        matches = self.get_available_matches(days_ahead)
        print(f"Found {len(matches)} total matches")
        star_matches = self.filter_star_matches(matches)
        print(f"Filtered to {len(star_matches)} matches with top 50 stars")
        unique_players = self.get_unique_players_from_matches(star_matches)
        print(f"Extracted {len(unique_players)} unique star players")
        all_props = []
        for i, player_info in enumerate(unique_players, 1):
            player = player_info['player']
            if not self.is_star_player(player):
                continue
            tournament = player_info['tournament']
            event_type = player_info['event_type']
            match_data = player_info['match_data']
            print(f"Processing star {i}/{len(unique_players)}: {player}")
            print(f"  Tournament: {tournament} ({event_type})")
            try:
                props = self.generate_underdog_props(match_data)
                all_props.extend(props)
                print(f"  Generated {len(props)} props")
            except Exception as e:
                print(f"  Error generating props: {e}")
                continue
        print(f"Total props generated: {len(all_props)}")
        return all_props
    
    def save_props_to_cache(self, props: List[Dict], filename: Optional[str] = None):
        """Save props to cache file."""
        self.ensure_cache_dir()
        if not filename or not isinstance(filename, str):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"tennis_props_{timestamp}.json"
        filepath = os.path.join(self.cache_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(props, f, indent=2, default=str)
        print(f"Props saved to {filepath}")
        return filepath
    
    def load_props_from_cache(self, filename: Optional[str]) -> List[Dict]:
        """Load props from cache file."""
        self.ensure_cache_dir()
        if not filename or not isinstance(filename, str):
            return []
        filepath = os.path.join(self.cache_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return []
    
    def get_latest_props(self) -> List[Dict]:
        """Get the latest cached props or fetch new ones."""
        self.ensure_cache_dir()
        cache_files = [f for f in os.listdir(self.cache_dir) if f.startswith('tennis_props_')]
        if cache_files:
            latest_file = max(cache_files)
            props = self.load_props_from_cache(latest_file)
            print(f"Loaded {len(props)} props from cache: {latest_file}")
            return props
        else:
            props = self.fetch_all_props()
            self.save_props_to_cache(props)
            return props

    def get_all_unique_singles_players(self, days_ahead: int = 1) -> set:
        """Return a set of all unique singles players for the next N days (default: today)."""
        matches = self.get_available_matches(days_ahead)
        singles_matches = [m for m in matches if 'singles' in m.get('event_type_type', '').lower()]
        players = set()
        for match in singles_matches:
            p1 = match.get('event_first_player', '').strip()
            p2 = match.get('event_second_player', '').strip()
            if p1:
                players.add(p1)
            if p2:
                players.add(p2)
        return players

    def dump_all_player_stats_and_odds(self, days_ahead: int = 1, output_file: str = 'all_player_stats_and_odds.json'):
        """Fetch and save all player stats, odds, and match info for every match today (for research/analysis)."""
        print(f"Dumping all player stats and odds for next {days_ahead} day(s)...")
        matches = self.get_available_matches(days_ahead)
        print(f"Found {len(matches)} matches")
        all_data = []
        for i, match in enumerate(matches, 1):
            player1 = match.get('event_first_player', '')
            player2 = match.get('event_second_player', '')
            player1_key = match.get('first_player_key')
            player2_key = match.get('second_player_key')
            event_time = match.get('event_time', '')
            tournament = match.get('tournament_name', '')
            event_type = match.get('event_type_type', '')
            match_key = match.get('event_key')
            # Fetch player stats
            p1_stats = get_players(player_key=player1_key) if player1_key else None
            p2_stats = get_players(player_key=player2_key) if player2_key else None
            # Fetch odds
            odds = get_odds(match_key) if match_key else None
            all_data.append({
                'player1': player1,
                'player2': player2,
                'event_time': event_time,
                'tournament': tournament,
                'event_type': event_type,
                'player1_stats': p1_stats,
                'player2_stats': p2_stats,
                'odds': odds,
                'raw_match': match
            })
            print(f"{i:3d}/{len(matches)}: {player1} vs {player2} ({tournament}) - Stats/odds fetched")
        # Save to file
        with open(output_file, 'w') as f:
            import json
            json.dump(all_data, f, indent=2, default=str)
        print(f"All player stats and odds saved to {output_file}")

def main():
    """Test the tennis prop fetcher."""
    fetcher = TennisPropFetcher()
    
    # Fetch all props
    props = fetcher.fetch_all_props()
    
    # Save to cache
    fetcher.save_props_to_cache(props)
    
    # Show sample props
    print(f"\n=== SAMPLE PROPS ===")
    for i, prop in enumerate(props[:10]):
        print(f"{i+1}. {prop['player']} - {prop['prop']} {prop['line']} ({prop['pick']})")
        print(f"   Match: {prop['match_info']}")
        print(f"   Tournament: {prop['tournament']}")
        print(f"   Confidence: {prop['confidence']}")
        print()

if __name__ == "__main__":
    fetcher = TennisPropFetcher()
    all_players = fetcher.get_all_unique_singles_players()
    print(f"All unique singles players for today: {len(all_players)}")
    for i, player in enumerate(sorted(all_players), 1):
        print(f"{i:3d}. {player}") 