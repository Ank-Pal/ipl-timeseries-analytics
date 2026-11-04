"""
IPL Player Hall of Fame, POTM & Franchise Analytics (2008–2026)
--------------------------------------------------------------
Builds canonical dim_players directly from authentic CricSheet deliveries and matches.
Generates publication figures:
  1. Most Player of the Match (POTM) awards
  2. Death Overs Strike Rate Kings (Min 300 death overs runs)
"""

import os
import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "outputs" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = PROCESSED_DIR / "ipl_master.db"

def run_player_and_franchise_analytics():
    print("[1/3] Loading regulation deliveries and matches from SQLite warehouse...")
    conn = sqlite3.connect(DB_PATH)
    
    d = pd.read_sql("SELECT * FROM deliveries WHERE is_super_over = 0", conn)
    m = pd.read_sql("SELECT match_id, date, season, potm FROM matches", conn)
    
    # 1. Batting aggregations per batter per match innings
    bat_inn = d.groupby(['batter', 'match_id', 'innings_no']).agg(
        inn_runs=('runs_batter', 'sum'),
        inn_balls=('is_legal', 'sum'),
        inn_fours=('runs_batter', lambda s: (s == 4).sum()),
        inn_sixes=('runs_batter', lambda s: (s == 6).sum())
    ).reset_index()

    bat_tot = bat_inn.groupby('batter').agg(
        runs=('inn_runs', 'sum'),
        balls=('inn_balls', 'sum'),
        fours=('inn_fours', 'sum'),
        sixes=('inn_sixes', 'sum'),
        innings=('inn_runs', 'count'),
        highest_score=('inn_runs', 'max'),
        fifties=('inn_runs', lambda s: ((s >= 50) & (s < 100)).sum()),
        hundreds=('inn_runs', lambda s: (s >= 100).sum())
    ).reset_index()

    # Outs
    outs = d[d['is_wicket'] == 1].groupby('player_out')['match_id'].count().reset_index()
    outs.columns = ['batter', 'outs']

    bat_tot = bat_tot.merge(outs, on='batter', how='left')
    bat_tot['outs'] = bat_tot['outs'].fillna(0)
    bat_tot['average'] = np.where(bat_tot['outs'] > 0, (bat_tot['runs'] / bat_tot['outs']).round(2), bat_tot['runs'])
    bat_tot['strike_rate'] = np.where(bat_tot['balls'] > 0, (bat_tot['runs'] * 100.0 / bat_tot['balls']).round(2), 0.0)

    # Phase batting
    pp = d[d['phase'] == 'Powerplay'].groupby('batter').agg(
        pp_runs=('runs_batter', 'sum'),
        pp_balls=('is_legal', 'sum')
    ).reset_index()
    pp['pp_strike_rate'] = np.where(pp['pp_balls'] > 0, (pp['pp_runs'] * 100.0 / pp['pp_balls']).round(2), 0.0)

    death = d[d['phase'] == 'Death'].groupby('batter').agg(
        death_runs=('runs_batter', 'sum'),
        death_balls=('is_legal', 'sum')
    ).reset_index()
    death['death_strike_rate'] = np.where(death['death_balls'] > 0, (death['death_runs'] * 100.0 / death['death_balls']).round(2), 0.0)

    # 2. Bowling aggregations
    bowl_tot = d.groupby('bowler').agg(
        runs_conceded=('runs_total', 'sum'),
        legal_balls=('is_legal', 'sum'),
        wickets=('is_wicket', 'sum'),
        dots=('runs_total', lambda s: (s == 0).sum())
    ).reset_index()
    bowl_tot['overs'] = (bowl_tot['legal_balls'] / 6.0).round(1)
    bowl_tot['economy'] = np.where(bowl_tot['legal_balls'] > 0, (bowl_tot['runs_conceded'] * 6.0 / bowl_tot['legal_balls']).round(2), 0.0)
    bowl_tot['bowling_avg'] = np.where(bowl_tot['wickets'] > 0, (bowl_tot['runs_conceded'] / bowl_tot['wickets']).round(2), 0.0)

    # 3. POTM awards from matches
    potm_counts = m[m['potm'].notna() & (m['potm'] != '')].groupby('potm')['match_id'].count().reset_index()
    potm_counts.columns = ['player', 'potm_awards']

    # 4. Total matches per player
    bat_matches = d.groupby('batter')['match_id'].nunique().reset_index().rename(columns={'batter': 'player', 'match_id': 'm_bat'})
    bowl_matches = d.groupby('bowler')['match_id'].nunique().reset_index().rename(columns={'bowler': 'player', 'match_id': 'm_bowl'})
    all_players = pd.DataFrame({'player': list(set(d['batter']).union(set(d['bowler'])).union(set(m['potm'].dropna())) )})
    all_players = all_players.merge(bat_matches, on='player', how='left').merge(bowl_matches, on='player', how='left')
    all_players['matches'] = all_players[['m_bat', 'm_bowl']].max(axis=1).fillna(0).astype(int)

    # Combine into dim_players
    dim = all_players[['player', 'matches']].copy()
    dim = dim.merge(bat_tot.rename(columns={'batter': 'player'}), on='player', how='left')
    dim = dim.merge(pp.rename(columns={'batter': 'player'}), on='player', how='left')
    dim = dim.merge(death.rename(columns={'batter': 'player'}), on='player', how='left')
    dim = dim.merge(bowl_tot.rename(columns={'bowler': 'player'}), on='player', how='left')
    dim = dim.merge(potm_counts, on='player', how='left')

    dim['potm_awards'] = dim['potm_awards'].fillna(0).astype(int)
    dim['display_name'] = dim['player']
    dim['full_name'] = dim['player']
    dim['player_name'] = dim['player']

    for col in ['runs', 'balls', 'fours', 'sixes', 'innings', 'highest_score', 'fifties', 'hundreds', 'outs', 'strike_rate', 'average', 'pp_runs', 'pp_balls', 'pp_strike_rate', 'death_runs', 'death_balls', 'death_strike_rate', 'runs_conceded', 'legal_balls', 'wickets', 'dots', 'overs', 'economy', 'bowling_avg']:
        dim[col] = dim[col].fillna(0)

    # Overwrite dim_players table
    dim.to_sql("dim_players", conn, if_exists="replace", index=False)
    conn.close()
    print(f"      dim_players successfully updated ({len(dim):,} players).")

    # Generate Figures
    print("[2/3] Generating POTM chart...")
    top_potm = dim.sort_values('potm_awards', ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    colors = ['#f59e0b' if i < 3 else '#38bdf8' for i in range(len(top_potm))]
    bars = ax.barh(top_potm['player'][::-1], top_potm['potm_awards'][::-1], color=colors[::-1], height=0.65)
    ax.set_title("IPL Hall of Fame: Most Player of the Match (POTM) Awards (2008–2026)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("POTM Awards Count", fontsize=11, fontweight='bold')
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{int(w)} awards", xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points", ha='left', va='center',
                    fontsize=9, fontweight='bold')
    ax.set_xlim(0, max(top_potm['potm_awards']) + 4)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "top_potm_awards.png")
    plt.close()

    print("[3/3] Generating Death Overs Strike Rate chart...")
    death_kings = dim[dim['death_runs'] >= 300].sort_values('death_strike_rate', ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    bars = ax.barh(death_kings['player'][::-1], death_kings['death_strike_rate'][::-1], color='#ef4444', height=0.65)
    ax.set_title("IPL Death Overs Strike Rate Titans (Overs 16–20, Min 300 Runs)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Death Overs Strike Rate", fontsize=11, fontweight='bold')
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{w:.1f} SR", xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points", ha='left', va='center',
                    fontsize=9, fontweight='bold')
    ax.set_xlim(0, max(death_kings['death_strike_rate']) + 25)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "death_overs_strike_rate_kings.png")
    plt.close()
    print("[SUCCESS] Player analytics pipeline completed cleanly.")

if __name__ == "__main__":
    run_player_and_franchise_analytics()
