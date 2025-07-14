import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from difflib import get_close_matches
from datetime import datetime

class TeacherStudentMemory:
    def __init__(self, memory_path: str = 'data/ghost_confidence/teacher_student_memory.json'):
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory = self._load_memory()

    def _load_memory(self) -> List[Dict]:
        if self.memory_path.exists():
            with open(self.memory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Backward compatibility: upgrade old format
                if data and isinstance(data[0], dict) and 'tags' not in data[0]:
                    for item in data:
                        item.setdefault('tags', {})
                        item.setdefault('date', None)
                        item.setdefault('rating', None)
                return data
        return []

    def _save_memory(self):
        with open(self.memory_path, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2)

    def get_answer(self, prompt: str, min_similarity: float = 0.85) -> Optional[str]:
        prompts = [item['prompt'] for item in self.memory]
        matches = get_close_matches(prompt, prompts, n=1, cutoff=min_similarity)
        if matches:
            for item in self.memory:
                if item['prompt'] == matches[0]:
                    return item['response']
        return None

    def save_answer(self, prompt: str, response: str, tags: Optional[Dict] = None):
        # Prevent dups: update if similar prompt exists, else add new
        prompts = [item['prompt'] for item in self.memory]
        matches = get_close_matches(prompt, prompts, n=1, cutoff=0.85)
        now = datetime.now().strftime('%Y-%m-%d')
        entry = {
            'prompt': prompt,
            'response': response,
            'date': now,
            'tags': tags or {},
            'rating': None
        }
        if matches:
            # Update existing
            for item in self.memory:
                if item['prompt'] == matches[0]:
                    item.update(entry)
                    self._save_memory()
                    return
        else:
            self.memory.append(entry)
            self._save_memory()

    def update_answer(self, prompt: str, response: str, tags: Optional[Dict] = None):
        # Force update (even if not similar)
        for item in self.memory:
            if item['prompt'] == prompt:
                item['response'] = response
                if tags:
                    item['tags'].update(tags)
                item['date'] = datetime.now().strftime('%Y-%m-%d')
                self._save_memory()
                return

    def rate_answer(self, prompt: str, rating: str):
        # rating: 'good', 'bad', 'uncertain'
        for item in self.memory:
            if item['prompt'] == prompt:
                item['rating'] = rating
                self._save_memory()
                return

    def search_by_tag(self, tag_key: str, tag_value: str) -> List[Dict]:
        return [item for item in self.memory if item['tags'].get(tag_key) == tag_value] 