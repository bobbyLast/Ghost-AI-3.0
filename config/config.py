"""
Configuration settings for Ghost AI.

This module contains configuration settings and constants used throughout the application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# OddsAPI configuration
ODDS_API_KEY = os.getenv('ODDS_API_KEY')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/ghost_ai.log')

# Data directories
DATA_DIR = os.getenv('DATA_DIR', 'data')
ROSTERS_DIR = os.path.join(DATA_DIR, 'rosters')
PROPS_DIR = os.path.join(DATA_DIR, 'player_props')

# API endpoints
ODDS_API_BASE_URL = 'https://api.the-odds-api.com/v4'

# Sports and leagues
MLB_LEAGUE = 'baseball_mlb'
WNBA_LEAGUE = 'basketball_wnba'
