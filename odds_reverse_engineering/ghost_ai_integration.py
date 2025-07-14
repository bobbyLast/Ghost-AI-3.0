"""
Ghost AI Integration with Reverse Engine Data
Shows how Ghost AI can use pre-calculated reverse engine analysis
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from ai_data_loader import AIDataLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GhostAIIntegration:
    """
    Integration layer for Ghost AI to use reverse engine data
    Eliminates need to recalculate historical patterns
    """
    
    def __init__(self):
        self.data_loader = AIDataLoader()
        
    def enhance_ticket_with_reverse_analysis(self, ticket: Dict) -> Dict:
        """
        Enhance a Ghost AI ticket with reverse engine analysis
        
        Args:
            ticket: Original Ghost AI ticket
            
        Returns:
            Enhanced ticket with reverse engine analysis
        """
        enhanced_selections = []
        
        for selection in ticket.get('selections', []):
            player_name = selection.get('player_name')
            prop_type = selection.get('prop_type')
            base_confidence = selection.get('confidence_score', 0.5)
            
            if not all([player_name, prop_type]):
                enhanced_selections.append(selection)
                continue
            
            # Get reverse engine analysis
            enhanced_confidence = self.data_loader.get_enhanced_confidence_score(
                player_name, prop_type, base_confidence
            )
            
            trend_tag = self.data_loader.get_player_trend_tag(player_name, prop_type)
            ghost_read = self.data_loader.get_player_ghost_read(player_name, prop_type)
            confidence_trend = self.data_loader.get_player_confidence_trend(player_name, prop_type)
            risk_rating = self.data_loader.get_player_risk_rating(player_name, prop_type)
            
            # Create enhanced selection
            enhanced_selection = {
                **selection,
                'enhanced_confidence_score': enhanced_confidence,
                'reverse_engine_analysis': {
                    'trend_tag': trend_tag,
                    'ghost_read': ghost_read,
                    'confidence_trend': confidence_trend,
                    'risk_rating': risk_rating,
                    'is_hot_pick': self.data_loader.is_hot_pick(player_name, prop_type),
                    'is_trap_risk': self.data_loader.is_trap_risk(player_name, prop_type)
                }
            }
            
            enhanced_selections.append(enhanced_selection)
        
        # Calculate enhanced ticket confidence
        enhanced_confidence = sum(
            sel.get('enhanced_confidence_score', 0.5) 
            for sel in enhanced_selections
        ) / len(enhanced_selections) if enhanced_selections else 0.5
        
        # Create enhanced ticket
        enhanced_ticket = {
            **ticket,
            'selections': enhanced_selections,
            'enhanced_confidence_score': enhanced_confidence,
            'reverse_engine_enhanced': True,
            'analysis_timestamp': self.data_loader.get_analysis_timestamp()
        }
        
        return enhanced_ticket
    
    def get_hot_picks_for_today(self) -> List[Dict]:
        """Get today's hot picks from reverse engine analysis"""
        return self.data_loader.get_hot_picks()
    
    def get_trap_risks_for_today(self) -> List[Dict]:
        """Get today's trap risks from reverse engine analysis"""
        return self.data_loader.get_trap_risks()
    
    def should_include_player_in_ticket(self, player_name: str, prop_type: str, base_confidence: float) -> bool:
        """
        Determine if a player should be included in a ticket based on reverse engine analysis
        
        Args:
            player_name: Name of the player
            prop_type: Type of prop
            base_confidence: Base confidence score
            
        Returns:
            True if player should be included, False otherwise
        """
        # Check if it's a hot pick
        if self.data_loader.is_hot_pick(player_name, prop_type):
            logger.info(f"✅ Including {player_name} {prop_type} - Hot pick detected")
            return True
        
        # Check if it's a trap risk
        if self.data_loader.is_trap_risk(player_name, prop_type):
            logger.info(f"⛔ Excluding {player_name} {prop_type} - Trap risk detected")
            return False
        
        # Check confidence trend
        trend = self.data_loader.get_player_confidence_trend(player_name, prop_type)
        if trend and "🔻" in trend:
            logger.info(f"⚠️ Excluding {player_name} {prop_type} - Falling confidence trend")
            return False
        
        # Check risk rating
        risk_rating = self.data_loader.get_player_risk_rating(player_name, prop_type)
        if risk_rating and "⛔" in risk_rating:
            logger.info(f"⛔ Excluding {player_name} {prop_type} - High risk rating")
            return False
        
        # Default: include if base confidence is good
        return base_confidence >= 0.6
    
    def get_analysis_status(self) -> Dict:
        """Get current analysis status"""
        return self.data_loader.get_analysis_status()
    
    def is_analysis_available(self) -> bool:
        """Check if reverse engine analysis is available and fresh"""
        return self.data_loader.is_analysis_fresh()

