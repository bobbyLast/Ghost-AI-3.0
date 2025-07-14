"""
Automated Integration System for Ghost AI Reverse Engine
Automatically hooks into ticket generation and results processing
"""

import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os
import json
from collections import defaultdict

from ghost_ai_integration import GhostAIIntegration
from auto_odds_analyzer import AutoOddsAnalyzer
from reverse_engine.odds_engine import OddsReverseEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PickRecord:
    """Record for tracking individual picks"""
    ticket_id: str
    player_name: str
    prop_type: str
    line: float
    odds: int
    confidence: float
    pick_side: str  # 'over' or 'under'
    game_id: str
    game_time: str
    opening_odds: Optional[int] = None
    closing_odds: Optional[int] = None
    result: Optional[str] = None  # 'W', 'L', 'P'
    actual_value: Optional[float] = None
    recorded_at: str = None
    result_updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.recorded_at is None:
            self.recorded_at = datetime.now(timezone.utc).isoformat()

class AutoIntegration:
    """
    Automated integration system that hooks into Ghost AI pipeline
    """
    
    def __init__(self):
        self.integration = GhostAIIntegration()
        self.analyzer = AutoOddsAnalyzer()
        self.odds_engine = OddsReverseEngine()
        
        # File paths
        self.picks_file = Path("odds_reverse_engineering/data/tracked_picks.json")
        self.results_file = Path("odds_reverse_engineering/data/results.json")
        self.performance_file = Path("odds_reverse_engineering/data/performance/performance.json")
        
        # Ensure directories exist
        self.picks_file.parent.mkdir(parents=True, exist_ok=True)
        self.results_file.parent.mkdir(parents=True, exist_ok=True)
        self.performance_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self.tracked_picks = self._load_tracked_picks()
        self.results = self._load_results()
        
    def _load_tracked_picks(self) -> Dict[str, Any]:
        """Load tracked picks from file"""
        if self.picks_file.exists():
            try:
                with open(self.picks_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracked picks: {e}")
        return {"picks": [], "last_updated": datetime.now(timezone.utc).isoformat()}
    
    def _load_results(self) -> Dict[str, Any]:
        """Load results from file"""
        if self.results_file.exists():
            try:
                with open(self.results_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading results: {e}")
        return {"results": [], "last_updated": datetime.now(timezone.utc).isoformat()}
    
    def _save_tracked_picks(self):
        """Save tracked picks to file"""
        try:
            self.tracked_picks["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(self.picks_file, 'w') as f:
                json.dump(self.tracked_picks, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracked picks: {e}")
    
    def _save_results(self):
        """Save results to file"""
        try:
            self.results["last_updated"] = datetime.now(timezone.utc).isoformat()
            with open(self.results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def record_ticket_picks(self, ticket: Dict) -> List[PickRecord]:
        """
        Automatically record picks when a ticket is generated
        
        Args:
            ticket: Generated ticket from Ghost AI
            
        Returns:
            List of recorded picks
        """
        logger.info(f"🎯 Recording picks for ticket {ticket.get('ticket_id', 'unknown')}")
        
        picks = []
        ticket_id = ticket.get('ticket_id', 'unknown')
        game_id = ticket.get('game_id', 'unknown')
        game_time = ticket.get('commence_time', '')
        
        for selection in ticket.get('selections', []):
            # Determine pick side from odds
            odds = selection.get('odds', 0)
            line = selection.get('line', 0)
            
            # Simple logic: negative odds usually mean over, positive odds usually mean under
            pick_side = 'over' if odds < 0 else 'under'
            
            pick = PickRecord(
                ticket_id=ticket_id,
                player_name=selection.get('player_name', 'Unknown'),
                prop_type=selection.get('prop_type', 'Unknown'),
                line=line,
                odds=odds,
                confidence=selection.get('confidence', 0.5),
                pick_side=pick_side,
                game_id=game_id,
                game_time=game_time,
                opening_odds=odds  # Assume opening odds are current odds when recorded
            )
            
            picks.append(pick)
            
            # Add to tracked picks
            self.tracked_picks["picks"].append(asdict(pick))
            
            logger.info(f"   📝 Recorded: {pick.player_name} {pick.prop_type} {pick.pick_side} {pick.line} @ {pick.odds}")
        
        self._save_tracked_picks()
        return picks
    
    async def update_closing_odds(self, game_id: str):
        """
        Update closing odds for picks in a specific game
        
        Args:
            game_id: ID of the game to update
        """
        logger.info(f"📊 Updating closing odds for game {game_id}")
        
        try:
            # Find picks for this game
            game_picks = [
                pick for pick in self.tracked_picks["picks"] 
                if pick.get('game_id') == game_id and pick.get('result') is None
            ]
            
            if not game_picks:
                logger.info(f"No pending picks found for game {game_id}")
                return
            
            # Fetch closing odds from OddsAPI
            closing_odds = await self._fetch_closing_odds(game_id)
            
            if closing_odds:
                for pick in game_picks:
                    player_name = pick.get('player_name')
                    prop_type = pick.get('prop_type')
                    
                    if player_name in closing_odds and prop_type in closing_odds[player_name]:
                        pick['closing_odds'] = closing_odds[player_name][prop_type]
                        logger.info(f"   📈 Updated {player_name} {prop_type}: {pick['closing_odds']}")
                
                self._save_tracked_picks()
            
        except Exception as e:
            logger.error(f"Error updating closing odds for game {game_id}: {e}")
    
    async def _fetch_closing_odds(self, game_id: str) -> Optional[Dict]:
        """
        Fetch closing odds from OddsAPI
        
        Args:
            game_id: Game ID to fetch odds for
            
        Returns:
            Dictionary of closing odds by player and prop type
        """
        # This is a placeholder - implement actual OddsAPI call
        logger.info(f"🔍 Fetching closing odds for game {game_id}")
        
        # Mock implementation - replace with actual API call
        return {
            "Player1": {
                "hits": -115,
                "runs": -105
            },
            "Player2": {
                "strikeouts": -110,
                "walks": -120
            }
        }
    
    def record_game_results(self, game_id: str, results: List[Dict]):
        """
        Record game results and update pick outcomes
        
        Args:
            game_id: ID of the game
            results: List of result dictionaries with player stats
        """
        logger.info(f"🏁 Recording results for game {game_id}")
        
        # Find picks for this game
        game_picks = [
            pick for pick in self.tracked_picks["picks"] 
            if pick.get('game_id') == game_id and pick.get('result') is None
        ]
        
        if not game_picks:
            logger.info(f"No pending picks found for game {game_id}")
            return
        
        # Process each pick
        for pick in game_picks:
            player_name = pick.get('player_name')
            prop_type = pick.get('prop_type')
            line = pick.get('line', 0)
            pick_side = pick.get('pick_side', 'over')
            
            # Find corresponding result
            result = None
            for r in results:
                if r.get('player_name') == player_name and r.get('prop_type') == prop_type:
                    result = r
                    break
            
            if result:
                actual_value = result.get('actual_value', 0)
                pick['actual_value'] = actual_value
                pick['result_updated_at'] = datetime.now(timezone.utc).isoformat()
                
                # Determine outcome
                if pick_side == 'over':
                    if actual_value > line:
                        pick['result'] = 'W'
                    elif actual_value < line:
                        pick['result'] = 'L'
                    else:
                        pick['result'] = 'P'
                else:  # under
                    if actual_value < line:
                        pick['result'] = 'W'
                    elif actual_value > line:
                        pick['result'] = 'L'
                    else:
                        pick['result'] = 'P'
                
                logger.info(f"   🎯 {player_name} {prop_type}: {actual_value} vs {line} {pick_side} = {pick['result']}")
                
                # Add to results
                self.results["results"].append({
                    "pick_id": f"{pick['ticket_id']}_{player_name}_{prop_type}",
                    "ticket_id": pick['ticket_id'],
                    "player_name": player_name,
                    "prop_type": prop_type,
                    "line": line,
                    "actual_value": actual_value,
                    "result": pick['result'],
                    "odds": pick['odds'],
                    "closing_odds": pick.get('closing_odds'),
                    "confidence": pick['confidence'],
                    "game_id": game_id,
                    "recorded_at": pick['recorded_at'],
                    "result_updated_at": pick['result_updated_at']
                })
        
        self._save_tracked_picks()
        self._save_results()
        
        # Update performance tracking
        self._update_performance_tracking()
    
    def _update_performance_tracking(self):
        """Update performance tracking with latest results"""
        try:
            # Calculate performance metrics
            total_picks = len(self.results["results"])
            wins = len([r for r in self.results["results"] if r.get('result') == 'W'])
            losses = len([r for r in self.results["results"] if r.get('result') == 'L'])
            pushes = len([r for r in self.results["results"] if r.get('result') == 'P'])
            
            win_rate = (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0
            
            # Calculate ROI (simplified)
            total_risk = sum(abs(r.get('odds', 0)) for r in self.results["results"])
            total_return = sum(
                (abs(r.get('odds', 0)) * 0.91) if r.get('result') == 'W' else -abs(r.get('odds', 0))
                for r in self.results["results"]
            )
            roi = ((total_return - total_risk) / total_risk) * 100 if total_risk > 0 else 0
            
            performance_data = {
                "total_picks": total_picks,
                "wins": wins,
                "losses": losses,
                "pushes": pushes,
                "win_rate": win_rate,
                "roi": roi,
                "total_risk": total_risk,
                "total_return": total_return,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            # Save performance data
            with open(self.performance_file, 'w') as f:
                json.dump(performance_data, f, indent=2)
            
            logger.info(f"📈 Performance Updated: {wins}W-{losses}L-{pushes}P ({win_rate:.1f}% win rate, {roi:.1f}% ROI)")
            
        except Exception as e:
            logger.error(f"Error updating performance tracking: {e}")
    
    def get_daily_summary(self, date: str = None) -> Dict:
        """
        Get daily summary of picks and results
        Also logs confidence tier performance to ghost_confidence_journal.json
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        # Filter picks for the date
        date_picks = [
            pick for pick in self.tracked_picks["picks"]
            if pick.get('recorded_at', '').startswith(date)
        ]
        date_results = [
            result for result in self.results["results"]
            if result.get('result_updated_at', '').startswith(date)
        ]
        wins = len([r for r in date_results if r.get('result') == 'W'])
        losses = len([r for r in date_results if r.get('result') == 'L'])
        pushes = len([r for r in date_results if r.get('result') == 'P'])
        # --- Confidence Journal Logic ---
        conf_tiers = defaultdict(lambda: {'wins': 0, 'losses': 0, 'pushes': 0, 'total': 0})
        for result in date_results:
            conf = result.get('confidence', None)
            if conf is not None:
                tier = round(float(conf) * 20) * 5  # e.g. 0.67 -> 65, 0.72 -> 70
                tier = int(tier)
                if result.get('result') == 'W':
                    conf_tiers[tier]['wins'] += 1
                elif result.get('result') == 'L':
                    conf_tiers[tier]['losses'] += 1
                elif result.get('result') == 'P':
                    conf_tiers[tier]['pushes'] += 1
                conf_tiers[tier]['total'] += 1
        journal_path = os.path.join(os.path.dirname(__file__), '../ghost_confidence_journal.json')
        journal_entry = {
            'date': date,
            'tiers': {str(k): v for k, v in conf_tiers.items()}
        }
        try:
            if os.path.exists(journal_path):
                with open(journal_path, 'r', encoding='utf-8') as f:
                    journal = json.load(f)
            else:
                journal = []
            journal.append(journal_entry)
            with open(journal_path, 'w', encoding='utf-8') as f:
                json.dump(journal, f, indent=2)
        except Exception as e:
            print(f"Error writing to ghost_confidence_journal.json: {e}")
        # --- End Confidence Journal Logic ---
        # --- Self-Reflection & Improvement Goals ---
        reflection = ""
        improvement_goal = ""
        if wins + losses > 0:
            if (wins / (wins + losses)) < 0.5:
                reflection = "Rough day. Many picks lost."
                improvement_goal = "Focus on higher-confidence picks and avoid risky parlays."
            elif (wins / (wins + losses)) > 0.7:
                reflection = "Great day! Most picks won."
                improvement_goal = "Keep doing what works, but watch for overconfidence."
            else:
                reflection = "Mixed results. Some picks worked, some didn't."
                improvement_goal = "Review losing picks and adjust confidence thresholds."
        else:
            reflection = "No picks graded today."
            improvement_goal = "Look for more opportunities tomorrow."
        # Analyze confidence tiers for more insight
        if conf_tiers:
            worst_tier = min(conf_tiers.items(), key=lambda x: x[1]['wins']/(x[1]['total'] or 1))
            best_tier = max(conf_tiers.items(), key=lambda x: x[1]['wins']/(x[1]['total'] or 1))
            if worst_tier[1]['total'] > 2 and (worst_tier[1]['wins']/(worst_tier[1]['total'] or 1)) < 0.3:
                reflection += f" Confidence tier {worst_tier[0]}% performed poorly."
                improvement_goal += f" Consider avoiding {worst_tier[0]}% confidence picks."
            if best_tier[1]['total'] > 2 and (best_tier[1]['wins']/(best_tier[1]['total'] or 1)) > 0.7:
                reflection += f" Confidence tier {best_tier[0]}% was strong."
        # --- End Self-Reflection & Improvement Goals ---
        # --- Accountability Loop ---
        accountability_report = ""
        try:
            diary_path = os.path.join(os.path.dirname(__file__), '../ghost_diary.json')
            if os.path.exists(diary_path):
                with open(diary_path, 'r', encoding='utf-8') as f:
                    diary = json.load(f)
                if len(diary) > 0:
                    yesterday = diary[-1]
                    y_goal = yesterday.get('stats', {}).get('improvement_goal') or yesterday.get('improvement_goal', '')
                    if y_goal:
                        # Simple check: if goal was to avoid low-confidence, did we use low-confidence today?
                        if 'avoid' in y_goal and 'confidence' in y_goal:
                            low_conf_picks = [r for r in date_results if r.get('confidence', 1) < 0.6]
                            if low_conf_picks:
                                accountability_report = f"Did NOT follow yesterday's advice: {y_goal} (used {len(low_conf_picks)} low-confidence picks)"
                            else:
                                accountability_report = f"Followed yesterday's advice: {y_goal}"
                        else:
                            accountability_report = f"Yesterday's goal: {y_goal} (not specifically checked)"
        except Exception as e:
            accountability_report = f"Could not check accountability: {e}"
        # --- End Accountability Loop ---
        return {
            "date": date,
            "total_picks": len(date_picks),
            "resolved_picks": len(date_results),
            "wins": wins,
            "losses": losses,
            "pushes": pushes,
            "win_rate": (wins / (wins + losses)) * 100 if (wins + losses) > 0 else 0,
            "picks": date_picks,
            "results": date_results,
            "reflection": reflection,
            "improvement_goal": improvement_goal,
            "accountability_report": accountability_report
        }
    
    def get_reverse_engine_insights(self) -> Dict:
        """Get insights from reverse engine analysis"""
        try:
            # Get hot picks and trap risks
            hot_picks = self.integration.get_hot_picks_for_today()
            trap_risks = self.integration.get_trap_risks_for_today()
            
            # Get analysis status
            status = self.integration.get_analysis_status()
            
            return {
                "analysis_status": status,
                "hot_picks": hot_picks,
                "trap_risks": trap_risks,
                "analysis_available": self.integration.is_analysis_available()
            }
        except Exception as e:
            logger.error(f"Error getting reverse engine insights: {e}")
            return {"error": str(e)}

# Load update webhook from config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')
def get_update_webhook_url():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config['discord'].get('update_webhook_url')
    except Exception:
        return None

# Discord webhook URL (for updates/reports)
DISCORD_WEBHOOK_URL = get_update_webhook_url()

def send_discord_webhook(content: str, username: str = "Ghost AI Reverse Engine") -> bool:
    """
    Send message to Discord webhook
    
    Args:
        content: Message content
        username: Bot username
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import requests
        
        payload = {
            "content": content,
            "username": username
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code in [200, 204]:
            logger.info("✅ Discord webhook sent successfully")
            return True
        else:
            logger.error(f"❌ Discord webhook failed: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error sending Discord webhook: {e}")
        return False

def send_daily_report_to_discord() -> bool:
    """
    Generate and send daily report to Discord webhook
    
    Returns:
        True if successful, False otherwise
    """
    try:
        report = get_daily_performance_report()
        
        # Split long reports if needed
        if len(report) > 2000:
            chunks = [report[i:i+1900] for i in range(0, len(report), 1900)]
            for i, chunk in enumerate(chunks):
                success = send_discord_webhook(f"📊 Daily Report (Part {i+1}):\n```{chunk}```")
                if not success:
                    return False
        else:
            success = send_discord_webhook(f"📊 Daily Report:\n```{report}```")
            if not success:
                return False
        
        logger.info("✅ Daily report sent to Discord webhook")
        return True
        
    except Exception as e:
        logger.error(f"Error sending daily report to Discord: {e}")
        return False

def send_tracking_update_to_discord(game_id: str, results_count: int) -> bool:
    """
    Send tracking update to Discord webhook
    
    Args:
        game_id: ID of the game
        results_count: Number of results processed
        
    Returns:
        True if successful, False otherwise
    """
    try:
        message = f"🏁 Game Results Processed: {game_id}\n📊 {results_count} picks updated"
        return send_discord_webhook(message)
        
    except Exception as e:
        logger.error(f"Error sending tracking update to Discord: {e}")
        return False

def send_ticket_generation_update_to_discord(ticket_count: int, enhanced_count: int) -> bool:
    """
    Send ticket generation update to Discord webhook
    
    Args:
        ticket_count: Number of tickets generated
        enhanced_count: Number of tickets enhanced
        
    Returns:
        True if successful, False otherwise
    """
    try:
        message = f"🎟️ Tickets Generated: {ticket_count}\n🚀 Enhanced with Reverse Engine: {enhanced_count}"
        return send_discord_webhook(message)
        
    except Exception as e:
        logger.error(f"Error sending ticket generation update to Discord: {e}")
        return False

# Global instance for easy access
auto_integration = AutoIntegration()

# Hook functions for Ghost AI pipeline
def hook_into_ticket_generation(ticket: Dict) -> Dict:
    """
    Hook function to be called when tickets are generated
    Records picks and enhances tickets with reverse engine analysis
    """
    try:
        # Record picks
        picks = auto_integration.record_ticket_picks(ticket)
        
        # Enhance ticket with reverse engine analysis
        enhanced_ticket = auto_integration.integration.enhance_ticket_with_reverse_analysis(ticket)
        
        logger.info(f"🎯 Hook: Recorded {len(picks)} picks and enhanced ticket {ticket.get('ticket_id')}")
        
        # Send Discord notification
        send_ticket_generation_update_to_discord(1, 1)
        
        return enhanced_ticket
        
    except Exception as e:
        logger.error(f"Error in ticket generation hook: {e}")
        return ticket

async def hook_into_results_processing(game_id: str, results: List[Dict]):
    """
    Hook function to be called when game results are processed
    Updates closing odds and records results
    """
    try:
        # Update closing odds
        await auto_integration.update_closing_odds(game_id)
        
        # Record results
        auto_integration.record_game_results(game_id, results)
        
        logger.info(f"🏁 Hook: Processed results for game {game_id}")
        
        # Send Discord notification
        send_tracking_update_to_discord(game_id, len(results))
        
    except Exception as e:
        logger.error(f"Error in results processing hook: {e}")

def hook_into_daily_summary():
    """
    Hook function to be called for daily summary
    Generates and sends daily report to Discord
    """
    try:
        # Send daily report to Discord
        success = send_daily_report_to_discord()
        
        if success:
            logger.info("✅ Daily report sent to Discord webhook")
        else:
            logger.error("❌ Failed to send daily report to Discord")
            
    except Exception as e:
        logger.error(f"Error in daily summary hook: {e}")

def get_daily_performance_report(date: str = None) -> str:
    """
    Generate a daily performance report for CLI/Discord
    
    Args:
        date: Date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        Formatted report string
    """
    try:
        summary = auto_integration.get_daily_summary(date)
        insights = auto_integration.get_reverse_engine_insights()
        
        report = f"""
📊 DAILY PERFORMANCE REPORT - {summary['date']}
{'='*50}

🎯 PICKS SUMMARY:
   Total Picks: {summary['total_picks']}
   Resolved: {summary['resolved_picks']}
   Wins: {summary['wins']}
   Losses: {summary['losses']}
   Pushes: {summary['pushes']}
   Win Rate: {summary['win_rate']:.1f}%

🔬 REVERSE ENGINE INSIGHTS:
   Analysis Available: {'✅' if insights.get('analysis_available') else '❌'}
   Hot Picks: {len(insights.get('hot_picks', []))}
   Trap Risks: {len(insights.get('trap_risks', []))}

📈 PERFORMANCE METRICS:
"""
        
        # Add performance metrics if available
        if auto_integration.performance_file.exists():
            try:
                with open(auto_integration.performance_file, 'r') as f:
                    perf = json.load(f)
                report += f"""
   Overall Win Rate: {perf.get('win_rate', 0):.1f}%
   ROI: {perf.get('roi', 0):.1f}%
   Total Picks: {perf.get('total_picks', 0)}
"""
            except Exception as e:
                report += f"   Error loading performance: {e}\n"
        
        return report
        
    except Exception as e:
        return f"Error generating report: {e}"

if __name__ == "__main__":
    # Test the integration
    print("🧪 Testing Auto Integration System")
    print("="*50)
    
    # Test with mock ticket
    mock_ticket = {
        'ticket_id': 'TEST_001',
        'game_id': 'test_game_1',
        'commence_time': datetime.now(timezone.utc).isoformat(),
        'selections': [
            {
                'player_name': 'Test Player 1',
                'prop_type': 'hits',
                'line': 1.5,
                'odds': -110,
                'confidence': 0.75
            },
            {
                'player_name': 'Test Player 2',
                'prop_type': 'strikeouts',
                'line': 5.5,
                'odds': -120,
                'confidence': 0.80
            }
        ]
    }
    
    # Test ticket generation hook
    enhanced_ticket = hook_into_ticket_generation(mock_ticket)
    print(f"✅ Enhanced ticket confidence: {enhanced_ticket.get('enhanced_confidence_score', 'N/A')}")
    
    # Test daily summary
    summary = auto_integration.get_daily_summary()
    print(f"📊 Daily summary: {summary['total_picks']} picks recorded")
    
    # Test performance report
    report = get_daily_performance_report()
    print(report) 