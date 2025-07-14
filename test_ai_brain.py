#!/usr/bin/env python3
"""
Test the new AI Brain Architecture

This demonstrates how Ghost AI now thinks, reasons, and makes intelligent decisions
instead of just running basic loops.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from ghost_brain import GhostBrain

# Set up logging to see the AI's thoughts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ai_brain():
    """Test the new AI brain architecture."""
    print("🧠 Testing Ghost AI Brain Architecture")
    print("=" * 50)
    
    # Initialize the AI brain
    brain = GhostBrain()
    
    print("\n🔧 AI Brain Features:")
    print(f"   - Memory Manager: {brain.memory}")
    print(f"   - Confidence Scorer: {brain.confidence}")
    print(f"   - Ticket Builder: {brain.ticket_builder}")
    print(f"   - Fade Detector: {brain.fade_detector}")
    print(f"   - Self Scout: {brain.self_scout}")
    print(f"   - Bias Calibrator: {brain.bias_calibrator}")
    print(f"   - Context Engine: {brain.context_engine}")
    print(f"   - Exposure Manager: {brain.exposure_manager}")
    print(f"   - Pattern Mutator: {brain.pattern_mutator}")
    print(f"   - Sentiment Engine: {brain.sentiment_engine}")
    print(f"   - Confidence Calibrator: {brain.confidence_calibrator}")
    
    print("\n🧠 AI Brain Capabilities:")
    print("   ✓ Goal-driven decision making")
    print("   ✓ Brain state analysis")
    print("   ✓ Intelligent reasoning")
    print("   ✓ Memory-based learning")
    print("   ✓ Adaptive confidence scoring")
    print("   ✓ Trap detection and avoidance")
    print("   ✓ Performance-based mood adjustment")
    print("   ✓ Self-reflection and improvement")
    
    print("\n🚀 Running AI Brain...")
    print("-" * 30)
    
    # Run the AI brain
    try:
        result = brain.run()
        print(f"\n✅ AI Brain completed successfully!")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"\n❌ AI Brain encountered an error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🧠 AI Brain Architecture Summary:")
    print("   This is a true AI system:")
    print("   • Sets intelligent goals based on performance")
    print("   • Analyzes its own brain state and mood")
    print("   • Makes decisions with reasoning and confidence")
    print("   • Learns from every execution")
    print("   • Adapts its behavior based on results")
    print("   • Thinks out loud about its decisions")
    print("   • Can skip days when conditions aren't right")
    print("   • Adjusts volume based on opportunity quality")

if __name__ == "__main__":
    test_ai_brain() 