#!/usr/bin/env python3
"""
auto_scheduler.py - Ghost AI 3.0 Auto-Scheduler
Automatically runs Ghost AI at scheduled times with full error handling and auto-evolution.
"""

import logging
import json
import time
import schedule
import threading
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Import core systems
sys.path.append(str(Path(__file__).parent.parent))
from core.ghost_ai_orchestrator import create_ghost_ai_orchestrator
from core.auto_evolution import create_auto_evolution
from core.ai_brain import AIBrain

logger = logging.getLogger('auto_scheduler')

class AutoScheduler:
    """Auto-scheduler for Ghost AI (no sleep/wake cycles, always active)."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.orchestrator = create_ghost_ai_orchestrator(base_dir)
        self.auto_evolution = create_auto_evolution(base_dir)
        self.is_running = False
        self.scheduler_thread = None
        self.cycle_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_run_time = None
        self.next_run_time = None
        # Remove schedule config and all sleep/wake times
        self.run_interval_minutes = 10  # Run every 10 minutes by default
        logger.info("⏰ Auto-Scheduler initialized (always active)")
    
    def _load_schedule_config(self) -> Dict:
        """Load schedule configuration."""
        try:
            config_file = self.base_dir / 'config' / 'schedule.json'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                # Default schedule
                default_config = {
                    'enabled': True,
                    'wake_up_time': '05:00',
                    'run_interval_hours': 6,
                    'max_cycles_per_day': 4,
                    'auto_cleanup_time': '02:00',
                    'auto_learning_time': '23:00',
                    'error_retry_delay_minutes': 30,
                    'max_retries': 3
                }
                
                # Save default config
                config_file.parent.mkdir(exist_ok=True)
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
                
        except Exception as e:
            logger.error(f"Failed to load schedule config: {e}")
            return {}
    
    def start_scheduler(self):
        """Start the auto-scheduler."""
        try:
            if self.is_running:
                logger.warning("⚠️ Scheduler is already running")
                return
            
            logger.info("🚀 Starting Auto-Scheduler...")
            
            # Set up schedule
            self._setup_schedule()
            
            # Start scheduler thread
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            logger.info("✅ Auto-Scheduler started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            self._auto_fix_scheduler_error(str(e), traceback.format_exc())
    
    def _setup_schedule(self):
        """Set up the schedule."""
        try:
            # Clear existing schedule
            schedule.clear()
            
            # Main Ghost AI cycle - every 6 hours
            schedule.every(self.schedule_config.get('run_interval_hours', 6)).hours.do(self._run_ghost_ai_cycle)
            
            # Daily wake-up at 5 AM
            schedule.every().day.at(self.schedule_config.get('wake_up_time', '05:00')).do(self._daily_wake_up)
            
            # Auto-cleanup at 2 AM
            schedule.every().day.at(self.schedule_config.get('auto_cleanup_time', '02:00')).do(self._auto_cleanup)
            
            # Auto-learning at 11 PM
            schedule.every().day.at(self.schedule_config.get('auto_learning_time', '23:00')).do(self._auto_learning)
            
            # Auto-config optimization every 12 hours
            schedule.every(12).hours.do(self._auto_optimize_configs)
            
            # Auto-feedback processing every 4 hours
            schedule.every(4).hours.do(self._auto_process_feedback)
            
            logger.info("📅 Schedule configured successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup schedule: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler loop (always active)."""
        try:
            logger.info("🔄 Scheduler loop started (always active)")
            while self.is_running:
                try:
                    # Run Ghost AI cycle
                    self._run_ghost_ai_cycle()
                    # Wait a short interval before next cycle
                    time.sleep(self.run_interval_minutes * 60)
                except Exception as e:
                    logger.error(f"❌ Scheduler loop error: {e}")
                    time.sleep(60)  # Wait before retrying
        except Exception as e:
            logger.error(f"❌ Scheduler thread failed: {e}")
    
    def _run_ghost_ai_cycle(self):
        """Run a complete Ghost AI cycle."""
        try:
            logger.info("🎭 Starting Ghost AI cycle...")
            
            # Check if we should run (respect max cycles per day)
            if not self._should_run_cycle():
                logger.info("⏭️ Skipping cycle due to daily limit")
                return
            
            # Run the cycle
            success = self.orchestrator.start()
            
            if success:
                self.success_count += 1
                logger.info("✅ Ghost AI cycle completed successfully")
            else:
                self.error_count += 1
                logger.error("❌ Ghost AI cycle failed")
                
                # Auto-fix cycle errors
                self._auto_fix_cycle_failure()
            
            self.cycle_count += 1
            self.last_run_time = datetime.now()
            self.next_run_time = self._calculate_next_run_time()
            
            # Save cycle statistics
            self._save_cycle_stats()
            
        except Exception as e:
            logger.error(f"❌ Ghost AI cycle failed: {e}")
            self.error_count += 1
            self._auto_fix_cycle_failure()
    
    def _should_run_cycle(self) -> bool:
        """Check if we should run a cycle based on daily limits."""
        try:
            max_cycles = self.schedule_config.get('max_cycles_per_day', 4)
            
            # Load today's cycle count
            today = datetime.now().strftime('%Y-%m-%d')
            stats_file = self.base_dir / 'data' / 'scheduler_stats.json'
            
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
                
                today_cycles = stats.get(today, {}).get('cycles', 0)
                return today_cycles < max_cycles
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check cycle limits: {e}")
            return True
    
    def _calculate_next_run_time(self) -> datetime:
        """Calculate next run time."""
        try:
            interval_hours = self.schedule_config.get('run_interval_hours', 6)
            return datetime.now() + timedelta(hours=interval_hours)
            
        except Exception as e:
            logger.error(f"Failed to calculate next run time: {e}")
            return datetime.now() + timedelta(hours=6)
    
    def _save_cycle_stats(self):
        """Save cycle statistics."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            stats_file = self.base_dir / 'data' / 'scheduler_stats.json'
            
            stats = {}
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats = json.load(f)
            
            if today not in stats:
                stats[today] = {
                    'cycles': 0,
                    'successes': 0,
                    'errors': 0,
                    'last_run': None
                }
            
            stats[today]['cycles'] += 1
            stats[today]['successes'] = self.success_count
            stats[today]['errors'] = self.error_count
            stats[today]['last_run'] = datetime.now().isoformat()
            
            stats_file.parent.mkdir(exist_ok=True)
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save cycle stats: {e}")
    
    def _daily_wake_up(self):
        """Daily wake-up routine."""
        try:
            logger.info("🌅 Daily wake-up routine started...")
            
            # Auto-cleanup old data
            self._auto_cleanup()
            
            # Auto-optimize configurations
            self._auto_optimize_configs()
            
            # Process feedback
            self._auto_process_feedback()
            
            # Run Ghost AI cycle
            self._run_ghost_ai_cycle()
            
            logger.info("✅ Daily wake-up routine completed")
            
        except Exception as e:
            logger.error(f"❌ Daily wake-up failed: {e}")
            self._auto_fix_wake_up_error(str(e), traceback.format_exc())
    
    def _auto_cleanup(self):
        """Auto-cleanup routine."""
        try:
            logger.info("🧹 Starting auto-cleanup...")
            
            # Clean old tickets
            self._cleanup_old_tickets()
            
            # Clean old data
            self._cleanup_old_data()
            
            # Clean old logs
            self._cleanup_old_logs()
            
            logger.info("✅ Auto-cleanup completed")
            
        except Exception as e:
            logger.error(f"❌ Auto-cleanup failed: {e}")
    
    def _cleanup_old_tickets(self):
        """Clean up old tickets."""
        try:
            tickets_dir = self.base_dir / 'ghost_ai_core_memory' / 'tickets' / 'generated'
            
            if tickets_dir.exists():
                # Keep only last 7 days of tickets
                cutoff_date = datetime.now() - timedelta(days=7)
                
                for ticket_file in tickets_dir.glob('*.json'):
                    if ticket_file.stat().st_mtime < cutoff_date.timestamp():
                        ticket_file.unlink()
                        logger.debug(f"Deleted old ticket: {ticket_file.name}")
                        
        except Exception as e:
            logger.error(f"Failed to cleanup old tickets: {e}")
    
    def _cleanup_old_data(self):
        """Clean up old data files."""
        try:
            data_dir = self.base_dir / 'data'
            
            # Clean historical odds older than 30 days
            historical_dir = data_dir / 'historical_odds'
            if historical_dir.exists():
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for sport_dir in historical_dir.iterdir():
                    if sport_dir.is_dir():
                        for date_dir in sport_dir.iterdir():
                            if date_dir.is_dir():
                                try:
                                    date_str = date_dir.name
                                    dir_date = datetime.strptime(date_str, '%Y-%m-%d')
                                    if dir_date < cutoff_date:
                                        import shutil
                                        shutil.rmtree(date_dir)
                                        logger.debug(f"Deleted old data: {date_dir}")
                                except ValueError:
                                    continue
                                    
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files."""
        try:
            logs_dir = self.base_dir / 'logs'
            
            if logs_dir.exists():
                # Keep only last 14 days of logs
                cutoff_date = datetime.now() - timedelta(days=14)
                
                for log_file in logs_dir.glob('*.log'):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        logger.debug(f"Deleted old log: {log_file.name}")
                        
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    def _auto_learning(self):
        """Auto-learning routine."""
        try:
            logger.info("🧠 Starting auto-learning...")
            
            # Learn from performance data
            performance_file = self.base_dir / 'data' / 'performance' / 'performance.json'
            if performance_file.exists():
                with open(performance_file, 'r') as f:
                    performance_data = json.load(f)
                
                self.auto_evolution.auto_learn_from_data("performance", performance_data)
            
            # Learn from feedback
            feedback_file = self.base_dir / 'data' / 'feedback.json'
            if feedback_file.exists():
                with open(feedback_file, 'r') as f:
                    feedback_data = json.load(f)
                
                self.auto_evolution.auto_learn_from_data("feedback", feedback_data)
            
            # Learn from ticket outcomes
            outcomes_file = self.base_dir / 'ghost_ai_core_memory' / 'prop_outcomes' / 'historical_props.json'
            if outcomes_file.exists():
                with open(outcomes_file, 'r') as f:
                    outcomes_data = json.load(f)
                
                self.auto_evolution.auto_learn_from_data("outcomes", outcomes_data)
            
            logger.info("✅ Auto-learning completed")
            
        except Exception as e:
            logger.error(f"❌ Auto-learning failed: {e}")
    
    def _auto_optimize_configs(self):
        """Auto-optimize configurations."""
        try:
            logger.info("⚙️ Starting auto-config optimization...")
            
            # Optimize strategy config
            self.orchestrator.auto_update_config('strategy')
            
            # Optimize confidence config
            self.orchestrator.auto_update_config('confidence')
            
            # Optimize schedule config
            self._auto_optimize_schedule()
            
            logger.info("✅ Auto-config optimization completed")
            
        except Exception as e:
            logger.error(f"❌ Auto-config optimization failed: {e}")
    
    def _auto_optimize_schedule(self):
        """Auto-optimize schedule based on performance."""
        try:
            # Load performance data
            performance_file = self.base_dir / 'data' / 'performance' / 'performance.json'
            performance_data = {}
            
            if performance_file.exists():
                with open(performance_file, 'r') as f:
                    performance_data = json.load(f)
            
            # Analyze performance and suggest schedule changes
            prompt = f"""
            You are Ghost AI 3.0's schedule optimizer. Analyze this performance data:
            
            Performance Data: {json.dumps(performance_data, indent=2)}
            Current Schedule: {json.dumps(self.schedule_config, indent=2)}
            
            Suggest optimal schedule changes based on performance patterns.
            Return ONLY the updated schedule configuration as JSON.
            """
            
            from core.ghost_teaching_loop import ghost_openai_wrapper
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'schedule_optimization'},
                model='gpt-4',
                max_tokens=1000
            )
            
            # Extract JSON from response
            new_schedule = self._extract_json_from_response(response)
            if new_schedule:
                # Update schedule config
                self.schedule_config.update(new_schedule)
                
                # Save updated config
                config_file = self.base_dir / 'config' / 'schedule.json'
                with open(config_file, 'w') as f:
                    json.dump(self.schedule_config, f, indent=2)
                
                # Re-setup schedule
                self._setup_schedule()
                
                logger.info("✅ Schedule auto-optimized")
            
        except Exception as e:
            logger.error(f"Failed to auto-optimize schedule: {e}")
    
    def _auto_process_feedback(self):
        """Auto-process feedback."""
        try:
            logger.info("📊 Processing feedback...")
            
            analysis = self.orchestrator.auto_process_feedback()
            
            if analysis:
                logger.info("✅ Feedback processed successfully")
            else:
                logger.info("📊 No feedback to process")
                
        except Exception as e:
            logger.error(f"❌ Feedback processing failed: {e}")
    
    def _auto_fix_cycle_failure(self):
        """Auto-fix cycle failures."""
        try:
            logger.info("🔧 Attempting to auto-fix cycle failure...")
            
            # Try to auto-generate fixes
            success = self.auto_evolution.auto_fix_error(
                error_type="cycle_failure",
                error_msg="Ghost AI cycle failed",
                error_details="Main cycle execution failed",
                context="Scheduled cycle execution"
            )
            
            if success:
                logger.info("✅ Cycle failure auto-fixed")
            else:
                logger.error("❌ Cycle failure auto-fix failed")
                
        except Exception as e:
            logger.error(f"❌ Auto-fix attempt failed: {e}")
    
    def _auto_fix_scheduler_error(self, error_msg: str, error_details: str):
        """Auto-fix scheduler errors."""
        try:
            success = self.auto_evolution.auto_fix_error(
                error_type="scheduler_error",
                error_msg=error_msg,
                error_details=error_details,
                context="Scheduler operation"
            )
            
            if success:
                logger.info("✅ Scheduler error auto-fixed")
                # Retry starting scheduler
                self.start_scheduler()
            else:
                logger.error("❌ Scheduler error auto-fix failed")
                
        except Exception as e:
            logger.error(f"❌ Scheduler auto-fix attempt failed: {e}")
    
    def _auto_fix_wake_up_error(self, error_msg: str, error_details: str):
        """Auto-fix wake-up errors."""
        try:
            success = self.auto_evolution.auto_fix_error(
                error_type="wake_up_error",
                error_msg=error_msg,
                error_details=error_details,
                context="Daily wake-up routine"
            )
            
            if success:
                logger.info("✅ Wake-up error auto-fixed")
            else:
                logger.error("❌ Wake-up error auto-fix failed")
                
        except Exception as e:
            logger.error(f"❌ Wake-up auto-fix attempt failed: {e}")
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from OpenAI response."""
        try:
            import re
            
            # Look for JSON blocks
            json_pattern = r'```json\s*\n(.*?)\n```'
            matches = re.findall(json_pattern, response, re.DOTALL)
            
            if matches:
                return json.loads(matches[0])
            
            # Look for JSON without markdown
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract JSON: {e}")
            return None
    
    def get_scheduler_status(self) -> Dict:
        """Get scheduler status."""
        try:
            status = {
                'is_running': self.is_running,
                'cycle_count': self.cycle_count,
                'success_count': self.success_count,
                'error_count': self.error_count,
                'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
                'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
                'schedule_config': self.schedule_config,
                'pending_jobs': len(schedule.jobs)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get scheduler status: {e}")
            return {'error': str(e)}
    
    def stop_scheduler(self):
        """Stop the auto-scheduler."""
        try:
            logger.info("🛑 Stopping Auto-Scheduler...")
            
            self.is_running = False
            
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            logger.info("✅ Auto-Scheduler stopped")
            
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")

def create_auto_scheduler(base_dir: Path) -> AutoScheduler:
    """Create and return an AutoScheduler instance."""
    return AutoScheduler(base_dir) 