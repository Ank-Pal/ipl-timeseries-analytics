-- ====================================================================
-- IPL TIME-SERIES ANALYTICS: CORE ANALYTICAL SQL SUITE
-- Advanced Analytical Queries, Window Functions & CTEs
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: THE TOSS PARADOX - PRE-2016 VS POST-2016 ERA COMPARISON
-- Business Insight: Proves why toss conversion rate diluted despite
-- teams overwhelmingly choosing to field first after 2016.
-- --------------------------------------------------------------------
SELECT 
    era,
    COUNT(*) AS total_matches,
    ROUND(100.0 * SUM(CASE WHEN toss_decision = 'field' THEN 1 ELSE 0 END) / COUNT(*), 2) AS field_first_toss_pct,
    ROUND(100.0 * SUM(toss_match_winner) / COUNT(*), 2) AS toss_win_match_win_pct,
    ROUND(100.0 * SUM(won_batting_second) / COUNT(*), 2) AS overall_chase_win_pct,
    ROUND(AVG(match_total_runs), 1) AS avg_match_runs,
    ROUND(AVG(inn1_runs), 1) AS avg_inn1_score
FROM fact_matches
GROUP BY era
ORDER BY era DESC;

-- --------------------------------------------------------------------
-- QUERY 2: ROLLING 3-YEAR CHASING SUCCESS RATE (WINDOW FUNCTIONS)
-- Business Insight: Smooths out single-season volatility to reveal the
-- structural rise of the chase strategy over the tournament's history.
-- --------------------------------------------------------------------
WITH season_chase_stats AS (
    SELECT 
        season,
        COUNT(*) AS season_matches,
        SUM(won_batting_second) AS chases_won,
        ROUND(100.0 * SUM(won_batting_second) / COUNT(*), 2) AS chase_win_pct
    FROM fact_matches
    GROUP BY season
)
SELECT 
    season,
    season_matches,
    chase_win_pct AS annual_chase_win_pct,
    ROUND(AVG(chase_win_pct) OVER (
        ORDER BY season 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_3yr_chase_win_pct,
    ROUND(SUM(chases_won) OVER (
        ORDER BY season
    ) * 100.0 / SUM(season_matches) OVER (
        ORDER BY season
    ), 2) AS cumulative_chase_win_pct
FROM season_chase_stats
ORDER BY season;

-- --------------------------------------------------------------------
-- QUERY 3: VENUE CHASE BIAS INDEX & BATTING PROFILES
-- Business Insight: Ranks stadiums where winning the toss and fielding
-- first creates an outsized tactical edge vs defend-friendly venues.
-- --------------------------------------------------------------------
WITH venue_metrics AS (
    SELECT 
        venue_name,
        city,
        COUNT(*) AS matches_played,
        SUM(won_batting_second) AS chases_won,
        SUM(CASE WHEN toss_decision = 'field' AND toss_match_winner = 1 THEN 1 ELSE 0 END) AS field_toss_wins,
        SUM(CASE WHEN toss_decision = 'field' THEN 1 ELSE 0 END) AS total_field_tosses,
        AVG(inn1_runs) AS avg_first_inn_runs,
        AVG(inn2_runs) AS avg_second_inn_runs
    FROM fact_matches
    GROUP BY venue_name, city
    HAVING COUNT(*) >= 20
)
SELECT 
    venue_name,
    city,
    matches_played,
    ROUND(100.0 * chases_won / matches_played, 2) AS chase_win_pct,
    ROUND(100.0 * field_toss_wins / NULLIF(total_field_tosses, 0), 2) AS field_first_toss_conversion_pct,
    ROUND(avg_first_inn_runs, 1) AS avg_par_score,
    CASE 
        WHEN (100.0 * chases_won / matches_played) >= 55.0 THEN 'High Chase Advantage (Chinnaswamy/Wankhede)'
        WHEN (100.0 * chases_won / matches_played) <= 46.0 THEN 'Defend Friendly (Chepauk/Ekana)'
        ELSE 'Balanced Pitch'
    END AS tactical_classification
FROM venue_metrics
ORDER BY chase_win_pct DESC;

-- --------------------------------------------------------------------
-- QUERY 4: DAY VS NIGHT SPLIT & THE DEW FACTOR
-- Business Insight: Assesses whether night matches suffer higher chase
-- bias due to second-innings dew dampening spin bowling.
-- --------------------------------------------------------------------
SELECT 
    match_type,
    era,
    COUNT(*) AS match_count,
    ROUND(100.0 * SUM(won_batting_second) / COUNT(*), 2) AS chase_win_pct,
    ROUND(100.0 * SUM(toss_match_winner) / COUNT(*), 2) AS toss_win_pct,
    ROUND(AVG(inn1_runs), 1) AS avg_first_innings_score,
    ROUND(AVG(inn2_runs), 1) AS avg_second_innings_score
FROM fact_matches
GROUP BY match_type, era
ORDER BY match_type, era DESC;

-- --------------------------------------------------------------------
-- QUERY 5: SCORING RATE EVOLUTION & 200+ SCORES HYPER-INFLATION
-- Business Insight: Tracks season-by-season run rate acceleration,
-- boundary aggression (% runs from 4s & 6s), and 200+ totals explosion.
-- --------------------------------------------------------------------
WITH innings_features AS (
    SELECT 
        season,
        COUNT(*) AS total_innings,
        AVG(run_rate) AS avg_run_rate,
        SUM(CASE WHEN total_runs >= 200 THEN 1 ELSE 0 END) AS scores_200_plus,
        SUM(fours * 4 + sixes * 6) * 100.0 / SUM(total_runs) AS boundary_run_pct,
        AVG(powerplay_runs) AS avg_powerplay_runs,
        AVG(death_runs) AS avg_death_overs_runs
    FROM fact_innings_summary
    GROUP BY season
)
SELECT 
    season,
    ROUND(avg_run_rate, 2) AS mean_innings_rpo,
    ROUND(boundary_run_pct, 2) AS boundary_run_share_pct,
    scores_200_plus,
    ROUND(100.0 * scores_200_plus / total_innings, 2) AS pct_innings_over_200,
    ROUND(avg_powerplay_runs, 1) AS avg_powerplay_runs,
    ROUND(avg_death_overs_runs, 1) AS avg_death_overs_runs,
    ROUND(avg_run_rate - LAG(avg_run_rate, 1) OVER (ORDER BY season), 2) AS yoy_rpo_growth
FROM innings_features
ORDER BY season;

-- --------------------------------------------------------------------
-- QUERY 6: FRANCHISE CHASE EFFICIENCY VS DEFENSE EFFICIENCY
-- Business Insight: Identifies which teams are structured as elite
-- chasing sides vs teams that specialize in defending totals.
-- --------------------------------------------------------------------
WITH team_bat_first AS (
    SELECT 
        bat_first_team AS team,
        COUNT(*) AS defended_games,
        SUM(CASE WHEN winner = bat_first_team THEN 1 ELSE 0 END) AS defenses_won
    FROM fact_matches
    GROUP BY bat_first_team
),
team_bat_second AS (
    SELECT 
        field_first_team AS team,
        COUNT(*) AS chased_games,
        SUM(CASE WHEN winner = field_first_team THEN 1 ELSE 0 END) AS chases_won
    FROM fact_matches
    GROUP BY field_first_team
)
SELECT 
    f.team,
    (d.defended_games + f.chased_games) AS total_games,
    ROUND(100.0 * (d.defenses_won + f.chases_won) / (d.defended_games + f.chased_games), 2) AS overall_win_pct,
    ROUND(100.0 * f.chases_won / f.chased_games, 2) AS chase_win_pct,
    ROUND(100.0 * d.defenses_won / d.defended_games, 2) AS defend_win_pct,
    ROUND((100.0 * f.chases_won / f.chased_games) - (100.0 * d.defenses_won / d.defended_games), 2) AS chase_bias_delta
FROM team_bat_second f
JOIN team_bat_first d ON f.team = d.team
WHERE (d.defended_games + f.chased_games) >= 80
ORDER BY overall_win_pct DESC;
