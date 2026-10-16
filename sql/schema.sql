-- ====================================================================
-- IPL TIME-SERIES ANALYTICS WAREHOUSE SCHEMA (2008–2024)
-- Star Schema Architecture optimized for Analytics, Power BI & SQL BI
-- ====================================================================

DROP TABLE IF EXISTS fact_innings_summary;
DROP TABLE IF EXISTS fact_matches;
DROP TABLE IF EXISTS dim_teams;
DROP TABLE IF EXISTS dim_venues;
DROP TABLE IF EXISTS dim_seasons;

-- --------------------------------------------------------------------
-- 1. DIMENSION: SEASONS
-- --------------------------------------------------------------------
CREATE TABLE dim_seasons (
    season_year INTEGER PRIMARY KEY,
    era TEXT NOT NULL,                         -- 'Pre-2016' or 'Post-2016'
    total_matches INTEGER NOT NULL,
    impact_player_active INTEGER DEFAULT 0     -- 1 for 2023+
);

-- --------------------------------------------------------------------
-- 2. DIMENSION: TEAMS
-- --------------------------------------------------------------------
CREATE TABLE dim_teams (
    team_code TEXT PRIMARY KEY,
    team_name TEXT NOT NULL,
    active_status TEXT DEFAULT 'Active'
);

-- --------------------------------------------------------------------
-- 3. DIMENSION: VENUES
-- --------------------------------------------------------------------
CREATE TABLE dim_venues (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT UNIQUE NOT NULL,
    city TEXT NOT NULL,
    chase_bias_category TEXT NOT NULL          -- 'High Chase Bias', 'Neutral', 'Defend Friendly'
);

-- --------------------------------------------------------------------
-- 4. FACT: MATCHES
-- --------------------------------------------------------------------
CREATE TABLE fact_matches (
    match_id INTEGER PRIMARY KEY,
    season INTEGER NOT NULL,
    match_date DATE NOT NULL,
    venue_name TEXT NOT NULL,
    city TEXT NOT NULL,
    match_type TEXT NOT NULL,                  -- 'Day' or 'Night'
    bat_first_team TEXT NOT NULL,
    field_first_team TEXT NOT NULL,
    toss_winner TEXT NOT NULL,
    toss_decision TEXT NOT NULL,               -- 'bat' or 'field'
    winner TEXT NOT NULL,
    toss_match_winner INTEGER NOT NULL,        -- 1 if toss winner won match, else 0
    won_batting_second INTEGER NOT NULL,       -- 1 if chasing team won, else 0
    win_by_runs INTEGER DEFAULT 0,
    win_by_wickets INTEGER DEFAULT 0,
    inn1_runs INTEGER NOT NULL,
    inn2_runs INTEGER NOT NULL,
    match_total_runs INTEGER NOT NULL,
    era TEXT NOT NULL,
    FOREIGN KEY (season) REFERENCES dim_seasons(season_year)
);

-- --------------------------------------------------------------------
-- 5. FACT: INNINGS SUMMARY
-- --------------------------------------------------------------------
CREATE TABLE fact_innings_summary (
    innings_id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    innings_num INTEGER NOT NULL,
    batting_team TEXT NOT NULL,
    bowling_team TEXT NOT NULL,
    total_runs INTEGER NOT NULL,
    wickets INTEGER NOT NULL,
    overs REAL NOT NULL,
    run_rate REAL NOT NULL,
    powerplay_runs INTEGER NOT NULL,
    middle_runs INTEGER NOT NULL,
    death_runs INTEGER NOT NULL,
    fours INTEGER NOT NULL,
    sixes INTEGER NOT NULL,
    is_chase INTEGER NOT NULL,
    chase_successful INTEGER DEFAULT 0,
    FOREIGN KEY (match_id) REFERENCES fact_matches(match_id),
    FOREIGN KEY (season) REFERENCES dim_seasons(season_year)
);

-- --------------------------------------------------------------------
-- INDEXES FOR HIGH-PERFORMANCE ANALYTICAL FILTERING
-- --------------------------------------------------------------------
CREATE INDEX idx_matches_season ON fact_matches(season);
CREATE INDEX idx_matches_era ON fact_matches(era);
CREATE INDEX idx_matches_venue ON fact_matches(venue_name);
CREATE INDEX idx_matches_toss_win ON fact_matches(toss_match_winner);
CREATE INDEX idx_innings_match ON fact_innings_summary(match_id);
CREATE INDEX idx_innings_season ON fact_innings_summary(season);
