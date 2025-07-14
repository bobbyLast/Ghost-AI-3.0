"""
Centralized logging configuration for Ghost AI.

This module provides a consistent way to configure logging across the entire application.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any
import sys
import os
import time
import threading
from datetime import datetime, timedelta

# Default log format
DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Default log file settings
DEFAULT_MAX_BYTES = 50 * 1024 * 1024  # 50MB (increased from 10MB)
DEFAULT_BACKUP_COUNT = 2  # Reduced from 5

# Environment variable to control logging
LOG_LEVEL_ENV = os.getenv('LOG_LEVEL', 'INFO').upper()
DISABLE_FILE_LOGGING = os.getenv('DISABLE_FILE_LOGGING', 'false').lower() == 'true'
DISABLE_LOGGING = os.getenv('DISABLE_LOGGING', 'false').lower() == 'true'
AUTO_CLEANUP_HOURS = int(os.getenv('AUTO_CLEANUP_HOURS', '24'))  # Auto-delete logs after 24 hours
AUTO_CLEANUP_ENABLED = os.getenv('AUTO_CLEANUP_ENABLED', 'true').lower() == 'true'

# Directories to clean up
CLEANUP_DIRECTORIES = [
    "logs",
    "mlb_props", 
    "wnba_props"
]

# Track deleted log files to prevent recreation
_deleted_log_files = set()
_cleanup_thread = None
_cleanup_running = False


def setup_logging(
    log_dir: str = "logs",
    log_file: str = "ghost_ai.log",
    log_level: int = None,
    console_log: bool = True,
    file_log: bool = True,
    log_format: str = DEFAULT_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        log_dir: Directory to store log files
        log_file: Name of the log file
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG)
        console_log: Whether to log to console
        file_log: Whether to log to file
        log_format: Log message format
        date_format: Date format for log messages
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
    """
    # Check if logging is completely disabled
    if DISABLE_LOGGING:
        logging.getLogger().disabled = True
        return
    
    # Use environment variable log level if not specified
    if log_level is None:
        log_level = getattr(logging, LOG_LEVEL_ENV, logging.INFO)
    
    # Respect environment variable for file logging
    if DISABLE_FILE_LOGGING:
        file_log = False
    
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Check if this specific log file was deleted
    log_file_path = log_path / log_file
    if str(log_file_path) in _deleted_log_files:
        file_log = False
        print(f"Log file {log_file} was previously deleted, skipping file logging")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    # Create formatter
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # Add console handler if enabled
    if console_log:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Add file handler if enabled
    if file_log:
        if log_file == 'ghost_ai.log':
            # Overwrite ghost_ai.log on every run
            file_handler = logging.FileHandler(
                log_path / log_file,
                encoding='utf-8',
                mode='w'
            )
        else:
            file_handler = logging.handlers.RotatingFileHandler(
                log_path / log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Start auto-cleanup if enabled
    # if AUTO_CLEANUP_ENABLED:
    #     start_auto_cleanup()


def get_logger(name: str, file_logging: bool = None) -> logging.Logger:
    """
    Get a logger with the given name.
    
    This is a convenience function that ensures consistent logger configuration.
    
    Args:
        name: Name of the logger (usually __name__)
        file_logging: Whether to enable file logging for this logger (None = use global setting)
        
    Returns:
        Configured logger instance
    """
    # Check if logging is completely disabled
    if DISABLE_LOGGING:
        logger = logging.getLogger(name)
        logger.disabled = True
        return logger
    
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist
    if logger.handlers:
        return logger
    
    # Determine if file logging should be enabled
    if file_logging is None:
        file_logging = not DISABLE_FILE_LOGGING
    
    # Check if this specific log file was deleted
    log_file_path = f"logs/{name}.log"
    if log_file_path in _deleted_log_files:
        file_logging = False
        print(f"Log file {name}.log was previously deleted, skipping file logging")
    
    # Get log level from environment
    log_level = getattr(logging, LOG_LEVEL_ENV, logging.INFO)
    
    # Create logs directory if it doesn't exist and file logging is enabled
    if file_logging:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure file handler
        file_handler = logging.FileHandler(
            log_dir / f"{name}.log",
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    
    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Set logger level
    logger.setLevel(logging.DEBUG)
    
    return logger


def cleanup_old_files(directory: str, max_age_hours: int = None, file_pattern: str = "*"):
    """
    Clean up old files in a directory to prevent disk space issues.
    
    Args:
        directory: Directory containing files to clean
        max_age_hours: Maximum age of files in hours (defaults to AUTO_CLEANUP_HOURS)
        file_pattern: File pattern to match (default: all files)
    """
    if max_age_hours is None:
        max_age_hours = AUTO_CLEANUP_HOURS
    
    dir_path = Path(directory)
    if not dir_path.exists():
        return
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    deleted_count = 0
    
    for file_path in dir_path.glob(file_pattern):
        if file_path.is_file():  # Only delete files, not directories
            try:
                file_time = os.path.getmtime(file_path)
                if file_time < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    print(f"Auto-deleted old file: {file_path.name} from {directory}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
    
    if deleted_count > 0:
        print(f"Auto-cleanup: Deleted {deleted_count} old files from {directory}")


def cleanup_old_logs(log_dir: str = "logs", max_age_hours: int = None):
    """
    Clean up old log files to prevent disk space issues.
    
    Args:
        log_dir: Directory containing log files
        max_age_hours: Maximum age of log files in hours (defaults to AUTO_CLEANUP_HOURS)
    """
    cleanup_old_files(log_dir, max_age_hours, "*.log*")


def cleanup_all_directories(max_age_hours: int = None):
    """
    Clean up all configured directories.
    
    Args:
        max_age_hours: Maximum age of files in hours (defaults to AUTO_CLEANUP_HOURS)
    """
    if max_age_hours is None:
        max_age_hours = AUTO_CLEANUP_HOURS
    
    for directory in CLEANUP_DIRECTORIES:
        if directory == "logs":
            cleanup_old_logs(directory, max_age_hours)
        else:
            cleanup_old_files(directory, max_age_hours)


def start_auto_cleanup():
    """Start automatic cleanup in a background thread."""
    global _cleanup_thread, _cleanup_running
    
    if _cleanup_running:
        return
    
    _cleanup_running = True
    
    def cleanup_worker():
        while _cleanup_running:
            try:
                cleanup_all_directories()
                # Sleep for 1 hour before next cleanup
                time.sleep(3600)
            except Exception as e:
                print(f"Error in auto-cleanup: {e}")
                time.sleep(3600)  # Continue trying
    
    _cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    _cleanup_thread.start()
    print(f"Auto-cleanup started: Will delete files older than {AUTO_CLEANUP_HOURS} hours from:")
    for directory in CLEANUP_DIRECTORIES:
        print(f"  - {directory}/")


def stop_auto_cleanup():
    """Stop automatic cleanup."""
    global _cleanup_running
    _cleanup_running = False
    if _cleanup_thread:
        _cleanup_thread.join(timeout=5)
    print("Auto-cleanup stopped")


def mark_log_deleted(log_file_path: str):
    """
    Mark a log file as deleted to prevent it from being recreated.
    
    Args:
        log_file_path: Path to the log file that was deleted
    """
    _deleted_log_files.add(log_file_path)
    print(f"Marked {log_file_path} as deleted - will not be recreated")


def clear_deleted_logs():
    """Clear the list of deleted log files, allowing them to be recreated."""
    global _deleted_log_files
    _deleted_log_files.clear()
    print("Cleared deleted log file list - logs can be recreated")


def get_logger_without_file(name: str) -> logging.Logger:
    """
    Get a logger that only logs to console, not to file.
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger instance with console-only logging
    """
    return get_logger(name, file_logging=False)


def get_deleted_logs() -> set:
    """Get the set of log files that have been marked as deleted."""
    return _deleted_log_files.copy()


def get_cleanup_directories() -> list:
    """Get the list of directories that are cleaned up automatically."""
    return CLEANUP_DIRECTORIES.copy()


def add_cleanup_directory(directory: str):
    """Add a directory to the auto-cleanup list."""
    if directory not in CLEANUP_DIRECTORIES:
        CLEANUP_DIRECTORIES.append(directory)
        print(f"Added {directory} to auto-cleanup list")


def remove_cleanup_directory(directory: str):
    """Remove a directory from the auto-cleanup list."""
    if directory in CLEANUP_DIRECTORIES:
        CLEANUP_DIRECTORIES.remove(directory)
        print(f"Removed {directory} from auto-cleanup list")
