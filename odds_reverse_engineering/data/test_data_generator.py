"""
Test Data Generator for Odds Reverse Engineering Engine
Creates realistic odds movement patterns for testing
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import os

class TestDataGenerator:
    """Generates realistic test data for odds reverse engineering"""
    
    def __init__(self):
        self.players = [
            "Juan Soto", "Aaron Judge", "Mookie Betts", "Ronald Acuña Jr.",
            "Shohei Ohtani", "Mike Trout", "Fernando Tatis Jr.", "Trea Turner",
            "Jose Altuve", "Yordan Alvarez", "Kyle Tucker", "Corey Seager",
            "Manny Machado", "Nolan Arenado", "Paul Goldschmidt", "Pete Alonso"
        ]
        
        self.prop_types = [
            "batter_total_bases", "batter_hits", "batter_runs", "batter_rbis",
            "batter_home_runs", "batter_stolen_bases", "pitcher_strikeouts",
            "pitcher_earned_runs", "pitcher_walks", "pitcher_hits_allowed"
        ]
        
        self.scenarios = {
            "book_scared": {
                "description": "Odds dropping while hitting - book is scared",
                "pattern": "falling_odds_rising_performance",
                "trend_tag": "🔥 Book Scared",
                "risk_level": "low"
            },
            "trap_risk": {
                "description": "Odds dropping but missing - book overestimated",
                "pattern": "falling_odds_falling_performance",
                "trend_tag": "🧊 Trap Risk",
                "risk_level": "high"
            },
            "hidden_value": {
                "description": "Odds rising but still hitting - books disrespecting",
                "pattern": "rising_odds_rising_performance",
                "trend_tag": "🐍 Demon Hidden Value",
                "risk_level": "low"
            },
            "book_validation": {
                "description": "Odds rising + missing - book was right",
                "pattern": "rising_odds_falling_performance",
                "trend_tag": "✅ Book Was Right",
                "risk_level": "high"
            },
            "volatile": {
                "description": "Mixed signals - volatile pattern",
                "pattern": "mixed_signals",
                "trend_tag": "🔄 Volatile",
                "risk_level": "medium"
            }
        }
    
    def generate_odds_sequence(self, scenario: str, days: int = 10) -> List[Dict]:
        """
        Generate a realistic odds sequence based on scenario
        """
        base_odds = random.randint(-200, +150)
        sequence = []
        
        if scenario == "book_scared":
            # Odds get more negative (falling) while performance improves
            odds_trend = [base_odds]
            for i in range(1, days):
                # Odds get more negative (falling)
                change = random.randint(-30, -10)
                odds_trend.append(odds_trend[-1] + change)
            
            # Performance improves over time
            win_prob = 0.4  # Start low
            for i in range(days):
                result = "W" if random.random() < win_prob else "L"
                sequence.append({
                    "date": (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d"),
                    "odds": odds_trend[i],
                    "result": result
                })
                win_prob += 0.1  # Improve performance
        
        elif scenario == "trap_risk":
            # Odds get more negative but performance declines
            odds_trend = [base_odds]
            for i in range(1, days):
                change = random.randint(-25, -5)
                odds_trend.append(odds_trend[-1] + change)
            
            # Performance declines over time
            win_prob = 0.7  # Start high
            for i in range(days):
                result = "W" if random.random() < win_prob else "L"
                sequence.append({
                    "date": (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d"),
                    "odds": odds_trend[i],
                    "result": result
                })
                win_prob -= 0.08  # Decline performance
        
        elif scenario == "hidden_value":
            # Odds get more positive (rising) but performance stays good
            odds_trend = [base_odds]
            for i in range(1, days):
                change = random.randint(10, 30)
                odds_trend.append(odds_trend[-1] + change)
            
            # Performance stays consistently good
            win_prob = 0.65
            for i in range(days):
                result = "W" if random.random() < win_prob else "L"
                sequence.append({
                    "date": (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d"),
                    "odds": odds_trend[i],
                    "result": result
                })
        
        elif scenario == "book_validation":
            # Odds get more positive and performance declines
            odds_trend = [base_odds]
            for i in range(1, days):
                change = random.randint(15, 35)
                odds_trend.append(odds_trend[-1] + change)
            
            # Performance declines
            win_prob = 0.6
            for i in range(days):
                result = "W" if random.random() < win_prob else "L"
                sequence.append({
                    "date": (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d"),
                    "odds": odds_trend[i],
                    "result": result
                })
                win_prob -= 0.1
        
        else:  # volatile
            # Mixed pattern
            odds_trend = [base_odds]
            for i in range(1, days):
                change = random.randint(-20, 20)
                odds_trend.append(odds_trend[-1] + change)
            
            # Inconsistent performance
            for i in range(days):
                win_prob = random.uniform(0.3, 0.7)
                result = "W" if random.random() < win_prob else "L"
                sequence.append({
                    "date": (datetime.now() - timedelta(days=days-i-1)).strftime("%Y-%m-%d"),
                    "odds": odds_trend[i],
                    "result": result
                })
        
        return sequence
    
    def generate_player_dataset(self, player: str, prop_type: str, 
                               scenario: str, days: int = 10) -> Dict:
        """Generate complete dataset for a player/prop combination"""
        odds_sequence = self.generate_odds_sequence(scenario, days)
        
        return {
            "player_name": player,
            "prop_type": prop_type,
            "scenario": scenario,
            "scenario_info": self.scenarios[scenario],
            "odds_log": odds_sequence,
            "expected_trend_tag": self.scenarios[scenario]["trend_tag"],
            "expected_risk_level": self.scenarios[scenario]["risk_level"]
        }
    
    def generate_comprehensive_test_data(self, num_players: int = 20) -> Dict:
        """Generate comprehensive test dataset with multiple scenarios"""
        test_data = {
            "metadata": {
                "generated_date": datetime.now().isoformat(),
                "total_players": num_players,
                "scenarios": list(self.scenarios.keys())
            },
            "players": {}
        }
        
        # Select random players
        selected_players = random.sample(self.players, min(num_players, len(self.players)))
        
        for i, player in enumerate(selected_players):
            # Assign different scenarios to different players
            scenario = list(self.scenarios.keys())[i % len(self.scenarios)]
            prop_type = random.choice(self.prop_types)
            
            player_data = self.generate_player_dataset(player, prop_type, scenario)
            test_data["players"][f"{player}_{prop_type}"] = player_data
        
        return test_data
    
    def save_test_data(self, data: Dict, filename: str = "test_odds_data.json"):
        """Save test data to file"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Test data saved to {filename}")
    
    def generate_today_odds(self, player_data: Dict) -> int:
        """Generate today's odds based on historical pattern"""
        odds_sequence = player_data["odds_log"]
        if not odds_sequence:
            return random.randint(-150, +150)
        
        # Get last few odds to determine trend
        recent_odds = [entry["odds"] for entry in odds_sequence[-3:]]
        avg_recent = sum(recent_odds) / len(recent_odds)
        
        # Add some variation based on scenario
        scenario = player_data["scenario"]
        if scenario == "book_scared":
            # Continue falling trend
            variation = random.randint(-25, -5)
        elif scenario == "trap_risk":
            # Continue falling trend
            variation = random.randint(-20, -5)
        elif scenario == "hidden_value":
            # Continue rising trend
            variation = random.randint(5, 25)
        elif scenario == "book_validation":
            # Continue rising trend
            variation = random.randint(10, 30)
        else:
            # Volatile - random variation
            variation = random.randint(-15, 15)
        
        return int(avg_recent + variation)
    
    def create_validation_scenarios(self) -> List[Dict]:
        """Create specific validation scenarios for testing"""
        scenarios = []
        
        # Scenario 1: Hot streak with falling odds
        scenarios.append({
            "name": "Hot Streak Falling Odds",
            "description": "Player hitting well, odds getting more negative",
            "player": "Juan Soto",
            "prop_type": "batter_total_bases",
            "historical_data": [
                {"date": "2024-06-15", "odds": -110, "result": "W"},
                {"date": "2024-06-16", "odds": -125, "result": "W"},
                {"date": "2024-06-17", "odds": -140, "result": "W"},
                {"date": "2024-06-18", "odds": -155, "result": "W"},
                {"date": "2024-06-19", "odds": -170, "result": "L"}
            ],
            "today_odds": -160,
            "expected_analysis": "🔥 rising confidence, ✅ play"
        })
        
        # Scenario 2: Cold streak with rising odds
        scenarios.append({
            "name": "Cold Streak Rising Odds",
            "description": "Player struggling, odds getting more positive",
            "player": "Aaron Judge",
            "prop_type": "batter_home_runs",
            "historical_data": [
                {"date": "2024-06-15", "odds": -120, "result": "L"},
                {"date": "2024-06-16", "odds": -105, "result": "L"},
                {"date": "2024-06-17", "odds": -90, "result": "L"},
                {"date": "2024-06-18", "odds": -75, "result": "W"},
                {"date": "2024-06-19", "odds": -60, "result": "L"}
            ],
            "today_odds": -50,
            "expected_analysis": "🔻 falling confidence, ⛔ avoid"
        })
        
        # Scenario 3: Mixed signals
        scenarios.append({
            "name": "Mixed Signals Volatile",
            "description": "Inconsistent performance with volatile odds",
            "player": "Mookie Betts",
            "prop_type": "batter_hits",
            "historical_data": [
                {"date": "2024-06-15", "odds": -110, "result": "W"},
                {"date": "2024-06-16", "odds": -95, "result": "L"},
                {"date": "2024-06-17", "odds": -120, "result": "W"},
                {"date": "2024-06-18", "odds": -105, "result": "L"},
                {"date": "2024-06-19", "odds": -115, "result": "W"}
            ],
            "today_odds": -110,
            "expected_analysis": "➡️ stable confidence, ⚠️ caution"
        })
        
        return scenarios

if __name__ == "__main__":
    # Initialize generator
    generator = TestDataGenerator()
    
    # Generate comprehensive test data
    print("Generating comprehensive test data...")
    test_data = generator.generate_comprehensive_test_data(num_players=15)
    
    # Save to file
    generator.save_test_data(test_data, "odds_reverse_engineering_test/data/test_odds_data.json")
    
    # Generate validation scenarios
    print("Generating validation scenarios...")
    validation_scenarios = generator.create_validation_scenarios()
    
    with open("odds_reverse_engineering_test/data/validation_scenarios.json", 'w') as f:
        json.dump(validation_scenarios, f, indent=2)
    
    print("Test data generation complete!")
    print(f"Generated {len(test_data['players'])} player datasets")
    print(f"Generated {len(validation_scenarios)} validation scenarios") 