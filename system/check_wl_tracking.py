#!/usr/bin/env python3
"""
Check and fix W/L tracking system for Ghost AI
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_wl_tracking():
    """Check the current W/L tracking status"""
    print("🔍 Checking W/L Tracking System")
    print("=" * 50)
    
    # Check results files
    results_dir = Path("ghost_ai_core_memory/tickets/results")
    if results_dir.exists():
        results_files = list(results_dir.glob("*.json"))
        print(f"📁 Found {len(results_files)} results files:")
        for file in results_files:
            print(f"   - {file.name}")
            
            # Load and analyze results
            try:
                with open(file, 'r') as f:
                    results = json.load(f)
                
                # Check if this is a full ticket result or individual prop results
                if isinstance(results, dict) and 'results' in results:
                    # Full ticket result format
                    ticket_results = results['results']
                    total_picks = results.get('total_picks', 0)
                    wins = results.get('wins', 0)
                    losses = results.get('losses', 0)
                    
                    # For full tickets: WIN = all legs hit, LOSS = any leg misses
                    if total_picks > 0:
                        if wins == total_picks:
                            ticket_result = "WIN"
                        else:
                            ticket_result = "LOSS"
                        print(f"     Ticket Result: {ticket_result} ({wins}/{total_picks} legs hit)")
                else:
                    # Individual prop results - need to convert to ticket results
                    print(f"     Individual props - need to convert to ticket results")
                    
            except Exception as e:
                print(f"     Error reading {file.name}: {e}")
    else:
        print("❌ No results directory found")
    
    # Check active streaks
    streaks_file = Path("data/streaks/active_streaks.json")
    if streaks_file.exists():
        try:
            with open(streaks_file, 'r') as f:
                streaks = json.load(f)
            print(f"🔥 Active streaks: {len(streaks)}")
        except Exception as e:
            print(f"❌ Error reading streaks: {e}")
    else:
        print("❌ No active streaks file found")

    # Check performance tracking
    print("\n📊 Performance Tracking:")
    perf_files = [
        "data/performance/performance.json",
        "odds_reverse_engineering/data/performance/performance.json"
    ]
    
    for perf_file in perf_files:
        file_path = Path(perf_file)
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    perf_data = json.load(f)
                
                total_predictions = perf_data.get('total_predictions', 0)
                print(f"   {perf_file}: {total_predictions} predictions recorded")
                
                if total_predictions > 0:
                    # Convert individual prop results to ticket results
                    predictions = perf_data.get('predictions', [])
                    ticket_results = convert_prop_results_to_ticket_results(predictions)
                    
                    total_tickets = len(ticket_results)
                    winning_tickets = len([r for r in ticket_results if r['result'] == 'WIN'])
                    losing_tickets = len([r for r in ticket_results if r['result'] == 'LOSS'])
                    
                    win_rate = (winning_tickets / total_tickets * 100) if total_tickets > 0 else 0
                    print(f"     Ticket Results: {winning_tickets}W-{losing_tickets}L ({total_tickets} tickets)")
                    print(f"     Ticket Win Rate: {win_rate:.1f}%")
                    
            except Exception as e:
                print(f"   Error reading {perf_file}: {e}")
        else:
            print(f"   {perf_file}: File not found")

def convert_prop_results_to_ticket_results(predictions: List[Dict]) -> List[Dict]:
    """
    Convert individual prop results to full ticket results.
    A ticket wins only if ALL legs hit, loses if ANY leg misses.
    """
    # Group predictions by ticket ID
    ticket_groups = {}
    for pred in predictions:
        ticket_id = pred.get('id', 'unknown')
        if ticket_id not in ticket_groups:
            ticket_groups[ticket_id] = []
        ticket_groups[ticket_id].append(pred)
    
    ticket_results = []
    for ticket_id, props in ticket_groups.items():
        # Check if ALL props in this ticket hit
        all_hit = all(prop.get('status', '').lower() == 'w' for prop in props)
        
        # Determine ticket result
        if all_hit:
            result = 'WIN'
        else:
            result = 'LOSS'
        
        # Create ticket result
        ticket_result = {
            'ticket_id': ticket_id,
            'total_legs': len(props),
            'hitting_legs': len([p for p in props if p.get('status', '').lower() == 'w']),
            'result': result,
            'props': props,
            'created_at': props[0].get('created_at', '') if props else '',
            'updated_at': datetime.now().isoformat()
        }
        
        ticket_results.append(ticket_result)
    
    return ticket_results

def fix_wl_tracking():
    """Fix the W/L tracking by processing results into ticket-based performance files"""
    print("\n🔧 Fixing W/L Tracking System")
    print("=" * 50)
    
    # Process results into ticket-based performance tracking
    results_dir = Path("ghost_ai_core_memory/tickets/results")
    if not results_dir.exists():
        print("❌ No results directory found")
        return
    
    # Load all results
    all_results = []
    for results_file in results_dir.glob("*.json"):
        try:
            with open(results_file, 'r') as f:
                results = json.load(f)
                all_results.extend(results)
        except Exception as e:
            logger.error(f"Error reading {results_file}: {e}")
    
    if not all_results:
        print("❌ No results found to process")
        return
    
    # Convert to ticket-based results
    ticket_results = convert_prop_results_to_ticket_results(all_results)
    
    # Process results into performance format
    performance_data = {
        "tickets": ticket_results,
        "last_updated": datetime.now().isoformat(),
        "total_tickets": len(ticket_results),
        "winning_tickets": len([r for r in ticket_results if r.get('result') == 'WIN']),
        "losing_tickets": len([r for r in ticket_results if r.get('result') == 'LOSS']),
        "ticket_win_rate": 0
    }
    
    # Calculate ticket win rate
    if performance_data["total_tickets"] > 0:
        performance_data["ticket_win_rate"] = (
            performance_data["winning_tickets"] / performance_data["total_tickets"]
        ) * 100
    
    # Save to both performance files
    perf_files = [
        "data/performance/performance.json",
        "odds_reverse_engineering/data/performance/performance.json"
    ]
    
    for perf_file in perf_files:
        file_path = Path(perf_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(performance_data, f, indent=2)
            print(f"✅ Updated {perf_file}")
        except Exception as e:
            print(f"❌ Error updating {perf_file}: {e}")
    
    # Print summary
    print(f"\n📈 Ticket Performance Summary:")
    print(f"   Total Tickets: {performance_data['total_tickets']}")
    print(f"   Winning Tickets: {performance_data['winning_tickets']}")
    print(f"   Losing Tickets: {performance_data['losing_tickets']}")
    print(f"   Ticket Win Rate: {performance_data['ticket_win_rate']:.1f}%")

if __name__ == "__main__":
    check_wl_tracking()
    fix_wl_tracking() 