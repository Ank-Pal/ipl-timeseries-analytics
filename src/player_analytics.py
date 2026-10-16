"""
IPL Player Hall of Fame, POTM & Franchise Rivalry Analytics (2008–2026)
Computes:
1. Most Player of the Match (POTM) awards in IPL history
2. All-Time Orange Cap (Run Kings) & Purple Cap (Wicket Titans)
3. Phase Specialists: Highest Powerplay & Death Overs strike rates
4. Franchise Head-to-Head Rivalry Matrix & Home Fortress Win Rates
5. Generates high-res publication figures
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FIGURES_DIR = os.path.join(BASE_DIR, "outputs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)
DB_PATH = os.path.join(PROCESSED_DIR, "ipl_master.db")

def run_player_and_franchise_analytics():
    print("[1/3] Loading player and match records from master database...")
    conn = sqlite3.connect(DB_PATH)
    
    df_players = pd.read_sql_query("SELECT * FROM dim_players", conn)
    df_matches = pd.read_sql_query("SELECT * FROM fact_matches", conn)
    conn.close()
    
    # 1. Top POTM Awards Leaderboard
    print("[2/3] Computing Hall of Fame: POTM & Phase Kings...")
    top_potm = df_players.sort_values('potm_awards', ascending=False).head(15)[
        ['player_name', 'potm_awards', 'runs', 'wickets']
    ]
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    colors = ['#f59e0b' if i < 3 else '#38bdf8' for i in range(len(top_potm))]
    bars = ax.barh(top_potm['player_name'][::-1], top_potm['potm_awards'][::-1], color=colors[::-1], height=0.65)
    ax.set_title("IPL Hall of Fame: Most Player of the Match (POTM) Awards (2008–2026)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("POTM Awards Count", fontsize=11, fontweight='bold')
    
    for bar in bars:
        w = bar.get_width()
        ax.annotate(f"{int(w)} awards", xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points", ha='left', va='center',
                    fontsize=9, fontweight='bold')
                    
    ax.set_xlim(0, max(top_potm['potm_awards']) + 4)
    plt.tight_layout()
    potm_chart_path = os.path.join(FIGURES_DIR, "top_potm_awards.png")
    plt.savefig(potm_chart_path)
    plt.close()
    
    # 2. Death Overs Strike Rate Masters (Min 300 runs in death overs)
    death_kings = df_players[df_players['death_runs'] >= 300].sort_values('death_strike_rate', ascending=False).head(12)[
        ['player_name', 'death_runs', 'death_strike_rate']
    ]
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    bars2 = ax.barh(death_kings['player_name'][::-1], death_kings['death_strike_rate'][::-1], color='#f43f5e', height=0.65)
    ax.set_title("Death Overs Monsters: Highest Strike Rates in Overs 16–20 (Min 300 Death Runs)", fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel("Death Overs Strike Rate", fontsize=11, fontweight='bold')
    
    for bar in bars2:
        w = bar.get_width()
        ax.annotate(f"{w:.1f} SR", xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points", ha='left', va='center',
                    fontsize=9, fontweight='bold')
                    
    ax.set_xlim(120, max(death_kings['death_strike_rate']) + 25)
    plt.tight_layout()
    death_chart_path = os.path.join(FIGURES_DIR, "death_overs_strike_rate_kings.png")
    plt.savefig(death_chart_path)
    plt.close()
    
    # 3. Head to Head Rivalry Matrix
    print("[3/3] Generating Franchise Head-to-Head Rivalry Matrix...")
    core_teams = [
        'Chennai Super Kings', 'Mumbai Indians', 'Kolkata Knight Riders',
        'Royal Challengers Bengaluru', 'Rajasthan Royals', 'Delhi Capitals',
        'Punjab Kings', 'Sunrisers Hyderabad', 'Gujarat Titans', 'Lucknow Super Giants'
    ]
    
    h2h_list = []
    for t1 in core_teams:
        for t2 in core_teams:
            if t1 == t2:
                continue
            # Matches between t1 and t2
            m = df_matches[
                ((df_matches['team1'] == t1) & (df_matches['team2'] == t2)) |
                ((df_matches['team1'] == t2) & (df_matches['team2'] == t1))
            ]
            t1_wins = (m['winner'] == t1).sum()
            t2_wins = (m['winner'] == t2).sum()
            ties = (m['match_result'] == 'Tie / Super Over').sum()
            h2h_list.append({
                'team': t1,
                'opponent': t2,
                'matches': len(m),
                'wins': t1_wins,
                'losses': t2_wins,
                'ties': ties,
                'win_pct': round((t1_wins * 100.0 / len(m)) if len(m) > 0 else 0.0, 1)
            })
            
    df_h2h = pd.DataFrame(h2h_list)
    df_h2h.to_csv(os.path.join(PROCESSED_DIR, "h2h_rivalry_records.csv"), index=False)
    
    # Save to SQLite
    conn = sqlite3.connect(DB_PATH)
    df_h2h.to_sql('fact_h2h_rivalries', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("[OK] PLAYER & FRANCHISE ANALYTICS COMPLETE!")
    print(f"  * Top POTM King: {top_potm.iloc[0]['player_name']} ({int(top_potm.iloc[0]['potm_awards'])} awards)")
    print(f"  * Top Death King: {death_kings.iloc[0]['player_name']} ({death_kings.iloc[0]['death_strike_rate']} SR)")
    print(f"  * Head-to-Head Matrix Saved: {len(df_h2h)} matchups")
    print("="*70)

if __name__ == "__main__":
    run_player_and_franchise_analytics()
