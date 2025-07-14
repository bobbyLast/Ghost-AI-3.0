#!/usr/bin/env python3
"""
Kaggle Top 50 Tennis Players Data Fetcher
Pulls data for the top 50 ATP tennis players from Kaggle dataset.
"""

import os
import sys
import json
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kaggle_tennis_fetcher')

class KaggleTop50TennisFetcher:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data" / "tennis_kaggle"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Top 50 ATP players (current and recent top players)
        self.top_50_players_full = [
            "Novak Djokovic", "Carlos Alcaraz", "Daniil Medvedev", "Jannik Sinner",
            "Andrey Rublev", "Stefanos Tsitsipas", "Alexander Zverev", "Holger Rune",
            "Hubert Hurkacz", "Taylor Fritz", "Casper Ruud", "Alex de Minaur",
            "Tommy Paul", "Ben Shelton", "Frances Tiafoe", "Sebastian Korda",
            "Karen Khachanov", "Cameron Norrie", "Lorenzo Musetti", "Ugo Humbert",
            "Grigor Dimitrov", "Adrian Mannarino", "Nicolas Jarry", "Sebastian Baez",
            "Alejandro Tabilo", "Tomas Machac", "Mariano Navone", "Luciano Darderi",
            "Flavio Cobolli", "Jakub Mensik", "Arthur Fils", "Luca Van Assche",
            "Alexei Popyrin", "Jordan Thompson", "Christopher Eubanks", "Max Purcell",
            "Mackenzie McDonald", "Marcos Giron", "Brandon Nakashima", "JJ Wolf",
            "Emil Ruusuvuori", "Mikael Ymer", "Tallon Griekspoor", "Botic van de Zandschulp",
            "Daniel Evans", "Andy Murray", "Stan Wawrinka", "Richard Gasquet",
            "Roberto Bautista Agut", "Marin Cilic", "Kei Nishikori"
        ]
        # Map to 'LastName F.' format for dataset matching
        self.top_50_players = [
            "Djokovic N.", "Alcaraz C.", "Medvedev D.", "Sinner J.",
            "Rublev A.", "Tsitsipas S.", "Zverev A.", "Rune H.",
            "Hurkacz H.", "Fritz T.", "Ruud C.", "de Minaur A.",
            "Paul T.", "Shelton B.", "Tiafoe F.", "Korda S.",
            "Khachanov K.", "Norrie C.", "Musetti L.", "Humbert U.",
            "Dimitrov G.", "Mannarino A.", "Jarry N.", "Baez S.",
            "Tabilo A.", "Machac T.", "Navone M.", "Darderi L.",
            "Cobolli F.", "Mensik J.", "Fils A.", "Van Assche L.",
            "Popyrin A.", "Thompson J.", "Eubanks C.", "Purcell M.",
            "McDonald M.", "Giron M.", "Nakashima B.", "Wolf J.",
            "Ruusuvuori E.", "Ymer M.", "Griekspoor T.", "van de Zandschulp B.",
            "Evans D.", "Murray A.", "Wawrinka S.", "Gasquet R.",
            "Bautista Agut R.", "Cilic M.", "Nishikori K."
        ]
        
        # Alternative spellings and variations for player matching
        self.player_variations = {
            "Novak Djokovic": ["Djokovic", "N. Djokovic"],
            "Carlos Alcaraz": ["Alcaraz", "C. Alcaraz"],
            "Daniil Medvedev": ["Medvedev", "D. Medvedev"],
            "Jannik Sinner": ["Sinner", "J. Sinner"],
            "Andrey Rublev": ["Rublev", "A. Rublev"],
            "Stefanos Tsitsipas": ["Tsitsipas", "S. Tsitsipas"],
            "Alexander Zverev": ["Zverev", "A. Zverev", "Sascha Zverev"],
            "Holger Rune": ["Rune", "H. Rune"],
            "Hubert Hurkacz": ["Hurkacz", "H. Hurkacz"],
            "Taylor Fritz": ["Fritz", "T. Fritz"],
            "Casper Ruud": ["Ruud", "C. Ruud"],
            "Alex de Minaur": ["de Minaur", "A. de Minaur", "Alex De Minaur"],
            "Tommy Paul": ["Paul", "T. Paul"],
            "Ben Shelton": ["Shelton", "B. Shelton"],
            "Frances Tiafoe": ["Tiafoe", "F. Tiafoe"],
            "Sebastian Korda": ["Korda", "S. Korda", "Seb Korda"],
            "Karen Khachanov": ["Khachanov", "K. Khachanov"],
            "Cameron Norrie": ["Norrie", "C. Norrie"],
            "Lorenzo Musetti": ["Musetti", "L. Musetti"],
            "Ugo Humbert": ["Humbert", "U. Humbert"],
            "Grigor Dimitrov": ["Dimitrov", "G. Dimitrov"],
            "Adrian Mannarino": ["Mannarino", "A. Mannarino"],
            "Nicolas Jarry": ["Jarry", "N. Jarry"],
            "Sebastian Baez": ["Baez", "S. Baez"],
            "Alejandro Tabilo": ["Tabilo", "A. Tabilo"],
            "Tomas Machac": ["Machac", "T. Machac"],
            "Mariano Navone": ["Navone", "M. Navone"],
            "Luciano Darderi": ["Darderi", "L. Darderi"],
            "Flavio Cobolli": ["Cobolli", "F. Cobolli"],
            "Jakub Mensik": ["Mensik", "J. Mensik"],
            "Arthur Fils": ["Fils", "A. Fils"],
            "Luca Van Assche": ["Van Assche", "L. Van Assche"],
            "Alexei Popyrin": ["Popyrin", "A. Popyrin"],
            "Jordan Thompson": ["Thompson", "J. Thompson"],
            "Christopher Eubanks": ["Eubanks", "C. Eubanks", "Chris Eubanks"],
            "Max Purcell": ["Purcell", "M. Purcell"],
            "Mackenzie McDonald": ["McDonald", "M. McDonald", "Mackie McDonald"],
            "Marcos Giron": ["Giron", "M. Giron"],
            "Brandon Nakashima": ["Nakashima", "B. Nakashima"],
            "JJ Wolf": ["Wolf", "J. Wolf", "J.J. Wolf"],
            "Emil Ruusuvuori": ["Ruusuvuori", "E. Ruusuvuori"],
            "Mikael Ymer": ["Ymer", "M. Ymer"],
            "Tallon Griekspoor": ["Griekspoor", "T. Griekspoor"],
            "Botic van de Zandschulp": ["van de Zandschulp", "B. van de Zandschulp"],
            "Daniel Evans": ["Evans", "D. Evans", "Dan Evans"],
            "Andy Murray": ["Murray", "A. Murray"],
            "Stan Wawrinka": ["Wawrinka", "S. Wawrinka"],
            "Richard Gasquet": ["Gasquet", "R. Gasquet"],
            "Roberto Bautista Agut": ["Bautista Agut", "R. Bautista Agut"],
            "Marin Cilic": ["Cilic", "M. Cilic"],
            "Kei Nishikori": ["Nishikori", "K. Nishikori"]
        }

    def download_kaggle_dataset(self):
        """Download the Kaggle ATP tennis dataset."""
        try:
            # Check if kaggle is installed
            import subprocess
            result = subprocess.run(['kaggle', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("Kaggle CLI not found. Please install with: pip install kaggle")
                return False
            
            # Download the dataset
            dataset_path = "dissfya/atp-tennis-2000-2023daily-pull"
            logger.info(f"Downloading Kaggle dataset: {dataset_path}")
            
            result = subprocess.run([
                'kaggle', 'datasets', 'download', '-d', dataset_path,
                '--path', str(self.data_dir), '--unzip'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Dataset downloaded successfully!")
                return True
            else:
                logger.error(f"Failed to download dataset: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading dataset: {e}")
            return False

    def load_and_filter_top50_data(self):
        """Load the dataset and filter for top 50 players and years 2024/2025 only."""
        try:
            # Find CSV files in the data directory
            csv_files = list(self.data_dir.glob("*.csv"))
            if not csv_files:
                logger.error("No CSV files found in data directory")
                return None
            
            logger.info(f"Found {len(csv_files)} CSV files")
            
            # Load the main dataset (assuming it's the largest file)
            main_file = max(csv_files, key=lambda x: x.stat().st_size)
            logger.info(f"Loading main dataset: {main_file.name}")
            
            df = pd.read_csv(main_file)
            logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
            
            # Filter for 2024 and 2025 only
            year_col = None
            for col in df.columns:
                if 'year' in col.lower() or 'date' in col.lower():
                    year_col = col
                    break
            if year_col:
                df[year_col] = df[year_col].astype(str)
                df = df[df[year_col].str.contains('2024') | df[year_col].str.contains('2025')]
                logger.info(f"Filtered for 2024/2025: {len(df)} rows remain")
            else:
                logger.warning("No year/date column found, skipping year filter!")
            
            # Filter for top 50 players
            top50_data = self.filter_for_top50_players(df)
            
            return top50_data
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return None

    def filter_for_top50_players(self, df):
        """Filter the dataset for top 50 players using 'LastName F.' format."""
        try:
            # Use only the exact 'LastName F.' format for matching
            player_set = set(self.top_50_players)
            player_columns = [col for col in df.columns if any(name_word in col.lower() for name_word in ['player', 'winner', 'loser', 'name'])]
            logger.info(f"Found potential player columns: {player_columns}")
            filtered_rows = []
            for _, row in df.iterrows():
                for col in player_columns:
                    val = str(row[col]) if col in row else ''
                    if val in player_set:
                        filtered_rows.append(row)
                        break
            filtered_df = pd.DataFrame(filtered_rows)
            logger.info(f"Filtered dataset: {len(filtered_df)} rows for top 50 players (exact match)")
            return filtered_df
        except Exception as e:
            logger.error(f"Error filtering for top 50 players: {e}")
            return df  # Return original if filtering fails

    def extract_player_stats(self, df):
        """Extract comprehensive stats for each top 50 player using 'LastName F.' format."""
        try:
            player_stats = {}
            for player in self.top_50_players:
                player_stats[player] = {
                    'name': player,
                    'matches_played': 0,
                    'wins': 0,
                    'losses': 0,
                    'win_percentage': 0.0,
                    'tournaments_played': set(),
                    'surfaces': set(),
                    'years_active': set(),
                    'recent_matches': [],
                    'head_to_head': {},
                    'performance_by_surface': {},
                    'performance_by_year': {},
                    'last_updated': datetime.now().isoformat()
                }
            for _, row in df.iterrows():
                tournament = self.extract_value(row, ['Tournament'])
                surface = self.extract_value(row, ['Surface'])
                year = str(row['Date'])[:4] if 'Date' in row else None
                winner = self.extract_value(row, ['Winner'])
                player1 = self.extract_value(row, ['Player_1'])
                player2 = self.extract_value(row, ['Player_2'])
                for player in self.top_50_players:
                    is_winner = (winner == player)
                    is_player1 = (player1 == player)
                    is_player2 = (player2 == player)
                    involved = is_player1 or is_player2
                    if involved:
                        stats = player_stats[player]
                        stats['matches_played'] += 1
                        if is_winner:
                            stats['wins'] += 1
                        else:
                            stats['losses'] += 1
                        if tournament:
                            stats['tournaments_played'].add(tournament)
                        if surface:
                            stats['surfaces'].add(surface)
                        if year:
                            stats['years_active'].add(str(year))
                        if surface:
                            if surface not in stats['performance_by_surface']:
                                stats['performance_by_surface'][surface] = {'wins': 0, 'losses': 0}
                            if is_winner:
                                stats['performance_by_surface'][surface]['wins'] += 1
                            else:
                                stats['performance_by_surface'][surface]['losses'] += 1
                        if year:
                            if str(year) not in stats['performance_by_year']:
                                stats['performance_by_year'][str(year)] = {'wins': 0, 'losses': 0}
                            if is_winner:
                                stats['performance_by_year'][str(year)]['wins'] += 1
                            else:
                                stats['performance_by_year'][str(year)]['losses'] += 1
                        # Head-to-head
                        opponent = player2 if is_player1 else player1
                        if opponent:
                            if opponent not in stats['head_to_head']:
                                stats['head_to_head'][opponent] = {'wins': 0, 'losses': 0}
                            if is_winner:
                                stats['head_to_head'][opponent]['wins'] += 1
                            else:
                                stats['head_to_head'][opponent]['losses'] += 1
                        # Recent matches
                        match_info = {
                            'tournament': tournament,
                            'surface': surface,
                            'year': year,
                            'result': 'W' if is_winner else 'L',
                            'opponent': opponent
                        }
                        stats['recent_matches'].append(match_info)
                        stats['recent_matches'] = stats['recent_matches'][-20:]
            for player, stats in player_stats.items():
                if stats['matches_played'] > 0:
                    stats['win_percentage'] = round(stats['wins'] / stats['matches_played'], 3)
                stats['tournaments_played'] = list(stats['tournaments_played'])
                stats['surfaces'] = list(stats['surfaces'])
                stats['years_active'] = list(stats['years_active'])
                stats['performance_by_surface'] = dict(stats['performance_by_surface'])
                stats['performance_by_year'] = dict(stats['performance_by_year'])
                stats['head_to_head'] = dict(stats['head_to_head'])
            return player_stats
        except Exception as e:
            logger.error(f"Error extracting player stats: {e}")
            return {}

    def extract_value(self, row, possible_columns):
        """Extract a value from a row using possible column names."""
        for col in possible_columns:
            if col in row.index:
                value = row[col]
                if pd.notna(value) and value != '':
                    return str(value)
        return None

    def save_player_stats(self, player_stats):
        """Save player statistics to JSON files (2024/2025 only)."""
        try:
            # Save individual player files
            for player, stats in player_stats.items():
                if stats['matches_played'] > 0:  # Only save players with data
                    filename = f"top50_player_{player.replace(' ', '_')}_2024_2025.json"
                    filepath = self.data_dir / filename
                    
                    with open(filepath, 'w') as f:
                        json.dump(stats, f, indent=2)
                    
                    logger.info(f"Saved stats for {player}: {stats['matches_played']} matches (2024/2025)")
            
            # Save combined stats file
            combined_file = self.data_dir / "top50_players_combined_2024_2025.json"
            with open(combined_file, 'w') as f:
                json.dump(player_stats, f, indent=2)
            
            logger.info(f"Saved combined stats for {len(player_stats)} players (2024/2025)")
            return True
            
        except Exception as e:
            logger.error(f"Error saving player stats: {e}")
            return False

    def generate_summary_report(self, player_stats):
        """Generate a summary report of top 50 players (2024/2025 only)."""
        try:
            summary = {
                'total_players_analyzed': len(player_stats),
                'players_with_data': len([p for p in player_stats.values() if p['matches_played'] > 0]),
                'total_matches': sum(p['matches_played'] for p in player_stats.values()),
                'date_generated': datetime.now().isoformat(),
                'top_players_by_matches': [],
                'top_players_by_win_percentage': [],
                'surfaces_covered': set(),
                'years_covered': set()
            }
            
            # Collect all surfaces and years
            for player, stats in player_stats.items():
                if stats['matches_played'] > 0:
                    summary['surfaces_covered'].update(stats['surfaces'])
                    summary['years_covered'].update(stats['years_active'])
            
            # Top players by matches played
            players_by_matches = [(p, s['matches_played']) for p, s in player_stats.items() if s['matches_played'] > 0]
            players_by_matches.sort(key=lambda x: x[1], reverse=True)
            summary['top_players_by_matches'] = players_by_matches[:10]
            
            # Top players by win percentage
            players_by_win_pct = [(p, s['win_percentage']) for p, s in player_stats.items() if s['matches_played'] > 10]
            players_by_win_pct.sort(key=lambda x: x[1], reverse=True)
            summary['top_players_by_win_percentage'] = players_by_win_pct[:10]
            
            # Convert sets to lists for JSON
            summary['surfaces_covered'] = list(summary['surfaces_covered'])
            summary['years_covered'] = list(summary['years_covered'])
            
            # Save summary
            summary_file = self.data_dir / "top50_summary_report_2024_2025.json"
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info("Generated summary report (2024/2025)")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary report: {e}")
            return None

    def run_full_fetch(self):
        """Run the complete top 50 players data fetch process."""
        logger.info("🎾 Starting Kaggle Top 50 Tennis Players Data Fetch")
        logger.info("=" * 60)
        
        # Step 1: Download dataset
        logger.info("📥 Step 1: Downloading Kaggle dataset...")
        if not self.download_kaggle_dataset():
            logger.error("Failed to download dataset. Exiting.")
            return False
        
        # Step 2: Load and filter data
        logger.info("🔍 Step 2: Loading and filtering for top 50 players...")
        df = self.load_and_filter_top50_data()
        if df is None:
            logger.error("Failed to load dataset. Exiting.")
            return False
        
        # Step 3: Extract player statistics
        logger.info("📊 Step 3: Extracting player statistics...")
        player_stats = self.extract_player_stats(df)
        if not player_stats:
            logger.error("Failed to extract player stats. Exiting.")
            return False
        
        # Step 4: Save statistics
        logger.info("💾 Step 4: Saving player statistics...")
        if not self.save_player_stats(player_stats):
            logger.error("Failed to save player stats. Exiting.")
            return False
        
        # Step 5: Generate summary report
        logger.info("📋 Step 5: Generating summary report...")
        summary = self.generate_summary_report(player_stats)
        
        # Final summary
        logger.info("✅ Top 50 Tennis Players Data Fetch Complete!")
        logger.info("=" * 60)
        
        if summary:
            logger.info(f"📊 Players with data: {summary['players_with_data']}")
            logger.info(f"🎾 Total matches analyzed: {summary['total_matches']}")
            logger.info(f"🏟️ Surfaces covered: {', '.join(summary['surfaces_covered'])}")
            if summary['years_covered']:
                logger.info(f"📅 Years covered: {min(summary['years_covered'])} - {max(summary['years_covered'])}")
            else:
                logger.info(f"📅 Years covered: No years found in filtered data")
        
        logger.info(f"📁 Data saved to: {self.data_dir}")
        return True

def main():
    """Main function to run the top 50 tennis players data fetcher."""
    fetcher = KaggleTop50TennisFetcher()
    success = fetcher.run_full_fetch()
    
    if success:
        print("\n🎾 Top 50 Tennis Players Data Fetch completed successfully!")
        print("📁 Check the data/tennis_kaggle/ directory for results.")
    else:
        print("\n❌ Top 50 Tennis Players Data Fetch failed.")
        print("🔍 Check the logs above for error details.")

if __name__ == "__main__":
    main() 