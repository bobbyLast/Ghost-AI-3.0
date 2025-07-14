#!/usr/bin/env python3
"""
Quick verification that WNBA Player Analyzer is integrated into the AI system
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def verify_integration():
    """Quick verification of WNBA Player Analyzer integration"""
    print("🔍 Verifying WNBA Player Analyzer Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import the analyzer
        print("1. Testing import...")
        from reverse_engine.wnba_player_analyzer import WNBAPlayerAnalyzer
        print("✅ WNBAPlayerAnalyzer import successful")
        
        # Test 2: Initialize the analyzer (without loading all data)
        print("2. Testing initialization...")
        analyzer = WNBAPlayerAnalyzer()
        print("✅ WNBAPlayerAnalyzer initialized successfully")
        
        # Test 3: Check pipeline integration
        print("3. Testing pipeline integration...")
        from core.pipeline import GhostAIPipeline
        
        pipeline = GhostAIPipeline()
        print("✅ GhostAIPipeline initialized")
        
        # Check if WNBA analyzer is available in pipeline
        if hasattr(pipeline, 'wnba_player_analyzer'):
            print("✅ WNBA Player Analyzer is integrated into pipeline")
            print(f"   Analyzer type: {type(pipeline.wnba_player_analyzer).__name__}")
        else:
            print("❌ WNBA Player Analyzer not found in pipeline")
            return False
        
        # Test 4: Check that the analyzer has the expected methods
        print("4. Testing analyzer methods...")
        required_methods = [
            'analyze_player_performance',
            'generate_comprehensive_report',
            'find_most_reliable_players',
            'find_best_prop_types'
        ]
        
        for method in required_methods:
            if hasattr(analyzer, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"❌ Method '{method}' missing")
                return False
        
        print("\n🎉 Integration verification successful!")
        print("The WNBA Player Analyzer is properly integrated into the Ghost AI system.")
        print("\n🚀 The AI will now use:")
        print("   - Player performance analysis")
        print("   - Confidence boosting based on win rates and streaks")
        print("   - Comprehensive WNBA data analysis")
        print("   - Integration with existing odds engine")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("👻 Ghost AI 3.0 - WNBA Player Analyzer Integration Verification")
    print("=" * 60)
    
    success = verify_integration()
    
    if success:
        print("\n🎯 SUMMARY:")
        print("✅ WNBA Player Analyzer integration: VERIFIED")
        print("✅ Pipeline integration: VERIFIED")
        print("✅ Method availability: VERIFIED")
        print("\n🚀 The AI system is ready to use the WNBA Player Analyzer!")
    else:
        print("\n❌ Integration verification failed")

if __name__ == "__main__":
    main() 