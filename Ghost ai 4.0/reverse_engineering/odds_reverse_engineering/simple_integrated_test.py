"""
Simplified Integrated Test - Tests the odds reverse engineering engine with mock data
"""

import asyncio
import sys
import os
import json
from datetime import datetime, timezone, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reverse_engineering.reverse_engine.odds_engine import OddsReverseEngine
# If you need ConfidenceAnalysis and it's not in __init__, use:
# from reverse_engineering.reverse_engine.odds_engine import ConfidenceAnalysis

def create_mock_tickets():
    """Create mock tickets for testing"""
    return [
        {
            'ticket_id': 'mock_1',
            'tier': 'elite',
            'game_id': 'mock_game_1',
            'home_team': 'Lakers',
            'away_team': 'Warriors',
            'commence_time': datetime.now(timezone.utc).isoformat(),
            'selections': [
                {
                    'player_name': 'LeBron James',
                    'prop_type': 'batter_total_bases',
                    'line': 1.5,
                    'odds': -110,
                    'bookmaker': 'DraftKings',
                    'confidence': 0.85,
                    'value_rating': 0.8
                },
                {
                    'player_name': 'Stephen Curry',
                    'prop_type': 'batter_hits',
                    'line': 2.5,
                    'odds': -120,
                    'bookmaker': 'FanDuel',
                    'confidence': 0.82,
                    'value_rating': 0.75
                }
            ],
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'confidence_score': 0.835,
            'avg_odds': -115,
            'stake': 8.35,
            'potential_payout': 0.0
        },
        {
            'ticket_id': 'mock_2',
            'tier': 'standard',
            'game_id': 'mock_game_2',
            'home_team': 'Celtics',
            'away_team': 'Heat',
            'commence_time': datetime.now(timezone.utc).isoformat(),
            'selections': [
                {
                    'player_name': 'Jayson Tatum',
                    'prop_type': 'batter_runs',
                    'line': 2.5,
                    'odds': -105,
                    'bookmaker': 'BetMGM',
                    'confidence': 0.78,
                    'value_rating': 0.7
                },
                {
                    'player_name': 'Jimmy Butler',
                    'prop_type': 'batter_hits',
                    'line': 1.5,
                    'odds': -130,
                    'bookmaker': 'Caesars',
                    'confidence': 0.75,
                    'value_rating': 0.65
                }
            ],
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'confidence_score': 0.765,
            'avg_odds': -117.5,
            'stake': 7.65,
            'potential_payout': 0.0
        }
    ]

def add_historical_data_for_player(odds_engine, player_name, prop_type, base_odds=-110):
    """Add historical odds data for a player (simulate past performance)"""
    # Add 10 historical entries with realistic patterns
    for i in range(5, 15):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        
        # Vary odds and results to create realistic patterns
        if i % 3 == 0:  # Every 3rd day, odds get more negative (falling)
            odds = base_odds - (i * 5)
            result = "W" if i % 2 == 0 else "L"
        else:  # Other days, odds stay similar or rise slightly
            odds = base_odds + (i * 2)
            result = "W" if i % 3 == 0 else "L"
        
        odds_engine.add_odds_entry(player_name, prop_type, date, odds, result)

