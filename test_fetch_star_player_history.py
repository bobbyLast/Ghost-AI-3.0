from core.tennis_prop_fetcher import TennisPropFetcher
from core.tennis_api_client import get_players
import json

# Use the same top 50 lists as in the fetcher
ATP_TOP_50 = TennisPropFetcher.ATP_TOP_50
WTA_TOP_50 = TennisPropFetcher.WTA_TOP_50

all_star_data = []

print("=== Fetching all available stats/history for ATP/WTA top 50 stars ===")

for star in ATP_TOP_50 + WTA_TOP_50:
    print(f"Fetching data for: {star}")
    # Try to fetch by full name and by last name (API may use either)
    player_data = get_players(player_name=star)
    if not player_data:
        # Try last name only
        last_name = star.split()[-1]
        player_data = get_players(player_name=last_name)
    all_star_data.append({
        'star_name': star,
        'data': player_data
    })
    print(f"  Data found: {'Yes' if player_data else 'No'}")

# Save all data to a JSON file
with open('star_player_full_stats.json', 'w') as f:
    json.dump(all_star_data, f, indent=2, default=str)

print("All star player data saved to star_player_full_stats.json") 