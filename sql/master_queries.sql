-- ====================================================================
-- IPL MASTER ANALYTICAL SQL SUITE (2008–2026)
-- Connect to: data/processed/ipl_master.db
-- 283,000+ Ball-by-Ball Deliveries | 1,193 Matches | Real Player Records
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: ALL-TIME PLAYER OF THE MATCH (POTM) LEADERBOARD
-- Business Insight: Ranks the most impactful match-winners in IPL history.
-- --------------------------------------------------------------------
SELECT 
    player_name,
    potm_awards,
    runs AS career_runs,
    wickets AS career_wickets,
    strike_rate AS career_strike_rate,
    highest_score
FROM dim_players
ORDER BY potm_awards DESC
LIMIT 15;

-- --------------------------------------------------------------------
-- QUERY 2: ALL-TIME ORANGE CAP KINGS (BATTING RUN TOTALS)
-- Business Insight: Identifies the most prolific run-scorers across 18 seasons.
-- --------------------------------------------------------------------
SELECT 
    player_name,
    matches,
    runs AS total_runs,
    average AS batting_average,
    strike_rate,
    fifties,
    hundreds,
    highest_score,
    (fours * 4 + sixes * 6) * 100.0 / NULLIF(runs, 0) AS boundary_run_pct
FROM dim_players
WHERE runs >= 2500
ORDER BY runs DESC
LIMIT 15;

-- --------------------------------------------------------------------
-- QUERY 3: ALL-TIME PURPLE CAP TITANS (BOWLING WICKET TOTALS)
-- Business Insight: Ranks the leading wicket-takers and their economy rates.
-- --------------------------------------------------------------------
SELECT 
    player_name,
    wickets AS total_wickets,
    overs,
    economy AS economy_rate,
    bowling_avg AS bowling_average,
    dots AS dot_balls_bowled,
    ROUND(dots * 100.0 / NULLIF(overs * 6, 0), 2) AS dot_ball_pct
FROM dim_players
WHERE wickets >= 80
ORDER BY wickets DESC
LIMIT 15;

-- --------------------------------------------------------------------
-- QUERY 4: THE HISTORIC TIE & SUPER OVER MATCH ARCHIVE
-- Business Insight: Details every match in IPL history that went to a Super Over!
-- --------------------------------------------------------------------
SELECT 
    date,
    season,
    team1,
    team2,
    venue,
    superover_winner,
    potm AS player_of_match
FROM fact_matches
WHERE match_result = 'Tie / Super Over'
ORDER BY season;

-- --------------------------------------------------------------------
-- QUERY 5: PHASE SCORING EVOLUTION ACROSS ERAS (POWERPLAY VS DEATH)
-- Business Insight: Tracks how scoring rates exploded in Powerplay and Death overs.
-- --------------------------------------------------------------------
SELECT 
    season,
    phase,
    run_rate AS phase_rpo,
    boundary_run_pct,
    dot_ball_pct,
    wickets AS phase_wickets_lost
FROM fact_phase_summary
WHERE season IN (2008, 2012, 2016, 2020, 2023, 2024, 2025)
ORDER BY season, 
    CASE phase 
        WHEN 'Powerplay' THEN 1 
        WHEN 'Middle' THEN 2 
        WHEN 'Death' THEN 3 
    END;

-- --------------------------------------------------------------------
-- QUERY 6: FRANCHISE "EL CLÁSICO" (CSK VS MI HEAD-TO-HEAD)
-- Business Insight: Complete rivalry breakdown of IPL's two 5-time champions.
-- --------------------------------------------------------------------
SELECT 
    season,
    date,
    venue,
    toss_winner,
    toss_decision,
    winner,
    win_outcome,
    potm
FROM fact_matches
WHERE (team1 = 'Chennai Super Kings' AND team2 = 'Mumbai Indians')
   OR (team1 = 'Mumbai Indians' AND team2 = 'Chennai Super Kings')
ORDER BY date DESC;

-- --------------------------------------------------------------------
-- QUERY 7: STADIUM CHASE BIAS & PAR SCORES (MIN 20 MATCHES)
-- Business Insight: Identifies chasing havens vs defend-friendly fortresses.
-- --------------------------------------------------------------------
SELECT 
    venue,
    city,
    COUNT(*) AS matches_hosted,
    ROUND(100.0 * SUM(won_by_chasing) / COUNT(*), 2) AS chase_win_pct,
    ROUND(AVG(inn1_runs), 1) AS avg_first_inn_runs,
    MAX(inn1_runs) AS highest_first_inn_score
FROM fact_matches
WHERE match_result = 'Normal Result'
GROUP BY venue, city
HAVING COUNT(*) >= 20
ORDER BY chase_win_pct DESC;

-- --------------------------------------------------------------------
-- QUERY 8: DEATH OVERS MONSTERS (OVERS 16–20 STRIKE RATES)
-- Business Insight: Identifies the deadliest finishers in tournament history.
-- --------------------------------------------------------------------
SELECT 
    player_name,
    death_runs,
    death_strike_rate,
    runs AS career_runs
FROM dim_players
WHERE death_runs >= 350
ORDER BY death_strike_rate DESC
LIMIT 12;

-- --------------------------------------------------------------------
-- QUERY 9: IPL 2026 CURRENT STANDINGS & NET RUN RATE (NRR)
-- Business Insight: Live standings from the 2026 season.
-- --------------------------------------------------------------------
SELECT 
    position,
    team,
    matches,
    wins,
    defeats,
    points,
    nrr
FROM ipl_2026_points_table
ORDER BY position;

-- --------------------------------------------------------------------
-- QUERY 10: ALL-TIME IPL CHAMPIONS & SEASON ROLL OF HONOR (2008–2026)
-- Business Insight: Details every IPL champion, runner-up, final margin, MVP, Orange/Purple caps.
-- --------------------------------------------------------------------
SELECT 
    season,
    champion,
    runner_up,
    final_venue,
    final_margin,
    player_of_final,
    player_of_tournament_mvp,
    orange_cap_winner,
    orange_cap_runs,
    purple_cap_winner,
    purple_cap_wickets
FROM dim_ipl_champions
ORDER BY season DESC;

-- --------------------------------------------------------------------
-- QUERY 11: FRANCHISE ALL-TIME TROPHY LEADERBOARD & FINALS CONVERSION
-- Business Insight: Franchise trophy ranking with finals win conversion percentage.
-- --------------------------------------------------------------------
SELECT 
    team,
    titles,
    winning_years,
    finals_played,
    win_rate_in_finals
FROM dim_franchise_trophies
ORDER BY titles DESC, finals_played DESC;

-- --------------------------------------------------------------------
-- QUERY 12: ALL 15 HISTORIC SUPER OVERS DEEP DIVE (TIED & SO SCORES)
-- Business Insight: Exact tied scores, super over scores, and hero match-winners.
-- --------------------------------------------------------------------
SELECT 
    date,
    season,
    match,
    venue,
    tied_score,
    super_over_winner,
    super_over_score,
    hero_potm
FROM fact_super_overs
ORDER BY date DESC;

