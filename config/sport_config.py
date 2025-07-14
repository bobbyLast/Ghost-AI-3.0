"""
Sport Configuration

Manages sport-specific configurations including API keys and unlock status.
"""
import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Set, Any

# Configure logging
logger = logging.getLogger('ghost_pp.sport_config')

class SportConfig:
    """Manages sport-specific configurations including API keys and unlock status."""
    
    def __init__(self, config_file: str = "config/sport_config.json"):
        """
        Initialize the sport configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {
            'sports': {},
            'api_keys': {},
            'unlocked_sports': set(),
            'required_roles': {}
        }
        
        # Ensure the config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing config if it exists
        self._load_config()
        
        # Initialize default sports if none exist
        if not self.config['sports']:
            self._initialize_default_sports()
    
    def _load_config(self) -> None:
        """Load the configuration from file."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Convert list of unlocked sports to a set
                    if 'unlocked_sports' in data and isinstance(data['unlocked_sports'], list):
                        data['unlocked_sports'] = set(data['unlocked_sports'])
                    
                    # Ensure all required keys exist
                    for key in ['sports', 'api_keys', 'unlocked_sports', 'required_roles']:
                        if key not in data:
                            data[key] = {}
                    
                    self.config = data
                    
                    # Ensure unlocked_sports is a set
                    if not isinstance(self.config['unlocked_sports'], set):
                        self.config['unlocked_sports'] = set(self.config.get('unlocked_sports', []))
                    
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading sport config: {e}")
            # Reset to defaults on error
            self.config = {
                'sports': {},
                'api_keys': {},
                'unlocked_sports': set(),
                'required_roles': {}
            }
    
    def _save_config(self) -> None:
        """Save the current configuration to file."""
        try:
            # Convert sets to lists for JSON serialization
            save_data = self.config.copy()
            save_data['unlocked_sports'] = list(save_data['unlocked_sports'])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Error saving sport config: {e}")
    
    def _initialize_default_sports(self) -> None:
        """Initialize default sports configuration."""
        self.config['sports'] = {
            'nba': {
                'name': 'NBA Basketball',
                'api_key_env': 'NBA_API_KEY',
                'default_unlocked': True,
                'required_role': 'admin'
            },
            'mlb': {
                'name': 'MLB Baseball',
                'api_key_env': 'MLB_API_KEY',
                'default_unlocked': True,
                'required_role': 'admin'
            },
            'wnba': {
                'name': 'WNBA Basketball',
                'api_key_env': 'WNBA_API_KEY',
                'default_unlocked': True,
                'required_role': 'admin'
            },
            'nfl': {
                'name': 'NFL Football',
                'api_key_env': 'NFL_API_KEY',
                'default_unlocked': False,
                'required_role': 'admin'
            },
            'nhl': {
                'name': 'NHL Hockey',
                'api_key_env': 'NHL_API_KEY',
                'default_unlocked': False,
                'required_role': 'admin'
            },
            'soccer': {
                'name': 'Soccer',
                'api_key_env': 'SOCCER_API_KEY',
                'default_unlocked': False,
                'required_role': 'admin'
            }
        }
        
        # Set default unlocked sports
        for sport_id, sport_data in self.config['sports'].items():
            if sport_data.get('default_unlocked', False):
                self.config['unlocked_sports'].add(sport_id)
        
        self._save_config()
    
    def get_sport(self, sport_id: str) -> Optional[Dict]:
        """
        Get configuration for a specific sport.
        
        Args:
            sport_id: The sport identifier (e.g., 'nba', 'mlb')
            
        Returns:
            Sport configuration dictionary or None if not found
        """
        return self.config['sports'].get(sport_id.lower())
    
    def get_all_sports(self) -> Dict[str, Dict]:
        """
        Get all configured sports.
        
        Returns:
            Dictionary of all sports and their configurations
        """
        return self.config['sports'].copy()
    
    def is_sport_unlocked(self, sport_id: str) -> bool:
        """
        Check if a sport is unlocked.
        
        Args:
            sport_id: The sport identifier
            
        Returns:
            True if the sport is unlocked, False otherwise
        """
        return sport_id.lower() in self.config['unlocked_sports']
    
    def unlock_sport(self, sport_id: str) -> bool:
        """
        Unlock a sport.
        
        Args:
            sport_id: The sport identifier to unlock
            
        Returns:
            True if the sport was unlocked, False if it doesn't exist
        """
        sport_id = sport_id.lower()
        if sport_id not in self.config['sports']:
            return False
            
        self.config['unlocked_sports'].add(sport_id)
        self._save_config()
        return True
    
    def lock_sport(self, sport_id: str) -> bool:
        """
        Lock a sport.
        
        Args:
            sport_id: The sport identifier to lock
            
        Returns:
            True if the sport was locked, False if it doesn't exist
        """
        sport_id = sport_id.lower()
        if sport_id not in self.config['sports']:
            return False
            
        self.config['unlocked_sports'].discard(sport_id)
        self._save_config()
        return True
    
    def get_api_key(self, sport_id: str) -> Optional[str]:
        """
        Get the API key for a sport.
        
        Args:
            sport_id: The sport identifier
            
        Returns:
            The API key if found, None otherwise
        """
        sport_id = sport_id.lower()
        
        # First check environment variables
        sport_config = self.get_sport(sport_id)
        if sport_config and 'api_key_env' in sport_config:
            return os.getenv(sport_config['api_key_env'])
        
        # Then check config file
        return self.config['api_keys'].get(sport_id)
    
    def set_api_key(self, sport_id: str, api_key: str) -> None:
        """
        Set the API key for a sport.
        
        Args:
            sport_id: The sport identifier
            api_key: The API key to set
        """
        sport_id = sport_id.lower()
        self.config['api_keys'][sport_id] = api_key
        self._save_config()
    
    def check_api_key(self, sport_id: str) -> bool:
        """
        Check if a valid API key is configured for a sport.
        
        Args:
            sport_id: The sport identifier
            
        Returns:
            True if a valid API key is configured, False otherwise
        """
        return bool(self.get_api_key(sport_id))
    
    def get_required_role(self, sport_id: str) -> Optional[str]:
        """
        Get the required role to access a sport.
        
        Args:
            sport_id: The sport identifier
            
        Returns:
            The required role name, or None if not restricted
        """
        sport_config = self.get_sport(sport_id)
        if not sport_config:
            return None
            
        return sport_config.get('required_role')
    
    def user_has_access(self, sport_id: str, user_roles: list) -> bool:
        """
        Check if a user has access to a sport based on their roles.
        
        Args:
            sport_id: The sport identifier
            user_roles: List of role names the user has
            
        Returns:
            True if the user has access, False otherwise
        """
        required_role = self.get_required_role(sport_id)
        if not required_role:
            return True
            
        return required_role.lower() in [r.lower() for r in user_roles]

# Global instance
sport_config = SportConfig()
