"""
Comprehensive Tests for Odds Reverse Engineering Engine
"""

import sys
import os
import json
import unittest
from datetime import datetime
from typing import Dict, List

# Add parent directory to path to import the engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reverse_engineering.reverse_engine.odds_engine import OddsReverseEngine
from data.test_data_generator import TestDataGenerator
from reverse_engineering.reverse_engine.odds_engine import ConfidenceAnalysis

class TestOddsReverseEngine(unittest.TestCase):
    """Test cases for the Odds Reverse Engineering Engine"""
    
    def setUp(self):
        """Set up test environment"""
        self.engine = OddsReverseEngine(data_dir="test_data")
        self.generator = TestDataGenerator()
        
        # Load test data
        self.test_data_file = "odds_reverse_engineering_test/data/test_odds_data.json"
        self.validation_file = "odds_reverse_engineering_test/data/validation_scenarios.json"
        
        # Generate test data if it doesn't exist
        if not os.path.exists(self.test_data_file):
            self.generator.generate_comprehensive_test_data(num_players=10)
            self.generator.save_test_data(
                self.generator.generate_comprehensive_test_data(num_players=10),
                self.test_data_file
            )
    
    def test_add_odds_entry(self):
        """Test adding odds entries"""
        # Test basic entry addition
        self.engine.add_odds_entry("Test Player", "batter_total_bases", "2024-06-20", -110, "W")
        
        key = "Test Player_batter_total_bases"
        self.assertIn(key, self.engine.prop_memory)
        self.assertEqual(len(self.engine.prop_memory[key].odds_log), 1)
        self.assertEqual(self.engine.prop_memory[key].odds_log[0].odds, -110)
        self.assertEqual(self.engine.prop_memory[key].odds_log[0].result, "W")
    
    def test_line_movement_calculation(self):
        """Test line movement calculation"""
        # Add multiple entries to test line movement
        self.engine.add_odds_entry("Test Player", "batter_hits", "2024-06-18", -110, "W")
        self.engine.add_odds_entry("Test Player", "batter_hits", "2024-06-19", -125, "W")  # Falling
        self.engine.add_odds_entry("Test Player", "batter_hits", "2024-06-20", -105, "L")  # Rising
        
        key = "Test Player_batter_hits"
        odds_log = self.engine.prop_memory[key].odds_log
        
        self.assertIsNone(odds_log[0].line_movement)  # First entry has no movement
        self.assertEqual(odds_log[1].line_movement, "falling")  # -110 to -125
        self.assertEqual(odds_log[2].line_movement, "rising")   # -125 to -105
    
    def test_trend_tag_generation(self):
        """Test trend tag generation for different scenarios"""
        # Scenario 1: Book Scared (falling odds, good performance)
        self.engine.add_odds_entry("Player1", "batter_total_bases", "2024-06-15", -110, "W")
        self.engine.add_odds_entry("Player1", "batter_total_bases", "2024-06-16", -125, "W")
        self.engine.add_odds_entry("Player1", "batter_total_bases", "2024-06-17", -140, "W")
        self.engine.add_odds_entry("Player1", "batter_total_bases", "2024-06-18", -155, "W")
        
        key1 = "Player1_batter_total_bases"
        self.assertEqual(self.engine.prop_memory[key1].trend_tag, "🔥 Book Scared")
        self.assertEqual(self.engine.prop_memory[key1].risk_level, "low")
        
        # Scenario 2: Trap Risk (falling odds, poor performance)
        self.engine.add_odds_entry("Player2", "batter_hits", "2024-06-15", -110, "L")
        self.engine.add_odds_entry("Player2", "batter_hits", "2024-06-16", -125, "L")
        self.engine.add_odds_entry("Player2", "batter_hits", "2024-06-17", -140, "L")
        self.engine.add_odds_entry("Player2", "batter_hits", "2024-06-18", -155, "L")
        
        key2 = "Player2_batter_hits"
        self.assertEqual(self.engine.prop_memory[key2].trend_tag, "🧊 Trap Risk")
        self.assertEqual(self.engine.prop_memory[key2].risk_level, "high")
    
    def test_confidence_drift_analysis(self):
        """Test confidence drift analysis"""
        # Set up a scenario with improving performance and falling odds
        self.engine.add_odds_entry("Test Player", "batter_runs", "2024-06-15", -110, "W")
        self.engine.add_odds_entry("Test Player", "batter_runs", "2024-06-16", -125, "W")
        self.engine.add_odds_entry("Test Player", "batter_runs", "2024-06-17", -140, "W")
        
        # Analyze confidence drift for today's odds
        analysis = self.engine.analyze_confidence_drift("Test Player", "batter_runs", -130)
        
        self.assertIsInstance(analysis, ConfidenceAnalysis)
        self.assertIn("rising", analysis.confidence_trend)
        self.assertIn("play", analysis.risk_rating)
    
    def test_market_comparison(self):
        """Test market comparison functionality"""
        # Set up historical data
        self.engine.add_odds_entry("Test Player", "batter_home_runs", "2024-06-15", -110, "W")
        self.engine.add_odds_entry("Test Player", "batter_home_runs", "2024-06-16", -125, "W")
        self.engine.add_odds_entry("Test Player", "batter_home_runs", "2024-06-17", -140, "W")
        
        # Test with much juicier odds today
        market_analysis = self.engine.compare_to_market_today("Test Player", "batter_home_runs", -180)
        
        self.assertEqual(market_analysis["status"], "highlight")
        self.assertIn("HOT PICK", market_analysis["message"])
    
    def test_hot_picks_detection(self):
        """Test hot picks detection"""
        # Create a hot pick scenario
        self.engine.add_odds_entry("Hot Player", "batter_total_bases", "2024-06-15", -110, "W")
        self.engine.add_odds_entry("Hot Player", "batter_total_bases", "2024-06-16", -125, "W")
        self.engine.add_odds_entry("Hot Player", "batter_total_bases", "2024-06-17", -140, "W")
        self.engine.add_odds_entry("Hot Player", "batter_total_bases", "2024-06-18", -155, "W")
        
        hot_picks = self.engine.get_hot_picks()
        
        self.assertGreater(len(hot_picks), 0)
        hot_player_found = any(pick["player"] == "Hot Player" for pick in hot_picks)
        self.assertTrue(hot_player_found)
    
    def test_trap_risks_detection(self):
        """Test trap risks detection"""
        # Create a trap risk scenario
        self.engine.add_odds_entry("Trap Player", "batter_hits", "2024-06-15", -110, "L")
        self.engine.add_odds_entry("Trap Player", "batter_hits", "2024-06-16", -125, "L")
        self.engine.add_odds_entry("Trap Player", "batter_hits", "2024-06-17", -140, "L")
        self.engine.add_odds_entry("Trap Player", "batter_hits", "2024-06-18", -155, "L")
        
        trap_risks = self.engine.get_trap_risks()
        
        self.assertGreater(len(trap_risks), 0)
        trap_player_found = any(risk["player"] == "Trap Player" for risk in trap_risks)
        self.assertTrue(trap_player_found)
    
    def test_player_summary(self):
        """Test player summary functionality"""
        # Add multiple props for a player
        self.engine.add_odds_entry("Multi Player", "batter_total_bases", "2024-06-15", -110, "W")
        self.engine.add_odds_entry("Multi Player", "batter_hits", "2024-06-15", -120, "L")
        
        summary = self.engine.get_player_summary("Multi Player")
        
        self.assertIn("batter_total_bases", summary)
        self.assertIn("batter_hits", summary)
        self.assertEqual(len(summary), 2)
    
    def test_memory_persistence(self):
        """Test memory save and load functionality"""
        # Add some data
        self.engine.add_odds_entry("Persist Player", "batter_runs", "2024-06-20", -110, "W")
        
        # Save memory
        self.engine.save_memory()
        
        # Create new engine instance to test loading
        new_engine = OddsReverseEngine(data_dir="test_data")
        
        # Check if data was loaded
        key = "Persist Player_batter_runs"
        self.assertIn(key, new_engine.prop_memory)
        self.assertEqual(len(new_engine.prop_memory[key].odds_log), 1)
    
    def test_insufficient_data_handling(self):
        """Test handling of insufficient data scenarios"""
        # Test confidence drift with no data
        analysis = self.engine.analyze_confidence_drift("No Data Player", "batter_hits", -110)
        
        self.assertEqual(analysis.confidence_trend, "❓ unknown")
        self.assertEqual(analysis.risk_rating, "⚠️ insufficient_data")
        
        # Test market comparison with no data
        market_analysis = self.engine.compare_to_market_today("No Data Player", "batter_hits", -110)
        
        self.assertEqual(market_analysis["status"], "no_history")
    
    def test_validation_scenarios(self):
        """Test with predefined validation scenarios"""
        if os.path.exists(self.validation_file):
            with open(self.validation_file, 'r') as f:
                scenarios = json.load(f)
            
            for scenario in scenarios:
                # Add historical data
                for entry in scenario["historical_data"]:
                    self.engine.add_odds_entry(
                        scenario["player"],
                        scenario["prop_type"],
                        entry["date"],
                        entry["odds"],
                        entry["result"]
                    )
                
                # Test confidence drift analysis
                analysis = self.engine.analyze_confidence_drift(
                    scenario["player"],
                    scenario["prop_type"],
                    scenario["today_odds"]
                )
                
                # Basic validation - analysis should be created
                self.assertIsInstance(analysis, ConfidenceAnalysis)
                self.assertIsNotNone(analysis.confidence_trend)
                self.assertIsNotNone(analysis.risk_rating)

