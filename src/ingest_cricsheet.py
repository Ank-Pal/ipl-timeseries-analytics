"""
Production CricSheet Ingestion Pipeline (2008–2026)
---------------------------------------------------
Parses authentic CricSheet ball-by-ball delivery records (IPL.csv)
and builds normalized, indexed SQLite tables:
  1. matches: 1,193 historical matches with toss, venues, winners, margins, and POTM
  2. deliveries: 283,678 legal & extra deliveries with phases, runs, and dismissals
"""

import os
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
from venues import VENUE
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = PROCESSED_DIR / "ipl_master.db"

# Discover source CSV: project data/raw/ or user's Downloads directory
local_csv = BASE_DIR / "data" / "raw" / "IPL.csv"
fallback_csv = Path(r"C:\Users\palan\Downloads\IPL Dataset(2008-2025)\IPL.csv")
RAW_CSV = local_csv if local_csv.exists() else fallback_csv

ALIAS = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant"
}

def clean_team(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return ALIAS.get(s, s)

def run_ingestion():
    if not RAW_CSV.exists():
        raise FileNotFoundError(f"CricSheet dataset not found at {RAW_CSV}")

    print(f"[1/4] Reading authentic CricSheet dataset from: {RAW_CSV}...")
    df = pd.read_csv(RAW_CSV, low_memory=False)
    print(f"      Loaded {len(df):,} deliveries across {df['match_id'].nunique():,} matches.")

    # 1. Build deliveries dataframe
    print("[2/4] Normalizing deliveries table with phases and legal balls...")
    deliveries = pd.DataFrame({
        'match_id': df['match_id'],
        'innings_no': df['innings'],
        'is_super_over': (df['innings'] > 2).astype(int),
        'over': df['over'],
        'phase': df['over'].apply(lambda o: "Powerplay" if o < 6 else ("Middle" if o < 15 else "Death")),
        'batting_team': df['batting_team'].apply(clean_team),
        'batter': df['batter'],
        'bowler': df['bowler'],
        'runs_batter': df['runs_batter'],
        'runs_extras': df['runs_extras'],
        'runs_total': df['runs_total'],
        'is_legal': df['valid_ball'].astype(int),
        'is_wicket': df['player_out'].notna().astype(int),
        'player_out': df['player_out']
    })

    # 2. Build matches dataframe
    print("[3/4] Aggregating match-level facts and results...")
    m_group = df.groupby('match_id').first().reset_index()

    inn_teams = df[df['innings'].isin([1, 2])].groupby(['match_id', 'innings'])['batting_team'].first().unstack()

    def parse_by_runs(val):
        if pd.isna(val): return None
        s = str(val).lower()
        if 'run' in s:
            nums = [int(w) for w in s.split() if w.isdigit()]
            return nums[0] if nums else None
        return None

    def parse_by_wickets(val):
        if pd.isna(val): return None
        s = str(val).lower()
        if 'wicket' in s:
            nums = [int(w) for w in s.split() if w.isdigit()]
            return nums[0] if nums else None
        return None

    matches = pd.DataFrame({
        'match_id': m_group['match_id'],
        'season': pd.to_datetime(m_group['date']).dt.year,
        'date': m_group['date'],
        'venue': m_group['venue'],
        'city': m_group['city'],
        'team1': m_group['batting_team'].apply(clean_team),
        'team2': m_group['bowling_team'].apply(clean_team),
        'toss_winner': m_group['toss_winner'].apply(clean_team),
        'toss_decision': m_group['toss_decision'],
        'winner': m_group['match_won_by'].apply(clean_team),
        'result': m_group['result_type'].fillna('normal'),
        'regular_result': (m_group['match_won_by'].notna() & m_group['superover_winner'].isna()).astype(int),
        'by_runs': m_group['win_outcome'].apply(parse_by_runs),
        'by_wickets': m_group['win_outcome'].apply(parse_by_wickets),
        'bat_first': m_group['match_id'].map(inn_teams[1]).apply(clean_team) if 1 in inn_teams else None,
        'chasing': m_group['match_id'].map(inn_teams[2]).apply(clean_team) if 2 in inn_teams else None,
        'stage': m_group['stage'],
        'potm': m_group['player_of_match']
    })

    # Flag ties/super overs
    superover_mids = df[df['innings'] > 2]['match_id'].unique()
    matches.loc[matches['match_id'].isin(superover_mids), 'result'] = 'tie'

    # Apply canonical venue mapping
    matches['venue_canon'] = matches['venue'].map(VENUE)
    assert matches['venue_canon'].nunique() == 36, f"Expected 36 canonical venues, got {matches['venue_canon'].nunique()}"

    # 3. Write to SQLite with indexing
    print(f"[4/4] Ingesting into SQLite warehouse: {DB_PATH}...")
    with sqlite3.connect(DB_PATH) as con:
        matches.to_sql("matches", con, if_exists="replace", index=False)
        deliveries.to_sql("deliveries", con, if_exists="replace", index=False)
        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_match ON deliveries(match_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_batter ON deliveries(batter);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_bowler ON deliveries(bowler);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);")

        # Create v_decided view for unbiased chase and toss analytics
        con.execute("DROP VIEW IF EXISTS v_decided;")
        con.execute("""
        CREATE VIEW v_decided AS
        SELECT m.*, b.bat_first_team,
               CASE WHEN m.winner = b.bat_first_team THEN 0 ELSE 1 END AS chase_won
        FROM matches m
        JOIN (SELECT match_id, MIN(batting_team) AS bat_first_team
              FROM deliveries WHERE innings_no = 1 AND is_super_over = 0
              GROUP BY match_id) b USING (match_id)
        WHERE m.result = 'normal' AND m.winner IS NOT NULL;
        """)

    print(f"[SUCCESS] Ingested {len(matches):,} matches and {len(deliveries):,} deliveries successfully!")

if __name__ == "__main__":
    run_ingestion()
