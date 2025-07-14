import os
import aiohttp
import asyncio
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import difflib
from datetime import datetime
from odds_reverse_engineering.utils.chatgpt_data_fetcher import ChatGPTDataFetcher

load_dotenv()

class DataFetcher:
    BASE_URL = "https://api.the-odds-api.com/v4/sports"

    def __init__(self):
        self.api_key = os.getenv("ODDS_API_KEY")
        if not self.api_key:
            raise ValueError("ODDS_API_KEY not set in environment variables.")
        self.session = None
        self.chatgpt_fetcher = ChatGPTDataFetcher()  # For tennis/golf and context pulls

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    def validate_response(self, data: Any, expected_type: type = dict) -> bool:
        """Validate API response data. Returns True if valid, False if corrupt/missing."""
        if data is None:
            print("[DataFetcher] Warning: Received None data from API.")
            return False
        if not isinstance(data, expected_type):
            print(f"[DataFetcher] Warning: Data type mismatch. Expected {expected_type}, got {type(data)}.")
            return False
        # Add more validation rules as needed
        return True

    async def get_odds(self, sport: str, regions: str = "us", markets: str = "h2h,spreads,totals", date: Optional[str] = None) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{sport}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": markets,
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        if date:
            params["date"] = date
        retries = 3
        for attempt in range(retries):
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if self.validate_response(data, expected_type=list):
                        return data
                    else:
                        print(f"[DataFetcher] Invalid data received on attempt {attempt+1}.")
                else:
                    text = await resp.text()
                    print(f"[DataFetcher] Failed to fetch odds: {resp.status} {text} (attempt {attempt+1})")
            await asyncio.sleep(1)
        raise Exception(f"Failed to fetch valid odds after {retries} attempts.")

    async def get_player_props(self, sport: str, event_id: str, prop_markets: str = "player_props") -> Optional[Dict[str, Any]]:
        url = f"{self.BASE_URL}/{sport}/events/{event_id}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",
            "markets": prop_markets,
            "oddsFormat": "american",
            "dateFormat": "iso"
        }
        retries = 3
        for attempt in range(retries):
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if self.validate_response(data, expected_type=dict):
                        return data
                    else:
                        print(f"[DataFetcher] Invalid player props data received on attempt {attempt+1}.")
                else:
                    text = await resp.text()
                    print(f"[DataFetcher] Failed to fetch player props: {resp.status} {text} (attempt {attempt+1})")
            await asyncio.sleep(1)
        raise Exception(f"Failed to fetch valid player props after {retries} attempts.")

    def deduplicate_props(self, props: list) -> list:
        """Remove duplicate props from a list based on event_id, player, market, line, side, bookmaker."""
        seen = set()
        unique_props = []
        for prop in props:
            key = (
                prop.get('event_id'),
                prop.get('player'),
                prop.get('market'),
                prop.get('line'),
                prop.get('side'),
                prop.get('bookmaker')
            )
            if key not in seen:
                seen.add(key)
                unique_props.append(prop)
        return unique_props

    def fuzzy_team_match(self, team_name, candidate_names, cutoff=0.7):
        """Return the best fuzzy match for team_name from candidate_names."""
        matches = difflib.get_close_matches(team_name.lower(), [c.lower() for c in candidate_names], n=1, cutoff=cutoff)
        return matches[0] if matches else None

    def normalize_event_time(self, event_time_str):
        """Normalize event time to date+hour (YYYY-MM-DD HH)."""
        try:
            dt = datetime.fromisoformat(event_time_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H')
        except Exception:
            return event_time_str[:13]  # fallback: first 13 chars (YYYY-MM-DDTHH)

    # Example fallback event lookup table
    EVENT_LOOKUP = {
        # (team1_slug, team2_slug, date_hour): event_id
        ("fever", "aces", "2024-07-01 19"): "evt12345",
        # Add more known mismatches here
    }

    def find_event_id(self, team1, team2, event_time, available_events):
        """Find event_id by fuzzy team matching and normalized time, with fallback."""
        norm_time = self.normalize_event_time(event_time)
        for event in available_events:
            home = event.get('home_team', '').lower()
            away = event.get('away_team', '').lower()
            if (self.fuzzy_team_match(team1, [home, away]) and self.fuzzy_team_match(team2, [home, away]) and
                self.normalize_event_time(event.get('commence_time', '')) == norm_time):
                return event.get('id')
        # Fallback lookup
        key = (team1.lower(), team2.lower(), norm_time)
        return self.EVENT_LOOKUP.get(key) 