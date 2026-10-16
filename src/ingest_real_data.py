"""
IPL Master Data Ingestion Pipeline (2008–2026)
Ingests and synthesizes:
1. CricSheet Official Ball-by-Ball Dataset (IPL.csv, ~290k balls, 1,193 matches)
2. IPL 2026 - Complete Dataset (Squads, Points Table, Batting/Bowling Stats, Venues)

Creates:
- SQLite Data Warehouse: data/processed/ipl_master.db
- High-speed analytical CSV extracts for player leaderboards, POTM rankings,
  phase-by-phase time series, and head-to-head records.
"""

import os
import re
import sqlite3
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)
DB_PATH = os.path.join(PROCESSED_DIR, "ipl_master.db")

IPL_RAW_CSV = r"C:\Users\palan\Downloads\IPL Dataset(2008-2025)\IPL.csv"
IPL_2026_DIR = r"C:\Users\palan\Downloads\IPL 2026 - Complete Dataset"

# Team Name Standardization Map
TEAM_RENAME_MAP = {
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru'
}

def clean_team_name(name):
    if pd.isna(name):
        return name
    return TEAM_RENAME_MAP.get(name.strip(), name.strip())

def clean_season(s):
    if pd.isna(s):
        return 2008
    s_str = str(s).strip()
    if '/' in s_str:
        # e.g. 2007/08 -> 2008, 2020/21 -> 2020
        parts = s_str.split('/')
        return int(parts[0]) if len(parts[0]) == 4 else int('20' + parts[1])
    try:
        return int(float(s_str))
    except Exception:
        return 2008

def assign_phase(over):
    # over is 0-indexed in CricSheet: 0..5 = overs 1..6 (Powerplay)
    if over < 6:
        return 'Powerplay'
    elif over < 15:
        return 'Middle'
    else:
        return 'Death'

