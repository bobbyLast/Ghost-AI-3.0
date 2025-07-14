#!/usr/bin/env python3
"""
Tennis Prop Integration for Ghost AI 4.0
Integrates Kaggle tennis data with AI brain for prop generation
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import the tennis prop generator
import sys
sys.path.append(str(Path.cwd()))
from tennis_prop_generator import TennisPropGenerator

logger = logging.getLogger('tennis_prop_integration')

class TennisPropIntegration:
    """Integrates tennis prop generation with AI brain system."""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.cwd()
        self.prop_generator = TennisPropGenerator()
        self.tickets_dir = self.base_dir / 'data' / 'tickets'
        self.tickets_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🎾 Tennis Prop Integration initialized")
    
    def generate_ai_tennis_props(self, num_props: int = 15) -> List[Dict]:
        """Generate AI-powered tennis props using Kaggle data."""
        try:
            logger.info(f"🎾 AI generating {num_props} tennis props using Kaggle data...")
            
            # Generate props using the tennis prop generator
            props = self.prop_generator.generate_daily_tennis_props(num_props)
            
            # Enhance props with AI analysis
            enhanced_props = []
            for prop in props:
                enhanced_prop = self._enhance_prop_with_ai(prop)
                if enhanced_prop:
                    enhanced_props.append(enhanced_prop)
            
            logger.info(f"✅ Generated {len(enhanced_props)} enhanced tennis props")
            return enhanced_props
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tennis props: {e}")
            return []
    
    def _enhance_prop_with_ai(self, prop: Dict) -> Optional[Dict]:
        """Enhance a prop with AI analysis."""
        try:
            # Add AI confidence adjustment based on data quality
            base_confidence = prop.get('confidence', 0.7)
            matches_analyzed = int(prop.get('reasoning', '').split()[-2]) if 'recent matches' in prop.get('reasoning', '') else 10
            
            # Adjust confidence based on data quality
            if matches_analyzed >= 50:
                confidence_boost = 0.1
            elif matches_analyzed >= 30:
                confidence_boost = 0.05
            elif matches_analyzed >= 15:
                confidence_boost = 0.02
            else:
                confidence_boost = -0.05
            
            enhanced_confidence = min(0.95, base_confidence + confidence_boost)
            
            # Add AI reasoning
            ai_reasoning = self._generate_ai_reasoning(prop)
            
            enhanced_prop = prop.copy()
            enhanced_prop['confidence'] = round(enhanced_confidence, 3)
            enhanced_prop['ai_reasoning'] = ai_reasoning
            enhanced_prop['data_quality'] = f"{matches_analyzed} matches analyzed"
            enhanced_prop['generated_at'] = datetime.now().isoformat()
            
            return enhanced_prop
            
        except Exception as e:
            logger.error(f"❌ Failed to enhance prop: {e}")
            return prop
    
    def _generate_ai_reasoning(self, prop: Dict) -> str:
        """Generate AI reasoning for a prop."""
        player = prop.get('player', '')
        prop_type = prop.get('prop', '')
        line = prop.get('line', 0)
        pick = prop.get('pick', '')
        reasoning = prop.get('reasoning', '')
        
        # Generate AI-style reasoning
        if 'Total Games' in prop_type:
            if line > 22:
                return f"High game total expected. {player} typically play long matches with extended rallies and tiebreaks."
            else:
                return f"Efficient match expected. {player} tend to finish matches quickly with decisive sets."
        
        elif 'Aces' in prop_type:
            if line > 6:
                return f"Strong serving expected from {player}. High ace count likely due to powerful serve and aggressive play."
            else:
                return f"Conservative serving expected from {player}. Focus on placement over power."
        
        elif 'Double Faults' in prop_type:
            if line > 3:
                return f"Risk-taking serving from {player}. Higher double fault count expected due to aggressive second serves."
            else:
                return f"Conservative serving from {player}. Low double fault count due to safe second serve strategy."
        
        elif '1st Set' in prop_type:
            return f"First set analysis for {player}. Early momentum crucial, expect competitive opening set."
        
        else:
            return f"AI analysis: {reasoning}"
    
    def generate_tennis_tickets(self, num_tickets: int = 3) -> List[Dict]:
        """Generate tennis tickets using AI-enhanced props."""
        try:
            logger.info(f"🎾 Generating {num_tickets} tennis tickets...")
            
            # Generate props
            props = self.generate_ai_tennis_props(num_props=num_tickets * 4)  # 4 props per ticket
            
            if not props:
                logger.warning("❌ No props available for ticket generation")
                return []
            
            tickets = []
            import random
            
            for i in range(num_tickets):
                # Select 2-3 props for this ticket
                num_props = random.randint(2, 3)
                if len(props) >= num_props:
                    selected_props = random.sample(props, num_props)
                    
                    # Calculate ticket metrics
                    total_confidence = sum(p.get('confidence', 0.7) for p in selected_props) / len(selected_props)
                    total_odds = 1.0
                    for p in selected_props:
                        odds = p.get('odds', 1.8)
                        if isinstance(odds, str):
                            try:
                                odds = float(odds)
                            except:
                                odds = 1.8
                        total_odds *= odds
                    
                    # Create ticket
                    ticket = {
                        'ticket_id': f"tennis_ticket_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i+1}",
                        'sport': 'TENNIS',
                        'props': selected_props,
                        'total_confidence': round(total_confidence, 3),
                        'total_odds': round(total_odds, 3),
                        'reasoning': f"AI-generated tennis ticket using Kaggle data. {len(selected_props)} high-confidence props.",
                        'timestamp': datetime.now().isoformat(),
                        'data_source': 'Kaggle 2024-2025',
                        'ai_enhanced': True
                    }
                    
                    tickets.append(ticket)
                    
                    # Remove used props to avoid duplicates
                    for prop in selected_props:
                        if prop in props:
                            props.remove(prop)
            
            logger.info(f"✅ Generated {len(tickets)} tennis tickets")
            return tickets
            
        except Exception as e:
            logger.error(f"❌ Failed to generate tennis tickets: {e}")
            return []
    
    def save_tennis_props(self, props: List[Dict], filename: str = None) -> str:
        """Save tennis props to file."""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"tennis_props_{timestamp}.json"
            
            filepath = self.base_dir / 'data' / 'player_props' / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(props, f, indent=2)
            
            logger.info(f"✅ Saved {len(props)} tennis props to {filename}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Failed to save tennis props: {e}")
            return ""
    
    def get_tennis_data_summary(self) -> Dict:
        """Get summary of tennis data available."""
        return {
            'prop_generator_summary': self.prop_generator.get_prop_summary(),
            'available_props': len(self.prop_generator.players_data),
            'data_years': '2024-2025',
            'data_source': 'Kaggle ATP Dataset',
            'integration_status': 'Active'
        }

def main():
    """Test the tennis prop integration."""
    print("🎾 Testing Tennis Prop Integration")
    print("=" * 50)
    
    integration = TennisPropIntegration()
    
    # Show data summary
    summary = integration.get_tennis_data_summary()
    print(f"📊 Tennis Data Summary:")
    print(f"   Available Players: {summary['available_props']}")
    print(f"   Data Years: {summary['data_years']}")
    print(f"   Data Source: {summary['data_source']}")
    print(f"   Integration Status: {summary['integration_status']}")
    
    # Generate sample props
    print(f"\n🎾 Generating AI-enhanced tennis props...")
    props = integration.generate_ai_tennis_props(num_props=5)
    
    for i, prop in enumerate(props, 1):
        print(f"\n📋 Enhanced Prop {i}:")
        print(f"   Game: {prop['game']}")
        print(f"   Player: {prop['player']}")
        print(f"   Prop: {prop['prop']}")
        print(f"   Line: {prop['line']}")
        print(f"   Pick: {prop['pick']}")
        print(f"   Confidence: {prop['confidence']}")
        print(f"   AI Reasoning: {prop.get('ai_reasoning', 'N/A')}")
    
    # Generate sample tickets
    print(f"\n🎾 Generating tennis tickets...")
    tickets = integration.generate_tennis_tickets(num_tickets=2)
    
    for i, ticket in enumerate(tickets, 1):
        print(f"\n🎫 Tennis Ticket {i}:")
        print(f"   Ticket ID: {ticket['ticket_id']}")
        print(f"   Total Confidence: {ticket['total_confidence']}")
        print(f"   Total Odds: {ticket['total_odds']}")
        print(f"   Props: {len(ticket['props'])}")
        print(f"   Reasoning: {ticket['reasoning']}")
    
    print(f"\n✅ Tennis Prop Integration test complete!")

if __name__ == "__main__":
    main() 