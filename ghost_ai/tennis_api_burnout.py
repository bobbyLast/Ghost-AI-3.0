import os
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path

TENNIS_API_KEY = os.getenv('TENNIS_API_KEY')
TENNIS_API_HOST = os.getenv('TENNIS_API_HOST', 'tennisapi1.p.rapidapi.com')
MEMORY_DIR = Path('ghost_ai_core_memory/tennis/burnout_vault')
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

# --- 1. Fetch all matches for the next 14 days ---
def fetch_matches_for_range(days=14):
    all_matches = []
    headers = {
        "X-RapidAPI-Key": TENNIS_API_KEY,
        "X-RapidAPI-Host": TENNIS_API_HOST
    }
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        url = f"https://{TENNIS_API_HOST}/getMatchList"
        params = {"date": date}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            resp.raise_for_status()
            matches = resp.json().get('matches', [])
            for match in matches:
                match['date'] = date
            all_matches.extend(matches)
            print(f"[Day {i+1}] Pulled {len(matches)} matches for {date}")
            # Save daily
            with open(MEMORY_DIR / f"matches_{date}.json", "w", encoding="utf-8") as f:
                json.dump(matches, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Fetching matches for {date}: {e}")
    return all_matches

# --- 2. Fetch player stats for each player in matches ---
def fetch_player_stats(player_name):
    headers = {
        "X-RapidAPI-Key": TENNIS_API_KEY,
        "X-RapidAPI-Host": TENNIS_API_HOST
    }
    url = f"https://{TENNIS_API_HOST}/getPlayerStats"
    params = {"player": player_name}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        stats = resp.json().get('stats', {})
        return stats
    except Exception as e:
        print(f"[ERROR] Fetching stats for {player_name}: {e}")
        return {}

# --- 3. Save all player stats for all matches ---
def save_all_player_stats(matches):
    player_stats = {}
    for match in matches:
        for player in [match.get('player1'), match.get('player2')]:
            if player and player not in player_stats:
                stats = fetch_player_stats(player)
                player_stats[player] = stats
                with open(MEMORY_DIR / f"player_{player.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
                    json.dump(stats, f, indent=2)
    return player_stats

# --- 4. (Optional) Generate prop ideas and explanations using OpenAI ---
def generate_prop_ideas_with_openai(match, player_stats):
    # TODO: Integrate OpenAI API here
    # Example prompt:
    # prompt = f"""
    # {match['player1']} vs {match['player2']} at {match['tournament']} on {match['date']}.
    # Player 1 stats: {player_stats.get(match['player1'], {})}
    # Player 2 stats: {player_stats.get(match['player2'], {})}
    # What are the best Underdog-style props for this match? Give confidence scores and risk tags."
    # response = openai.ChatCompletion.create(...)
    # Save Q&A to memory
    # with open(MEMORY_DIR / f"qa_{match['player1']}_vs_{match['player2']}_{match['date']}.json", "w", encoding="utf-8") as f:
    #     json.dump({"prompt": prompt, "response": response}, f, indent=2)
    pass

# --- 5. Main burnout loop ---
def main():
    print("\n=== Tennis API Burnout Engine: 14-Day Data Harvest ===")
    matches = fetch_matches_for_range(days=14)
    print(f"\n[Summary] Pulled {len(matches)} matches for next 14 days.")
    player_stats = save_all_player_stats(matches)
    print(f"[Summary] Saved stats for {len(player_stats)} unique players.")
    # TODO: For each match, generate prop ideas and explanations
    # for match in matches:
    #     generate_prop_ideas_with_openai(match, player_stats)
    print("\n[Done] All data saved to:", MEMORY_DIR)
    print("\nTODO: Run validation/tagging script to match props to Underdog and tag results.")

if __name__ == "__main__":
    main() 