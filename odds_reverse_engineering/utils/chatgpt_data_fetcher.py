import os
import json
import time
from typing import List, Dict, Optional, Any
import openai
from pathlib import Path
import threading
from dotenv import load_dotenv
from .teacher_student_memory import TeacherStudentMemory

load_dotenv()

CACHE_DIR = Path('data/cache')
CACHE_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = CACHE_DIR / 'chatgpt_fetcher.log'

def log_event(msg):
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")

class ChatGPTDataFetcher:
    CIRCUIT_BREAKER_THRESHOLD = 5  # max errors before open
    CIRCUIT_BREAKER_RESET = 300    # seconds to reset after open
    MAX_CALLS_PER_MIN = 20         # rate limit
    _lock = threading.Lock()
    _call_times = []
    _error_count = 0
    _circuit_open_until = 0

    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 3600):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError('OPENAI_API_KEY not set in environment variables.')
        self.client = openai.OpenAI(api_key=self.api_key)
        self.cache_ttl = cache_ttl  # seconds
        self.memory = TeacherStudentMemory()

    def _cache_path(self, key: str) -> Path:
        return CACHE_DIR / f'{key}.json'

    def _load_cache(self, key: str) -> Optional[Any]:
        path = self._cache_path(key)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if time.time() - data.get('_ts', 0) < self.cache_ttl:
                return data.get('result')
        return None

    def _save_cache(self, key: str, result: Any):
        path = self._cache_path(key)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump({'_ts': time.time(), 'result': result}, f)

    def _rate_limited(self):
        now = time.time()
        with self._lock:
            # Remove old calls
            self._call_times = [t for t in self._call_times if now - t < 60]
            if len(self._call_times) >= self.MAX_CALLS_PER_MIN:
                return True
            self._call_times.append(now)
        return False

    def _circuit_open(self):
        return time.time() < self._circuit_open_until

    def _record_error(self):
        with self._lock:
            self._error_count += 1
            if self._error_count >= self.CIRCUIT_BREAKER_THRESHOLD:
                self._circuit_open_until = time.time() + self.CIRCUIT_BREAKER_RESET
                msg = f"[ChatGPTDataFetcher] Circuit breaker OPEN for {self.CIRCUIT_BREAKER_RESET}s due to errors."
                print(msg)
                log_event(msg)
                self._error_count = 0

    def _reset_errors(self):
        with self._lock:
            self._error_count = 0

    def _chatgpt_call(self, prompt: str, model: str = 'gpt-3.5-turbo', max_tokens: int = 1024) -> str:
        # Check memory first
        mem_answer = self.memory.get_answer(prompt)
        if mem_answer:
            return mem_answer
        if self._circuit_open():
            msg = "[ChatGPTDataFetcher] Circuit breaker is OPEN. Returning fallback."
            print(msg)
            log_event(msg)
            return ''
        if self._rate_limited():
            msg = "[ChatGPTDataFetcher] Rate limit exceeded. Returning fallback."
            print(msg)
            log_event(msg)
            return ''
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2
            )
            self._reset_errors()
            content = response.choices[0].message.content
            content = content if content is not None else ''
            # Save to memory
            self.memory.save_answer(prompt, content)
            return content
        except Exception as e:
            msg = f"[ChatGPTDataFetcher] OpenAI API error: {e}"
            print(msg)
            log_event(msg)
            self._record_error()
            return ''

    def get_soccer_nhl_matchups(self, sport: str, date: str) -> List[Dict[str, Any]]:
        """
        Pull daily soccer/nhl matchups (teams, matchups, start times) using ChatGPT or memory.
        Returns a list of dicts: [{"team_a": ..., "team_b": ..., "start_time": ...}, ...]
        """
        cache_key = f"{sport}_matchups_{date}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = f"List all {sport.upper()} games scheduled for {date}. Include team names, matchups, and start times in JSON."
        result = self._chatgpt_call(prompt)
        try:
            matchups = json.loads(result)
        except Exception:
            matchups = []
        self._save_cache(cache_key, matchups)
        return matchups

    def get_favorite_and_trap(self, sport: str, player_a: str, player_b: str, date: str) -> Dict[str, Any]:
        """
        Ask ChatGPT who is the favorite, underdog, and if there is a trap spot for a given matchup.
        Returns dict: {"favorite": ..., "underdog": ..., "trap": ..., "reason": ...}
        """
        cache_key = f"{sport}_favtrap_{player_a}_{player_b}_{date}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = (
            f"For the {sport.upper()} match {player_a} vs {player_b} on {date}, "
            f"who is the favorite, who is the underdog, and is this a trap match? "
            f"Explain why, and summarize in JSON with keys: favorite, underdog, trap, reason."
        )
        result = self._chatgpt_call(prompt)
        try:
            info = json.loads(result)
        except Exception:
            info = {"favorite": None, "underdog": None, "trap": None, "reason": result}
        self._save_cache(cache_key, info)
        return info

    def get_win_probability(self, sport: str, player_a: str, player_b: str, date: str) -> Dict[str, Any]:
        """
        Ask ChatGPT to estimate win probability for a matchup.
        Returns dict: {"player_a": ..., "player_b": ..., "win_prob_a": float, "win_prob_b": float, "reason": ...}
        """
        cache_key = f"{sport}_winprob_{player_a}_{player_b}_{date}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = (
            f"Estimate the win probability for the {sport.upper()} match {player_a} vs {player_b} on {date}. "
            f"Consider recent form, head-to-head, surface/course, and public sentiment. "
            f"Return JSON: player_a, player_b, win_prob_a, win_prob_b, reason."
        )
        result = self._chatgpt_call(prompt)
        try:
            info = json.loads(result)
        except Exception:
            info = {"player_a": player_a, "player_b": player_b, "win_prob_a": None, "win_prob_b": None, "reason": result}
        self._save_cache(cache_key, info)
        return info

    def get_player_stats(self, sport: str, player: str, date: str) -> Dict[str, Any]:
        """
        Ask ChatGPT for recent stats/context for a player.
        Returns dict: {"player": ..., "stats": ..., "reason": ...}
        """
        cache_key = f"{sport}_stats_{player}_{date}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = (
            f"Give recent stats and context for {player} in {sport.upper()} as of {date}. "
            f"Return JSON: player, stats, reason."
        )
        result = self._chatgpt_call(prompt)
        try:
            info = json.loads(result)
        except Exception:
            info = {"player": player, "stats": None, "reason": result}
        self._save_cache(cache_key, info)
        return info

    def get_ticket_explanation(self, ticket: Dict[str, Any]) -> str:
        """
        Ask ChatGPT to generate a human-readable explanation for a ticket.
        Returns a string explanation.
        """
        cache_key = f"ticket_expl_{hash(json.dumps(ticket, sort_keys=True))}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = (
            f"Explain this sports betting ticket in plain English: {json.dumps(ticket)}"
        )
        result = self._chatgpt_call(prompt)
        self._save_cache(cache_key, result)
        return result

    def get_mlb_slate(self, date: str) -> List[Dict[str, Any]]:
        """
        Pull today's MLB games (home/away teams and start times) using ChatGPT.
        Returns a list of dicts: [{"home_team": ..., "away_team": ..., "start_time": ...}, ...]
        """
        cache_key = f"mlb_slate_{date}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = f"List all MLB games scheduled for {date}. Include home and away teams and start times in JSON."
        result = self._chatgpt_call(prompt)
        try:
            games = json.loads(result)
        except Exception:
            games = []
        self._save_cache(cache_key, games)
        return games

    def get_wnba_slate(self, date: str) -> List[Dict[str, Any]]:
        """
        Pull today's WNBA games (home/away teams and start times) using ChatGPT.
        Returns a list of dicts: [{"home_team": ..., "away_team": ..., "start_time": ...}, ...]
        """
        cache_key = f"wnba_slate_{date}"
        cached = self._load_cache(cache_key)
        if cached:
            return cached
        prompt = (
            f"List all WNBA games scheduled for {date}. "
            f"Only include home and away teams and start times in JSON. "
            f"Do NOT include weather or any irrelevant info."
        )
        result = self._chatgpt_call(prompt)
        try:
            games = json.loads(result)
        except Exception:
            games = []
        self._save_cache(cache_key, games)
        return games 