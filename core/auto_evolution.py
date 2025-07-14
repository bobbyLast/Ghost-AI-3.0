#!/usr/bin/env python3
"""
auto_evolution.py - Ghost AI 3.0 Auto-Evolution System
Allows the AI to generate code, fix errors, update configs, and evolve independently.
"""

import logging
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast
import re

from ghost_teaching_loop import ghost_openai_wrapper

logger = logging.getLogger('auto_evolution')

class AutoEvolution:
    """Ghost AI Auto-Evolution System - Makes the AI completely self-sufficient."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.evolution_log = []
        self.code_generation_count = 0
        self.error_fixes_count = 0
        self.config_updates_count = 0
        logger.info("🧬 Auto-Evolution System initialized")
    
    def auto_fix_error(self, error_type: str, error_msg: str, error_details: str, context: str = "") -> bool:
        """Automatically fix errors using OpenAI code generation."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's auto-fix system. Fix this error:
            
            Error Type: {error_type}
            Error Message: {error_msg}
            Error Details: {error_details}
            Context: {context}
            
            Generate the complete fixed code. Include:
            1. Import statements
            2. Class/function definitions
            3. Error handling
            4. Proper logging
            
            Return ONLY the complete, working Python code.
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'auto_fix', 'error_type': error_type},
                model='gpt-4',
                max_tokens=2000
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            if code:
                # Save the fix
                fix_file = self._save_auto_fix(error_type, code, context)
                logger.info(f"🔧 Auto-fixed {error_type}: {fix_file}")
                self.error_fixes_count += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-fix failed: {e}")
            return False
    
    def auto_generate_feature(self, feature_request: str, context: Dict = None) -> bool:
        """Automatically generate new features using OpenAI."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's auto-feature generator. Create this feature:
            
            Feature Request: {feature_request}
            Context: {json.dumps(context, indent=2) if context else 'None'}
            
            Generate complete Python code for this feature. Include:
            1. Proper imports
            2. Class/function definitions
            3. Error handling
            4. Logging
            5. Documentation
            
            Make it integrate seamlessly with Ghost AI 3.0.
            Return ONLY the complete, working Python code.
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'auto_feature', 'feature': feature_request},
                model='gpt-4',
                max_tokens=3000
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            if code:
                # Save the feature
                feature_file = self._save_auto_feature(feature_request, code)
                logger.info(f"✨ Auto-generated feature: {feature_file}")
                self.code_generation_count += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-feature generation failed: {e}")
            return False
    
    def auto_update_config(self, config_type: str, current_config: Dict, performance_data: Dict) -> bool:
        """Automatically update configurations based on performance."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's auto-config optimizer. Update this configuration:
            
            Config Type: {config_type}
            Current Config: {json.dumps(current_config, indent=2)}
            Performance Data: {json.dumps(performance_data, indent=2)}
            
            Analyze the performance data and suggest optimal configuration changes.
            Return ONLY the updated configuration as JSON.
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'auto_config', 'config_type': config_type},
                model='gpt-4',
                max_tokens=1000
            )
            
            # Extract JSON from response
            new_config = self._extract_json_from_response(response)
            if new_config:
                # Apply the config update
                self._apply_config_update(config_type, new_config)
                logger.info(f"⚙️ Auto-updated {config_type} config")
                self.config_updates_count += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-config update failed: {e}")
            return False
    
    def auto_process_feedback(self, feedback_data: List[Dict]) -> Dict:
        """Automatically process feedback and generate improvement strategies."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's feedback processor. Analyze this feedback:
            
            Feedback Data: {json.dumps(feedback_data, indent=2)}
            
            Provide:
            1. Performance analysis
            2. Strategy improvements
            3. Configuration changes needed
            4. Learning objectives
            
            Return as JSON with keys: analysis, improvements, config_changes, learning_objectives
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'auto_feedback', 'feedback_count': len(feedback_data)},
                model='gpt-4',
                max_tokens=1500
            )
            
            # Extract JSON from response
            analysis = self._extract_json_from_response(response)
            if analysis:
                # Apply the improvements
                self._apply_feedback_improvements(analysis)
                logger.info(f"📊 Auto-processed {len(feedback_data)} feedback entries")
                return analysis
            
            return {}
            
        except Exception as e:
            logger.error(f"Auto-feedback processing failed: {e}")
            return {}
    
    def auto_optimize_performance(self, performance_metrics: Dict) -> bool:
        """Automatically optimize performance based on metrics."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's performance optimizer. Optimize based on these metrics:
            
            Performance Metrics: {json.dumps(performance_metrics, indent=2)}
            
            Suggest:
            1. Code optimizations
            2. Algorithm improvements
            3. Configuration tweaks
            4. Resource management
            
            Return as JSON with optimization strategies.
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'auto_optimization'},
                model='gpt-4',
                max_tokens=1500
            )
            
            # Extract JSON from response
            optimizations = self._extract_json_from_response(response)
            if optimizations:
                # Apply the optimizations
                self._apply_performance_optimizations(optimizations)
                logger.info("🚀 Auto-optimized performance")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-optimization failed: {e}")
            return False
    
    def auto_learn_from_data(self, data_type: str, data: Any) -> bool:
        """Automatically learn from data and update strategies."""
        try:
            prompt = f"""
            You are Ghost AI 3.0's learning system. Learn from this data:
            
            Data Type: {data_type}
            Data: {json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)}
            
            Extract insights and suggest:
            1. Pattern recognition
            2. Strategy improvements
            3. Risk management updates
            4. Performance optimizations
            
            Return as JSON with learning insights.
            """
            
            response = ghost_openai_wrapper(
                prompt,
                tags={'type': 'auto_learning', 'data_type': data_type},
                model='gpt-4',
                max_tokens=1500
            )
            
            # Extract JSON from response
            insights = self._extract_json_from_response(response)
            if insights:
                # Apply the learning insights
                self._apply_learning_insights(insights)
                logger.info(f"🧠 Auto-learned from {data_type} data")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto-learning failed: {e}")
            return False
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """Extract Python code from OpenAI response."""
        try:
            # Look for code blocks
            code_pattern = r'```python\s*\n(.*?)\n```'
            matches = re.findall(code_pattern, response, re.DOTALL)
            
            if matches:
                return matches[0].strip()
            
            # Look for code without markdown
            lines = response.split('\n')
            code_lines = []
            in_code = False
            
            for line in lines:
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    in_code = True
                elif line.strip().startswith('class ') or line.strip().startswith('def '):
                    in_code = True
                
                if in_code:
                    code_lines.append(line)
                
                if line.strip() == '' and in_code:
                    break
            
            if code_lines:
                return '\n'.join(code_lines).strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract code: {e}")
            return None
    
    def _extract_json_from_response(self, response: str) -> Optional[Dict]:
        """Extract JSON from OpenAI response."""
        try:
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
    
    def _save_auto_fix(self, error_type: str, code: str, context: str) -> str:
        """Save auto-generated fix to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"auto_fix_{error_type}_{timestamp}.py"
            filepath = self.base_dir / 'auto_fixes' / filename
            
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(f"# Auto-fix for {error_type}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Context: {context}\n\n")
                f.write(code)
            
            # Log the evolution
            evolution_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'auto_fix',
                'error_type': error_type,
                'file': str(filepath),
                'context': context
            }
            self.evolution_log.append(evolution_entry)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save auto-fix: {e}")
            return ""
    
    def _save_auto_feature(self, feature_request: str, code: str) -> str:
        """Save auto-generated feature to file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', feature_request)
            filename = f"auto_feature_{safe_name}_{timestamp}.py"
            filepath = self.base_dir / 'auto_features' / filename
            
            filepath.parent.mkdir(exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(f"# Auto-generated feature: {feature_request}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n\n")
                f.write(code)
            
            # Log the evolution
            evolution_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'auto_feature',
                'feature_request': feature_request,
                'file': str(filepath)
            }
            self.evolution_log.append(evolution_entry)
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save auto-feature: {e}")
            return ""
    
    def _apply_config_update(self, config_type: str, new_config: Dict):
        """Apply configuration update."""
        try:
            config_file = self.base_dir / 'config' / f'{config_type}.json'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    current_config = json.load(f)
                
                # Merge with new config
                current_config.update(new_config)
                
                with open(config_file, 'w') as f:
                    json.dump(current_config, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to apply config update: {e}")
    
    def _apply_feedback_improvements(self, analysis: Dict):
        """Apply feedback-based improvements."""
        try:
            # Save analysis to memory
            analysis_file = self.base_dir / 'data' / 'feedback_analysis.json'
            analysis_file.parent.mkdir(exist_ok=True)
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            # Apply strategy improvements if specified
            if 'improvements' in analysis:
                self._apply_strategy_improvements(analysis['improvements'])
            
        except Exception as e:
            logger.error(f"Failed to apply feedback improvements: {e}")
    
    def _apply_performance_optimizations(self, optimizations: Dict):
        """Apply performance optimizations."""
        try:
            # Save optimizations to memory
            optimizations_file = self.base_dir / 'data' / 'performance_optimizations.json'
            optimizations_file.parent.mkdir(exist_ok=True)
            
            with open(optimizations_file, 'w') as f:
                json.dump(optimizations, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to apply performance optimizations: {e}")
    
    def _apply_learning_insights(self, insights: Dict):
        """Apply learning insights."""
        try:
            # Save insights to memory
            insights_file = self.base_dir / 'data' / 'learning_insights.json'
            insights_file.parent.mkdir(exist_ok=True)
            
            with open(insights_file, 'w') as f:
                json.dump(insights, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to apply learning insights: {e}")
    
    def _apply_strategy_improvements(self, improvements: Dict):
        """Apply strategy improvements."""
        try:
            # Update strategy files based on improvements
            strategy_file = self.base_dir / 'config' / 'strategy.json'
            
            if strategy_file.exists():
                with open(strategy_file, 'r') as f:
                    current_strategy = json.load(f)
                
                # Apply improvements
                current_strategy.update(improvements)
                
                with open(strategy_file, 'w') as f:
                    json.dump(current_strategy, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to apply strategy improvements: {e}")
    
    def get_evolution_stats(self) -> Dict:
        """Get evolution statistics."""
        return {
            'code_generation_count': self.code_generation_count,
            'error_fixes_count': self.error_fixes_count,
            'config_updates_count': self.config_updates_count,
            'total_evolutions': len(self.evolution_log),
            'evolution_log': self.evolution_log
        }

def create_auto_evolution(base_dir: Path) -> AutoEvolution:
    """Create and return an AutoEvolution instance."""
    return AutoEvolution(base_dir) 