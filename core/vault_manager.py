"""
Vault Manager - Placeholder for disabled vault system

This is a placeholder module since the vault system has been disabled
in favor of the new mlb_props/wnba_props system.
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class VaultManager:
    """Placeholder VaultManager class for disabled vault system."""
    
    def __init__(self, vault_path: Path):
        """Initialize the placeholder vault manager."""
        self.vault_path = vault_path
        logger.info(f"VaultManager initialized (DISABLED) with path: {vault_path}")
    
    def __getattr__(self, name):
        """Return a no-op method for any attribute access."""
        logger.debug(f"VaultManager method '{name}' called (DISABLED)")
        return lambda *args, **kwargs: None
    
    def __call__(self, *args, **kwargs):
        """Return a no-op method for any method calls."""
        logger.debug(f"VaultManager called (DISABLED)")
        return None 