def analyze_tickets_with_odds_engine(tickets, odds_engine):
    """Analyze each ticket's selections with the odds reverse engineering engine"""
    enhanced_tickets = []
    
    for ticket in tickets:
        print(f"Analyzing ticket {ticket.get('ticket_id', 'unknown')}")
        
        enhanced_selections = []
        ticket_analysis = {
            'hot_picks': 0,
            'trap_risks': 0,
            'confidence_drift': [],
            'market_analysis': []
        }
        
        for selection in ticket.get('selections', []):
            player_name = selection.get('player_name')
            prop_type = selection.get('prop_type')
            current_odds = selection.get('odds')
            
            if not all([player_name, prop_type, current_odds]):
                enhanced_selections.append(selection)
                continue
            
            # Add historical odds data to the engine (simulate past performance)
            add_historical_data_for_player(odds_engine, player_name, prop_type, current_odds)
            
            # Analyze confidence drift
            drift_analysis = odds_engine.analyze_confidence_drift(
                player_name, prop_type, current_odds
            )
            
            # Compare to market today
            market_analysis = odds_engine.compare_to_market_today(
                player_name, prop_type, current_odds
            )
            
            # Get trend tag and ghost read
            key = f"{player_name}_{prop_type}"
            trend_tag = None
            ghost_read = None
            if key in odds_engine.prop_memory:
                trend_tag = odds_engine.prop_memory[key].trend_tag
                ghost_read = odds_engine.prop_memory[key].ghost_read
            
            # Enhance selection with analysis
            enhanced_selection = {
                **selection,
                'odds_analysis': {
                    'confidence_drift': {
                        'trend': drift_analysis.confidence_trend,
                        'risk_rating': drift_analysis.risk_rating,
                        'recommendation': drift_analysis.recommendation,
                        'odds_drift': drift_analysis.odds_drift
                    },
                    'market_analysis': market_analysis,
                    'trend_tag': trend_tag,
                    'ghost_read': ghost_read
                }
            }
            
            enhanced_selections.append(enhanced_selection)
            
            # Track analysis for ticket-level summary (convert to dict for JSON serialization)
            if "🔥" in drift_analysis.confidence_trend:
                ticket_analysis['hot_picks'] += 1
            elif "⛔" in drift_analysis.risk_rating:
                ticket_analysis['trap_risks'] += 1
            
            # Convert ConfidenceAnalysis to dict for JSON serialization
            drift_dict = {
                'confidence_trend': drift_analysis.confidence_trend,
                'risk_rating': drift_analysis.risk_rating,
                'recommendation': drift_analysis.recommendation,
                'odds_drift': drift_analysis.odds_drift,
                'result_drift': drift_analysis.result_drift
            }
            ticket_analysis['confidence_drift'].append(drift_dict)
            ticket_analysis['market_analysis'].append(market_analysis)
        
        # Create enhanced ticket
        enhanced_ticket = {
            **ticket,
            'selections': enhanced_selections,
            'odds_analysis': ticket_analysis,
            'enhanced_confidence_score': calculate_enhanced_confidence(ticket_analysis),
            'risk_assessment': assess_ticket_risk(ticket_analysis),
            'recommendation': generate_ticket_recommendation(ticket_analysis)
        }
        
        enhanced_tickets.append(enhanced_ticket)
    
    return enhanced_tickets

def calculate_enhanced_confidence(ticket_analysis):
    """Calculate enhanced confidence score based on odds analysis"""
    base_confidence = 0.5
    
    # Boost for hot picks
    hot_picks = ticket_analysis.get('hot_picks', 0)
    base_confidence += hot_picks * 0.1
    
    # Penalty for trap risks
    trap_risks = ticket_analysis.get('trap_risks', 0)
    base_confidence -= trap_risks * 0.15
    
    # Analyze confidence drift patterns
    drift_analyses = ticket_analysis.get('confidence_drift', [])
    rising_count = sum(1 for analysis in drift_analyses if "🔥" in analysis.get('confidence_trend', ''))
    falling_count = sum(1 for analysis in drift_analyses if "🔻" in analysis.get('confidence_trend', ''))
    
    if rising_count > falling_count:
        base_confidence += 0.1
    elif falling_count > rising_count:
        base_confidence -= 0.1
    
    return max(0.0, min(1.0, base_confidence))

def assess_ticket_risk(ticket_analysis):
    """Assess overall ticket risk level"""
    trap_risks = ticket_analysis.get('trap_risks', 0)
    hot_picks = ticket_analysis.get('hot_picks', 0)
    
    if trap_risks > hot_picks:
        return "HIGH"
    elif trap_risks == 0 and hot_picks > 0:
        return "LOW"
    else:
        return "MEDIUM"

def generate_ticket_recommendation(ticket_analysis):
    """Generate ticket-level recommendation"""
    hot_picks = ticket_analysis.get('hot_picks', 0)
    trap_risks = ticket_analysis.get('trap_risks', 0)
    
    if hot_picks > trap_risks:
        return f"✅ PLAY - {hot_picks} hot picks detected"
    elif trap_risks > hot_picks:
        return f"⛔ AVOID - {trap_risks} trap risks detected"
    else:
        return "⚠️ CAUTION - Mixed signals, proceed carefully"

