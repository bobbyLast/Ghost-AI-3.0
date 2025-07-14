import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import time

# --- Canonical GhostBrain and subsystems ---
from ghost_ai_core_memory.ghost_brain import GhostBrain
from ai_brain.ticket_generator import TicketGenerator
from ghost_ai_core_memory.poster import Poster

AI_BRAIN_STATE_FILE = 'ghost_ai_core_memory/ai_brain_state.json'

class AIBrain:
    SUPPORTED_ACTIONS = [
        'fetch_props',
        'process_props',
        'generate_tickets',
        'post_tickets',
        'grade_results',
        'cleanup',
        # Advanced/custom actions
        'urgent_action',
        'retrain_model',
        'update_config',
        'run_self_test',
        'analyze_market',
        'react_to_event',
        'auto_patch',
        'run_experiment',
        'fetch_external_advice',
        'summarize_performance',
        'auto_document',
        'monitor_health',
        'escalate_issue',
        'pause_operations',
        'resume_operations',
        # Add more as needed
    ]

    def __init__(self, base_dir: Optional[str] = None):
        self.state = self._load_state()
        self.base_dir = Path(base_dir) if base_dir else Path('.')
        self.ghost_brain = GhostBrain(self.base_dir)
        self.ticket_generator = TicketGenerator(self.base_dir, memory_manager=self.ghost_brain)
        self.poster = Poster(self.ghost_brain)
        self.paused = False

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(AI_BRAIN_STATE_FILE):
            try:
                with open(AI_BRAIN_STATE_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {'actions': [], 'last_action': None, 'plans': [], 'openai_feedback': [], 'self_reflection': [], 'change_log': []}
        return {'actions': [], 'last_action': None, 'plans': [], 'openai_feedback': [], 'self_reflection': [], 'change_log': []}

    def _save_state(self):
        with open(AI_BRAIN_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def log_action(self, action_type: str, details: Optional[Dict[str, Any]] = None, result: Optional[str] = None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'details': details or {},
            'result': result
        }
        self.state['actions'].append(entry)
        self.state['last_action'] = entry
        self._save_state()

    def log_change(self, change: Dict[str, Any]):
        self.state.setdefault('change_log', []).append(change)
        self._save_state()

    def has_done_action(self, action_type: str, unique_id: Optional[str] = None) -> bool:
        today = datetime.now().strftime('%Y-%m-%d')
        for action in self.state['actions']:
            if action['action_type'] == action_type:
                ts = action.get('timestamp', '')
                if today in ts:
                    if unique_id is None or action['details'].get('unique_id') == unique_id:
                        return True
        return False

    def _read_all_docs(self) -> str:
        """Read and concatenate all relevant README and .md files for planning context."""
        doc_files = [
            'README.md',
            'docs/README.md',
            'docs/GHOST_AI_3.0_FIXES.md',
            'docs/MODULAR_ARCHITECTURE.md',
            'docs/HISTORICAL_DATA_SOLUTION.md',
        ]
        # Also include any other .md files in the root
        for file in os.listdir('.'):
            if file.endswith('.md') and file not in doc_files:
                doc_files.append(file)
        docs_content = []
        for file in doc_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    docs_content.append(f"\n---\n# {file}\n" + f.read())
            except Exception:
                continue
        return '\n'.join(docs_content)

    def plan_day_with_openai(self, context: Optional[str] = None) -> List[Dict[str, Any]]:
        import openai
        today = datetime.now().strftime('%Y-%m-%d')
        docs_context = self._read_all_docs()
        full_context = (context or '') + '\n' + docs_context
        prompt = f"Ghost AI Brain daily planning. Today is {today}. Current state: {json.dumps(self.state, indent=2)}. Context: {full_context}. Plan a full, adaptive sequence of actions for the day (all supported actions), skipping steps already done today. Suggest any new actions or improvements. Return a JSON list of actions."
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=900
        )
        plan_text = response.choices[0].message.content
        try:
            plan_json = json.loads(plan_text)
        except Exception:
            plan_json = []
        self.state.setdefault('plans', []).append({'date': today, 'plan': plan_json, 'raw': plan_text})
        self._save_state()
        return plan_json

    def get_next_actions(self) -> List[Dict[str, Any]]:
        today = datetime.now().strftime('%Y-%m-%d')
        # If we already have a plan for today, use it
        todays_plan = None
        for plan in self.state.get('plans', []):
            if plan.get('date') == today:
                todays_plan = plan.get('plan')
                break
        if not todays_plan:
            # Ask OpenAI for a plan if not present
            todays_plan = self.plan_day_with_openai()
        # Allow urgent/reactive actions (e.g., if OpenAI suggests an urgent fix)
        urgent = self.state.get('urgent_action', None)
        actions = []
        if urgent:
            actions.append({'action_type': 'urgent_action', 'details': urgent})
        for action in todays_plan:
            action_type = action.get('action_type')
            details = action.get('details', {})
            if action_type in self.SUPPORTED_ACTIONS and not self.has_done_action(action_type, details.get('unique_id') or details.get('date')):
                actions.append({'action_type': action_type, 'details': details})
        return actions

    def plan_with_openai(self, context: Optional[str] = None) -> str:
        import openai
        docs_context = self._read_all_docs()
        full_context = (context or '') + '\n' + docs_context
        prompt = f"Ghost AI Brain planning. Current state: {json.dumps(self.state, indent=2)}. Context: {full_context}. What should I do next?"
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=400
        )
        feedback = response.choices[0].message.content
        self.state.setdefault('openai_feedback', []).append({'timestamp': datetime.now().isoformat(), 'context': context, 'feedback': feedback})
        self._save_state()
        return feedback

    def self_reflect_with_openai(self, context: Optional[str] = None):
        import openai
        prompt = f"Ghost AI Brain self-reflection. Current state: {json.dumps(self.state, indent=2)}. Context: {context if context else 'None'}. What did I do well? What should I improve? Suggest code, logic, or planning improvements. If you suggest a code/config change, output a JSON object or list with keys: 'type', 'file', 'code', 'reason', 'safe' (true/false), 'mode' (overwrite/append/insert/patch), and optionally 'line'."
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}],
            max_tokens=900
        )
        reflection = response.choices[0].message.content
        self.state.setdefault('self_reflection', []).append({'timestamp': datetime.now().isoformat(), 'context': context, 'reflection': reflection})
        self._save_state()
        # Try to auto-apply safe code/config changes
        self.auto_apply_openai_suggestions(reflection)
        return reflection

    def handle_action(self, action: Dict[str, Any]):
        action_type = action.get('action_type')
        details = action.get('details', {})
        if self.paused and action_type not in ['resume_operations', 'monitor_health', 'escalate_issue']:
            print(f"[AIBrain] Paused. Skipping action: {action_type}")
            return
        if action_type not in self.SUPPORTED_ACTIONS:
            print(f"[AIBrain] Unsupported action: {action_type}")
            return
        # Plan with OpenAI before each action
        plan = self.plan_with_openai(f"About to perform {action_type} with details: {details}")
        print(f"[AIBrain] OpenAI plan for {action_type}: {plan}")
        # Dispatch to handler
        handler = getattr(self, f'_handle_{action_type}', None)
        result = None
        if handler:
            result = handler(details)
        else:
            print(f"[AIBrain] No handler implemented for {action_type}")
        self.log_action(action_type, details, result=result)
        # After each action, self-reflect
        self.self_reflect_with_openai(f"After {action_type} with details: {details}")

    # --- Action Handlers wired to real logic ---
    def _handle_fetch_props(self, details):
        print(f"[AIBrain] Fetching props for {details}")
        self.ghost_brain.think("Props fetched (handled in ticket generation pipeline)")

    def _handle_process_props(self, details):
        print(f"[AIBrain] Processing props for {details}")
        self.ghost_brain.think("Props processed (handled in ticket generation pipeline)")

    def _handle_generate_tickets(self, details):
        print(f"[AIBrain] Generating tickets for {details}")
        num_tickets = details.get('num_tickets', 5)
        tickets = self.ticket_generator.generate_tickets(num_tickets=num_tickets)
        print(f"[AIBrain] Generated {len(tickets)} tickets.")
        self.ghost_brain.think(f"Generated {len(tickets)} tickets.")
        self.state['last_generated_tickets'] = tickets
        self._save_state()
        return {'tickets': tickets}

    def _handle_post_tickets(self, details):
        print(f"[AIBrain] Posting tickets for {details}")
        tickets = details.get('tickets') or self.state.get('last_generated_tickets', [])
        if not tickets:
            print("[AIBrain] No tickets to post.")
            return
        self.poster.post_tickets(tickets)
        print(f"[AIBrain] Posted {len(tickets)} tickets.")
        self.ghost_brain.think(f"Posted {len(tickets)} tickets.")
        return {'posted': len(tickets)}

    def _handle_grade_results(self, details):
        print(f"[AIBrain] Grading results for {details}")
        self.ghost_brain.think("Results graded (stub, implement grading logic)")
        return {'graded': True}

    def _handle_cleanup(self, details):
        print(f"[AIBrain] Cleaning up for {details}")
        self.ghost_brain.cleanup_old_memory()
        try:
            from system.auto_cleanup import cleanup_old_prop_files
            cleanup_old_prop_files()
        except Exception as e:
            print(f"[AIBrain] Cleanup error: {e}")
        self.ghost_brain.think("Cleanup complete.")
        return {'cleanup': 'done'}

    # --- Advanced/custom action handlers ---
    def _handle_urgent_action(self, details):
        print(f"[AIBrain] Handling urgent action: {details}")
        self.ghost_brain.think(f"Urgent action handled: {details}")
        return {'urgent': details}

    def _handle_retrain_model(self, details):
        print(f"[AIBrain] Retraining model: {details}")
        self.ghost_brain.think("Model retraining triggered (stub)")
        return {'retrained': True}

    def _handle_update_config(self, details):
        print(f"[AIBrain] Updating config: {details}")
        self.ghost_brain.think("Config update triggered (stub)")
        return {'config_updated': True}

    def _handle_run_self_test(self, details):
        print(f"[AIBrain] Running self-test: {details}")
        self.ghost_brain.think("Self-test run (stub)")
        return {'self_test': 'done'}

    def _handle_analyze_market(self, details):
        print(f"[AIBrain] Analyzing market: {details}")
        self.ghost_brain.think("Market analysis complete (stub)")
        return {'market_analysis': 'done'}

    def _handle_react_to_event(self, details):
        print(f"[AIBrain] Reacting to event: {details}")
        self.ghost_brain.think(f"Reacted to event: {details}")
        return {'event_reacted': True}

    def _handle_auto_patch(self, details):
        print(f"[AIBrain] Auto-patching code: {details}")
        # Stub: could call auto_apply_openai_suggestions or log intent
        self.ghost_brain.think(f"Auto-patch handled: {details}")
        return {'auto_patch': details}

    def _handle_run_experiment(self, details):
        print(f"[AIBrain] Running experiment: {details}")
        self.ghost_brain.think(f"Experiment run: {details}")
        return {'experiment': details}

    def _handle_fetch_external_advice(self, details):
        print(f"[AIBrain] Fetching external advice: {details}")
        self.ghost_brain.think(f"External advice fetched: {details}")
        return {'external_advice': details}

    def _handle_summarize_performance(self, details):
        print(f"[AIBrain] Summarizing performance: {details}")
        self.ghost_brain.think(f"Performance summary: {details}")
        return {'performance_summary': details}

    def _handle_auto_document(self, details):
        print(f"[AIBrain] Auto-documenting: {details}")
        self.ghost_brain.think(f"Auto-documentation: {details}")
        return {'auto_document': details}

    def _handle_monitor_health(self, details):
        print(f"[AIBrain] Monitoring health: {details}")
        self.ghost_brain.think(f"Health monitored: {details}")
        return {'health': details}

    def _handle_escalate_issue(self, details):
        print(f"[AIBrain] Escalating issue: {details}")
        self.ghost_brain.think(f"Issue escalated: {details}")
        return {'escalated': details}

    def _handle_pause_operations(self, details):
        print(f"[AIBrain] Pausing operations: {details}")
        self.paused = True
        self.ghost_brain.think(f"Operations paused: {details}")
        return {'paused': True}

    def _handle_resume_operations(self, details):
        print(f"[AIBrain] Resuming operations: {details}")
        self.paused = False
        self.ghost_brain.think(f"Operations resumed: {details}")
        return {'resumed': True}

    def analyze_tennis_match(self, match_data: Dict[str, Any]) -> str:
        """Analyze a tennis match using AI"""
        try:
            player1 = match_data.get('player1', 'Unknown')
            player2 = match_data.get('player2', 'Unknown')
            tournament = match_data.get('tournament', 'Unknown')
            surface = match_data.get('surface', 'Unknown')
            
            # Basic analysis based on available data
            analysis = f"🎾 Match Analysis: {player1} vs {player2}\n"
            analysis += f"   Tournament: {tournament}\n"
            analysis += f"   Surface: {surface}\n"
            
            # Analyze H2H data if available
            h2h = match_data.get('h2h')
            if h2h and 'H2H' in h2h and h2h['H2H']:
                h2h_count = len(h2h['H2H'])
                analysis += f"   H2H Meetings: {h2h_count}\n"
                
                # Find recent meetings
                recent_h2h = h2h['H2H'][:3]  # Last 3 meetings
                if recent_h2h:
                    analysis += f"   Recent H2H: "
                    for meeting in recent_h2h:
                        winner = meeting.get('event_winner', 'Unknown')
                        result = meeting.get('event_final_result', 'Unknown')
                        analysis += f"{winner} ({result}), "
                    analysis = analysis.rstrip(', ') + "\n"
            
            # Analyze player stats if available
            p1_stats = match_data.get('player1_stats')
            p2_stats = match_data.get('player2_stats')
            
            if p1_stats or p2_stats:
                analysis += "   Player Analysis:\n"
                
                if p1_stats:
                    analysis += f"   {player1}: "
                    if isinstance(p1_stats, list) and p1_stats:
                        stats = p1_stats[0].get('stats', [])
                        for stat in stats:
                            if 'aces' in stat:
                                analysis += f"Aces: {stat['aces']}, "
                            if 'first_serve_percent' in stat:
                                analysis += f"1st Serve: {stat['first_serve_percent']}%, "
                        analysis = analysis.rstrip(', ') + "\n"
                
                if p2_stats:
                    analysis += f"   {player2}: "
                    if isinstance(p2_stats, list) and p2_stats:
                        stats = p2_stats[0].get('stats', [])
                        for stat in stats:
                            if 'aces' in stat:
                                analysis += f"Aces: {stat['aces']}, "
                            if 'first_serve_percent' in stat:
                                analysis += f"1st Serve: {stat['first_serve_percent']}%, "
                        analysis = analysis.rstrip(', ') + "\n"
            
            # AI prediction based on data
            analysis += "   🤖 AI Prediction: "
            if h2h and 'H2H' in h2h and h2h['H2H']:
                recent_wins = {}
                for meeting in h2h['H2H'][:5]:  # Last 5 meetings
                    winner = meeting.get('event_winner')
                    if winner:
                        recent_wins[winner] = recent_wins.get(winner, 0) + 1
                
                if recent_wins:
                    most_wins = max(recent_wins.items(), key=lambda x: x[1])
                    analysis += f"Based on recent H2H, {most_wins[0]} has advantage ({most_wins[1]} recent wins)\n"
                else:
                    analysis += "Insufficient H2H data for prediction\n"
            else:
                analysis += "No H2H data available\n"
            
            return analysis
            
        except Exception as e:
            return f"Error analyzing match: {str(e)}"

    # --- Self-evolution: auto-apply OpenAI suggestions if safe, with patch/append support ---
    def auto_apply_openai_suggestions(self, reflection: Optional[str] = None):
        import re
        if not reflection:
            return
        # Try to extract JSON or list of JSON objects
        matches = re.findall(r'\{[\s\S]*?\}', reflection)
        suggestions = []
        for m in matches:
            try:
                suggestions.append(json.loads(m))
            except Exception:
                continue
        if not suggestions:
            return
        for suggestion in suggestions:
            if suggestion.get('safe') is True and suggestion.get('type') in ('code', 'config'):
                file_path = suggestion.get('file')
                code = suggestion.get('code')
                reason = suggestion.get('reason', '')
                mode = suggestion.get('mode', 'overwrite')
                line = suggestion.get('line', None)
                change_result = {'timestamp': datetime.now().isoformat(), 'file': file_path, 'reason': reason, 'mode': mode, 'success': False}
                try:
                    if mode == 'overwrite':
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(code)
                    elif mode == 'append':
                        with open(file_path, 'a', encoding='utf-8') as f:
                            f.write('\n' + code)
                    elif mode == 'insert' and line is not None:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        lines.insert(int(line), code + '\n')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.writelines(lines)
                    elif mode == 'patch':
                        # Simple patch: look for a marker or line, replace it
                        marker = suggestion.get('marker')
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if marker and marker in content:
                            content = content.replace(marker, code)
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        else:
                            raise Exception('Marker not found for patch')
                    else:
                        raise Exception('Unknown mode or missing line/marker')
                    change_result['success'] = True
                    print(f"[AIBrain] Successfully applied OpenAI suggestion to {file_path} ({mode})")
                    self.ghost_brain.think(f"Auto-applied OpenAI suggestion to {file_path} ({mode}): {reason}")
                except Exception as e:
                    print(f"[AIBrain] Failed to apply OpenAI suggestion: {e}")
                    change_result['error'] = str(e)
                self.log_change(change_result)
            else:
                print("[AIBrain] OpenAI suggestion not marked safe or not code/config type; not applied.")

    # --- Real-time management loop ---
    def manage_realtime(self, poll_interval: int = 30):
        print("[AIBrain] Starting real-time management loop...")
        while True:
            if self.paused:
                print("[AIBrain] Operations paused. Waiting to resume...")
                time.sleep(poll_interval)
                continue
            actions = self.get_next_actions()
            if not actions:
                print("[AIBrain] No actions to perform. Idling...")
                time.sleep(poll_interval)
                continue
            for action in actions:
                self.handle_action(action)
            # After all actions, check for escalations or urgent/reactive needs
            if self.state.get('urgent_action') or any(a['action_type'] == 'escalate_issue' for a in actions):
                print("[AIBrain] Urgent or escalated issue detected. Prioritizing...")
                continue
            time.sleep(poll_interval) 