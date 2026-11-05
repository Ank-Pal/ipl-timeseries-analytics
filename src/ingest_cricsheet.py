"""
Production CricSheet JSON Ingestion Pipeline (2008–2026)
-------------------------------------------------------
Parses authentic CricSheet JSON ball-by-ball delivery records (1,243 matches)
and builds normalized, indexed SQLite warehouse:
  1. matches: 1,243 historical matches with toss, venues, winners, margins, stage, and POTM
  2. deliveries: 295,732 legal & extra deliveries with phases, runs, and dismissals
"""

import os
import sys
import json
import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))
from venues import VENUE

PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = PROCESSED_DIR / "ipl_master.db"
RAW_DIR = BASE_DIR / "data" / "raw" / "cricsheet"

ALIAS = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant"
}

NOT_BOWLER = ("run out", "retired hurt", "retired out", "obstructing the field")

def clean_team(x):
    if not x:
        return None
    s = str(x).strip()
    return ALIAS.get(s, s)

def run_ingestion():
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"CricSheet JSON directory not found at {RAW_DIR}")

    files = sorted(RAW_DIR.glob("*.json"))
    if not files:
        raise FileNotFoundError(f"No JSON match files found in {RAW_DIR}")

    print(f"[1/4] Found {len(files):,} authentic CricSheet JSON match files in {RAW_DIR}...")

    matches_rows = []
    deliv_rows = []

    print("[2/4] Parsing ball-by-ball deliveries, dismissals, phases, and match outcomes...")
    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        mid = int(p.stem)
        info = d["info"]
        dates = info.get("dates", [])
        date_str = str(dates[0]) if dates else None
        season = int(date_str.split("-")[0]) if date_str else int(str(info.get("season"))[:4])
        venue = info.get("venue")
        venue_canon = VENUE.get(venue)
        if venue_canon is None:
            raise ValueError(f"Unmapped venue string '{venue}' in match {mid}")
        city = info.get("city")
        teams = [clean_team(t) for t in info.get("teams", [None, None])]
        team1 = teams[0] if len(teams) > 0 else None
        team2 = teams[1] if len(teams) > 1 else None

        toss = info.get("toss", {})
        toss_winner = clean_team(toss.get("winner"))
        toss_decision = toss.get("decision")

        outcome = info.get("outcome", {})
        winner_raw = outcome.get("winner") or outcome.get("eliminator")
        winner = clean_team(winner_raw) if winner_raw else None

        innings = d.get("innings", [])
        has_super_over = (outcome.get("result") == "tie") or any(inn.get("super_over", False) for inn in innings)
        is_no_result = (outcome.get("result") == "no result")

        if has_super_over:
            result = "tie"
            regular_result = 0
        elif is_no_result:
            result = "no result"
            regular_result = 0
            winner = None  # No result matches have no winner
        else:
            result = "normal"
            regular_result = 1 if winner else 0

        by = outcome.get("by", {})
        by_runs = by.get("runs")
        by_wickets = by.get("wickets")

        event = info.get("event", {})
        stage = event.get("stage") if event else None
        if not stage:
            stage = "League"

        poms = info.get("player_of_match", [])
        potm = poms[0] if (poms and len(poms) > 0) else None

        bat_first = clean_team(innings[0].get("team")) if len(innings) > 0 else None
        chasing = clean_team(innings[1].get("team")) if len(innings) > 1 else (team2 if bat_first == team1 else team1)

        matches_rows.append((
            mid, season, date_str, venue, venue_canon, city, team1, team2,
            toss_winner, toss_decision, winner, result, regular_result,
            by_runs, by_wickets, bat_first, chasing, stage, potm
        ))

        for inn_idx, inn in enumerate(innings, 1):
            is_so = 1 if (inn.get("super_over", False) or inn_idx > 2) else 0
            b_team = clean_team(inn.get("team"))
            for ov in inn.get("overs", []):
                over_no = ov.get("over")
                phase = "Powerplay" if over_no < 6 else ("Middle" if over_no < 15 else "Death")
                legal_in_over = 0
                for deliv in ov.get("deliveries", []):
                    batter = deliv.get("batter")
                    bowler = deliv.get("bowler")
                    runs = deliv.get("runs", {})
                    rb = runs.get("batter", 0)
                    re = runs.get("extras", 0)
                    rt = runs.get("total", 0)
                    ex = deliv.get("extras", {})
                    is_illegal = ("wides" in ex) or ("noballs" in ex)
                    if not is_illegal:
                        if is_so or legal_in_over < 6:
                            is_legal = 1
                            legal_in_over += 1
                        else:
                            is_legal = 0
                    else:
                        is_legal = 0
                    wicks = deliv.get("wickets", [])
                    is_w = 1 if len(wicks) > 0 else 0
                    w_kind = wicks[0].get("kind") if is_w else None
                    p_out = wicks[0].get("player_out") if is_w else None
                    is_bowler_w = 1 if (is_w and w_kind not in NOT_BOWLER) else 0

                    deliv_rows.append((
                        mid, inn_idx, is_so, over_no, phase, b_team, batter, bowler,
                        rb, re, rt, is_legal, is_w, w_kind, w_kind, is_bowler_w, p_out
                    ))

    matches_df = pd.DataFrame(matches_rows, columns=[
        "match_id", "season", "date", "venue", "venue_canon", "city", "team1", "team2",
        "toss_winner", "toss_decision", "winner", "result", "regular_result",
        "by_runs", "by_wickets", "bat_first", "chasing", "stage", "potm"
    ])

    deliv_df = pd.DataFrame(deliv_rows, columns=[
        "match_id", "innings_no", "is_super_over", "over", "phase", "batting_team",
        "batter", "bowler", "runs_batter", "runs_extras", "runs_total",
        "is_legal", "is_wicket", "kind", "wicket_kind", "is_bowler_wicket", "player_out"
    ])

    print(f"[3/4] Validating {len(matches_df):,} matches and {len(deliv_df):,} deliveries...")
    assert len(matches_df) == 1243, f"Expected 1,243 matches, got {len(matches_df)}"
    assert matches_df["match_id"].nunique() == 1243, "Duplicate matches found!"
    assert matches_df["venue_canon"].nunique() == 36, f"Expected 36 canonical venues, got {matches_df['venue_canon'].nunique()}"

    print(f"[4/4] Writing SQLite warehouse to {DB_PATH}...")
    fact_matches = pd.DataFrame({
        'match_id': matches_df['match_id'],
        'date': matches_df['date'],
        'season': matches_df['season'],
        'venue': matches_df['venue'],
        'city': matches_df['city'],
        'team1': matches_df['team1'],
        'team2': matches_df['team2'],
        'toss_winner': matches_df['toss_winner'],
        'toss_decision': matches_df['toss_decision'],
        'winner': matches_df['winner'],
        'win_outcome': matches_df.apply(lambda r: f"{int(r['by_runs'])} runs" if pd.notna(r['by_runs']) else (f"{int(r['by_wickets'])} wickets" if pd.notna(r['by_wickets']) else None), axis=1),
        'result_type': matches_df['result'],
        'superover_winner': matches_df.apply(lambda r: r['winner'] if r['result'] == 'tie' else None, axis=1),
        'potm': matches_df['potm'],
        'match_result': matches_df['result'].apply(lambda res: 'Tie / Super Over' if res == 'tie' else ('No Result / Abandoned' if res == 'no result' else 'Normal Result')),
        'toss_winner_won': (matches_df['toss_winner'] == matches_df['winner']).astype(int),
        'win_by_runs': matches_df['by_runs'].fillna(0).astype(int),
        'win_by_wickets': matches_df['by_wickets'].fillna(0).astype(int),
        'won_by_chasing': (matches_df['winner'] != matches_df['bat_first']).astype(int),
        'era': matches_df['season'].apply(lambda s: 'Pre-2016' if s < 2016 else 'Post-2016')
    })

    with sqlite3.connect(DB_PATH) as con:
        matches_df.to_sql("matches", con, if_exists="replace", index=False)
        fact_matches.to_sql("fact_matches", con, if_exists="replace", index=False)
        deliv_df.to_sql("deliveries", con, if_exists="replace", index=False)

        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_match ON deliveries(match_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_batter ON deliveries(batter);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_bowler ON deliveries(bowler);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_deliv_phase ON deliveries(phase);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_matches_season ON matches(season);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_matches_venue ON matches(venue_canon);")

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

    print(f"[SUCCESS] Ingested {len(matches_df):,} matches and {len(deliv_df):,} deliveries into {DB_PATH}!")

if __name__ == "__main__":
    run_ingestion()
