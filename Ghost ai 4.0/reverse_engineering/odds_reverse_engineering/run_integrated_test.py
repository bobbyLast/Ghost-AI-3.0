"""
Simple runner script to test the integrated ticket analyzer
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_ticket_analyzer import IntegratedTicketAnalyzer
from reverse_engineering.reverse_engine.odds_engine import OddsReverseEngine
# If you need ConfidenceAnalysis and it's not in __init__, use:
# from reverse_engineering.reverse_engine.odds_engine import ConfidenceAnalysis

async def test_integrated_system():
    """Test the integrated ticket analyzer system"""
    print("🚀 Testing Integrated Ticket Analyzer with Odds Reverse Engineering")
    print("=" * 70)
    
    # Initialize the analyzer
    analyzer = IntegratedTicketAnalyzer()
    
    # Test with different sports
    sports_to_test = ['basketball_nba', 'baseball_mlb']
    
    for sport in sports_to_test:
        print(f"\n🎯 Testing {sport.upper()}")
        print("-" * 50)
        
        try:
            # Run the full pipeline
            enhanced_tickets = await analyzer.run_full_pipeline(sport)
            
            if enhanced_tickets:
                print(f"✅ Successfully processed {len(enhanced_tickets)} tickets for {sport}")
                
                # Show summary of results
                for i, ticket in enumerate(enhanced_tickets, 1):
                    print(f"\n🎟️ Ticket {i}: {ticket.get('ticket_id', 'unknown')}")
                    print(f"   Tier: {ticket.get('tier', 'unknown')}")
                    print(f"   Confidence Trend: {ticket.get('overall_confidence_trend', 'Unknown')}")
                    print(f"   Risk Assessment: {ticket.get('risk_assessment', 'Unknown')}")
                    print(f"   Recommendation: {ticket.get('recommendation', 'No recommendation')}")
                    
                    # Show selections with odds analysis
                    selections = ticket.get('selections', [])
                    print(f"   Selections ({len(selections)}):")
                    
                    for j, selection in enumerate(selections, 1):
                        player_name = selection.get('player_name', 'Unknown')
                        odds_analysis = selection.get('odds_analysis', {})
                        drift_analysis = odds_analysis.get('confidence_drift', {})
                        trend_tag = odds_analysis.get('trend_tag', 'No tag')
                        
                        print(f"     {j}. {player_name}")
                        print(f"        Trend: {trend_tag}")
                        print(f"        Confidence: {drift_analysis.get('trend', 'Unknown')}")
                        print(f"        Risk: {drift_analysis.get('risk_rating', 'Unknown')}")
            else:
                print(f"❌ No tickets generated for {sport}")
                
        except Exception as e:
            print(f"❌ Error testing {sport}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Integrated system test completed!")
    
    # Show hot picks and trap risks from the odds engine
    print("\n🔥 Hot Picks Detected:")
    hot_picks = analyzer.odds_engine.get_hot_picks()
    for pick in hot_picks[:5]:  # Show top 5
        print(f"   {pick['player']} - {pick['prop']}: {pick['trend_tag']}")
    
    print("\n🧊 Trap Risks Detected:")
    trap_risks = analyzer.odds_engine.get_trap_risks()
    for risk in trap_risks[:5]:  # Show top 5
        print(f"   {risk['player']} - {risk['prop']}: {risk['trend_tag']}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_integrated_system()) 