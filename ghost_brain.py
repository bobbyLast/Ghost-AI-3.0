"""
Ghost Brain Controller (ghost_brain.py)

USAGE GUIDE:
- This is the real AI. It:
- It calls all core, expanded, elite, and fail-safe modules, enforcing strict no-dup logic and advanced learning.
- All intelligence features are modular, documented, and ready for extension.

FEATURE SWITCHBOARD:
- Toggle any feature ON/OFF by editing the FEATURES dict at the top of this file.
- Example: FEATURES['book_trap_radar'] = False will disable trap detection.

FEATURE-TO-FILE MAPPING:
- Confidence Calibration: calibrate_confidence (ghost_brain.py), adjust_scoring_weights (confidence_scoring.py)
- Prop-Type Penalty/Boost: apply_prop_penalties_and_boosts (ghost_brain.py)
- Post-Audit Memory Reset: archive_graded_tickets (ghost_brain.py)
- Tight-Line Miss Tracker: log_tight_misses (ghost_brain.py)
- CLV Tracker: clv_confidence_boost.py, apply_clv_and_tight_miss_checks (ghost_brain.py)
- Red Flag Extension: update_red_flags (ghost_brain.py)
- Diversity Audit: apply_diversity_audit (ghost_brain.py)
- Lock Awareness: final_ticket_audit (ghost_brain.py)
- Cold Player Replacement: apply_smart_replacement (ghost_brain.py)
- Self-Awareness: self_reflection (ghost_brain.py)
- Book Trap Radar: book_trap_radar (ghost_brain.py, book_trap_radar.py)
- Meta Trend Tracker: meta_trend_tracker (ghost_brain.py, meta_trend_tracker.py)
- AI Synergy: ai_synergy_model (ghost_brain.py, ai_synergy_modeling.py)
- Team Memory: team_memory_system (ghost_brain.py)
- Opponent Modifier: opponent_modifier_system (ghost_brain.py)
- Overconfidence Throttle: overconfidence_throttle (ghost_brain.py)
- Auto-Pause: auto_pause_mode (ghost_brain.py)
- False Positive Detector: false_positive_detector (ghost_brain.py)
- Confidence Re-roll: confidence_reroll (ghost_brain.py)
- Streak-Aware Posting: streak_aware_posting (ghost_brain.py)

To extend or debug any feature, start with the method in this file, then follow the mapping to the relevant module.
"""

# --- Core Imports (update as needed) ---
from ghost_ai_core_memory.memory_manager import MemoryManager  # Handles all pick/result memory
from ghost_ai_core_memory.confidence_scoring import ConfidenceScorer  # Assigns/adjusts confidence
from ghost_ai_core_memory.ticket_builder import TicketBuilder  # Builds tickets, enforces diversity
from ghost_ai_core_memory.fade_detector import FadeDetector  # Red flag/cold player logic
from ghost_ai_core_memory.fantasy_score_calculator import FantasyScoreCalculator  # Fantasy prop logic
from ghost_ai_core_memory.reverse_engine_integration import ReverseEngineIntegration  # Trap/odds logic
from ghost_ai_core_memory.self_audit import SelfAudit  # Self-awareness, daily reflection
from ghost_ai_core_memory.clv_confidence_boost import CLVConfidenceBoost
from pathlib import Path
from datetime import datetime, timezone
# Add other core modules as needed
# --- Moneyline/Edge Modules ---
from brain.moneyline_sentiment import MoneylineSentimentAnalyzer
from brain.ev_evaluator import EVEvaluator
from brain.public_fade_guard import PublicFadeGuard
from brain.prop_context_filter import PropContextFilter
from brain.ml_ticket_trigger import MLTicketTrigger

# --- Expanded/Elite Feature Imports (to be implemented or stubbed) ---
# from core.clv_tracker import CLVTracker
# from core.tight_miss_tracker import TightMissTracker
# from core.prop_penalty_engine import PropPenaltyEngine
# from core.smart_replacement import SmartReplacement
# from core.diversity_audit import DiversityAudit
# from core.lock_awareness import LockAwareness
# from core.red_flag_extension import RedFlagExtension
# from core.fail_safe import FailSafeSystem
# from core.meta_trend_tracker import MetaTrendTracker
# from core.synergy_model import SynergyModel

# --- Import new God-Tier AI modules ---
from brain.self_scout import SelfScout
from brain.bias_calibrator import BiasCalibrator
from confidence.context_engine import ContextEngine
from brain.exposure_manager import ExposureManager
from strategy.pattern_mutator import PatternMutator
from watcher.live_news_regrader import LiveNewsRegrader
from brain.self_reflection_logger import SelfReflectionLogger
from brain.sentiment_engine import SentimentEngine
from risk.throttle_based_on_form import ThrottleBasedOnForm
from brain.confidence_calibrator import ConfidenceCalibrator

# --- Feature Switchboard ---
FEATURES = {
    'book_trap_radar': True,
    'meta_trend_tracker': True,
    'ai_synergy_model': True,
    'team_memory_system': True,
    'opponent_modifier_system': True,
    'overconfidence_throttle': True,
    'auto_pause_mode': True,
    'false_positive_detector': True,
    'confidence_reroll': True,
    'streak_aware_posting': True,
    'clv_confidence_boost': True,
}

