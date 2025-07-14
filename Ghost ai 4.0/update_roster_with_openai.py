#!/usr/bin/env python3
"""
OpenAI-Powered Roster Updater for Ghost AI 4.0
Uses OpenAI to intelligently assign teams to unknown players from fetch logs.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_manual_unknown_players() -> List[Dict]:
    """Get manually defined unknown players from recent fetch output."""
    # These are players that showed as "Unknown" in recent fetch output
    unknown_players = [
        # MLB Players from recent fetch
        {"name": "Jasson Domínguez", "game_context": "Chicago Cubs vs New York Yankees"},
        {"name": "Jacob Wilson", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Denzel Clarke", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Nick Kurtz", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Max Muncy", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Ernie Clement", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Tyler Heineman", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Myles Straw", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Leo Jimenez", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Jacob Lopez", "game_context": "Toronto Blue Jays vs Oakland Athletics"},
        {"name": "Matt Shaw", "game_context": "Chicago Cubs vs New York Yankees"},
        {"name": "Oswald Peraza", "game_context": "Chicago Cubs vs New York Yankees"},
        {"name": "Reese McGuire", "game_context": "Chicago Cubs vs New York Yankees"},
        {"name": "Cam Smith", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Wyatt Langford", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Josh Smith", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Christian Walker", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Brice Matthews", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Zack Short", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Ezequiel Duran", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Taylor Trammell", "game_context": "Texas Rangers vs Houston Astros"},
        {"name": "Martin Maldonado", "game_context": "Philadelphia Phillies vs San Diego Padres"},
        {"name": "Trenton Brooks", "game_context": "Philadelphia Phillies vs San Diego Padres"},
        {"name": "Randal Grichuk", "game_context": "Arizona Diamondbacks vs Los Angeles Angels"},
        {"name": "Travis d'Arnaud", "game_context": "Arizona Diamondbacks vs Los Angeles Angels"},
        {"name": "Alek Thomas", "game_context": "Arizona Diamondbacks vs Los Angeles Angels"},
        {"name": "Miguel Rojas", "game_context": "Los Angeles Dodgers vs San Francisco Giants"},
        {"name": "Dominic Smith", "game_context": "Los Angeles Dodgers vs San Francisco Giants"},
        {"name": "Mike Yastrzemski", "game_context": "Los Angeles Dodgers vs San Francisco Giants"},
        {"name": "Casey Schmitt", "game_context": "Los Angeles Dodgers vs San Francisco Giants"},
        {"name": "Robbie Ray", "game_context": "Los Angeles Dodgers vs San Francisco Giants"},
        
        # WNBA Players from recent fetch
        {"name": "Li Yueru", "game_context": "Dallas Wings vs Indiana Fever"},
        {"name": "Kelsey Plum", "game_context": "Connecticut Sun vs Los Angeles Sparks"},
        {"name": "Gabby Williams", "game_context": "Washington Mystics vs Seattle Storm"},
        {"name": "Erica Wheeler", "game_context": "Washington Mystics vs Seattle Storm"},
        {"name": "Kiki Iriafen", "game_context": "Washington Mystics vs Seattle Storm"},
        {"name": "Sonia Citron", "game_context": "Washington Mystics vs Seattle Storm"},
        {"name": "Shakira Austin", "game_context": "Washington Mystics vs Seattle Storm"},
    ]
    
    return unknown_players

def extract_unknown_players_from_logs() -> List[Dict]:
    """Extract unknown players from recent fetch logs."""
    unknown_players = []
    
    # Check for recent log files
    log_patterns = [
        "logs/*.log",
        "*.log",
        "../logs/*.log"
    ]
    
    for pattern in log_patterns:
        try:
            import glob
            log_files = glob.glob(pattern)
            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extract unknown player entries
                        matches = re.findall(r'(\w+(?:\s+\w+)*): Unknown - Unknown \(([^)]+)\)', content)
                        for player_name, game_context in matches:
                            unknown_players.append({
                                'name': player_name.strip(),
                                'game_context': game_context.strip(),
                                'source': log_file
                            })
        except Exception as e:
            logger.warning(f"Error reading log file {pattern}: {e}")
    
    # If no players found in logs, use manual list
    if not unknown_players:
        logger.info("No unknown players found in logs, using manual list...")
        unknown_players = get_manual_unknown_players()
    
    # Remove duplicates
    unique_players = []
    seen_names = set()
    for player in unknown_players:
        if player['name'] not in seen_names:
            unique_players.append(player)
            seen_names.add(player['name'])
    
    return unique_players

def get_team_assignment_from_openai(player_name: str, game_context: str) -> Dict:
    """Use OpenAI to determine the correct team for a player."""
    
    prompt = f"""
    You are a sports data expert. Based on the following information, determine which team this player belongs to:

    Player Name: {player_name}
    Game Context: {game_context}

    Rules:
    1. Look at the game context to see which teams are playing
    2. Use your knowledge of current MLB/WNBA rosters to assign the player to the correct team
    3. If the player could be on either team, use recent roster information to determine the most likely team
    4. If you're not confident, mark as "Unknown"

    Return your response as JSON with these fields:
    - "team": The team name (e.g., "New York Yankees", "Las Vegas Aces")
    - "confidence": A number from 0-1 indicating your confidence
    - "reasoning": Brief explanation of your decision
    - "position": Player position if known (e.g., "Pitcher", "Batter", "Guard", "Forward")

    Example response:
    {{
        "team": "New York Yankees",
        "confidence": 0.9,
        "reasoning": "Jasson Domínguez is a known Yankees prospect who has been called up recently",
        "position": "Outfielder"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a sports data expert specializing in MLB and WNBA rosters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        logger.error(f"OpenAI API error for {player_name}: {e}")
        return {
            "team": "Unknown",
            "confidence": 0.0,
            "reasoning": f"Error: {str(e)}",
            "position": "Unknown"
        }

def update_roster_file(roster_path: str, new_players: List[Dict]) -> bool:
    """Update roster file with new player-team mappings."""
    try:
        # Load existing roster
        if os.path.exists(roster_path):
            with open(roster_path, 'r', encoding='utf-8') as f:
                roster = json.load(f)
        else:
            roster = {"teams": []}
        
        # Group new players by team
        team_updates = {}
        for player in new_players:
            team = player['team']
            if team != 'Unknown' and player['confidence'] > 0.5:
                if team not in team_updates:
                    team_updates[team] = []
                team_updates[team].append({
                    'name': player['name'],
                    'position': player.get('position', 'Unknown'),
                    'status': 'Active',
                    'added_by': 'OpenAI',
                    'confidence': player['confidence']
                })
        
        # Update roster with new players
        updated = False
        for team_name, new_players_list in team_updates.items():
            # Find the team in the roster
            team_found = False
            for team in roster.get('teams', []):
                if team.get('team') == team_name:
                    existing_players = {p.get('name') for p in team.get('players', [])}
                    
                    # Add new players that aren't already in the roster
                    for new_player in new_players_list:
                        if new_player['name'] not in existing_players:
                            team['players'].append(new_player)
                            updated = True
                            logger.info(f"Added {new_player['name']} to {team_name} roster (confidence: {new_player['confidence']})")
                    team_found = True
                    break
            
            # If team doesn't exist, create it
            if not team_found:
                roster['teams'].append({
                    'team': team_name,
                    'players': new_players_list
                })
                updated = True
                logger.info(f"Created new team {team_name} with {len(new_players_list)} players")
        
        # Save updated roster if changes were made
        if updated:
            # Create backup
            backup_path = f"{roster_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(roster_path):
                import shutil
                shutil.copy2(roster_path, backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            with open(roster_path, "w", encoding="utf-8") as f:
                json.dump(roster, f, indent=2)
            logger.info(f"Updated roster file: {roster_path}")
            return True
        else:
            logger.info("No changes made to roster file")
            return False
        
    except Exception as e:
        logger.error(f"Error updating roster file: {e}")
        return False

def main():
    """Main function to update rosters with OpenAI assistance."""
    logger.info("🤖 OpenAI-Powered Roster Updater for Ghost AI 4.0")
    
    # Extract unknown players from logs
    unknown_players = extract_unknown_players_from_logs()
    logger.info(f"Found {len(unknown_players)} unknown players in logs")
    
    if not unknown_players:
        logger.info("No unknown players found in logs")
        return
    
    # Get team assignments from OpenAI
    logger.info("🔍 Using OpenAI to determine team assignments...")
    updated_players = []
    
    for i, player in enumerate(unknown_players, 1):
        logger.info(f"Processing {i}/{len(unknown_players)}: {player['name']}")
        
        assignment = get_team_assignment_from_openai(player['name'], player['game_context'])
        
        updated_player = {
            'name': player['name'],
            'team': assignment['team'],
            'confidence': assignment['confidence'],
            'reasoning': assignment['reasoning'],
            'position': assignment.get('position', 'Unknown'),
            'game_context': player['game_context']
        }
        
        updated_players.append(updated_player)
        
        if assignment['team'] != 'Unknown':
            logger.info(f"  ✅ {player['name']} → {assignment['team']} (confidence: {assignment['confidence']})")
            logger.info(f"     Reasoning: {assignment['reasoning']}")
        else:
            logger.warning(f"  ❌ {player['name']} → Unknown")
    
    # Update MLB roster
    mlb_players = [p for p in updated_players if p['team'] != 'Unknown' and p['confidence'] > 0.5]
    if mlb_players:
        logger.info(f"Updating MLB roster with {len(mlb_players)} players...")
        update_roster_file("data/mlb/rosters/mlb_rosters_2024.json", mlb_players)
    
    # Update WNBA roster
    wnba_players = [p for p in updated_players if p['team'] != 'Unknown' and p['confidence'] > 0.5]
    if wnba_players:
        logger.info(f"Updating WNBA roster with {len(wnba_players)} players...")
        update_roster_file("data/wnba/rosters/wnba_rosters_2025.json", wnba_players)
    
    # Save detailed results
    results_file = f"roster_update_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(updated_players, f, indent=2)
    
    logger.info(f"✅ Roster update complete! Results saved to: {results_file}")
    logger.info("🔄 You can now re-run the fetch scripts to test the updated rosters")

if __name__ == "__main__":
    main() 