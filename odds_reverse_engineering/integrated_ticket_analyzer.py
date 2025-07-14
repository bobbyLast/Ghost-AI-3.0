"""
Integrated Ticket Analyzer with Odds Reverse Engineering
Combines ticket generation with odds pattern analysis and enhanced posting
"""

import sys
import os
import json
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the odds reverse engineering engine
from reverse_engine import OddsReverseEngine

# Import ticket generation (assuming it's in the parent directory)
try:
    from generate_tickets import TicketGenerator
except ImportError:
    print("Warning: generate_tickets.py not found. Using mock data for testing.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IntegratedTicketAnalyzer:
    """
    Integrated system that:
    1. Generates tickets using existing system
    2. Analyzes odds patterns with reverse engineering engine
    3. Enhances tickets with confidence drift analysis
    4. Posts enhanced results
    """
    
    def __init__(self):
        self.ticket_generator = TicketGenerator() if 'TicketGenerator' in globals() else None
        self.odds_engine = OddsReverseEngine(data_dir="odds_reverse_engineering_test/data")
        self.enhanced_tickets = []
        
    async def run_full_pipeline(self, sport_key: str = 'basketball_nba') -> List[Dict]:
        """
        Run the complete pipeline: generate tickets → analyze odds → enhance → post
        """
        logger.info(f"🚀 Starting integrated ticket analysis for {sport_key}")
        
        try:
            # Step 1: Generate tickets
            tickets = await self._generate_tickets(sport_key)
            if not tickets:
                logger.warning("No tickets generated - stopping pipeline")
                return []
            
            logger.info(f"✅ Generated {len(tickets)} tickets")
            
            # Step 2: Analyze odds patterns for each ticket
            enhanced_tickets = await self._analyze_tickets_with_odds_engine(tickets)
            
            # Step 3: Apply confidence drift analysis
            final_tickets = self._apply_confidence_drift_analysis(enhanced_tickets)
            
            # Step 4: Save enhanced tickets
            self._save_enhanced_tickets(final_tickets, sport_key)
            
            # Step 5: Post results
            await self._post_enhanced_results(final_tickets, sport_key)
            
            logger.info(f"🎉 Pipeline complete! Enhanced {len(final_tickets)} tickets")
            return final_tickets
            
        except Exception as e:
            logger.error(f"❌ Error in pipeline: {e}", exc_info=True)
            return []
    
    async def _generate_tickets(self, sport_key: str) -> List[Dict]:
        """Generate tickets using existing system"""
        if self.ticket_generator:
            logger.info("Using TicketGenerator to generate tickets...")
            return await self.ticket_generator.run(sport_key)
        else:
            logger.info("Using mock ticket data for testing...")
            return self._generate_mock_tickets(sport_key)
    
    def _generate_mock_tickets(self, sport_key: str) -> List[Dict]:
        """Generate mock tickets for testing when TicketGenerator is not available"""
        mock_tickets = [
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
            }
        ]
        return mock_tickets
    
    async def _analyze_tickets_with_odds_engine(self, tickets: List[Dict]) -> List[Dict]:
        """Analyze each ticket's selections with the odds reverse engineering engine"""
        enhanced_tickets = []
        
        for ticket in tickets:
            logger.info(f"Analyzing ticket {ticket.get('ticket_id', 'unknown')}")
            
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
                self._add_historical_data_for_player(player_name, prop_type)
                
                # Analyze confidence drift
                drift_analysis = self.odds_engine.analyze_confidence_drift(
                    player_name, prop_type, current_odds
                )
                
                # Compare to market today
                market_analysis = self.odds_engine.compare_to_market_today(
                    player_name, prop_type, current_odds
                )
                
                # Enhance selection with analysis
                enhanced_selection = {
                    **selection,
                    'odds_analysis': {
                        'confidence_drift': {
                            'trend': drift_analysis.confidence_trend,
                            'risk_rating': drift_analysis.risk_rating,
                            'recommendation': getattr(drift_analysis, 'recommendation', 'N/A'),
                            'odds_drift': drift_analysis.odds_drift
                        },
                        'market_analysis': market_analysis,
                        'trend_tag': self._get_trend_tag_for_player(player_name, prop_type),
                        'ghost_read': self._get_ghost_read_for_player(player_name, prop_type)
                    }
                }
                
                enhanced_selections.append(enhanced_selection)
                
                # Track analysis for ticket-level summary
                if "🔥" in drift_analysis.confidence_trend:
                    ticket_analysis['hot_picks'] += 1
                elif "⛔" in drift_analysis.risk_rating:
                    ticket_analysis['trap_risks'] += 1
                
                ticket_analysis['confidence_drift'].append(drift_analysis)
                ticket_analysis['market_analysis'].append(market_analysis)
            
            # Create enhanced ticket
            enhanced_ticket = {
                **ticket,
                'selections': enhanced_selections,
                'odds_analysis': ticket_analysis,
                'enhanced_confidence_score': self._calculate_enhanced_confidence(ticket_analysis),
                'risk_assessment': self._assess_ticket_risk(ticket_analysis),
                'recommendation': self._generate_ticket_recommendation(ticket_analysis)
            }
            
            enhanced_tickets.append(enhanced_ticket)
        
        return enhanced_tickets
    
    def _add_historical_data_for_player(self, player_name: str, prop_type: str):
        """Add historical odds data for a player (simulate past performance)"""
        # This would normally come from your historical database
        # For now, we'll add some realistic historical data
        
        # Generate some historical entries based on the player's current odds
        base_odds = -110  # Default base odds
        
        # Add 5-10 historical entries with realistic patterns
        for i in range(5, 15):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            
            # Vary odds and results to create realistic patterns
            if i % 3 == 0:  # Every 3rd day, odds get more negative (falling)
                odds = base_odds - (i * 5)
                result = "W" if i % 2 == 0 else "L"
            else:  # Other days, odds stay similar or rise slightly
                odds = base_odds + (i * 2)
                result = "W" if i % 3 == 0 else "L"
            
            self.odds_engine.add_odds_entry(player_name, prop_type, date, odds, result)
    
    def _get_trend_tag_for_player(self, player_name: str, prop_type: str) -> Optional[str]:
        """Get trend tag for a player/prop combination"""
        key = f"{player_name}_{prop_type}"
        if key in self.odds_engine.prop_memory:
            return self.odds_engine.prop_memory[key].trend_tag
        return None
    
    def _get_ghost_read_for_player(self, player_name: str, prop_type: str) -> Optional[str]:
        """Get ghost read for a player/prop combination"""
        key = f"{player_name}_{prop_type}"
        if key in self.odds_engine.prop_memory:
            return self.odds_engine.prop_memory[key].ghost_read
        return None
    
    def _apply_confidence_drift_analysis(self, enhanced_tickets: List[Dict]) -> List[Dict]:
        """Apply confidence drift analysis to enhance ticket recommendations"""
        for ticket in enhanced_tickets:
            # Analyze overall ticket confidence drift
            drift_analyses = ticket['odds_analysis']['confidence_drift']
            
            if not drift_analyses:
                continue
            
            # Calculate overall drift metrics
            rising_count = sum(1 for analysis in drift_analyses if "🔥" in analysis.confidence_trend)
            falling_count = sum(1 for analysis in drift_analyses if "🔻" in analysis.confidence_trend)
            avoid_count = sum(1 for analysis in drift_analyses if "⛔" in analysis.risk_rating)
            
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
    
    def _calculate_enhanced_confidence(self, ticket_analysis: Dict) -> float:
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
        rising_count = sum(1 for analysis in drift_analyses if "🔥" in analysis.confidence_trend)
        falling_count = sum(1 for analysis in drift_analyses if "🔻" in analysis.confidence_trend)
        
        if rising_count > falling_count:
            base_confidence += 0.1
        elif falling_count > rising_count:
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def _assess_ticket_risk(self, ticket_analysis: Dict) -> str:
        """Assess overall ticket risk level"""
        trap_risks = ticket_analysis.get('trap_risks', 0)
        hot_picks = ticket_analysis.get('hot_picks', 0)
        
        if trap_risks > hot_picks:
            return "HIGH"
        elif trap_risks == 0 and hot_picks > 0:
            return "LOW"
        else:
            return "MEDIUM"
    
    def _generate_ticket_recommendation(self, ticket_analysis: Dict) -> str:
        """Generate ticket-level recommendation"""
        hot_picks = ticket_analysis.get('hot_picks', 0)
        trap_risks = ticket_analysis.get('trap_risks', 0)
        
        if hot_picks > trap_risks:
            return f"✅ PLAY - {hot_picks} hot picks detected"
        elif trap_risks > hot_picks:
            return f"⛔ AVOID - {trap_risks} trap risks detected"
        else:
            return "⚠️ CAUTION - Mixed signals, proceed carefully"
    
    def _save_enhanced_tickets(self, tickets: List[Dict], sport_key: str):
        """Save enhanced tickets to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"odds_reverse_engineering_test/data/enhanced_tickets_{sport_key}_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(tickets, f, indent=2)
        
        logger.info(f"💾 Saved {len(tickets)} enhanced tickets to {filename}")
    
    async def _post_enhanced_results(self, tickets: List[Dict], sport_key: str):
        """Post enhanced results (simulate Discord posting)"""
        logger.info(f"📢 Posting enhanced results for {sport_key}")
        
        for ticket in tickets:
            await self._post_enhanced_ticket(ticket)
    
    async def _post_enhanced_ticket(self, ticket: Dict):
        """Post a single enhanced ticket (simulate Discord embed)"""
        ticket_id = ticket.get('ticket_id', 'unknown')
        tier = ticket.get('tier', 'unknown')
        confidence_trend = ticket.get('overall_confidence_trend', 'Unknown')
        recommendation = ticket.get('recommendation', 'No recommendation')
        
        # Log the enhanced ticket details
        logger.info(f"🎟️ Enhanced Ticket {ticket_id}")
        logger.info(f"   Tier: {tier}")
        logger.info(f"   Confidence Trend: {confidence_trend}")
        logger.info(f"   Recommendation: {recommendation}")
        
        # Log selections with odds analysis
        for i, selection in enumerate(ticket.get('selections', []), 1):
            player_name = selection.get('player_name', 'Unknown')
            odds_analysis = selection.get('odds_analysis', {})
            drift_analysis = odds_analysis.get('confidence_drift', {})
            trend_tag = odds_analysis.get('trend_tag', 'No tag')
            
            logger.info(f"   Selection {i}: {player_name}")
            logger.info(f"     Trend: {trend_tag}")
            logger.info(f"     Confidence: {drift_analysis.get('trend', 'Unknown')}")
            logger.info(f"     Risk: {drift_analysis.get('risk_rating', 'Unknown')}")
        
        logger.info("   " + "="*50)

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integrated Ticket Analyzer with Odds Reverse Engineering')
    parser.add_argument('--sport', default='basketball_nba', 
                       help='Sport key (e.g., basketball_nba, baseball_mlb)')
    parser.add_argument('--output', help='Output file for enhanced tickets (JSON)')
    args = parser.parse_args()
    
    analyzer = IntegratedTicketAnalyzer()
    enhanced_tickets = await analyzer.run_full_pipeline(args.sport)
    
    if args.output and enhanced_tickets:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(enhanced_tickets, f, indent=2)
        logger.info(f"Saved {len(enhanced_tickets)} enhanced tickets to {output_path}")
    
    return enhanced_tickets

if __name__ == "__main__":
    # Run the integrated analyzer
    asyncio.run(main()) 