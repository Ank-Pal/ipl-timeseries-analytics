import os
import sys
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.load_champions_and_superovers import load_data
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "ipl_master.db")

def update_championship_and_matches():
    # 1. Reload dim_ipl_champions, dim_franchise_trophies, fact_super_overs
    load_data()
    print("[1/2] dim_ipl_champions and dim_franchise_trophies refreshed!")

    # 2. Insert or update the 2026 Final in fact_matches
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if 2026 final match (match_id = 2026074) is already present
    cur.execute("SELECT COUNT(*) FROM fact_matches WHERE match_id = 2026074 OR (season = 2026 AND venue LIKE '%Narendra Modi%' AND winner LIKE '%Bengaluru%')")
    count = cur.fetchone()[0]

    final_match_record = {
        "match_id": 2026074,
        "date": "2026-05-31",
        "season": 2026,
        "venue": "Narendra Modi Stadium, Ahmedabad",
        "city": "Ahmedabad",
        "team1": "Gujarat Titans",
        "team2": "Royal Challengers Bengaluru",
        "toss_winner": "Royal Challengers Bengaluru",
        "toss_decision": "field",
        "winner": "Royal Challengers Bengaluru",
        "win_outcome": "5 wickets",
        "result_type": "Normal Result",
        "superover_winner": None,
        "potm": "V Kohli",
        "inn1_runs": 155,
        "inn2_runs": 161,
        "inn3_runs": 0,
        "inn4_runs": 0,
        "inn5_runs": 0,
        "inn6_runs": 0,
        "match_total_runs": 316,
        "match_result": "Normal Result",
        "toss_winner_won": 1,
        "win_by_runs": 0,
        "win_by_wickets": 5,
        "won_by_chasing": 1,
        "era": "Modern/Impact Player Era (2023–2026)"
    }

    if count == 0:
        cols = list(final_match_record.keys())
        placeholders = ", ".join(["?"] * len(cols))
        sql = f"INSERT INTO fact_matches ({', '.join(cols)}) VALUES ({placeholders})"
        cur.execute(sql, list(final_match_record.values()))
        print("[2/2] Inserted IPL 2026 Final match (RCB defeated GT by 5 wickets) into fact_matches!")
    else:
        print("[2/2] 2026 Final match already in fact_matches, updated details.")
        cur.execute("""
            UPDATE fact_matches 
            SET winner = 'Royal Challengers Bengaluru',
                win_outcome = '5 wickets',
                potm = 'V Kohli',
                inn1_runs = 155,
                inn2_runs = 161,
                match_total_runs = 316,
                won_by_chasing = 1,
                win_by_wickets = 5
            WHERE match_id = 2026074 OR (season = 2026 AND venue LIKE '%Narendra Modi%' AND winner LIKE '%Bengaluru%')
        """)

    conn.commit()
    conn.close()
    print("[SUCCESS] All IPL 2026 championship data successfully applied.")

if __name__ == "__main__":
    update_championship_and_matches()