class TestDataGeneratorTests(unittest.TestCase):
    """Test cases for the Test Data Generator"""
    
    def setUp(self):
        self.generator = TestDataGenerator()
    
    def test_odds_sequence_generation(self):
        """Test odds sequence generation for different scenarios"""
        scenarios = ["book_scared", "trap_risk", "hidden_value", "book_validation", "volatile"]
        
        for scenario in scenarios:
            sequence = self.generator.generate_odds_sequence(scenario, days=5)
            
            self.assertEqual(len(sequence), 5)
            self.assertIsInstance(sequence[0]["odds"], int)
            self.assertIn(sequence[0]["result"], ["W", "L"])
            self.assertIsInstance(sequence[0]["date"], str)
    
    def test_player_dataset_generation(self):
        """Test complete player dataset generation"""
        dataset = self.generator.generate_player_dataset("Test Player", "batter_hits", "book_scared")
        
        self.assertEqual(dataset["player_name"], "Test Player")
        self.assertEqual(dataset["prop_type"], "batter_hits")
        self.assertEqual(dataset["scenario"], "book_scared")
        self.assertIn("odds_log", dataset)
        self.assertIn("expected_trend_tag", dataset)
    
    def test_comprehensive_test_data(self):
        """Test comprehensive test data generation"""
        test_data = self.generator.generate_comprehensive_test_data(num_players=5)
        
        self.assertIn("metadata", test_data)
        self.assertIn("players", test_data)
        self.assertEqual(test_data["metadata"]["total_players"], 5)
        self.assertGreater(len(test_data["players"]), 0)
    
    def test_validation_scenarios_creation(self):
        """Test validation scenarios creation"""
        scenarios = self.generator.create_validation_scenarios()
        
        self.assertGreater(len(scenarios), 0)
        for scenario in scenarios:
            self.assertIn("name", scenario)
            self.assertIn("historical_data", scenario)
            self.assertIn("today_odds", scenario)
            self.assertIn("expected_analysis", scenario)

