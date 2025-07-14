#!/usr/bin/env python3
"""
Moneyline Ticket Generator for Ghost AI
Generates moneyline tickets with intelligent analysis and unified storage.
"""

import os
import json
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

# Add import for unified ticket manager
from ghost_ai_core_memory.tickets.integration_hooks import hook_ticket_generation

import os
import json
import logging
import requests
from pathlib import Path
from datetime import datetime, timezone
import os
from datetime import datetime
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher

SUPPORTED_API_SPORTS = ["mlb", "wnba"]
SUPPORTED_CHATGPT_SPORTS = ["tennis", "golf"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('moneyline_ticket_generator')

# Load config
CONFIG_PATH = Path('config/config.json')
if CONFIG_PATH.exists():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    ml_cfg = config.get('moneyline_ticketing', {})
else:
    raise RuntimeError('Missing config/config.json')

ODDS_API_KEY = os.getenv('ODDS_API_KEY')
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
ODDS_API_ODDS = f"{ODDS_API_BASE_URL}/sports/{{sport_key}}/odds"

# Load min_confidence from config
try:
    with open('config/config.json', 'r') as f:
        config = json.load(f)
    min_confidence = config.get('moneyline_ticketing', {}).get('min_confidence', 0.70)
except Exception:
    min_confidence = 0.70

def get_today_date():
    return datetime.now().strftime("%Y-%m-%d")

class MoneylineTicketGenerator:
    def __init__(self):
        self.chatgpt_fetcher = ChatGPTDataFetcher()
        # ... existing initialization ...

    def fetch_moneyline_data(self, sport: str, date: str = None):
        date = date or get_today_date()
        if sport.lower() in SUPPORTED_API_SPORTS:
            # ... existing OddsAPI logic ...
            return self.fetch_from_oddsapi(sport, date)
        elif sport.lower() in SUPPORTED_CHATGPT_SPORTS:
            return self.fetch_from_chatgpt(sport, date)
        else:
            raise ValueError(f"Unsupported sport: {sport}")

    def fetch_from_chatgpt(self, sport: str, date: str):
        matchups = self.chatgpt_fetcher.get_tennis_golf_matchups(sport, date)
        moneyline_data = []
        for matchup in matchups:
            player_a = matchup.get("player_a")
            player_b = matchup.get("player_b")
            start_time = matchup.get("start_time")
            favtrap = self.chatgpt_fetcher.get_favorite_and_trap(sport, player_a, player_b, date)
            winprob = self.chatgpt_fetcher.get_win_probability(sport, player_a, player_b, date)
            moneyline_data.append({
                "player_a": player_a,
                "player_b": player_b,
                "start_time": start_time,
                "favorite": favtrap.get("favorite"),
                "underdog": favtrap.get("underdog"),
                "trap": favtrap.get("trap"),
                "trap_reason": favtrap.get("reason"),
                "win_prob_a": winprob.get("win_prob_a"),
                "win_prob_b": winprob.get("win_prob_b"),
                "win_prob_reason": winprob.get("reason"),
            })
        return moneyline_data

    def generate_tickets(self, sport: str, date: str = None):
        date = date or get_today_date()
        moneyline_data = self.fetch_moneyline_data(sport, date)
        tickets = []
        for ml in moneyline_data:
            # Confidence logic: combine win probability, trap, and narrative context
            confidence = 0.5
            if ml["win_prob_a"] and ml["win_prob_b"]:
                confidence = max(ml["win_prob_a"], ml["win_prob_b"])
            if ml["trap"]:
                confidence -= 0.1  # Penalize for trap
            # Build ticket
            ticket = {
                "sport": sport,
                "date": date,
                "matchup": f"{ml['player_a']} vs {ml['player_b']}",
                "favorite": ml["favorite"],
                "underdog": ml["underdog"],
                "confidence": confidence,
                "trap": ml["trap"],
                "trap_reason": ml["trap_reason"],
                "win_prob_reason": ml["win_prob_reason"],
                "start_time": ml["start_time"],
            }
            # Add human-readable explanation
            ticket["explanation"] = self.chatgpt_fetcher.get_ticket_explanation(ticket)
            tickets.append(ticket)
        return tickets

# Helper: American to decimal odds
def american_to_decimal(odds):
    if odds > 0:
        return (odds / 100) + 1
    else:
        return (100 / abs(odds)) + 1

def implied_prob_from_american(odds):
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)

