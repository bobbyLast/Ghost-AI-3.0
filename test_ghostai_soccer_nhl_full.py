from dotenv import load_dotenv
import os
from datetime import datetime
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher

load_dotenv()
fetcher = ChatGPTDataFetcher()
today = datetime.now().strftime('%Y-%m-%d')

sports = ['soccer', 'nhl']

for sport in sports:
    print(f"\n⚽🏒 [1] Fetching {sport.upper()} matchups for {today} (first call, should use OpenAI if not in memory)...")
    matchups = fetcher.get_soccer_nhl_matchups(sport, today)
    if matchups:
        for m in matchups:
            print(m)
    else:
        print(f"No {sport} matchups returned.")

    print(f"\n⚽🏒 [2] Fetching {sport.upper()} matchups for {today} again (should use memory)...")
    matchups2 = fetcher.get_soccer_nhl_matchups(sport, today)
    if matchups2:
        for m in matchups2:
            print(m)
    else:
        print(f"No {sport} matchups returned on second call.")

print("\n✅ Teacher-Student memory test complete. Check data/ghost_confidence/teacher_student_memory.json to see the memory grow!") 