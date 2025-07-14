import os
import json
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

class WNBAPlayerAnalyzer:
    def __init__(self, 
                 odds_data_path='data/historical_odds/basketball_wnba',
                 player_tags_path='ghost_ai_core_memory/player_tags',
                 prop_memory_path='odds_reverse_engineering/data/prop_memory.json',
                 historical_props_path='ghost_ai_core_memory/prop_outcomes/historical_props.json'):
        self.odds_data_path = odds_data_path
        self.player_tags_path = player_tags_path
        self.prop_memory_path = prop_memory_path
        self.historical_props_path = historical_props_path
        
        self.players_data = {}
        self.teams_data = {}
        self.matchups_data = {}
        self.game_odds_data = {}
        self.player_prop_data = {}
        
        self.load_all_data()
    
    def load_all_data(self):
        """Load all WNBA data from multiple sources"""
        print("Loading WNBA historical data...")
        
        # Load historical game odds data
        self.load_historical_odds()
        
        # Load player tracking data
        self.load_player_tags()
        
        # Load prop memory data
        self.load_prop_memory()
        
        # Load historical props outcomes
        self.load_historical_props()
        
        print(f"Loaded data for {len(self.players_data)} players across {len(self.teams_data)} teams")
        print(f"Processed {len(self.game_odds_data)} games with odds data")
        print(f"Loaded {len(self.player_prop_data)} player prop records")
    
    def load_historical_odds(self):
        """Load historical game odds data"""
        print("Loading historical game odds...")
        
        for date_folder in os.listdir(self.odds_data_path):
            date_path = os.path.join(self.odds_data_path, date_folder)
            if os.path.isdir(date_path):
                date = date_folder
                print(f"Processing odds data for {date}...")
                
                for game_file in os.listdir(date_path):
                    if game_file.endswith('.json'):
                        game_path = os.path.join(date_path, game_file)
                        self.process_game_odds(game_path, date)
    
    def process_game_odds(self, game_path, date):
        """Process game odds data and extract team/line information"""
        try:
            with open(game_path, 'r') as f:
                game_data = json.load(f)
            
            if 'data' in game_data:
                game_info = game_data['data']
                home_team = game_info.get('home_team')
                away_team = game_info.get('away_team')
                game_id = game_info.get('id')
                commence_time = game_info.get('commence_time')
                
                # Store game data
                self.game_odds_data[game_id] = {
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'commence_time': commence_time,
                    'bookmakers': game_info.get('bookmakers', [])
                }
                
                # Initialize team data
                for team in [home_team, away_team]:
                    if team and team not in self.teams_data:
                        self.teams_data[team] = {
                            'games': [],
                            'head_to_head': defaultdict(list),
                            'odds_history': []
                        }
                
                # Store team game data
                game_record = {
                    'date': date,
                    'game_id': game_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'commence_time': commence_time
                }
                
                if home_team:
                    self.teams_data[home_team]['games'].append(game_record)
                    self.teams_data[home_team]['head_to_head'][away_team].append(game_record)
                
                if away_team:
                    self.teams_data[away_team]['games'].append(game_record)
                    self.teams_data[away_team]['head_to_head'][home_team].append(game_record)
                
                # Extract odds data
                self.extract_odds_data(game_info, game_id)
        
        except Exception as e:
            print(f"Error processing {game_path}: {e}")
    
    def extract_odds_data(self, game_info, game_id):
        """Extract and store odds data for analysis"""
        bookmakers = game_info.get('bookmakers', [])
        
        for bookmaker in bookmakers:
            bookmaker_key = bookmaker.get('key')
            markets = bookmaker.get('markets', [])
            
            for market in markets:
                market_key = market.get('key')
                outcomes = market.get('outcomes', [])
                
                # Store odds data for analysis
                for outcome in outcomes:
                    odds_record = {
                        'game_id': game_id,
                        'bookmaker': bookmaker_key,
                        'market': market_key,
                        'outcome': outcome.get('name', ''),
                        'price': outcome.get('price', 0),
                        'point': outcome.get('point', 0)
                    }
                    
                    # Store in appropriate team data
                    if outcome.get('name') in self.teams_data:
                        self.teams_data[outcome['name']]['odds_history'].append(odds_record)
    
    def load_player_tags(self):
        """Load player tracking data from player tags"""
        print("Loading player tracking data...")
        
        if not os.path.exists(self.player_tags_path):
            print(f"Player tags path not found: {self.player_tags_path}")
            return
        
        for filename in os.listdir(self.player_tags_path):
            if filename.endswith('.json'):
                player_path = os.path.join(self.player_tags_path, filename)
                try:
                    with open(player_path, 'r') as f:
                        player_data = json.load(f)
                    
                    player_name = player_data.get('player_name', '')
                    if player_name:
                        self.players_data[player_name] = {
                            'team': player_data.get('team', 'Unknown'),
                            'sport': player_data.get('sport', 'wnba'),
                            'total_picks': player_data.get('total_picks', 0),
                            'hits': player_data.get('hits', 0),
                            'misses': player_data.get('misses', 0),
                            'pushes': player_data.get('pushes', 0),
                            'current_streak': player_data.get('current_streak', 0),
                            'best_streak': player_data.get('best_streak', 0),
                            'prop_types': player_data.get('prop_types', {}),
                            'last_updated': player_data.get('last_updated', ''),
                            'games': [],
                            'odds_history': []
                        }
                
                except Exception as e:
                    print(f"Error loading player {filename}: {e}")
    
    def load_prop_memory(self):
        """Load prop memory data"""
        print("Loading prop memory data...")
        
        if not os.path.exists(self.prop_memory_path):
            print(f"Prop memory path not found: {self.prop_memory_path}")
            return
        
        try:
            with open(self.prop_memory_path, 'r') as f:
                prop_memory = json.load(f)
            
            for key, data in prop_memory.items():
                if '_player_' in key:
                    # Extract player name and prop type from key
                    parts = key.split('_player_')
                    if len(parts) == 2:
                        player_name = parts[0].replace('_', ' ')
                        prop_type = parts[1]
                        
                        if player_name not in self.player_prop_data:
                            self.player_prop_data[player_name] = {}
                        
                        self.player_prop_data[player_name][prop_type] = data
        
        except Exception as e:
            print(f"Error loading prop memory: {e}")
    
    def load_historical_props(self):
        """Load historical props outcomes"""
        print("Loading historical props outcomes...")
        
        if not os.path.exists(self.historical_props_path):
            print(f"Historical props path not found: {self.historical_props_path}")
            return
        
        try:
            with open(self.historical_props_path, 'r') as f:
                historical_props = json.load(f)
            
            # Process historical props data
            for prop_record in historical_props:
                player_name = prop_record.get('player_name', '')
                if player_name and player_name in self.players_data:
                    if 'historical_props' not in self.players_data[player_name]:
                        self.players_data[player_name]['historical_props'] = []
                    
                    self.players_data[player_name]['historical_props'].append(prop_record)
        
        except Exception as e:
            print(f"Error loading historical props: {e}")
    
    def analyze_team_performance(self, team_name):
        """Analyze team performance patterns"""
        if team_name not in self.teams_data:
            return None
        
        team_data = self.teams_data[team_name]
        games = team_data['games']
        
        if not games:
            return None
        
        # Analyze head-to-head matchups
        h2h_analysis = {}
        for opponent, h2h_games in team_data['head_to_head'].items():
            h2h_analysis[opponent] = {
                'total_games': len(h2h_games),
                'recent_games': h2h_games[-5:] if len(h2h_games) >= 5 else h2h_games
            }
        
        # Analyze odds patterns
        odds_analysis = self.analyze_team_odds(team_data['odds_history'])
        
        return {
            'team': team_name,
            'total_games': len(games),
            'head_to_head': h2h_analysis,
            'odds_analysis': odds_analysis,
            'recent_games': games[-10:] if len(games) >= 10 else games
        }
    
    def analyze_team_odds(self, odds_history):
        """Analyze team odds patterns"""
        if not odds_history:
            return {}
        
        # Group by market type
        market_analysis = defaultdict(list)
        for odds in odds_history:
            market_analysis[odds['market']].append(odds)
        
        analysis = {}
        for market, odds_list in market_analysis.items():
            prices = [odds['price'] for odds in odds_list]
            points = [odds['point'] for odds in odds_list if odds['point'] != 0]
            
            analysis[market] = {
                'total_odds': len(odds_list),
                'avg_price': np.mean(prices) if prices else 0,
                'price_range': (min(prices), max(prices)) if prices else (0, 0),
                'avg_point': np.mean(points) if points else 0,
                'point_range': (min(points), max(points)) if points else (0, 0)
            }
        
        return analysis
    
    def analyze_player_performance(self, player_name):
        """Analyze player performance patterns"""
        if player_name not in self.players_data:
            return None
        
        player_data = self.players_data[player_name]
        
        # Calculate performance metrics
        total_picks = player_data.get('total_picks', 0)
        hits = player_data.get('hits', 0)
        misses = player_data.get('misses', 0)
        pushes = player_data.get('pushes', 0)
        
        win_rate = (hits / total_picks * 100) if total_picks > 0 else 0
        push_rate = (pushes / total_picks * 100) if total_picks > 0 else 0
        
        # Analyze prop types
        prop_analysis = {}
        for prop_type, data in player_data.get('prop_types', {}).items():
            attempts = data.get('attempts', 0)
            hits = data.get('hits', 0)
            prop_win_rate = (hits / attempts * 100) if attempts > 0 else 0
            
            prop_analysis[prop_type] = {
                'attempts': attempts,
                'hits': hits,
                'win_rate': prop_win_rate
            }
        
        # Get prop memory data if available
        prop_memory = self.player_prop_data.get(player_name, {})
        
        return {
            'player': player_name,
            'team': player_data.get('team', 'Unknown'),
            'total_picks': total_picks,
            'hits': hits,
            'misses': misses,
            'pushes': pushes,
            'win_rate': win_rate,
            'push_rate': push_rate,
            'current_streak': player_data.get('current_streak', 0),
            'best_streak': player_data.get('best_streak', 0),
            'prop_analysis': prop_analysis,
            'prop_memory': prop_memory,
            'historical_props': player_data.get('historical_props', [])
        }
    
    def find_most_reliable_players(self, min_picks=10):
        """Find players with the most reliable performance"""
        reliable_players = []
        
        for player_name, player_data in self.players_data.items():
            total_picks = player_data.get('total_picks', 0)
            if total_picks >= min_picks:
                hits = player_data.get('hits', 0)
                win_rate = (hits / total_picks * 100) if total_picks > 0 else 0
                
                reliable_players.append({
                    'player': player_name,
                    'team': player_data.get('team', 'Unknown'),
                    'total_picks': total_picks,
                    'hits': hits,
                    'win_rate': win_rate,
                    'current_streak': player_data.get('current_streak', 0)
                })
        
        # Sort by win rate
        reliable_players.sort(key=lambda x: x['win_rate'], reverse=True)
        return reliable_players
    
    def find_best_prop_types(self, min_attempts=5):
        """Find the most profitable prop types"""
        prop_type_stats = defaultdict(lambda: {'total_attempts': 0, 'total_hits': 0})
        
        for player_data in self.players_data.values():
            for prop_type, data in player_data.get('prop_types', {}).items():
                attempts = data.get('attempts', 0)
                hits = data.get('hits', 0)
                
                prop_type_stats[prop_type]['total_attempts'] += attempts
                prop_type_stats[prop_type]['total_hits'] += hits
        
        # Calculate win rates
        prop_performance = []
        for prop_type, stats in prop_type_stats.items():
            if stats['total_attempts'] >= min_attempts:
                win_rate = (stats['total_hits'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
                prop_performance.append({
                    'prop_type': prop_type,
                    'total_attempts': stats['total_attempts'],
                    'total_hits': stats['total_hits'],
                    'win_rate': win_rate
                })
        
        # Sort by win rate
        prop_performance.sort(key=lambda x: x['win_rate'], reverse=True)
        return prop_performance
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive analysis report"""
        print("\n=== WNBA COMPREHENSIVE ANALYSIS REPORT ===\n")
        
        # Team Analysis
        print("=== TEAM ANALYSIS ===")
        for team_name in sorted(self.teams_data.keys()):
            team_analysis = self.analyze_team_performance(team_name)
            if team_analysis:
                print(f"\n{team_name}:")
                print(f"  Total Games: {team_analysis['total_games']}")
                print(f"  Head-to-Head Matchups: {len(team_analysis['head_to_head'])}")
        
        # Player Performance
        print("\n=== PLAYER PERFORMANCE ANALYSIS ===")
        reliable_players = self.find_most_reliable_players(min_picks=5)
        print(f"\nTop 10 Most Reliable Players (min 5 picks):")
        for i, player in enumerate(reliable_players[:10], 1):
            print(f"{i}. {player['player']} ({player['team']}) - {player['win_rate']:.1f}% ({player['hits']}/{player['total_picks']})")
        
        # Prop Type Analysis
        print("\n=== PROP TYPE ANALYSIS ===")
        prop_performance = self.find_best_prop_types(min_attempts=10)
        print(f"\nProp Type Performance (min 10 attempts):")
        for prop in prop_performance:
            print(f"{prop['prop_type']}: {prop['win_rate']:.1f}% ({prop['total_hits']}/{prop['total_attempts']})")
        
        # Summary Statistics
        print("\n=== SUMMARY STATISTICS ===")
        total_players = len(self.players_data)
        total_games = len(self.game_odds_data)
        total_prop_records = len(self.player_prop_data)
        
        print(f"Total Players Tracked: {total_players}")
        print(f"Total Games Analyzed: {total_games}")
        print(f"Total Prop Records: {total_prop_records}")
        print(f"Teams Analyzed: {len(self.teams_data)}")
        
        return {
            'teams': len(self.teams_data),
            'players': total_players,
            'games': total_games,
            'prop_records': total_prop_records,
            'reliable_players': reliable_players,
            'prop_performance': prop_performance
        }

# Main execution
if __name__ == "__main__":
    analyzer = WNBAPlayerAnalyzer()
    report = analyzer.generate_comprehensive_report()
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("The analyzer has processed all available WNBA data and generated comprehensive insights.")
    print("Use the analyzer methods to get specific player or team analysis.") 