def apply_confidence_drift_analysis(enhanced_tickets):
    """Apply confidence drift analysis to enhance ticket recommendations"""
    for ticket in enhanced_tickets:
        # Analyze overall ticket confidence drift
        drift_analyses = ticket['odds_analysis']['confidence_drift']
        
        if not drift_analyses:
            continue
        
        # Calculate overall drift metrics
        rising_count = sum(1 for analysis in drift_analyses if "🔥" in analysis.get('confidence_trend', ''))
        falling_count = sum(1 for analysis in drift_analyses if "🔻" in analysis.get('confidence_trend', ''))
        avoid_count = sum(1 for analysis in drift_analyses if "⛔" in analysis.get('risk_rating', ''))
        
        # Determine overall ticket confidence trend
        if rising_count > falling_count and avoid_count == 0:
            ticket['overall_confidence_trend'] = "🔥 Rising Confidence"
            ticket['recommendation'] = "Strong play - multiple rising confidence signals"
        elif falling_count > rising_count or avoid_count > 0:
            ticket['overall_confidence_trend'] = "🔻 Declining Confidence"
            ticket['recommendation'] = f"Caution - {avoid_count} avoid signals detected"
        else:
            ticket['overall_confidence_trend'] = "➡️ Stable Confidence"
            ticket['recommendation'] = "Neutral - mixed signals, monitor closely"
    
    return enhanced_tickets

async def test_integrated_system():
    """Test the integrated ticket analyzer system"""
    print("🚀 Testing Odds Reverse Engineering Engine with Mock Tickets")
    print("=" * 70)
    
    # Initialize the odds engine
    odds_engine = OddsReverseEngine(data_dir="data")
    
    # Create mock tickets
    mock_tickets = create_mock_tickets()
    print(f"✅ Created {len(mock_tickets)} mock tickets")
    
    # Analyze tickets with odds engine
    print("\n🔍 Analyzing tickets with odds reverse engineering engine...")
    enhanced_tickets = analyze_tickets_with_odds_engine(mock_tickets, odds_engine)
    
    # Apply confidence drift analysis
    final_tickets = apply_confidence_drift_analysis(enhanced_tickets)
    
    # Display results
    print(f"\n🎉 Analysis complete! Enhanced {len(final_tickets)} tickets")
    
    for i, ticket in enumerate(final_tickets, 1):
        print(f"\n🎟️ Ticket {i}: {ticket.get('ticket_id', 'unknown')}")
        print(f"   Tier: {ticket.get('tier', 'unknown')}")
        print(f"   Confidence Trend: {ticket.get('overall_confidence_trend', 'Unknown')}")
        print(f"   Risk Assessment: {ticket.get('risk_assessment', 'Unknown')}")
        print(f"   Recommendation: {ticket.get('recommendation', 'No recommendation')}")
        print(f"   Enhanced Confidence: {ticket.get('enhanced_confidence_score', 0):.3f}")
        
        # Show selections with odds analysis
        selections = ticket.get('selections', [])
        print(f"   Selections ({len(selections)}):")
        
        for j, selection in enumerate(selections, 1):
            player_name = selection.get('player_name', 'Unknown')
            odds_analysis = selection.get('odds_analysis', {})
            drift_analysis = odds_analysis.get('confidence_drift', {})
            trend_tag = odds_analysis.get('trend_tag', 'No tag')
            ghost_read = odds_analysis.get('ghost_read', 'No read')
            
            print(f"     {j}. {player_name}")
            print(f"        Trend: {trend_tag}")
            print(f"        Ghost Read: {ghost_read}")
            print(f"        Confidence: {drift_analysis.get('trend', 'Unknown')}")
            print(f"        Risk: {drift_analysis.get('risk_rating', 'Unknown')}")
            print(f"        Recommendation: {drift_analysis.get('recommendation', 'No recommendation')}")
    
    # Show hot picks and trap risks from the odds engine
    print("\n" + "=" * 70)
    print("🔥 Hot Picks Detected:")
    hot_picks = odds_engine.get_hot_picks()
    if hot_picks:
        for pick in hot_picks[:5]:  # Show top 5
            print(f"   {pick['player']} - {pick['prop']}: {pick['trend_tag']}")
    else:
        print("   No hot picks detected")
    
    print("\n🧊 Trap Risks Detected:")
    trap_risks = odds_engine.get_trap_risks()
    if trap_risks:
        for risk in trap_risks[:5]:  # Show top 5
            print(f"   {risk['player']} - {risk['prop']}: {risk['trend_tag']}")
    else:
        print("   No trap risks detected")
    
    # Save enhanced tickets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/enhanced_tickets_mock_{timestamp}.json"
    
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(final_tickets, f, indent=2)
    
    print(f"\n💾 Saved enhanced tickets to {filename}")
    print("\n🎉 Test completed successfully!")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_integrated_system()) 