def get_bovada_all_bets(sport_key='baseball_mlb'):
    url = ODDS_API_ODDS.format(sport_key=sport_key)
    params = {
        'apiKey': ODDS_API_KEY,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'bookmakers': 'bovada',
        'oddsFormat': 'american'
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        logger.error(f"Failed to fetch odds: {resp.status_code} {resp.text}")
        return []
    games = resp.json()
    all_bets = []
    for game in games:
        game_id = game.get('id')
        home_team = game.get('home_team')
        away_team = game.get('away_team')
        commence_time = game.get('commence_time')
        for book in game.get('bookmakers', []):
            if book.get('key') != 'bovada':
                continue
            for market in book.get('markets', []):
                market_key = market.get('key')
                for outcome in market.get('outcomes', []):
                    bet = {
                        'game_id': game_id,
                        'home_team': home_team,
                        'away_team': away_team,
                        'commence_time': commence_time,
                        'team': outcome.get('name', ''),
                        'odds': outcome.get('price'),
                        'market': market_key,
                        'bookmaker': 'bovada',
                        'opponent': away_team if outcome.get('name') == home_team else home_team,
                        'line': outcome.get('point', None),
                        'label': outcome.get('name', ''),
                    }
                    all_bets.append(bet)
    return all_bets

def get_ghost_win_prob(team, opponent, game_id):
    # TODO: Integrate with Ghost's reverse engine/model
    # For now, stub with 0.7 for testing
    return 0.7

def detect_trap(line_history):
    # TODO: Implement real line movement/trap detection
    # For now, always return False
    return False

def build_best_bet_tickets(all_bets, legs_list, min_conf, max_juice, trap_filter):
    # Group all bets by game
    games = {}
    for bet in all_bets:
        game_id = bet['game_id']
        if game_id not in games:
            games[game_id] = []
        games[game_id].append(bet)
    
    # For each game, pick the best bet (highest value edge/confidence)
    best_bets = []
    for game_bets in games.values():
        best = None
        best_score = float('-inf')
        for bet in game_bets:
            odds = bet['odds']
            if odds is None:
                continue
            if bet['market'] == 'h2h' and odds < max_juice:
                continue
            # Use ghost win prob for moneyline, or a stub for others (extend as needed)
            if bet['market'] == 'h2h':
                ghost_prob = get_ghost_win_prob(bet['team'], bet['opponent'], bet['game_id'])
            else:
                ghost_prob = 0.7  # TODO: Replace with real model for spreads/totals
            implied_prob = implied_prob_from_american(odds)
            value_edge = ghost_prob - implied_prob
            confidence = ghost_prob
            if confidence < min_conf:
                continue
            if value_edge < 0:
                continue
            trap = False
            if trap_filter:
                trap = detect_trap([])
            if trap:
                continue
            score = value_edge  # Could use more advanced scoring
            if score > best_score:
                best_score = score
                best = {**bet, 'ghost_prob': ghost_prob, 'implied_prob': implied_prob, 'value_edge': value_edge, 'confidence': confidence, 'trap': trap}
        if best:
            best_bets.append(best)
    
    # Sort by value edge descending
    best_bets.sort(key=lambda x: x['value_edge'], reverse=True)
    
    # ENSURE NO DUPLICATE GAMES IN TICKETS
    tickets = []
    for legs in legs_list:
        if len(best_bets) < legs:
            continue
        
        # Create ticket with different games
        ticket_legs = []
        used_games = set()
        
        for bet in best_bets:
            if len(ticket_legs) >= legs:
                break
            
            # Check if this game is already used
            game_id = bet['game_id']
            if game_id in used_games:
                continue
            
            # Add this bet to ticket
            ticket_legs.append(bet)
            used_games.add(game_id)
        
        # Only create ticket if we have enough legs from different games
        if len(ticket_legs) == legs:
            combined_odds = 1.0
            min_conf = 1.0
            for leg in ticket_legs:
                dec = american_to_decimal(leg['odds'])
                combined_odds *= dec
                min_conf = min(min_conf, leg['confidence'])
            
            tickets.append({
                'ticket_type': 'best_bet',
                'legs': ticket_legs,
                'total_legs': legs,
                'combined_payout': round(combined_odds, 2),
                'confidence_floor': min_conf,
                'games_count': len(used_games),
                'unique_games': True
            })
    
    logger.info(f"Created {len(tickets)} tickets with no duplicate games")
    return tickets

def format_best_bet_ticket_for_discord(ticket, variance_warning_legs):
    legs = ticket['legs']
    lines = []
    if ticket['total_legs'] >= variance_warning_legs:
        lines.append('⚠️ **High Variance Parlay!** ⚠️')
    lines.append(f"Parlay ({ticket['total_legs']} Picks)")
    lines.append(f"Risk: $12.00   Win: ${ticket['combined_payout']*12:.2f}")
    lines.append("")
    for leg in legs:
        # Format: Team +1.5 (-160) or Team ML (-163) or Team O 8.5 (-105)
        if leg['market'] == 'spreads':
            line_str = f"{leg['team']} {leg['line']:+.1f} ({leg['odds']:+})"
        elif leg['market'] == 'totals':
            ou = 'O' if 'over' in leg['label'].lower() else 'U'
            line_str = f"{ou} {leg['line']} ({leg['odds']:+})"
        else:  # moneyline
            line_str = f"{leg['team']} ML ({leg['odds']:+})"
        lines.append(line_str)
    return '\n'.join(lines)

def post_to_discord(webhook_url, content):
    data = {"content": content}
    resp = requests.post(webhook_url, json=data)
    if resp.status_code in (200, 204):
        logger.info("Posted ML ticket to Discord.")
    else:
        logger.error(f"Failed to post to Discord: {resp.status_code} {resp.text}")

TICKETS_GENERATED_DIR = Path('ghost_ai_core_memory/tickets/generated')
TICKETS_GENERATED_DIR.mkdir(parents=True, exist_ok=True)

def save_moneyline_tickets(tickets):
    """Save moneyline tickets using unified ticket manager."""
    try:
        # Use the unified ticket manager hook to save tickets
        saved_tickets = hook_ticket_generation(tickets)
        logger.info(f"💾 Saved {len(saved_tickets)} moneyline tickets to unified storage")
        return saved_tickets
    except Exception as e:
        logger.error(f"Error saving moneyline tickets: {e}")
        return tickets

def main():
    print("[DEBUG] Entered moneyline_ticket_generator.main()")
    logger.info('[DEBUG] Entered moneyline_ticket_generator.main()')
    # Always use the provided Discord webhook for moneyline tickets
    webhook_url = os.getenv('DISCORD_TICKETS_WEBHOOK', '')
    print("STARTING BEST BET TICKET GENERATION PIPELINE")
    logger.info("=" * 60)
    logger.info("STARTING BEST BET TICKET GENERATION PIPELINE")
    logger.info("=" * 60)
    min_conf = 0.55  # Lowered threshold to allow more moneyline tickets
    min_value_edge = 0.10  # Raised minimum value edge to filter out weaker bets
    max_juice = ml_cfg.get('max_juice', -250)
    trap_filter = ml_cfg.get('trap_filter_enabled', True)
    variance_warning_legs = ml_cfg.get('variance_warning_legs', 10)
    # Step 1: Fetch all bets
    print("STEP 1: Fetching Bovada all bets (ML, RL, Total)...")
    all_bets = get_bovada_all_bets('baseball_mlb')
    print(f"[STEP 1] Found {len(all_bets)} bets")
    if not all_bets:
        print("No bets found. Exiting.")
        return
    # Step 2: Filter for sharp bets with stricter rules for run line/underdog
    print("STEP 2: Filtering for sharp bets with run line safety...")
    sharp_bets = []
    for bet in all_bets:
        odds = bet['odds']
        if odds is None:
            continue
        if bet['market'] == 'h2h' and odds < max_juice:
            continue
        if bet['market'] == 'h2h':
            ghost_prob = get_ghost_win_prob(bet['team'], bet['opponent'], bet['game_id'])
        else:
            ghost_prob = 0.7  # TODO: Replace with real model for spreads/totals
        implied_prob = implied_prob_from_american(odds)
        value_edge = ghost_prob - implied_prob
        confidence = ghost_prob
        # More balanced filter - include both favorites and underdogs
        is_runline = bet['market'] == 'spreads' and bet.get('line') == -1.5
        is_high_odds = odds >= 140
        is_favorite = odds <= -120  # Include favorites too
        is_underdog = odds >= 120   # Include underdogs too
        
        if is_runline or is_high_odds:
            if confidence < 0.88 or value_edge < 0.10:
                continue  # Only allow if super sharp
        elif is_favorite or is_underdog:
            # Allow both favorites and underdogs with same thresholds
            if confidence < min_conf or value_edge < min_value_edge:
                continue
        else:
            # For middle odds, be more selective
            if confidence < min_conf + 0.05 or value_edge < min_value_edge + 0.02:
                continue
        trap = False
        if trap_filter:
            trap = detect_trap([])
        if trap:
            continue
        sharp_bets.append({**bet, 'ghost_prob': ghost_prob, 'implied_prob': implied_prob, 'value_edge': value_edge, 'confidence': confidence, 'trap': trap})
    print(f"[STEP 2] Found {len(sharp_bets)} sharp bets")
    if len(sharp_bets) < 2:
        print("Not enough sharp bets for a parlay. Exiting.")
        return
    # Step 3: Build the parlay from sharp bets (limit to 3-5 legs for realistic payouts)
    print("STEP 3: Building realistic parlay from sharp bets (3-5 legs max)...")
    sharp_bets.sort(key=lambda x: x['value_edge'], reverse=True)
    
    # Limit to 2-3 legs for very realistic payouts
    max_legs = 3
    min_legs = 2
    
    # Filter out duplicate teams to ensure each team only appears once
    unique_teams = set()
    filtered_bets = []
    for bet in sharp_bets:
        team = bet.get('team', '')
        if team and team not in unique_teams:
            unique_teams.add(team)
            filtered_bets.append(bet)
    
    if len(filtered_bets) > max_legs:
        ticket_legs = filtered_bets[:max_legs]
    else:
        ticket_legs = filtered_bets
    
    if len(ticket_legs) < min_legs:
        print(f"Not enough unique teams for a {min_legs}-leg parlay. Exiting.")
        return
    combined_odds = 1.0
    min_conf = 1.0
    for leg in ticket_legs:
        dec = american_to_decimal(leg['odds'])
        combined_odds *= dec
        min_conf = min(min_conf, leg['confidence'])
    ticket = {
        'ticket_type': 'best_bet',
        'legs': ticket_legs,
        'total_legs': len(ticket_legs),
        'combined_payout': round(combined_odds, 2),
        'confidence_floor': min_conf
    }
    # Step 4: Save using unified ticket manager
    print("STEP 4: Saving ticket using unified storage...")
    saved_tickets = save_moneyline_tickets([ticket])
    if saved_tickets:
        print(f"[STEP 4] Saved ticket to unified storage")
        logger.info(f"[STEP 4] Saved ticket to unified storage")
    else:
        print(f"[STEP 4] Failed to save ticket")
        logger.error(f"[STEP 4] Failed to save ticket")
        return
    # Step 5: Post to Discord
    print("STEP 5: Posting ticket to Discord...")
    if webhook_url:
        content = format_best_bet_ticket_for_discord(ticket, variance_warning_legs)
        # Before posting to Discord, ensure ticket has 'saved_at'
        if 'saved_at' not in ticket:
            ticket['saved_at'] = datetime.now(timezone.utc).isoformat()
        moneyline_confidence = ticket['confidence_floor']
        print(f"[DEBUG] Moneyline confidence: {moneyline_confidence}, threshold: {min_confidence}")
        logger.info(f"[DEBUG] Moneyline confidence: {moneyline_confidence}, threshold: {min_confidence}")
        if moneyline_confidence >= min_confidence:
            post_to_discord(webhook_url, content)
            print(f"[STEP 5] Posted ticket to Discord")
            print("[DEBUG] Moneyline ticket posted to Discord.")
            logger.info('[DEBUG] Moneyline ticket posted to Discord.')
        else:
            print(f"[DEBUG] Moneyline bet below threshold, not posting.")
            logger.info(f"[DEBUG] Moneyline bet below threshold, not posting.")
    else:
        print("[STEP 5] No Discord webhook URL configured")
    # Print summary
    print("\n🎯 BEST BET PIPELINE SUMMARY:")
    print(f"   Total Legs: {len(ticket_legs)}")
    print(f"   Combined Odds: {combined_odds:.2f}")
    print(f"   Min Confidence: {min_conf:.3f}")
    logger.info("=" * 60)
    logger.info("🏁 BEST BET PIPELINE COMPLETE!")
    logger.info(f"🎫 Ticket legs: {len(ticket_legs)}")
    logger.info("💾 Saved to unified storage")
    logger.info("=" * 60)

if __name__ == '__main__':
    main() 