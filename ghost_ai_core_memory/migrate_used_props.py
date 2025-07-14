import os
import json
from pathlib import Path
import re

USED_PROPS_DIR = Path(__file__).parent / 'used_props'

# Regex to extract sport and date from filename
FILENAME_RE = re.compile(r'^(?P<date>\d{4}-\d{2}-\d{2})_(?P<gameid>[a-f0-9]+)_(?P<home>.+)_vs_(?P<away>.+)\.json$')

# Map team names to sport (customize as needed)
TEAM_SPORT_MAP = {
    'Astros': 'mlb', 'Yankees': 'mlb', 'Red Sox': 'mlb', 'Cubs': 'mlb',
    'Aces': 'wnba', 'Liberty': 'wnba', 'Fever': 'wnba', 'Sun': 'wnba',
    # Add more as needed
}

def infer_sport_from_filename(filename):
    match = FILENAME_RE.match(filename)
    if not match:
        return None, None
    date = match.group('date')
    home = match.group('home').replace('_', ' ')
    for team, sport in TEAM_SPORT_MAP.items():
        if team in home:
            return sport, date
    return None, date

def migrate_used_props():
    merged = {}
    for file in USED_PROPS_DIR.glob('*.json'):
        sport, date = infer_sport_from_filename(file.name)
        if not sport or not date:
            print(f"Skipping {file.name} (could not infer sport/date)")
            continue
        key = f"{sport}_{date}"
        if key not in merged:
            merged[key] = {}
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        game_id = file.name.split('_')[2]  # crude, but works for now
        merged[key][game_id] = data
    # Write merged files
    for key, props in merged.items():
        out_file = USED_PROPS_DIR / f"used_props_{key}.json"
        with open(out_file, 'w', encoding='utf-8') as f:
            json.dump(props, f, indent=2)
        print(f"Wrote {out_file}")
    # Delete old files
    for file in USED_PROPS_DIR.glob('*.json'):
        if not file.name.startswith('used_props_'):
            file.unlink()
            print(f"Deleted {file}")

if __name__ == "__main__":
    migrate_used_props() 