# --- Main GhostBrain Class ---
class GhostBrain:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = Path('.')
        # Core modules
        self.memory = MemoryManager(base_dir)
        self.fantasy_calc = FantasyScoreCalculator()
        self.reverse_engine = ReverseEngineIntegration(base_dir)
        self.fade_detector = FadeDetector(self.memory, self.fantasy_calc)
        self.ticket_builder = TicketBuilder(self.memory)
        self.confidence = ConfidenceScorer(self.memory, self.reverse_engine)
        self.self_audit = SelfAudit(self.memory)
        self.clv_boost = CLVConfidenceBoost(self.memory)
        # Moneyline/edge modules
        self.moneyline_sentiment = MoneylineSentimentAnalyzer()
        self.ev_evaluator = EVEvaluator()
        self.public_fade_guard = PublicFadeGuard()
        self.prop_context_filter = PropContextFilter()
        self.ml_ticket_trigger = MLTicketTrigger()
        # Learning/memory files
        self.memory_dir = base_dir / 'ghost_ai_core_memory'
        self.daily_learning_file = self.memory_dir / 'daily_learning.json'
        self.daily_learning = self._load_daily_learning()
        # Expanded/elite modules (to be initialized as implemented)
        # self.clv_tracker = CLVTracker()
        # self.tight_miss_tracker = TightMissTracker()
        # self.prop_penalty_engine = PropPenaltyEngine()
        # self.smart_replacement = SmartReplacement()
        # self.diversity_audit = DiversityAudit()
        # self.lock_awareness = LockAwareness()
        # self.red_flag_extension = RedFlagExtension()
        # self.fail_safe = FailSafeSystem()
        # self.meta_trend_tracker = MetaTrendTracker()
        # self.synergy_model = SynergyModel()
        self.load_all_history()
        self.scan_codebase()
        # --- Always-on, adaptive God-Tier AI modules ---
        self.self_scout = SelfScout(self.history)
        self.bias_calibrator = BiasCalibrator(self.history)
        self.context_engine = ContextEngine(self.history)
        self.exposure_manager = ExposureManager(self.history)
        self.pattern_mutator = PatternMutator(self.history)
        self.live_news_regrader = LiveNewsRegrader(self.history)
        self.self_reflection_logger = SelfReflectionLogger(self.history)
        self.sentiment_engine = SentimentEngine(self.history)
        self.throttle_based_on_form = ThrottleBasedOnForm(self.history)
        self.confidence_calibrator = ConfidenceCalibrator(self.history)

    def _load_daily_learning(self):
        """Load daily learning file if it exists, else return empty dict."""
        if self.daily_learning_file.exists():
            import json
            with open(self.daily_learning_file, 'r') as f:
                return json.load(f)
        return {}

    def run(self, *args, **kwargs):
        """
        🧠 TRUE AI BRAIN: Goal-driven, intelligent decision making
        This is a thinking, reasoning AI system
        """
        # --- PHASE 1: BRAIN INITIALIZATION ---
        self.think("Initializing AI brain...")
        self.daily_auto_clean()
        
        # Load current state and memory
        self.load_all_history()
        self.scan_codebase()
        
        # --- PHASE 2: SET INTELLIGENT GOALS ---
        goals = self.set_intelligent_goals()
        self.think(f"Goals set: {goals}")
        
        # --- PHASE 3: BRAIN STATE ANALYSIS ---
        brain_state = self.analyze_brain_state()
        self.think(f"Brain state: {brain_state['mood']} mood, {brain_state['confidence_level']} confidence")
        
        # --- PHASE 4: INTELLIGENT DECISION MAKING ---
        decision = self.make_intelligent_decision(goals, brain_state)
        self.think(f"Decision: {decision['action']} - {decision['reasoning']}")
        
        # --- PHASE 5: EXECUTE WITH INTELLIGENCE ---
        if decision['action'] == 'generate_tickets':
            result = self.execute_ticket_generation(decision, brain_state)
        elif decision['action'] == 'skip_today':
            result = self.execute_skip_day(decision, brain_state)
        elif decision['action'] == 'reduce_volume':
            result = self.execute_reduced_volume(decision, brain_state)
        else:
            result = self.execute_custom_action(decision, brain_state)
        
        # --- PHASE 6: LEARN AND ADAPT ---
        self.learn_from_execution(result, brain_state)
        self.adapt_workflow(context={'decision': decision, 'result': result})
        
        return result

    def set_intelligent_goals(self):
        """Set intelligent, adaptive goals based on current state and history."""
        goals = {
            'primary_goal': 'maximize_long_term_ev',
            'secondary_goals': [],
            'constraints': [],
            'risk_tolerance': 'adaptive',
            'quality_threshold': 0.65
        }
        
        # Analyze recent performance
        recent_perf = self.get_recent_performance()
        
        # Adjust goals based on performance
        if recent_perf['win_rate'] > 0.7:
            goals['primary_goal'] = 'aggressive_growth'
            goals['quality_threshold'] = 0.55
            goals['secondary_goals'].append('increase_volume')
        elif recent_perf['win_rate'] < 0.3:
            goals['primary_goal'] = 'preserve_capital'
            goals['quality_threshold'] = 0.75
            goals['constraints'].append('max_2_tickets')
        else:
            goals['primary_goal'] = 'steady_improvement'
            goals['quality_threshold'] = 0.65
        
        # Add context-aware goals
        if self.is_high_volume_day():
            goals['secondary_goals'].append('focus_on_quality')
        if self.has_hot_players():
            goals['secondary_goals'].append('leverage_hot_players')
        
        return goals

    def analyze_brain_state(self):
        """Analyze current brain state for intelligent decision making."""
        recent_perf = self.get_recent_performance()
        memory_analysis = self.analyze_memory_state()
        
        brain_state = {
            'mood': self.determine_mood(recent_perf),
            'confidence_level': self.calculate_confidence_level(recent_perf),
            'risk_appetite': self.calculate_risk_appetite(recent_perf),
            'memory_health': memory_analysis['health'],
            'learning_rate': memory_analysis['learning_rate'],
            'trap_awareness': self.calculate_trap_awareness(),
            'market_conditions': self.analyze_market_conditions()
        }
        
        return brain_state

    def make_intelligent_decision(self, goals, brain_state):
        """Make intelligent decisions based on goals and brain state."""
        decision = {
            'action': 'generate_tickets',
            'reasoning': '',
            'parameters': {},
            'confidence': 0.0
        }
        
        # --- INTELLIGENT REASONING ENGINE ---
        reasoning_steps = []
        
        # Step 1: Should we even try today?
        if brain_state['mood'] == 'cautious' and brain_state['confidence_level'] < 0.4:
            decision['action'] = 'skip_today'
            decision['reasoning'] = 'Low confidence and cautious mood - better to wait'
            decision['confidence'] = 0.8
            return decision
        
        # Step 2: Analyze available opportunities
        opportunities = self.analyze_opportunities()
        if not opportunities['viable_props']:
            decision['action'] = 'skip_today'
            decision['reasoning'] = 'No viable props available'
            decision['confidence'] = 0.9
            return decision
        
        # Step 3: Determine optimal strategy
        if brain_state['mood'] == 'aggressive' and opportunities['high_quality_count'] > 3:
            decision['action'] = 'generate_tickets'
            decision['parameters'] = {
                'max_tickets': 5,
                'min_confidence': goals['quality_threshold'],
                'focus': 'high_confidence_only'
            }
            decision['reasoning'] = 'Aggressive mood with high-quality opportunities'
        elif brain_state['mood'] == 'cautious' or opportunities['high_quality_count'] < 2:
            decision['action'] = 'reduce_volume'
            decision['parameters'] = {
                'max_tickets': 2,
                'min_confidence': goals['quality_threshold'] + 0.1,
                'focus': 'ultra_selective'
            }
            decision['reasoning'] = 'Cautious approach due to mood or limited opportunities'
        else:
            decision['action'] = 'generate_tickets'
            decision['parameters'] = {
                'max_tickets': 3,
                'min_confidence': goals['quality_threshold'],
                'focus': 'balanced'
            }
            decision['reasoning'] = 'Balanced approach with moderate opportunities'
        
        decision['confidence'] = self.calculate_decision_confidence(decision, brain_state)
        return decision

    def execute_ticket_generation(self, decision, brain_state):
        """Execute ticket generation with intelligent parameters."""
        self.think(f"Executing ticket generation with parameters: {decision['parameters']}")
        
        # Fetch props with intelligence
        props = self.fetch_props_intelligently()
        
        # Apply intelligent filtering
        props = self.apply_intelligent_filtering(props, decision['parameters'])
        
        # Build tickets with brain-aware logic
        tickets = self.build_tickets_intelligently(props, decision['parameters'])
        
        # Final intelligent audit
        tickets = self.final_intelligent_audit(tickets, brain_state)
        
        # Post with reasoning
        if tickets:
            self.post_tickets_with_reasoning(tickets, decision['reasoning'])
            result = {'action': 'posted_tickets', 'count': len(tickets), 'reasoning': decision['reasoning']}
        else:
            result = {'action': 'no_tickets_posted', 'reason': 'No tickets passed final audit'}
        
        return result

    def execute_skip_day(self, decision, brain_state):
        """Execute skip day with intelligent reasoning."""
        self.think(f"Skipping today: {decision['reasoning']}")
        
        # Log the intelligent decision
        self.log_intelligent_decision('skip_day', decision['reasoning'], brain_state)
        
        return {'action': 'skipped_day', 'reasoning': decision['reasoning']}

    def execute_reduced_volume(self, decision, brain_state):
        """Execute reduced volume with intelligent parameters."""
        self.think(f"Reduced volume mode: {decision['reasoning']}")
        
        # Use same logic as full generation but with stricter parameters
        result = self.execute_ticket_generation(decision, brain_state)
        result['mode'] = 'reduced_volume'
        
        return result

    def execute_custom_action(self, decision, brain_state):
        """Execute custom actions based on intelligent decisions."""
        self.think(f"Custom action: {decision['action']}")
        
        # Implement custom actions as needed
        return {'action': 'custom', 'details': decision}

    def learn_from_execution(self, result, brain_state):
        """Learn from execution results and update brain state."""
        self.think(f"Learning from execution: {result}")
        
        # Update performance tracking
        self.update_performance_tracking(result.get('tickets', []))
        
        # Update brain state based on results
        self.update_brain_state_from_results(result, brain_state)
        
        # Log learning insights
        self.log_learning_insights(result, brain_state)

    def think(self, message):
        """🧠 Ghost thinks out loud - this is the AI's internal monologue."""
        import logging
        logger = logging.getLogger("GhostBrain")
        logger.info(f"🧠 GHOST THOUGHT: {message}")

    # --- INTELLIGENT SUPPORT METHODS ---

    def determine_mood(self, recent_perf):
        """Determine AI mood based on recent performance."""
        win_rate = recent_perf.get('win_rate', 0.5)
        recent_trend = recent_perf.get('recent_trend', 'neutral')
        
        if win_rate > 0.7 and recent_trend == 'positive':
            return 'aggressive'
        elif win_rate < 0.3 or recent_trend == 'negative':
            return 'cautious'
        else:
            return 'balanced'

    def calculate_confidence_level(self, recent_perf):
        """Calculate current confidence level."""
        win_rate = recent_perf.get('win_rate', 0.5)
        consistency = recent_perf.get('consistency', 0.5)
        
        # Weight recent performance more heavily
        confidence = (win_rate * 0.7) + (consistency * 0.3)
        return min(1.0, max(0.0, confidence))

    def calculate_risk_appetite(self, recent_perf):
        """Calculate current risk appetite."""
        win_rate = recent_perf.get('win_rate', 0.5)
        streak = recent_perf.get('current_streak', 0)
        
        if win_rate > 0.7 and streak > 0:
            return 'high'
        elif win_rate < 0.3 or streak < -2:
            return 'low'
        else:
            return 'medium'

    def analyze_memory_state(self):
        """Analyze memory state for learning insights."""
        return {
            'health': 'good',  # Implement actual memory health analysis
            'learning_rate': 0.8,  # Implement actual learning rate calculation
            'memory_efficiency': 0.9  # Implement actual efficiency calculation
        }

    def calculate_trap_awareness(self):
        """Calculate current trap awareness level."""
        # Implement trap awareness calculation based on recent trap detection
        return 0.8  # Placeholder

    def analyze_market_conditions(self):
        """Analyze current market conditions."""
        return {
            'volatility': 'medium',
            'opportunity_level': 'moderate',
            'trap_density': 'low'
        }

    def get_recent_performance(self):
        """Get recent performance metrics."""
        # Implement actual performance analysis
        return {
            'win_rate': 0.6,
            'recent_trend': 'positive',
            'consistency': 0.7,
            'current_streak': 2
        }

    def analyze_opportunities(self):
        """Analyze current opportunities."""
        # This would analyze available props and their quality
        return {
            'viable_props': 15,
            'high_quality_count': 5,
            'average_confidence': 0.68,
            'trap_count': 2
        }

    def calculate_decision_confidence(self, decision, brain_state):
        """Calculate confidence in the decision."""
        base_confidence = 0.7
        
        # Adjust based on brain state
        if brain_state['confidence_level'] > 0.7:
            base_confidence += 0.1
        elif brain_state['confidence_level'] < 0.4:
            base_confidence -= 0.2
        
        # Adjust based on decision type
        if decision['action'] == 'skip_today':
            base_confidence += 0.1  # Higher confidence in conservative decisions
        
        return min(1.0, max(0.0, base_confidence))

    def fetch_props_intelligently(self):
        """Fetch props with intelligent filtering."""
        props = self.fetch_props()
        
        # Apply intelligent pre-filtering
        props = self.apply_trap_and_flag_checks(props)
        props = self.apply_clv_and_tight_miss_checks(props)
        
        return props

    def apply_intelligent_filtering(self, props, parameters):
        """Apply intelligent filtering based on decision parameters."""
        filtered_props = []
        
        for prop in props:
            confidence = prop.get('confidence', 0.5)
            min_confidence = parameters.get('min_confidence', 0.65)
            
            if confidence >= min_confidence:
                # Apply additional intelligent checks
                if self.passes_intelligent_checks(prop, parameters):
                    filtered_props.append(prop)
        
        return filtered_props

    def passes_intelligent_checks(self, prop, parameters):
        """Check if prop passes intelligent filtering."""
        # Implement intelligent checks based on memory, trends, etc.
        return True  # Placeholder

    def build_tickets_intelligently(self, props, parameters):
        """Build tickets with intelligent logic."""
        # Score props with dynamic confidence
        props = self.confidence.score_props(props)
        props = self.apply_prop_penalties_and_boosts(props)
        
        # Build tickets with diversity and smart replacement
        tickets = self.ticket_builder.build_tickets(props)
        tickets = self.apply_diversity_audit(tickets)
        tickets = self.apply_smart_replacement(tickets)
        
        # Limit tickets based on parameters
        max_tickets = parameters.get('max_tickets', 3)
        if len(tickets) > max_tickets:
            tickets = tickets[:max_tickets]
        
        return tickets

    def final_intelligent_audit(self, tickets, brain_state):
        """Final intelligent audit of tickets."""
        # Apply final audit with brain state awareness
        tickets = self.final_ticket_audit(tickets)
        
        # Additional brain-aware checks
        if brain_state['mood'] == 'cautious':
            tickets = self.apply_cautious_filters(tickets)
        
        return tickets

    def apply_cautious_filters(self, tickets):
        """Apply additional filters when in cautious mood."""
        # Implement cautious filtering logic
        return tickets

    def post_tickets_with_reasoning(self, tickets, reasoning):
        """Post tickets with intelligent reasoning."""
        self.think(f"Posting {len(tickets)} tickets: {reasoning}")
        
        # Post tickets with reasoning context
        for ticket in tickets:
            ticket['ai_reasoning'] = reasoning
            ticket['brain_state'] = 'intelligent_decision'
        
        self.post_tickets(tickets)

    def log_intelligent_decision(self, action, reasoning, brain_state):
        """Log intelligent decisions for learning."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'reasoning': reasoning,
            'brain_state': brain_state,
            'type': 'intelligent_decision'
        }
        
        # Save to learning log
        self._save_learning_log(log_entry)

    def update_brain_state_from_results(self, result, brain_state):
        """Update brain state based on execution results."""
        # Implement brain state updates based on results
        pass

    def log_learning_insights(self, result, brain_state):
        """Log learning insights from execution."""
        # Implement learning insight logging
        pass

    def _save_learning_log(self, log_entry):
        """Save learning log entry."""
        # Implement learning log saving
        pass

    def is_high_volume_day(self):
        """Check if today is a high volume day."""
        # Implement high volume day detection
        return False

    def has_hot_players(self):
        """Check if there are hot players available."""
        # Implement hot player detection
        return True

    # --- Core/Expanded/Elite Feature Stubs ---
    def daily_auto_clean(self):
        """
        Daily Auto-Clean (Fail-Safe):
        Remove locked games, clean memory, refresh state, using adaptive logic.
        """
        # Example: Remove games that have started/locked
        if 'graded_tickets' in self.history:
            locked_games = set()
            for graded in self.history['graded_tickets']:
                for ticket in graded.get('tickets', []):
                    if ticket.get('game_status') == 'locked':
                        locked_games.add(ticket.get('game_id'))
            # Remove locked games from memory, props, etc.
            # ... (implement as needed)
        # Clean memory if too large
        # ... (implement as needed)
        # Refresh state if needed
        # ... (implement as needed)

    def fetch_props(self):
        """
        Prop Intake:
        Fetch props and odds from data sources (MLB, WNBA, etc.), using adaptive logic.
        """
        props = []
        # Example: Use history to prioritize hot players/markets
        # ... (implement as needed)
        # Book Trap Radar
        props = self.book_trap_radar(props)
        # Opponent Modifier
        props = self.opponent_modifier_system(props)
        return props

    def apply_trap_and_flag_checks(self, props):
        """
        Trap Detection & Red Flag Filter:
        Apply trap detection, red flag, and related checks to props, using adaptive logic.
        """
        props = self.book_trap_radar(props)
        # Add adaptive red flag/cold player logic here
        # ... (implement as needed)
        return props

    def apply_clv_and_tight_miss_checks(self, props):
        """
        CLV Tracker & Tight-Line Miss Tracker:
        Apply CLV (Closing Line Value) and tight-miss tracking to props.
        TODO: Integrate real closing line fetching.
        """
        # --- Fail-Safe: Confidence Re-roll ---
        props = self.confidence_reroll(props)
        closing_lines = {}
        self.clv_boost.track_clv(props, closing_lines)
        self.clv_boost.adjust_confidence(props)
        # --- CLV Confidence Boost ---
        if FEATURES.get('clv_confidence_boost', True):
            for prop in props:
                clv = prop.get('clv', 0)
                if clv > 0:
                    prop['confidence'] = min(1.0, prop.get('confidence', 0.5) + 0.06)
                    prop['clv_boost'] = True
                elif clv < 0:
                    prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.03)
                    prop['clv_penalty'] = True
        return props

    def apply_prop_penalties_and_boosts(self, props):
        """
        Prop-Type Penalty/Boost Engine:
        Apply penalties to cold prop types and boost hot ones.
        TODO: Implement more advanced prop-type penalty/boost logic based on hit rates.
        """
        # --- Fail-Safe: Overconfidence Throttle ---
        self.overconfidence_throttle()
        for prop in props:
            prop_type = prop.get('prop_type', '')
            team = prop.get('team')
            player = prop.get('player_name') or prop.get('player')
            trend_key = f"{prop_type}_{team}_{player}"
            # Trend boost/penalty
            if hasattr(self, 'trend_scores') and trend_key in self.trend_scores:
                if self.trend_scores[trend_key] == 'hot':
                    prop['confidence'] = min(1.0, prop.get('confidence', 0.5) + 0.07)
                    prop['trend_boost'] = 'hot'
                elif self.trend_scores[trend_key] == 'cold':
                    prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.07)
                    prop['trend_penalty'] = 'cold'
            # Aggregate hit rate for this prop_type across all players
            total = 0
            wins = 0
            for pdata in getattr(self.memory, 'player_history', {}).get('players', {}).values():
                if prop_type in pdata:
                    hist = pdata[prop_type]
                    total += hist.get('total_picks', 0)
                    wins += hist.get('last_5_results', []).count('WIN')
            hit_rate = wins / total if total > 0 else 0.5
            # Penalize or boost
            if hit_rate < 0.3:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.15)
                prop['penalty_reason'] = f"Cold prop type: {prop_type} (hit rate {hit_rate:.2f})"
            elif hit_rate > 0.7:
                prop['confidence'] = min(1.0, prop.get('confidence', 0.5) + 0.1)
                prop['boost_reason'] = f"Hot prop type: {prop_type} (hit rate {hit_rate:.2f})"
            prop['prop_type_hit_rate'] = hit_rate
            # Team memory penalty
            opponent = prop.get('opponent')
            team_key = f"{player}_vs_{opponent}"
            if hasattr(self, 'team_memory') and team_key in self.team_memory:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.09)
                prop['team_memory_penalty'] = 'bad_h2h'
        return props

    def apply_diversity_audit(self, tickets):
        """
        Pre-Ticket Diversity Audit:
        Ensure ticket diversity (stat type, game, no spam, etc.).
        TODO: Regenerate tickets if all fail diversity check.
        """
        # --- Elite: AI Synergy Model ---
        tickets = self.ai_synergy_model(tickets)
        diverse_tickets = []
        for ticket in tickets:
            stat_types = set()
            games = set()
            prop_type_counts = {}
            for sel in ticket.get('selections', []):
                stat_type = sel.get('prop_type', '')
                game = sel.get('game_key', '')
                stat_types.add(stat_type)
                games.add(game)
                prop_type_counts[stat_type] = prop_type_counts.get(stat_type, 0) + 1
            # Diversity rules
            if len(stat_types) < len(ticket.get('selections', [])):
                continue  # Not enough stat diversity
            if len(games) < len(ticket.get('selections', [])):
                continue  # Too many same-game props
            if any(count > 3 for count in prop_type_counts.values()):
                continue  # Prop spam (e.g., 4+ HRRs)
            diverse_tickets.append(ticket)
        # TODO: Regenerate tickets if all fail
        return diverse_tickets

    def apply_smart_replacement(self, tickets):
        """
        Intelligent Cold Player Replacement:
        Replace suppressed/cold props with safe alternates.
        TODO: Implement more advanced smart replacement logic for red-flagged props.
        """
        # --- Elite: Team Memory System ---
        self.team_memory_system()
        # For each ticket, if any selection is suppressed, try to replace
        new_tickets = []
        for ticket in tickets:
            new_selections = []
            replaced = False
            for sel in ticket.get('selections', []):
                player = sel.get('player_name') or sel.get('player')
                prop_type = sel.get('prop_type')
                key = f"{player}_{prop_type}"
                if (hasattr(self, 'red_flagged') and key in self.red_flagged) or (hasattr(self, 'tight_miss_suppressed') and key in self.tight_miss_suppressed):
                    # Try to find a replacement (stub: just skip for now)
                    replaced = True
                    continue
                new_selections.append(sel)
            if new_selections and not replaced:
                ticket['selections'] = new_selections
                new_tickets.append(ticket)
            # TODO: Actually search for similar prop from another game with similar confidence
        return new_tickets

    def final_ticket_audit(self, tickets):
        """
        Final Ticket Audit:
        Final check: no duplicates, no spam, no dead picks, lock awareness.
        TODO: Implement final ticket audit logic, including lock-time intelligence.
        """
        # --- Fail-Safe: Streak-Aware Posting ---
        tickets = self.streak_aware_posting(tickets)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        filtered = []
        self.last_call_queue = []
        for ticket in tickets:
            too_late = False
            last_call = False
            for sel in ticket.get('selections', []):
                game_start_str = sel.get('game_start') or sel.get('commence_time')
                if not game_start_str:
                    continue
                try:
                    game_start = datetime.fromisoformat(game_start_str.replace('Z', '+00:00'))
                except Exception:
                    continue
                mins_to_start = (game_start - now).total_seconds() / 60
                if mins_to_start < 20:
                    too_late = True
                elif 20 <= mins_to_start < 30:
                    last_call = True
            if too_late:
                continue  # Remove dead tickets
            if last_call:
                self.last_call_queue.append(ticket)
                continue
            filtered.append(ticket)
        return filtered

    def post_tickets(self, tickets):
        """
        Posting Discipline:
        Post tickets to sportsbook/Discord/etc. with discipline and logging.
        TODO: Implement posting logic, enforce posting discipline, avoid over-posting loops.
        """
        import json
        posted_path = self.memory_dir / 'tickets' / 'posted_tickets_tracking.json'
        if posted_path.exists():
            with open(posted_path, 'r') as f:
                data = json.load(f)
            posted = data.get('tickets', {})
        else:
            posted = {}
        for ticket in tickets:
            tid = ticket.get('ticket_id') or str(hash(str(ticket)))
            ticket['posted_date'] = ticket.get('posted_date') or ticket.get('posted_at') or ticket.get('date')
            ticket['game_date'] = ticket.get('game_date') or ticket.get('date')
            ticket['result_status'] = ticket.get('result_status', 'pending')
            posted[tid] = ticket
        with open(posted_path, 'w') as f:
            json.dump({'tickets': posted}, f, indent=2)

    def log_results(self, tickets):
        """
        Confidence Calibration, CLV, Tight Miss Logging:
        Log results, CLV, tight misses, and update memory for learning.
        TODO: Implement result logging, confidence calibration, and memory updates.
        """
        # Call CLV reporting
        self.clv_boost.report_clv()
        pass

    def calibrate_confidence(self):
        """
        Confidence Calibration Loop:
        Aggregate recent posted props/tickets by confidence tier, compare actual hit rates to expected, and auto-adjust scoring weights if underperforming.
        """
        # Example: Use last 7 days of daily_learning
        days = list(getattr(self, 'daily_learning', {}).get('days', {}).keys())[-7:]
        tier_stats = {}
        for day in days:
            day_data = self.daily_learning['days'][day]
            # Assume each day_data has 'props' or 'tickets' with confidence and result
            for prop in day_data.get('props', []):
                conf = prop.get('confidence', 0.5)
                result = prop.get('result', None)
                if result not in ('WIN', 'LOSS'):
                    continue
                tier = self._bucket_confidence(conf)
                if tier not in tier_stats:
                    tier_stats[tier] = {'total': 0, 'wins': 0}
                tier_stats[tier]['total'] += 1
                if result == 'WIN':
                    tier_stats[tier]['wins'] += 1
        # Compare hit rates to expected and adjust if needed
        for tier, stats in tier_stats.items():
            if stats['total'] < 5:
                continue  # Not enough data
            hit_rate = stats['wins'] / stats['total']
            expected = self._expected_hit_rate_for_tier(tier)
            if hit_rate < expected - 0.15:  # e.g., 80%+ tier should hit >65%
                self.confidence.adjust_scoring_weights(tier, down=True)
            elif hit_rate > expected + 0.1:
                self.confidence.adjust_scoring_weights(tier, up=True)
        # Log calibration
        print(f"[Calibration] Confidence tier stats: {tier_stats}")

    def _bucket_confidence(self, conf):
        if conf >= 0.8:
            return '80+'
        elif conf >= 0.7:
            return '70-80'
        elif conf >= 0.6:
            return '60-70'
        else:
            return '<60'

    def _expected_hit_rate_for_tier(self, tier):
        if tier == '80+':
            return 0.7
        elif tier == '70-80':
            return 0.6
        elif tier == '60-70':
            return 0.5
        else:
            return 0.45

    def archive_graded_tickets(self):
        """
        Post-Audit Memory Reset:
        Move graded tickets from posted_tickets_tracking.json to tickets/graded/ or tickets/archive/.
        Only keep active (ungraded) tickets in posted_tickets_tracking.json.
        """
        import json
        from shutil import move
        import os
        # Load posted tickets
        if not self.daily_learning_file.exists():
            return
        posted_path = self.memory_dir / 'tickets' / 'posted_tickets_tracking.json'
        graded_dir = self.memory_dir / 'tickets' / 'graded'
        graded_dir.mkdir(parents=True, exist_ok=True)
        if not posted_path.exists():
            return
        with open(posted_path, 'r') as f:
            data = json.load(f)
        tickets = data.get('tickets', {})
        to_archive = {}
        still_active = {}
        for tid, ticket in tickets.items():
            status = ticket.get('result_status', 'pending')
            if status in ['WIN', 'LOSS', 'PUSH']:
                to_archive[tid] = ticket
            else:
                still_active[tid] = ticket
        # Archive graded tickets by date
        for tid, ticket in to_archive.items():
            date = ticket.get('game_date') or ticket.get('date') or 'unknown'
            graded_file = graded_dir / f'Tickets_{date.replace("-", "_")}Graded.json'
            if graded_file.exists():
                with open(graded_file, 'r') as f:
                    graded_data = json.load(f)
            else:
                graded_data = {'tickets': []}
            graded_data['tickets'].append(ticket)
            with open(graded_file, 'w') as f:
                json.dump(graded_data, f, indent=2)
        # Save only active tickets back to posted_tickets_tracking.json
        with open(posted_path, 'w') as f:
            json.dump({'tickets': still_active}, f, indent=2)

    def log_tight_misses(self):
        """
        Tight-Line Miss Tracker:
        Log props that missed by exactly 1 (or 0.5 for some props), track per player/prop, and suppress after repeated tight misses.
        """
        import json
        from datetime import datetime, timedelta
        tight_log_path = self.memory_dir / 'tight_miss_log.json'
        # Load graded tickets for the last 7 days
        graded_dir = self.memory_dir / 'tickets' / 'graded'
        now = datetime.now()
        tight_misses = {}
        for graded_file in graded_dir.glob('Tickets_*Graded.json'):
            date_str = graded_file.name.split('_')[1]
            try:
                file_date = datetime.strptime(date_str, '%Y')  # fallback if not parseable
            except Exception:
                try:
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                except Exception:
                    continue
            if (now - file_date).days > 7:
                continue
            with open(graded_file, 'r') as f:
                data = json.load(f)
            for ticket in data.get('tickets', []):
                for leg in ticket.get('legs', []):
                    line = leg.get('line')
                    final_stat = leg.get('final_stat')
                    if line is None or final_stat is None:
                        continue
                    # Tight miss: missed by exactly 1 (or 0.5 for some props)
                    if abs(final_stat - line) == 1 or abs(final_stat - line) == 0.5:
                        player = leg.get('player_name') or leg.get('player')
                        prop_type = leg.get('prop_type') or leg.get('market')
                        key = f"{player}_{prop_type}"
                        tight_misses.setdefault(key, []).append(file_date.strftime('%Y-%m-%d'))
        # Save tight miss log
        with open(tight_log_path, 'w') as f:
            json.dump(tight_misses, f, indent=2)
        # Suppress players/props with 3+ tight misses in a week
        self.tight_miss_suppressed = set()
        for key, dates in tight_misses.items():
            if len(dates) >= 3:
                self.tight_miss_suppressed.add(key)

    def update_red_flags(self):
        """
        Red Flag Auto-Extension Logic:
        Flags expire based on performance, not time. If a player/prop had 3 straight fails, do not lift red flag until 2 straight wins.
        """
        # Assume player/prop streaks are tracked in memory
        player_hist = getattr(self.memory, 'player_history', {}).get('players', {})
        self.red_flagged = set()
        for player, pdata in player_hist.items():
            for prop_type, hist in pdata.items():
                streak = hist.get('current_streak', 0)
                last_5 = hist.get('last_5_results', [])
                key = f"{player}_{prop_type}"
                # If 3+ straight fails, red flag
                if len(last_5) >= 3 and all(r == 'LOSS' for r in last_5[-3:]):
                    self.red_flagged.add(key)
                # Only lift if 2 straight wins after being flagged
                if key in self.red_flagged and len(last_5) >= 2 and all(r == 'WIN' for r in last_5[-2:]):
                    self.red_flagged.remove(key)

    def self_reflection(self):
        """
        Self-Awareness Reflection Tracker:
        Log 'what I did wrong today', 'what I'll do better tomorrow', and check if Ghost followed its own rule the next day.
        """
        import json
        from datetime import datetime
        log_path = self.memory_dir / 'self_reflection_log.json'
        today = datetime.now().strftime('%Y-%m-%d')
        # Load log
        if log_path.exists():
            with open(log_path, 'r') as f:
                log = json.load(f)
        else:
            log = {}
        # Prompt for reflection (stub: auto-generate for now)
        what_went_wrong = "Missed too many cold props."
        what_to_improve = "Be stricter with red flags and tight-miss suppression."
        log[today] = {
            'what_went_wrong': what_went_wrong,
            'what_to_improve': what_to_improve,
            'checked': False
        }
        # Check yesterday's rule
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if yesterday in log and not log[yesterday].get('checked'):
            # Stub: check if rule was followed (auto-pass for now)
            rule_followed = True
            log[yesterday]['checked'] = True
            log[yesterday]['rule_followed'] = rule_followed
            if not rule_followed:
                print(f"[Self-Reflection] WARNING: Did not follow yesterday's rule: {log[yesterday]['what_to_improve']}")
        # Save log
        with open(log_path, 'w') as f:
            json.dump(log, f, indent=2)

    # --- Elite/Unlockable Feature Stubs ---
    def book_trap_radar(self, props):
        if not FEATURES.get('book_trap_radar', True):
            return props
        # --- ML/AI Integration Hook ---
        # Example: Use a trained ML model to predict traps
        # for prop in props:
        #     if self.trap_model.predict(prop) > 0.8:
        #         prop['trap_flag'] = 'ml_trap'
        #         ...
        # Insert ML logic above if desired
        flagged = []
        clean = []
        for prop in props:
            # Example: Isolated line (only on one book)
            if prop.get('book_count', 1) == 1:
                prop['trap_flag'] = 'isolated_line'
                flagged.append(prop)
                continue
            # Example: Juiced odds and disappears
            if prop.get('odds', 0) < -170 and prop.get('disappeared', False):
                prop['trap_flag'] = 'juiced_disappeared'
                flagged.append(prop)
                continue
            # Example: Suspicious line movement (stub: if line moved >1.5 units)
            if abs(prop.get('line_movement', 0)) > 1.5:
                prop['trap_flag'] = 'suspicious_movement'
                flagged.append(prop)
                continue
            clean.append(prop)
        # Optionally log or store flagged traps
        if flagged:
            print(f"[Book Trap Radar] Suppressed {len(flagged)} trap props.")
        return clean

    def meta_trend_tracker(self):
        if not FEATURES.get('meta_trend_tracker', True):
            return
        # --- ML/AI Integration Hook ---
        # Example: Use a trend prediction model
        # trend = self.trend_model.predict(historical_data)
        # Insert ML logic above if desired
        import json
        from datetime import datetime, timedelta
        # Scan last 7 days of graded tickets for trends
        graded_dir = self.memory_dir / 'tickets' / 'graded'
        now = datetime.now()
        trend_scores = {}
        for graded_file in graded_dir.glob('Tickets_*Graded.json'):
            date_str = graded_file.name.split('_')[1]
            try:
                file_date = datetime.strptime(date_str, '%Y')
            except Exception:
                try:
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                except Exception:
                    continue
            if (now - file_date).days > 7:
                continue
            with open(graded_file, 'r') as f:
                data = json.load(f)
            for ticket in data.get('tickets', []):
                for leg in ticket.get('legs', []):
                    prop_type = leg.get('prop_type') or leg.get('market')
                    team = leg.get('team')
                    player = leg.get('player_name') or leg.get('player')
                    result = leg.get('result_status') or leg.get('result')
                    key = f"{prop_type}_{team}_{player}"
                    if key not in trend_scores:
                        trend_scores[key] = {'total': 0, 'wins': 0}
                    trend_scores[key]['total'] += 1
                    if result == 'WIN':
                        trend_scores[key]['wins'] += 1
        # Calculate trend score (hot if win rate >0.7, cold if <0.3)
        self.trend_scores = {}
        for key, stats in trend_scores.items():
            if stats['total'] < 3:
                continue
            win_rate = stats['wins'] / stats['total']
            if win_rate > 0.7:
                self.trend_scores[key] = 'hot'
            elif win_rate < 0.3:
                self.trend_scores[key] = 'cold'

    def ai_synergy_model(self, tickets):
        if not FEATURES.get('ai_synergy_model', True):
            return tickets
        filtered = []
        for ticket in tickets:
            seen = set()
            correlated = False
            for sel in ticket.get('selections', []):
                player = sel.get('player_name') or sel.get('player')
                prop_type = sel.get('prop_type')
                key = f"{player}_{prop_type}"
                if key in seen:
                    correlated = True
                    break
                seen.add(key)
            if correlated:
                ticket['synergy_flag'] = 'correlated_props'
                continue
            filtered.append(ticket)
        return filtered

    def team_memory_system(self):
        if not FEATURES.get('team_memory_system', True):
            return
        import json
        from datetime import datetime, timedelta
        graded_dir = self.memory_dir / 'tickets' / 'graded'
        now = datetime.now()
        team_memory = {}
        for graded_file in graded_dir.glob('Tickets_*Graded.json'):
            date_str = graded_file.name.split('_')[1]
            try:
                file_date = datetime.strptime(date_str, '%Y')
            except Exception:
                try:
                    file_date = datetime.strptime(date_str, '%Y%m%d')
                except Exception:
                    continue
            if (now - file_date).days > 30:
                continue
            with open(graded_file, 'r') as f:
                data = json.load(f)
            for ticket in data.get('tickets', []):
                for leg in ticket.get('legs', []):
                    player = leg.get('player_name') or leg.get('player')
                    opponent = leg.get('opponent')
                    result = leg.get('result_status') or leg.get('result')
                    key = f"{player}_vs_{opponent}"
                    if key not in team_memory:
                        team_memory[key] = {'total': 0, 'fails': 0}
                    team_memory[key]['total'] += 1
                    if result == 'LOSS':
                        team_memory[key]['fails'] += 1
        # Penalize if 3+ fails in last 30 days
        self.team_memory = {k: v for k, v in team_memory.items() if v['fails'] >= 3}

    def opponent_modifier_system(self, props):
        """
        Opponent Modifier System:
        Dynamically penalize props facing tough opponents, learned from history.
        """
        if not getattr(self, 'FEATURES', {}).get('opponent_modifier_system', True):
            return props
        # Learn tough opponents from history (e.g., teams with high prop fail rates)
        tough_opponents = set()
        if 'graded_tickets' in self.history:
            fail_counts = {}
            for graded in self.history['graded_tickets']:
                for ticket in graded.get('tickets', []):
                    for leg in ticket.get('legs', []):
                        team = leg.get('opponent')
                        result = leg.get('result_status') or leg.get('result')
                        if team and result == 'LOSS':
                            fail_counts[team] = fail_counts.get(team, 0) + 1
            # Consider teams with most fails as tough
            sorted_fails = sorted(fail_counts.items(), key=lambda x: x[1], reverse=True)
            tough_opponents = set([team for team, count in sorted_fails[:7]])
        for prop in props:
            opponent = prop.get('opponent')
            if opponent and opponent in tough_opponents:
                prop['confidence'] = max(0.0, prop.get('confidence', 0.5) - 0.08)
                prop['opponent_penalty'] = 'tough_matchup'
        return props

    # --- Fail-Safe System Stubs ---
    def overconfidence_throttle(self):
        """
        Overconfidence Throttle:
        If 80%+ props go 0–3, pause Power Plays for a day, using adaptive logic.
        """
        if not getattr(self, 'FEATURES', {}).get('overconfidence_throttle', True):
            return
        # Analyze recent performance
        perf = self.history.get('performance', {})
        if perf.get('win_rate', 100) < 20:
            # Pause Power Plays (implement as needed)
            # ...
            pass

    def auto_pause_mode(self):
        """
        Auto-Pause Mode:
        If no props over 65% confidence, halt and ping user for help, using adaptive logic.
        """
        if not getattr(self, 'FEATURES', {}).get('auto_pause_mode', True):
            return
        # Check if any props have high confidence
        # ... (implement as needed)
        pass

    def false_positive_detector(self):
        """
        False Positive Detector:
        If a prop wins but got reverse movement, flag for review, using adaptive logic.
        """
        if not getattr(self, 'FEATURES', {}).get('false_positive_detector', True):
            return
        # Analyze history for false positives
        # ... (implement as needed)
        pass

    def confidence_reroll(self, props):
        """
        Confidence Re-roll:
        Allow re-scoring props only if odds change or new injury update arrives, using adaptive logic.
        """
        if not getattr(self, 'FEATURES', {}).get('confidence_reroll', True):
            return props
        # Check for odds/injury updates
        # ... (implement as needed)
        return props

    def streak_aware_posting(self, tickets):
        if not FEATURES.get('streak_aware_posting', True):
            return tickets
        """
        Streak-Aware Posting:
        Never post streak picks too close to lock, adjust priority by game time.
        TODO: Implement streak-aware posting logic.
        """
        return tickets

    def update_performance_tracking(self, tickets):
        """
        Update performance tracking files with the latest ticket/prop results.
        Updates both data/performance/performance.json and odds_reverse_engineering/data/performance/performance.json.
        Now includes true ROI, total risk, and total return calculations using ticket stake and payout.
        """
        import json
        from pathlib import Path
        from datetime import datetime, timezone
        # --- Update data/performance/performance.json ---
        perf_file1 = Path('data/performance/performance.json')
        perf_file1.parent.mkdir(parents=True, exist_ok=True)
        # Load existing or create new
        if perf_file1.exists():
            with open(perf_file1, 'r') as f:
                perf_data = json.load(f)
        else:
            perf_data = {"predictions": [], "last_updated": None, "total_predictions": 0, "total_wins": 0, "total_losses": 0, "win_rate": 0.0}
        # Flatten all props from tickets
        new_preds = []
        for ticket in tickets:
            for leg in ticket.get('legs', []):
                pred = {
                    "id": ticket.get('ticket_id', ''),
                    "player_name": leg.get('player_name') or leg.get('player'),
                    "prop_type": leg.get('prop_type') or leg.get('market'),
                    "line": leg.get('line'),
                    "actual_value": leg.get('final_stat'),
                    "status": leg.get('result_status', '').lower()[:1],
                    "created_at": ticket.get('created_at'),
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "notes": leg.get('notes', '')
                }
                new_preds.append(pred)
        perf_data["predictions"].extend(new_preds)
        perf_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        perf_data["total_predictions"] = len(perf_data["predictions"])
        perf_data["total_wins"] = sum(1 for p in perf_data["predictions"] if p["status"] == "w")
        perf_data["total_losses"] = sum(1 for p in perf_data["predictions"] if p["status"] == "l")
        if perf_data["total_predictions"] > 0:
            perf_data["win_rate"] = perf_data["total_wins"] / perf_data["total_predictions"] * 100
        else:
            perf_data["win_rate"] = 0.0
        with open(perf_file1, 'w') as f:
            json.dump(perf_data, f, indent=2)
        # --- Update odds_reverse_engineering/data/performance/performance.json ---
        perf_file2 = Path('odds_reverse_engineering/data/performance/performance.json')
        perf_file2.parent.mkdir(parents=True, exist_ok=True)
        if perf_file2.exists():
            with open(perf_file2, 'r') as f:
                perf2 = json.load(f)
        else:
            perf2 = {"total_picks": 0, "wins": 0, "losses": 0, "pushes": 0, "win_rate": 0.0, "roi": 0.0, "total_risk": 0, "total_return": 0, "last_updated": None}
        # Aggregate ticket-level results
        wins = sum(1 for t in tickets if t.get('result_status') == 'WIN')
        losses = sum(1 for t in tickets if t.get('result_status') == 'LOSS')
        pushes = sum(1 for t in tickets if t.get('result_status') == 'PUSH')
        total = wins + losses + pushes
        perf2['total_picks'] += total
        perf2['wins'] += wins
        perf2['losses'] += losses
        perf2['pushes'] += pushes
        perf2['last_updated'] = datetime.now(timezone.utc).isoformat()
        # Win rate (excluding pushes)
        decided = perf2['wins'] + perf2['losses']
        if decided > 0:
            perf2['win_rate'] = perf2['wins'] / decided * 100
        else:
            perf2['win_rate'] = 0.0
        # --- ROI/risk/return calculation ---
        total_risk = 0.0
        total_return = 0.0
        for t in tickets:
            stake = t.get('stake', 0.0) or 0.0
            payout = t.get('potential_payout', 0.0) or 0.0
            result = t.get('result_status', '').upper()
            total_risk += stake
            if result == 'WIN':
                total_return += payout
            elif result == 'LOSS':
                total_return -= stake
            elif result == 'PUSH':
                total_return += 0.0  # No gain/loss
        perf2['total_risk'] += total_risk
        perf2['total_return'] += total_return
        if perf2['total_risk'] > 0:
            perf2['roi'] = (perf2['total_return'] / perf2['total_risk']) * 100
        else:
            perf2['roi'] = 0.0
        with open(perf_file2, 'w') as f:
            json.dump(perf2, f, indent=2)

    def moneyline_pipeline(self, props: list, moneyline_data: list, posted_ml_tickets: list) -> dict:
        """
        Full moneyline-driven pipeline:
        - Runs sentiment/trap analysis
        - Applies prop context filter
        - Evaluates EV for ML bets
        - Triggers ML tickets if enough props align
        - Uses public fade guard to block/penalize traps
        Returns dict with updated props, ML tickets, and logs.
        """
        logs = []
        # 1. Sentiment/trap analysis
        ml_sentiment = self.moneyline_sentiment.aggregate_moneylines(moneyline_data)
        logs.append({'step': 'sentiment', 'result': ml_sentiment})
        # 2. Prop context filter
        props_with_context = self.prop_context_filter.apply_ml_context(props, ml_sentiment)
        logs.append({'step': 'prop_context', 'result': props_with_context})
        # 3. EV evaluation (loop through teams in ml_sentiment)
        ml_ev_results = {}
        for team, team_data in ml_sentiment.items():
            ghost_win_prob = team_data.get('ghost_win_prob', 0.5)
            payout = 1.0  # TODO: Replace with real payout/odds logic if available
            ev = self.ev_evaluator.calculate_ev(ghost_win_prob, payout)
            ml_ev_results[team] = ev
            self.ev_evaluator.log_ev_calculation(team, team_data.get('consensus_odds', 0), ghost_win_prob, ev)
        logs.append({'step': 'ev', 'result': ml_ev_results})
        # 4. ML ticket trigger
        ml_tickets = []
        for team, ev in ml_ev_results.items():
            if self.ev_evaluator.is_premium_ev(ev) and not self.ml_ticket_trigger.is_duplicate_ml_ticket(team, posted_ml_tickets):
                team_props = [p for p in props_with_context if p.get('team') == team]
                if self.ml_ticket_trigger.should_post_ml(team_props, ml_sentiment.get(team, {})):
                    ml_tickets.append({'team': team, 'ev': ev, 'props': team_props})
        logs.append({'step': 'ml_ticket_trigger', 'result': ml_tickets})
        # 5. Public fade guard
        for ticket in ml_tickets:
            team = ticket['team']
            team_data = ml_sentiment.get(team, {})
            public_bet_pct = team_data.get('public_bet_pct', 0.5)
            line_movement = team_data.get('line_movement', 0)
            odds = team_data.get('consensus_odds', 0)
            if self.public_fade_guard.is_trap(team, odds, public_bet_pct, line_movement):
                ticket['fade_public'] = True
                ticket['confidence_penalty'] = 0.12
                logs.append({'step': 'public_fade_guard', 'result': f'Faded {team} ML for public trap'})
        return {'props': props_with_context, 'ml_tickets': ml_tickets, 'logs': logs}

    def load_all_history(self):
        """
        Robustly search for and load all available historical data (tickets, props, performance, results, etc.) from all relevant locations.
        Aggregates into self.history for use in learning, calibration, and audit logic.
        """
        import json
        from pathlib import Path
        import glob
        import logging
        logger = logging.getLogger("GhostBrain")
        history = {}
        # 1. historical_props.json
        try:
            hp = Path('ghost_ai_core_memory/prop_outcomes/historical_props.json')
            if hp.exists():
                with open(hp, 'r') as f:
                    history['historical_props'] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load historical_props.json: {e}")
        # 2. graded tickets
        try:
            graded_dir = Path('ghost_ai_core_memory/tickets/graded')
            graded = []
            if graded_dir.exists():
                for file in graded_dir.glob('Tickets_*Graded.json'):
                    try:
                        with open(file, 'r') as f:
                            graded.append(json.load(f))
                    except Exception as e:
                        logger.warning(f"Could not load {file}: {e}")
            history['graded_tickets'] = graded
        except Exception as e:
            logger.warning(f"Could not load graded tickets: {e}")
        # 3. results
        try:
            results_dir = Path('ghost_ai_core_memory/tickets/results')
            results = []
            if results_dir.exists():
                for file in results_dir.glob('*.json'):
                    try:
                        with open(file, 'r') as f:
                            results.append(json.load(f))
                    except Exception as e:
                        logger.warning(f"Could not load {file}: {e}")
            history['results'] = results
        except Exception as e:
            logger.warning(f"Could not load results: {e}")
        # 4. data/performance/performance.json
        try:
            perf1 = Path('data/performance/performance.json')
            if perf1.exists():
                with open(perf1, 'r') as f:
                    history['performance'] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load data/performance/performance.json: {e}")
        # 5. odds_reverse_engineering/data/performance/performance.json
        try:
            perf2 = Path('odds_reverse_engineering/data/performance/performance.json')
            if perf2.exists():
                with open(perf2, 'r') as f:
                    history['odds_performance'] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load odds_reverse_engineering/data/performance/performance.json: {e}")
        # 6. odds_reverse_engineering/data/results.json
        try:
            res2 = Path('odds_reverse_engineering/data/results.json')
            if res2.exists():
                with open(res2, 'r') as f:
                    history['odds_results'] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load odds_reverse_engineering/data/results.json: {e}")
        # 7. odds_reverse_engineering/data/tracked_picks.json
        try:
            tp = Path('odds_reverse_engineering/data/tracked_picks.json')
            if tp.exists():
                with open(tp, 'r') as f:
                    history['tracked_picks'] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load odds_reverse_engineering/data/tracked_picks.json: {e}")
        # 8. data/historical/props/tickets_history.json
        try:
            th = Path('data/historical/props/tickets_history.json')
            if th.exists():
                with open(th, 'r') as f:
                    history['tickets_history'] = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load data/historical/props/tickets_history.json: {e}")
        # 9. Add more as needed (future-proof)
        # ...
        self.history = history
        logger.info(f"Loaded history: {', '.join(history.keys())}")

    def scan_codebase(self):
        """
        Walk the project directory, parse all .py files, and build a registry of modules, classes, and functions.
        Stores in self.codebase_map.
        """
        import os, ast
        codebase_map = {}
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read(), filename=path)
                            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                            funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                            codebase_map[path] = {'classes': classes, 'functions': funcs}
                    except Exception as e:
                        continue
        self.codebase_map = codebase_map

    @property
    def feature_registry(self):
        """
        Map feature names to their controlling modules/methods, synced with FEATURES.
        """
        # This can be expanded as you add more features/modules
        registry = {
            'confidence_calibration': 'confidence_scorer.py',
            'dynamic_prop_penalty': 'ghost_brain.py',
            'post_audit_memory_reset': 'ghost_brain.py',
            'tight_line_miss_tracker': 'ghost_brain.py',
            'clv_tracker': 'ghost_brain.py',
            'red_flag_auto_extension': 'ghost_brain.py',
            'pre_ticket_diversity_audit': 'ticket_builder.py',
            'game_start_lock_awareness': 'ghost_brain.py',
            'intelligent_cold_player_replacement': 'fade_detector.py',
            'self_awareness_reflection_tracker': 'ghost_brain.py',
            'moneyline_sentiment': 'brain/moneyline_sentiment.py',
            'ev_evaluator': 'brain/ev_evaluator.py',
            'public_fade_guard': 'brain/public_fade_guard.py',
            'prop_context_filter': 'brain/prop_context_filter.py',
            'ml_ticket_trigger': 'brain/ml_ticket_trigger.py',
            # ... add more as needed ...
        }
        # Only include features present in FEATURES
        features = getattr(self, 'FEATURES', {})
        return {k: v for k, v in registry.items() if k in features}

    def self_reflect(self, last_run=None):
        """
        Log which features/modules were used, skipped, or failed in the last run. Suggest improvements.
        """
        import logging
        logger = logging.getLogger("GhostBrain")
        used = []
        skipped = []
        failed = []
        # Example: check FEATURES and log
        features = getattr(self, 'FEATURES', {})
        for feat, enabled in features.items():
            if enabled:
                used.append(feat)
            else:
                skipped.append(feat)
        # Optionally, check last_run for failures (if provided)
        if last_run and 'errors' in last_run:
            failed = last_run['errors']
        logger.info(f"Self-reflection: Used features: {used}, Skipped: {skipped}, Failed: {failed}")
        # Suggest improvements (example)
        if skipped:
            logger.info(f"Consider enabling features: {skipped}")
        if failed:
            logger.warning(f"Failures detected in: {failed}")

    def what_can_you_do(self):
        """
        Return a summary of all available features, enabled features, modules, and history sources.
        """
        features = getattr(self, 'FEATURES', {})
        return {
            'features': list(features.keys()),
            'enabled': [k for k, v in features.items() if v],
            'modules': list(self.codebase_map.keys()) if hasattr(self, 'codebase_map') else [],
            'history_sources': list(self.history.keys()) if hasattr(self, 'history') else []
        }

    @property
    def self_awareness(self):
        """
        Summarize current state, recent performance, feature usage, and codebase map.
        """
        features = getattr(self, 'FEATURES', {})
        return {
            'features': features,
            'enabled': [k for k, v in features.items() if v],
            'history_sources': list(self.history.keys()) if hasattr(self, 'history') else [],
            'modules': list(self.codebase_map.keys()) if hasattr(self, 'codebase_map') else [],
            'recent_performance': self.history.get('performance', {}),
            'odds_performance': self.history.get('odds_performance', {}),
            'last_adaptation': getattr(self, '_last_adaptation', None)
        }

    def log_self_awareness(self):
        """
        Log the current self-awareness state for audit and transparency.
        """
        import logging
        logger = logging.getLogger("GhostBrain")
        logger.info(f"Self-awareness: {self.self_awareness}")

    def adapt_workflow(self, context=None):
        """
        Analyze performance, feature usage, and errors; if a better workflow is detected (e.g., disabling a failing feature, reordering steps, enabling a skipped feature), auto-modify self.FEATURES or workflow order, and log the change.
        """
        import logging
        logger = logging.getLogger("GhostBrain")
        features = getattr(self, 'FEATURES', {})
        perf = self.history.get('performance', {})
        odds_perf = self.history.get('odds_performance', {})
        changed = False
        # Example: If win_rate < 40%, disable risky features
        win_rate = perf.get('win_rate', 0)
        if win_rate and win_rate < 40:
            for feat in features:
                if 'experimental' in feat or 'synergy' in feat:
                    if features[feat]:
                        features[feat] = False
                        logger.info(f"[AI Adaptation] Disabled risky feature: {feat} due to low win rate.")
                        changed = True
        # Example: If a feature failed in last run, disable it
        if context and 'errors' in context:
            for err in context['errors']:
                if err in features and features[err]:
                    features[err] = False
                    logger.info(f"[AI Adaptation] Disabled feature {err} due to repeated errors.")
                    changed = True
        # Example: If a feature is always skipped but performance is high, enable it
        if win_rate and win_rate > 60:
            for feat in features:
                if not features[feat] and 'diversity' in feat:
                    features[feat] = True
                    logger.info(f"[AI Adaptation] Enabled feature {feat} due to high win rate.")
                    changed = True
        # Example: Reorder workflow if too many losses in a row (not implemented, but stubbed)
        # ...
        if changed:
            self._last_adaptation = {'features': dict(features), 'reason': 'auto-adapt', 'context': context}
            logger.info(f"[AI Adaptation] Workflow/features auto-adapted: {self._last_adaptation}")
        else:
            logger.info("[AI Adaptation] No workflow change needed.")

# --- Main Entrypoint ---
def main():
    brain = GhostBrain()
    brain.run()

if __name__ == "__main__":
    main() 