"""
Configuration mappings for the GHOST-PP Intake System.
"""

# Sport key mappings for OddsAPI
SPORT_KEY_MAP = {
    # Major US Sports
    "mlb": "baseball_mlb",
    "nba": "basketball_nba",
    "nfl": "americanfootball_nfl",
    "nhl": "icehockey_nhl",
    "ncaaf": "americanfootball_ncaaf",
    "ncaab": "basketball_ncaab",
    "wnba": "basketball_wnba",
    
    # Soccer
    "epl": "soccer_epl",
    "la_liga": "soccer_spain_la_liga",
    "serie_a": "soccer_italy_serie_a",
    "bundesliga": "soccer_germany_bundesliga",
    "ligue_1": "soccer_france_ligue_one",
    "mls": "soccer_usa_mls",
    "champions_league": "soccer_uefa_champs_league",
    "europa_league": "soccer_uefa_europa_league",
    
    # Other Sports
    "tennis": "tennis_atp",
    "golf": "golf_pga",
    "mma": "mma_mixed_martial_arts",
    "boxing": "boxing_boxing",
    "f1": "motorsports_formula_1",
    "nascar": "motorsports_nascar_cup",
    "afl": "aussierules_afl",
    "cfl": "americanfootball_cfl",
    "nrl": "rugbyleague_nrl"
}