def run_performance_test():
    """Run performance test with large dataset"""
    print("Running performance test...")
    
    engine = OddsReverseEngine(data_dir="test_data")
    generator = TestDataGenerator()
    
    # Generate large dataset
    test_data = generator.generate_comprehensive_test_data(num_players=50)
    
    # Add all data to engine
    start_time = datetime.now()
    
    for key, player_data in test_data["players"].items():
        for entry in player_data["odds_log"]:
            engine.add_odds_entry(
                player_data["player_name"],
                player_data["prop_type"],
                entry["date"],
                entry["odds"],
                entry["result"]
            )
    
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    print(f"Processed {len(test_data['players'])} players in {processing_time:.2f} seconds")
    print(f"Average time per player: {processing_time/len(test_data['players']):.4f} seconds")
    
    # Test analysis performance
    start_time = datetime.now()
    
    hot_picks = engine.get_hot_picks()
    trap_risks = engine.get_trap_risks()
    
    end_time = datetime.now()
    analysis_time = (end_time - start_time).total_seconds()
    
    print(f"Analysis completed in {analysis_time:.4f} seconds")
    print(f"Found {len(hot_picks)} hot picks and {len(trap_risks)} trap risks")

if __name__ == "__main__":
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance test
    print("\n" + "="*50)
    run_performance_test()
    
    print("\nAll tests completed!") 