import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MoneylineData:
    """Container for moneyline data from a sportsbook"""
    sportsbook: str
    team1_odds: int
    team2_odds: int
    team1_name: str
    team2_name: str
    last_update: str

@dataclass
class GameScriptAnalysis:
    """Analysis of game script based on moneylines"""
    game_id: str
    team1: str
    team2: str
    consensus_favorite: str
    consensus_odds: int
    blowout_risk: float  # 0-1 scale
    pace_expectation: str  # "high", "medium", "low"
    confidence_impact: float  # -1 to 1 (negative = reduce confidence, positive = boost)
    reasoning: str

class MoneylineIntelligence:
    """Intelligence system for analyzing moneylines and their impact on props"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4/sports"
        
    def fetch_moneylines_for_game(self, sport: str, game_id: str, team1: str, team2: str) -> List[MoneylineData]:
        """Fetch moneylines from all available sportsbooks for a specific game (robust multi-sportsbook version)"""
        try:
            url = f"{self.base_url}/{sport}/odds"
            params = {
                'apiKey': self.api_key,
                'regions': 'us',
                'markets': 'h2h',
                'oddsFormat': 'american'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            games_data = response.json()

            # Find the specific game (robust match)
            target_game = None
            for game in games_data:
                home = game.get('home_team', '').lower()
                away = game.get('away_team', '').lower()
                if (
                    (team1.lower() in home and team2.lower() in away) or
                    (team2.lower() in home and team1.lower() in away)
                ):
                    target_game = game
                    break

            if not target_game:
                logger.warning(f"Game not found: {team1} vs {team2}")
                return []

            moneylines = []
            for bookmaker in target_game.get('bookmakers', []):
                book_title = bookmaker.get('title', 'Unknown')
                book_key = bookmaker.get('key', 'unknown')
                for market in bookmaker.get('markets', []):
                    if market.get('key') == 'h2h':
                        outcomes = market.get('outcomes', [])
                        if len(outcomes) >= 2:
                            # Always take the first two outcomes as the two teams
                            ml_data = MoneylineData(
                                sportsbook=book_title,
                                team1_odds=outcomes[0].get('price'),
                                team2_odds=outcomes[1].get('price'),
                                team1_name=outcomes[0].get('name'),
                                team2_name=outcomes[1].get('name'),
                                last_update=market.get('last_update', '')
                            )
                            moneylines.append(ml_data)
                            logger.debug(f"{book_title} ({book_key}): {outcomes[0].get('name')} {outcomes[0].get('price')}, {outcomes[1].get('name')} {outcomes[1].get('price')}")
            logger.info(f"Fetched {len(moneylines)} moneylines for {team1} vs {team2} (books: {[ml.sportsbook for ml in moneylines]})")
            return moneylines
        except Exception as e:
            logger.error(f"Error fetching moneylines: {e}")
            return []
    
    def analyze_game_script(self, moneylines: List[MoneylineData], sport: str = "mlb") -> GameScriptAnalysis:
        """Analyze game script based on consensus moneylines"""
        if not moneylines:
            return None
        
        # Calculate consensus odds
        team1_avg = sum(ml.team1_odds for ml in moneylines) / len(moneylines)
        team2_avg = sum(ml.team2_odds for ml in moneylines) / len(moneylines)
        
        # Determine favorite
        if team1_avg < team2_avg:
            favorite = moneylines[0].team1_name
            favorite_odds = team1_avg
            underdog_odds = team2_avg
        else:
            favorite = moneylines[0].team2_name
            favorite_odds = team2_avg
            underdog_odds = team1_avg
        
        # Calculate blowout risk
        odds_difference = abs(favorite_odds - underdog_odds)
        blowout_risk = self._calculate_blowout_risk(odds_difference, sport)
        
        # Determine pace expectation
        pace_expectation = self._determine_pace_expectation(favorite_odds, underdog_odds, sport)
        
        # Calculate confidence impact
        confidence_impact = self._calculate_confidence_impact(blowout_risk, pace_expectation, sport)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(favorite, favorite_odds, underdog_odds, blowout_risk, pace_expectation, sport)
        
        return GameScriptAnalysis(
            game_id=f"{moneylines[0].team1_name}_{moneylines[0].team2_name}",
            team1=moneylines[0].team1_name,
            team2=moneylines[0].team2_name,
            consensus_favorite=favorite,
            consensus_odds=int(favorite_odds),
            blowout_risk=blowout_risk,
            pace_expectation=pace_expectation,
            confidence_impact=confidence_impact,
            reasoning=reasoning
        )
    
    def _calculate_blowout_risk(self, odds_difference: float, sport: str) -> float:
        """Calculate blowout risk based on odds difference"""
        if sport == "mlb":
            # MLB blowout thresholds
            if odds_difference > 200:  # -300 vs +100
                return 0.8
            elif odds_difference > 150:  # -250 vs +100
                return 0.6
            elif odds_difference > 100:  # -200 vs +100
                return 0.4
            elif odds_difference > 50:   # -150 vs +100
                return 0.2
            else:
                return 0.1
        elif sport == "wnba":
            # WNBA blowout thresholds (generally tighter)
            if odds_difference > 150:
                return 0.7
            elif odds_difference > 100:
                return 0.5
            elif odds_difference > 50:
                return 0.3
            else:
                return 0.1
        else:
            return 0.1
    
    def _determine_pace_expectation(self, favorite_odds: float, underdog_odds: float, sport: str) -> str:
        """Determine expected game pace based on odds"""
        odds_difference = abs(favorite_odds - underdog_odds)
        
        if sport == "mlb":
            # Close games often have higher totals (more competitive at-bats)
            if odds_difference < 50:
                return "high"  # Close game, likely more runs
            elif odds_difference < 100:
                return "medium"
            else:
                return "low"  # Blowout potential, starters might be pulled
        elif sport == "wnba":
            # Similar logic for WNBA
            if odds_difference < 50:
                return "high"
            elif odds_difference < 100:
                return "medium"
            else:
                return "low"
        else:
            return "medium"
    
    def _calculate_confidence_impact(self, blowout_risk: float, pace_expectation: str, sport: str) -> float:
        """Calculate how moneylines should impact prop confidence"""
        impact = 0.0
        
        # Blowout risk reduces confidence
        impact -= blowout_risk * 0.3
        
        # Pace expectation adjustments
        if pace_expectation == "high":
            impact += 0.1  # Slight boost for high-scoring games
        elif pace_expectation == "low":
            impact -= 0.2  # Reduce confidence for low-scoring games
        
        # Sport-specific adjustments
        if sport == "mlb":
            # In MLB, blowouts often mean fewer ABs for losing team
            if blowout_risk > 0.5:
                impact -= 0.2
        
        return max(-1.0, min(1.0, impact))  # Clamp between -1 and 1
    
    def _generate_reasoning(self, favorite: str, favorite_odds: float, underdog_odds: float, 
                          blowout_risk: float, pace_expectation: str, sport: str) -> str:
        """Generate human-readable reasoning for the analysis"""
        reasoning_parts = []
        
        reasoning_parts.append(f"{favorite} is the consensus favorite at {int(favorite_odds)} odds")
        
        if blowout_risk > 0.6:
            reasoning_parts.append("High blowout risk - starters may be pulled early")
        elif blowout_risk > 0.3:
            reasoning_parts.append("Moderate blowout risk - monitor game script")
        else:
            reasoning_parts.append("Low blowout risk - game should remain competitive")
        
        if pace_expectation == "high":
            reasoning_parts.append("Expected high-scoring game - favorable for offensive props")
        elif pace_expectation == "low":
            reasoning_parts.append("Expected low-scoring game - defensive props may have edge")
        else:
            reasoning_parts.append("Expected moderate pace")
        
        if sport == "mlb":
            if blowout_risk > 0.5:
                reasoning_parts.append("MLB blowout risk: Fewer ABs for losing team, bullpen usage changes")
        
        return ". ".join(reasoning_parts)
    
    def get_prop_confidence_adjustment(self, game_analysis: GameScriptAnalysis, prop_type: str, 
                                     player_team: str) -> float:
        """Get specific confidence adjustment for a prop based on game script"""
        if not game_analysis:
            return 0.0
        
        adjustment = game_analysis.confidence_impact
        
        # Team-specific adjustments
        if player_team == game_analysis.consensus_favorite:
            # Props for favorite team players
            if game_analysis.blowout_risk > 0.6:
                adjustment -= 0.2  # Risk of being pulled early
            else:
                adjustment += 0.1  # More opportunities in winning script
        else:
            # Props for underdog team players
            if game_analysis.blowout_risk > 0.6:
                adjustment -= 0.3  # High risk of blowout
            else:
                adjustment += 0.05  # Slight boost in competitive game
        
        # Prop-type specific adjustments
        if prop_type in ["hits", "total_bases", "runs_batted_in"]:
            if game_analysis.pace_expectation == "high":
                adjustment += 0.1
            elif game_analysis.pace_expectation == "low":
                adjustment -= 0.1
        
        elif prop_type in ["strikeouts", "earned_runs"]:
            if game_analysis.pace_expectation == "low":
                adjustment += 0.1  # Pitcher's duel favors K props
            elif game_analysis.pace_expectation == "high":
                adjustment -= 0.1
        
        return max(-1.0, min(1.0, adjustment))

    def analyze_market_sentiment_and_traps(self, moneylines: List[MoneylineData], team: str) -> Dict:
        """
        Analyze market sentiment and detect traps for a given team using all sportsbook moneylines.
        Returns a dict with 'sentiment', 'trap', 'trap_reason', and 'consensus'.
        """
        if not moneylines or not team:
            return {
                'sentiment': 'neutral',
                'trap': False,
                'trap_reason': '',
                'consensus': None
            }

        # Gather all odds for the team
        team_odds = []
        other_odds = []
        for ml in moneylines:
            if ml.team1_name.lower() == team.lower():
                team_odds.append(ml.team1_odds)
                other_odds.append(ml.team2_odds)
            elif ml.team2_name.lower() == team.lower():
                team_odds.append(ml.team2_odds)
                other_odds.append(ml.team1_odds)

        if not team_odds:
            return {
                'sentiment': 'neutral',
                'trap': False,
                'trap_reason': 'No odds found for team',
                'consensus': None
            }

        # Calculate consensus and outliers
        avg_odds = sum(team_odds) / len(team_odds)
        min_odds = min(team_odds)
        max_odds = max(team_odds)
        spread = max_odds - min_odds
        consensus = abs(spread) < 30  # All books within 30 points = consensus

        # Sentiment
        if avg_odds < -120:
            sentiment = 'bullish'  # Market expects team to win
        elif avg_odds > 120:
            sentiment = 'bearish'  # Market expects team to lose
        else:
            sentiment = 'neutral'

        # Trap detection
        trap = False
        trap_reason = ''
        # Outlier: one book is >50 points off consensus
        for odds in team_odds:
            if abs(odds - avg_odds) > 50:
                trap = True
                trap_reason = f"Outlier detected: {odds} vs avg {avg_odds:.1f}"
                break
        # Heavy juice trap
        if not trap and (min_odds < -200 or max_odds > 200):
            trap = True
            trap_reason = f"Heavy juice detected: min {min_odds}, max {max_odds}"
        # Contrarian trap: market is bearish but prop is juiced over
        # (This will be checked in the pipeline with prop odds)

        return {
            'sentiment': sentiment,
            'trap': trap,
            'trap_reason': trap_reason,
            'consensus': consensus,
            'avg_odds': avg_odds,
            'min_odds': min_odds,
            'max_odds': max_odds,
            'spread': spread
        }

# Example usage and testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('ODDS_API_KEY')
    
    if not api_key:
        print("Please set ODDS_API_KEY environment variable")
        exit(1)
    
    # Test the moneyline intelligence
    ml_intel = MoneylineIntelligence(api_key)
    
    # Test with a sample MLB game
    print("Testing Moneyline Intelligence...")
    moneylines = ml_intel.fetch_moneylines_for_game(
        sport="baseball_mlb",
        game_id="test",
        team1="New York Yankees",
        team2="Oakland Athletics"
    )
    
    if moneylines:
        print(f"Found {len(moneylines)} moneylines:")
        for ml in moneylines:
            print(f"  {ml.sportsbook}: {ml.team1_name} {ml.team1_odds}, {ml.team2_name} {ml.team2_odds}")
        
        analysis = ml_intel.analyze_game_script(moneylines, "mlb")
        if analysis:
            print(f"\nGame Script Analysis:")
            print(f"  Favorite: {analysis.consensus_favorite} ({analysis.consensus_odds})")
            print(f"  Blowout Risk: {analysis.blowout_risk:.2f}")
            print(f"  Pace Expectation: {analysis.pace_expectation}")
            print(f"  Confidence Impact: {analysis.confidence_impact:.2f}")
            print(f"  Reasoning: {analysis.reasoning}")
    else:
        print("No moneylines found") 