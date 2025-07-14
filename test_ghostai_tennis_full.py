from dotenv import load_dotenv
import os
from datetime import datetime
import openai
import json

# 1. Load .env and get the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env!")

client = openai.OpenAI(api_key=api_key)
today = datetime.now().strftime('%Y-%m-%d')

# --- 1. Match Schedules ---
prompt_schedule = (
    f"List all ATP and WTA matches scheduled for {today}, with start times and players. "
    "Return a JSON array: [{\"player_a\":..., \"player_b\":..., \"start_time\":..., \"tournament\":...}, ...]"
)
print(f"\n🎾 [1] Match Schedule for {today}")
schedule = []
try:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_schedule}],
        max_tokens=512,
        temperature=0.2
    )
    raw_content = resp.choices[0].message.content or ""
    try:
        schedule = json.loads(raw_content)
        for match in schedule:
            print(match)
    except Exception as parse_err:
        print("⚠️ Could not parse JSON. Raw response from ChatGPT:")
        print(raw_content)
        print("Parse error:", parse_err)
except Exception as e:
    print("❌ Error fetching match schedule:", e)
    schedule = []

# --- 2. Available Props ---
prompt_props = "What are the typical prop markets offered on Underdog for tennis? Return as a JSON array."
print(f"\n🎾 [2] Available Prop Markets")
try:
    resp = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt_props}],
        max_tokens=256,
        temperature=0.2
    )
    props = json.loads(resp.choices[0].message.content)
    for p in props:
        print(p)
except Exception as e:
    print("❌ Error fetching prop markets:", e)

# --- 3. For each match, get odds, form, H2H, surface, trap check ---
for match in schedule[:2]:  # Limit to 2 matches for demo
    player_a = match.get("player_a")
    player_b = match.get("player_b")
    tournament = match.get("tournament", "")
    print(f"\n🎾 [3] Deep Dive: {player_a} vs {player_b} ({tournament})")

    # a) Odds
    prompt_odds = f"What are the current betting odds for {player_a} vs {player_b}? Return JSON."
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_odds}],
            max_tokens=128,
            temperature=0.2
        )
        odds = json.loads(resp.choices[0].message.content)
        print("Odds:", odds)
    except Exception as e:
        print("❌ Error fetching odds:", e)

    # b) Recent Form
    prompt_form = f"What’s {player_a}’s form in their last 5 matches? Return JSON."
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_form}],
            max_tokens=128,
            temperature=0.2
        )
        form = json.loads(resp.choices[0].message.content)
        print(f"{player_a} form:", form)
    except Exception as e:
        print(f"❌ Error fetching form for {player_a}:", e)

    # c) H2H
    prompt_h2h = f"What’s the H2H record between {player_a} and {player_b}? Return JSON."
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_h2h}],
            max_tokens=128,
            temperature=0.2
        )
        h2h = json.loads(resp.choices[0].message.content)
        print("H2H:", h2h)
    except Exception as e:
        print("❌ Error fetching H2H:", e)

    # d) Surface Advantage
    prompt_surface = f"Is {player_a} better on grass, hard, or clay? Return JSON."
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_surface}],
            max_tokens=128,
            temperature=0.2
        )
        surface = json.loads(resp.choices[0].message.content)
        print(f"{player_a} surface advantage:", surface)
    except Exception as e:
        print(f"❌ Error fetching surface for {player_a}:", e)

    # e) Trap Spot Detection
    prompt_trap = f"Does this matchup or line seem suspicious based on public sentiment? Return JSON."
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_trap}],
            max_tokens=128,
            temperature=0.2
        )
        trap = json.loads(resp.choices[0].message.content)
        print("Trap check:", trap)
    except Exception as e:
        print("❌ Error fetching trap check:", e)

    # f) Example: Build a prop object
    prop_obj = {
        "player": player_a,
        "prop": "1st Set Games Played",
        "line": 9.5,
        "side": "Higher",
        "odds": odds.get("odds_a") if 'odds' in locals() else None,
        "confidence": 0.81  # Example static confidence
    }
    print("Example prop object:", prop_obj)

# --- 4. Grading (Postgame) ---
if schedule:
    match = schedule[0]
    player_a = match.get("player_a")
    player_b = match.get("player_b")
    tournament = match.get("tournament", "")
    prompt_grade = f"What was the result of {player_a} vs {player_b} today in {tournament}? Return JSON."
    print(f"\n🎾 [4] Grading Result: {player_a} vs {player_b} ({tournament})")
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt_grade}],
            max_tokens=128,
            temperature=0.2
        )
        result = json.loads(resp.choices[0].message.content)
        print("Result:", result)
    except Exception as e:
        print("❌ Error fetching grading result:", e) 