def demo_integration():
    """Demonstrate how Ghost AI can integrate with reverse engine data"""
    integration = GhostAIIntegration()
    
    # Check if analysis is available
    if not integration.is_analysis_available():
        logger.warning("❌ Reverse engine analysis not available or stale")
        logger.info("💡 Run the auto odds analyzer to generate fresh analysis")
        return
    
    logger.info("✅ Reverse engine analysis available and fresh")
    
    # Get analysis status
    status = integration.get_analysis_status()
    logger.info(f"📊 Analysis Status: {status}")
    
    # Get hot picks and trap risks
    hot_picks = integration.get_hot_picks_for_today()
    trap_risks = integration.get_trap_risks_for_today()
    
    logger.info(f"🔥 Hot Picks ({len(hot_picks)}):")
    for pick in hot_picks:
        logger.info(f"   {pick['player']} - {pick['prop']} ({pick['trend_tag']})")
    
    logger.info(f"⛔ Trap Risks ({len(trap_risks)}):")
    for risk in trap_risks:
        logger.info(f"   {risk['player']} - {risk['prop']} ({risk['trend_tag']})")
    
    # Example: Enhance a mock ticket
    mock_ticket = {
        'ticket_id': 'TICKET_001',
        'tier': 'GOLD',
        'selections': [
            {
                'player_name': 'Mike Trout',
                'prop_type': 'hits',
                'odds': -110,
                'confidence_score': 0.75
            },
            {
                'player_name': 'Shohei Ohtani',
                'prop_type': 'strikeouts',
                'odds': -120,
                'confidence_score': 0.80
            }
        ]
    }
    
    logger.info("\n🎟️ Original Ticket:")
    logger.info(f"   Ticket ID: {mock_ticket['ticket_id']}")
    logger.info(f"   Tier: {mock_ticket['tier']}")
    for sel in mock_ticket['selections']:
        logger.info(f"   {sel['player_name']} {sel['prop_type']}: {sel['confidence_score']:.3f}")
    
    # Enhance ticket with reverse engine analysis
    enhanced_ticket = integration.enhance_ticket_with_reverse_analysis(mock_ticket)
    
    logger.info("\n🚀 Enhanced Ticket:")
    logger.info(f"   Enhanced Confidence: {enhanced_ticket['enhanced_confidence_score']:.3f}")
    for sel in enhanced_ticket['selections']:
        analysis = sel.get('reverse_engine_analysis', {})
        logger.info(f"   {sel['player_name']} {sel['prop_type']}:")
        logger.info(f"     Base Confidence: {sel.get('confidence_score', 0):.3f}")
        logger.info(f"     Enhanced Confidence: {sel.get('enhanced_confidence_score', 0):.3f}")
        logger.info(f"     Trend Tag: {analysis.get('trend_tag', 'None')}")
        logger.info(f"     Ghost Read: {analysis.get('ghost_read', 'None')}")
        logger.info(f"     Hot Pick: {analysis.get('is_hot_pick', False)}")
        logger.info(f"     Trap Risk: {analysis.get('is_trap_risk', False)}")
    
    # Example: Check if players should be included
    logger.info("\n✅ Player Inclusion Analysis:")
    for sel in mock_ticket['selections']:
        should_include = integration.should_include_player_in_ticket(
            sel['player_name'], 
            sel['prop_type'], 
            sel['confidence_score']
        )
        logger.info(f"   {sel['player_name']} {sel['prop_type']}: {'INCLUDE' if should_include else 'EXCLUDE'}")

if __name__ == "__main__":
    demo_integration() 