# Prop type mappings for OddsAPI - Comprehensive list of all player props
PROP_TYPE_MAP = {
    # ====== BASEBALL (MLB) ======
    # Batter Props
    "hits": "batter_hits",
    "total_bases": "batter_total_bases",
    "home_runs": "batter_home_runs",
    "rbi": "batter_rbis",
    "runs_scored": "batter_runs_scored",
    "hits_runs_rbi": "batter_hits_runs_rbis",
    "singles": "batter_singles",
    "doubles": "batter_doubles",
    "triples": "batter_triples",
    "walks": "batter_walks",
    "strikeouts": "batter_strikeouts",
    "stolen_bases": "batter_stolen_bases",
    "first_home_run": "batter_first_home_run",
    
    # Pitcher Props
    "pitcher_strikeouts": "pitcher_strikeouts",
    "pitcher_win": "pitcher_record_a_win",
    "hits_allowed": "pitcher_hits_allowed",
    "pitcher_walks": "pitcher_walks",
    "earned_runs": "pitcher_earned_runs",
    "outs_recorded": "pitcher_outs",
    
    # ====== BASKETBALL (NBA, NCAAB, WNBA) ======
    "points": "player_points",
    "points_q1": "player_points_q1",
    "rebounds": "player_rebounds",
    "rebounds_q1": "player_rebounds_q1",
    "assists": "player_assists",
    "assists_q1": "player_assists_q1",
    "threes": "player_threes",
    "blocks": "player_blocks",
    "steals": "player_steals",
    "blocks_steals": "player_blocks_steals",
    "turnovers": "player_turnovers",
    "points_rebounds_assists": "player_points_rebounds_assists",
    "points_rebounds": "player_points_rebounds",
    "points_assists": "player_points_assists",
    "rebounds_assists": "player_rebounds_assists",
    "field_goals": "player_field_goals",
    "free_throws_made": "player_frees_made",
    "free_throws_attempted": "player_frees_attempts",
    "first_basket": "player_first_basket",
    "first_team_basket": "player_first_team_basket",
    "double_double": "player_double_double",
    "triple_double": "player_triple_double",
    "method_of_first_basket": "player_method_of_first_basket",
    
    # ====== FOOTBALL (NFL, NCAAF) ======
    # Offensive Player Props
    "pass_attempts": "player_pass_attempts",
    "pass_completions": "player_pass_completions",
    "pass_yards": "player_pass_yds",
    "pass_tds": "player_pass_tds",
    "pass_interceptions": "player_pass_interceptions",
    "longest_pass": "player_pass_longest_completion",
    "rush_attempts": "player_rush_attempts",
    "rush_yards": "player_rush_yds",
    "rush_tds": "player_rush_tds",
    "longest_rush": "player_rush_longest",
    "receptions": "player_receptions",
    "receiving_yards": "player_reception_yds",
    "receiving_tds": "player_reception_tds",
    "longest_reception": "player_reception_longest",
    "pass_rush_rec_tds": "player_pass_rush_reception_tds",
    "pass_rush_rec_yds": "player_pass_rush_reception_yds",
    "rush_rec_tds": "player_rush_reception_tds",
    "rush_rec_yds": "player_rush_reception_yds",
    "first_td": "player_1st_td",
    "anytime_td": "player_anytime_td",
    "last_td": "player_last_td",
    
    # Defensive Player Props
    "tackles": "player_solo_tackles",
    "tackles_assists": "player_tackles_assists",
    "sacks": "player_sacks",
    "interceptions": "player_defensive_interceptions",
    
    # Kicking Props
    "field_goals_made": "player_field_goals",
    "xp_made": "player_pats",
    "kicking_points": "player_kicking_points",
    
    # ====== HOCKEY (NHL) ======
    "goals": "player_goals",
    "points": "player_points",
    "assists": "player_assists",
    "power_play_points": "player_power_play_points",
    "shots_on_goal": "player_shots_on_goal",
    "blocked_shots": "player_blocked_shots",
    "saves": "player_total_saves",
    "first_goal": "player_goal_scorer_first",
    "last_goal": "player_goal_scorer_last",
    "anytime_goal": "player_goal_scorer_anytime",
    
    # ====== SOCCER ======
    "scorer_anytime": "player_goal_scorer_anytime",
    "scorer_first": "player_first_goal_scorer",
    "scorer_last": "player_last_goal_scorer",
    "player_card": "player_to_receive_card",
    "player_red_card": "player_to_receive_red_card",
    "shots_on_target": "player_shots_on_target",
    "shots": "player_shots",
    "assists": "player_assists",
    
    # ====== AUSTRALIAN RULES FOOTBALL (AFL) ======
    "disposals": "player_disposals",
    "goals_scored": "player_goals_scored_over",
    "marks": "player_marks_over",
    "tackles": "player_tackles_over",
    "fantasy_points": "player_afl_fantasy_points",
    
    # ====== RUGBY LEAGUE (NRL) ======
    "try_scorer_anytime": "player_try_scorer_anytime",
    "try_scorer_first": "player_try_scorer_first",
    "try_scorer_last": "player_try_scorer_last",
    "tries_scored": "player_try_scorer_over",
    
    # ====== COMMON/UNIVERSAL ======
    "fantasy_points": "player_fantasy_points",
    "player_prop_points": "player_points",
    "player_prop_rebounds": "player_rebounds",
    "player_prop_assists": "player_assists"
}

# Bookmakers to use for odds (prioritized in order)
BOOKMAKERS = [
    "draftkings",    # Good for US markets
    "fanduel",       # Good for US markets
    "pointsbetus",   # Good for US markets
    "betmgm",        # Good for US markets
    "barstool",      # Good for US markets
    "betrivers",     # Good for US markets
    "williamhill",   # Good for international markets
    "bet365",        # Good for international markets
    "pinnacle",      # Good for international markets (sharps)
    "unibet",        # Good for European markets
    "betfair"        # Exchange with good liquidity
]

# Regions to use for odds (prioritized in order)
REGIONS = [
    "us",    # United States
    "uk",     # United Kingdom
    "eu",     # Europe (general)
    "au",     # Australia
    "global"  # Global/International
]

# Odds format (american, decimal, or fractional)
ODDS_FORMAT = "american"

# Maximum number of retries for API calls
MAX_RETRIES = 3

# Timeout for API requests in seconds
REQUEST_TIMEOUT = 30

# Cache TTL in seconds (1 hour)
CACHE_TTL = 3600
