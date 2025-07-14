from dotenv import load_dotenv
import os
from datetime import datetime
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher

load_dotenv()

fetcher = ChatGPTDataFetcher()
today = datetime.now().strftime('%Y-%m-%d')

print(f"Testing ChatGPTDataFetcher.get_tennis_golf_matchups for tennis on {today}...")
try:
    matchups = fetcher.get_tennis_golf_matchups('tennis', today)
    print("✅ Tennis matchups fetched:")
    for m in matchups:
        print(m)
    if not matchups:
        print("⚠️ No matchups returned. (May be no matches today or API returned empty)")
except Exception as e:
    print(f"❌ ChatGPTDataFetcher tennis test failed: {e}") 