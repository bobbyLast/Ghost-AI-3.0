#!/usr/bin/env python3
"""
Direct pipeline test to see where it's failing
"""

import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('direct_test')

async def test_direct_pipeline():
    """Test the pipeline directly step by step."""
    logger.info("=== TESTING DIRECT PIPELINE ===")
    
    try:
        # Import the pipeline
        from core.pipeline import GhostAIPipeline
        
        # Create pipeline
        pipeline = GhostAIPipeline()
        logger.info("✅ Pipeline created successfully")
        
        # Test prop processing
        logger.info("Testing prop processing...")
        mlb_props = await pipeline._process_mlb_props()
        logger.info(f"✅ MLB props processed: {len(mlb_props)}")
        
        wnba_props = await pipeline._process_wnba_props()
        logger.info(f"✅ WNBA props processed: {len(wnba_props)}")
        
        all_props = mlb_props + wnba_props
        logger.info(f"✅ Total props: {len(all_props)}")
        
        if len(all_props) == 0:
            logger.error("❌ No props found - stopping here")
            return
        
        # Test ticket generation
        logger.info("Testing ticket generation...")
        from core.ticket_generator import create_ticket_generator
        
        ticket_generator = create_ticket_generator(Path('.'))
        
        # Generate tickets for MLB
        mlb_tickets = ticket_generator.generate_tickets(mlb_props, 'MLB')
        logger.info(f"✅ MLB tickets generated: {len(mlb_tickets)}")
        
        # Generate tickets for WNBA
        wnba_tickets = ticket_generator.generate_tickets(wnba_props, 'WNBA')
        logger.info(f"✅ WNBA tickets generated: {len(wnba_tickets)}")
        
        all_tickets = mlb_tickets + wnba_tickets
        logger.info(f"✅ Total tickets: {len(all_tickets)}")
        
        if len(all_tickets) == 0:
            logger.error("❌ No tickets generated - stopping here")
            return
        
        # Show some ticket details
        for i, ticket in enumerate(all_tickets[:3]):
            selections = ticket.get('selections', [])
            logger.info(f"Ticket {i+1}: {len(selections)} legs, confidence: {ticket.get('confidence', 0):.2f}")
            for j, selection in enumerate(selections):
                logger.info(f"  Leg {j+1}: {selection.get('player_name')} {selection.get('prop_type')}")
        
        # Test Discord posting
        logger.info("Testing Discord posting...")
        await pipeline._post_tickets_to_discord(all_tickets)
        logger.info("✅ Discord posting completed")
        
    except Exception as e:
        logger.error(f"❌ Error in pipeline test: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the direct pipeline test."""
    asyncio.run(test_direct_pipeline())

if __name__ == "__main__":
    main() 