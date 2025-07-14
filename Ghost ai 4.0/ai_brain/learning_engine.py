import json
import os
from pathlib import Path
from datetime import datetime, timedelta

TICKETS_PATH = Path('data/historical/props/tickets_history.json')
CHATGPT_PATH = Path('data/cache/chatgpt_fetches.json')
LEARNING_PATH = Path('ghost_ai_core_memory/daily_learning.json')

class LearningEngine:
    def __init__(self):
        self.tickets = self._load_json(TICKETS_PATH)
        self.chatgpt = self._load_json(CHATGPT_PATH)
        self.learning = self._load_json(LEARNING_PATH, default={})

    def _load_json(self, path, default=None):
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default if default is not None else []

    def _save_learning(self):
        with open(LEARNING_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.learning, f, indent=2)

    def analyze_win_loss(self, days=7):
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        results = {'total': 0, 'win': 0, 'loss': 0, 'push': 0, 'by_sport': {}}
        for t in self.tickets:
            date = t.get('date', '')
            if date < cutoff:
                continue
            sport = t.get('sport', 'unknown')
            result = t.get('result', '').lower()
            results['total'] += 1
            if sport not in results['by_sport']:
                results['by_sport'][sport] = {'total': 0, 'win': 0, 'loss': 0, 'push': 0}
            results['by_sport'][sport]['total'] += 1
            if result == 'win':
                results['win'] += 1
                results['by_sport'][sport]['win'] += 1
            elif result == 'loss':
                results['loss'] += 1
                results['by_sport'][sport]['loss'] += 1
            elif result == 'push':
                results['push'] += 1
                results['by_sport'][sport]['push'] += 1
        return results

    def chatgpt_hit_rate(self, days=7):
        # Measures how often ChatGPT's favorite/win_prob was correct
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        correct = 0
        total = 0
        for t in self.tickets:
            date = t.get('date', '')
            if date < cutoff or t.get('sport') not in ['tennis', 'golf']:
                continue
            fav = t.get('favorite')
            winner = t.get('winner')
            if fav and winner:
                total += 1
                if fav == winner:
                    correct += 1
        return {'total': total, 'correct': correct, 'hit_rate': correct/total if total else None}

    def trap_detection_accuracy(self, days=7):
        # Measures how often trap/narrative tags matched actual upsets
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        trap_called = 0
        trap_correct = 0
        for t in self.tickets:
            date = t.get('date', '')
            if date < cutoff or t.get('sport') not in ['tennis', 'golf']:
                continue
            if t.get('trap'):
                trap_called += 1
                if t.get('result', '').lower() == 'loss' and t.get('favorite') == t.get('winner'):
                    trap_correct += 1
        return {'trap_called': trap_called, 'trap_correct': trap_correct, 'accuracy': trap_correct/trap_called if trap_called else None}

    def chatgpt_cost_per_ticket(self, days=7):
        # Estimate OpenAI cost per ticket (assume $0.002 per 1K tokens, ~500 tokens per call)
        cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        calls = [c for c in self.chatgpt if datetime.fromtimestamp(c.get('ts', 0)).strftime('%Y-%m-%d') >= cutoff]
        tickets = [t for t in self.tickets if t.get('date', '') >= cutoff]
        cost = len(calls) * 0.001  # $0.001 per call (estimate)
        return {'calls': len(calls), 'tickets': len(tickets), 'cost': cost, 'cost_per_ticket': cost/len(tickets) if tickets else None}

    def generate_learning_summary(self, days=7):
        win_loss = self.analyze_win_loss(days)
        hit_rate = self.chatgpt_hit_rate(days)
        trap_acc = self.trap_detection_accuracy(days)
        cost = self.chatgpt_cost_per_ticket(days)
        summary = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'days': days,
            'win_loss': win_loss,
            'chatgpt_hit_rate': hit_rate,
            'trap_detection_accuracy': trap_acc,
            'chatgpt_cost': cost
        }
        self.learning[summary['date']] = summary
        self._save_learning()
        return summary

    def get_recent_learning(self, n=7):
        # Return last n learning summaries
        keys = sorted(self.learning.keys(), reverse=True)
        return [self.learning[k] for k in keys[:n]] 