def process_and_load_data():
    print("[1/5] Loading real CricSheet ball-by-ball dataset (IPL.csv)...")
    df_raw = pd.read_csv(IPL_RAW_CSV, low_memory=False)
    print(f" -> Loaded {len(df_raw):,} deliveries across {df_raw['match_id'].nunique()} unique matches.")

    # 1. Clean basic fields
    df_raw['season'] = df_raw['season'].apply(clean_season)
    df_raw['batting_team'] = df_raw['batting_team'].apply(clean_team_name)
    df_raw['bowling_team'] = df_raw['bowling_team'].apply(clean_team_name)
    df_raw['toss_winner'] = df_raw['toss_winner'].apply(clean_team_name)
    df_raw['match_won_by'] = df_raw['match_won_by'].apply(clean_team_name)
    df_raw['phase'] = df_raw['over'].apply(assign_phase)
    
    # Boundary and dot ball indicators
    df_raw['is_four'] = (df_raw['runs_batter'] == 4).astype(int)
    df_raw['is_six'] = (df_raw['runs_batter'] == 6).astype(int)
    df_raw['is_dot'] = ((df_raw['runs_total'] == 0) & (df_raw['valid_ball'] == 1)).astype(int)

    # 2. Extract Match Level Dimension & Facts
    print("[2/5] Building fact_matches & season records...")
    match_group = df_raw.groupby('match_id')
    
    matches_meta = df_raw.drop_duplicates(subset=['match_id']).copy()
    
    # Innings scores
    inn_scores = df_raw.groupby(['match_id', 'innings'])['runs_total'].sum().unstack(fill_value=0)
    inn_scores.columns = [f'inn{col}_runs' for col in inn_scores.columns]
    
    matches_df = matches_meta[['match_id', 'date', 'season', 'venue', 'city', 'batting_team', 'bowling_team',
                               'toss_winner', 'toss_decision', 'match_won_by', 'win_outcome', 'result_type',
                               'superover_winner', 'player_of_match']].copy()
                               
    matches_df.rename(columns={
        'batting_team': 'team1',
        'bowling_team': 'team2',
        'match_won_by': 'winner',
        'player_of_match': 'potm'
    }, inplace=True)
    
    matches_df = matches_df.merge(inn_scores, on='match_id', how='left')
    matches_df['inn1_runs'] = matches_df['inn1_runs'].fillna(0).astype(int)
    matches_df['inn2_runs'] = matches_df['inn2_runs'].fillna(0).astype(int)
    matches_df['match_total_runs'] = matches_df['inn1_runs'] + matches_df['inn2_runs']
    
    # Determine result category
    def parse_result_type(row):
        if pd.notna(row['superover_winner']) or row['result_type'] == 'tie':
            return 'Tie / Super Over'
        if row['result_type'] == 'no result' or pd.isna(row['winner']):
            return 'No Result / Abandoned'
        return 'Normal Result'
        
    matches_df['match_result'] = matches_df.apply(parse_result_type, axis=1)
    
    # Toss match winner & chase winner indicators
    matches_df['toss_winner_won'] = (matches_df['toss_winner'] == matches_df['winner']).astype(int)
    
    # Parse win margin runs / wickets
    def parse_margin(outcome):
        if pd.isna(outcome):
            return 0, 0
        outcome = str(outcome).lower()
        if 'run' in outcome:
            m = re.search(r'(\d+)', outcome)
            return int(m.group(1)) if m else 0, 0
        elif 'wicket' in outcome:
            m = re.search(r'(\d+)', outcome)
            return 0, int(m.group(1)) if m else 0
        return 0, 0
        
    margins = matches_df['win_outcome'].apply(parse_margin)
    matches_df['win_by_runs'] = [m[0] for m in margins]
    matches_df['win_by_wickets'] = [m[1] for m in margins]
    matches_df['won_by_chasing'] = (matches_df['win_by_wickets'] > 0).astype(int)
    matches_df['era'] = matches_df['season'].apply(lambda s: 'Pre-2016' if s < 2016 else 'Post-2016')

    # 3. Phase Run Rate Time Series
    print("[3/5] Aggregating Phase-by-Phase Time-Series (Powerplay vs Middle vs Death)...")
    phase_agg = df_raw.groupby(['season', 'phase']).agg(
        total_runs=('runs_total', 'sum'),
        legal_balls=('valid_ball', 'sum'),
        wickets=('wicket_kind', lambda x: x.notna().sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        dots=('is_dot', 'sum')
    ).reset_index()
    
    phase_agg['overs'] = phase_agg['legal_balls'] / 6.0
    phase_agg['run_rate'] = (phase_agg['total_runs'] / phase_agg['overs']).round(2)
    phase_agg['boundary_run_pct'] = ((phase_agg['fours']*4 + phase_agg['sixes']*6) * 100.0 / phase_agg['total_runs']).round(2)
    phase_agg['dot_ball_pct'] = (phase_agg['dots'] * 100.0 / phase_agg['legal_balls']).round(2)

    # 4. Player Career Analytics & POTM Leaderboard
    print("[4/5] Computing Player All-Time Records, POTM Awards, and Phase Strike Rates...")
    # Batting
    batting_agg = df_raw.groupby('batter').agg(
        runs=('runs_batter', 'sum'),
        balls=('valid_ball', 'sum'),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum'),
        matches=('match_id', 'nunique'),
        innings=('innings', 'count'),
        outs=('wicket_kind', lambda x: x.notna().sum())
    ).reset_index()
    
    batting_agg['strike_rate'] = (batting_agg['runs'] * 100.0 / batting_agg['balls'].replace(0, np.nan)).round(2)
    batting_agg['average'] = (batting_agg['runs'] / batting_agg['outs'].replace(0, 1)).round(2)
    
    # 50s and 100s
    match_batting = df_raw.groupby(['match_id', 'batter'])['runs_batter'].sum().reset_index()
    fifties = match_batting[(match_batting['runs_batter'] >= 50) & (match_batting['runs_batter'] < 100)].groupby('batter').size().rename('fifties')
    hundreds = match_batting[match_batting['runs_batter'] >= 100].groupby('batter').size().rename('hundreds')
    highest_score = match_batting.groupby('batter')['runs_batter'].max().rename('highest_score')
    
    batting_agg = batting_agg.merge(fifties, on='batter', how='left').merge(hundreds, on='batter', how='left').merge(highest_score, on='batter', how='left')
    batting_agg['fifties'] = batting_agg['fifties'].fillna(0).astype(int)
    batting_agg['hundreds'] = batting_agg['hundreds'].fillna(0).astype(int)
    batting_agg['highest_score'] = batting_agg['highest_score'].fillna(0).astype(int)

    # Bowling
    bowling_agg = df_raw[df_raw['valid_ball'] == 1].groupby('bowler').agg(
        runs_conceded=('runs_bowler', 'sum'),
        legal_balls=('valid_ball', 'sum'),
        wickets=('bowler_wicket', 'sum'),
        dots=('is_dot', 'sum')
    ).reset_index()
    
    bowling_agg['overs'] = (bowling_agg['legal_balls'] / 6.0).round(1)
    bowling_agg['economy'] = (bowling_agg['runs_conceded'] / (bowling_agg['legal_balls'] / 6.0).replace(0, np.nan)).round(2)
    bowling_agg['bowling_avg'] = (bowling_agg['runs_conceded'] / bowling_agg['wickets'].replace(0, np.nan)).round(2)

    # POTM Awards
    potm_counts = matches_df['potm'].dropna().value_counts().reset_index()
    potm_counts.columns = ['player', 'potm_awards']
    
    # Phase Strike Rates (Powerplay vs Death)
    pp_batting = df_raw[df_raw['phase'] == 'Powerplay'].groupby('batter').agg(
        pp_runs=('runs_batter', 'sum'),
        pp_balls=('valid_ball', 'sum')
    ).reset_index()
    pp_batting['pp_strike_rate'] = (pp_batting['pp_runs'] * 100.0 / pp_batting['pp_balls'].replace(0, np.nan)).round(2)
    
    death_batting = df_raw[df_raw['phase'] == 'Death'].groupby('batter').agg(
        death_runs=('runs_batter', 'sum'),
        death_balls=('valid_ball', 'sum')
    ).reset_index()
    death_batting['death_strike_rate'] = (death_batting['death_runs'] * 100.0 / death_batting['death_balls'].replace(0, np.nan)).round(2)

    # Merge into Master Player Dimension
    players_df = batting_agg.merge(bowling_agg, left_on='batter', right_on='bowler', how='outer')
    players_df['player_name'] = players_df['batter'].combine_first(players_df['bowler'])
    players_df = players_df.merge(potm_counts, left_on='player_name', right_on='player', how='left')
    players_df['potm_awards'] = players_df['potm_awards'].fillna(0).astype(int)
    players_df = players_df.merge(pp_batting[['batter', 'pp_strike_rate', 'pp_runs']], left_on='player_name', right_on='batter', how='left')
    players_df = players_df.merge(death_batting[['batter', 'death_strike_rate', 'death_runs']], left_on='player_name', right_on='batter', how='left')

    # 5. Ingest 2026 Datasets
    print("[5/5] Ingesting IPL 2026 Season Datasets & Points Table...")
    df_2026_points = pd.read_csv(os.path.join(IPL_2026_DIR, "points_table.csv"))
    df_2026_squads = pd.read_csv(os.path.join(IPL_2026_DIR, "squads.csv"))
    df_2026_venues = pd.read_csv(os.path.join(IPL_2026_DIR, "venues.csv"))
    df_2026_batting = pd.read_csv(os.path.join(IPL_2026_DIR, "batting_stats.csv"))
    df_2026_bowling = pd.read_csv(os.path.join(IPL_2026_DIR, "bowling_stats.csv"))
    df_2026_matches = pd.read_csv(os.path.join(IPL_2026_DIR, "matches.csv"))

    # Save to SQLite Warehouse
    conn = sqlite3.connect(DB_PATH)
    matches_df.to_sql('fact_matches', conn, if_exists='replace', index=False)
    phase_agg.to_sql('fact_phase_summary', conn, if_exists='replace', index=False)
    players_df.to_sql('dim_players', conn, if_exists='replace', index=False)
    
    # 2026 tables
    df_2026_points.to_sql('ipl_2026_points_table', conn, if_exists='replace', index=False)
    df_2026_squads.to_sql('ipl_2026_squads', conn, if_exists='replace', index=False)
    df_2026_venues.to_sql('ipl_2026_venues', conn, if_exists='replace', index=False)
    df_2026_batting.to_sql('ipl_2026_batting', conn, if_exists='replace', index=False)
    df_2026_bowling.to_sql('ipl_2026_bowling', conn, if_exists='replace', index=False)
    df_2026_matches.to_sql('ipl_2026_matches', conn, if_exists='replace', index=False)
    
    # Create indexes for high-speed lookups
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_m_season ON fact_matches(season);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_m_winner ON fact_matches(winner);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p_name ON dim_players(player_name);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p_runs ON dim_players(runs);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_p_wkts ON dim_players(wickets);")
    conn.commit()
    conn.close()

    # Save CSV caches for ultra-fast Streamlit loading
    matches_df.to_csv(os.path.join(PROCESSED_DIR, "matches_master.csv"), index=False)
    phase_agg.to_csv(os.path.join(PROCESSED_DIR, "phase_annual_runrates.csv"), index=False)
    players_df.to_csv(os.path.join(PROCESSED_DIR, "player_career_stats.csv"), index=False)
    potm_counts.to_csv(os.path.join(PROCESSED_DIR, "player_potm_leaderboard.csv"), index=False)
    
    print("\n" + "="*70)
    print("[OK] INGESTION COMPLETE! MASTER DATABASE READY AT:")
    print(f"  {DB_PATH}")
    print(f"  * Total Matches Ingested: {len(matches_df):,}")
    print(f"  * Total Players Profiled: {len(players_df):,}")
    print(f"  * 2026 Standings Loaded:  {len(df_2026_points)} teams")
    print("="*70)

if __name__ == "__main__":
    process_and_load_data()
