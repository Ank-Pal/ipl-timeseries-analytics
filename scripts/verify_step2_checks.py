import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect("d:/Learnings/ipl-timeseries-analytics/data/processed/ipl_master.db")
q = lambda s: pd.read_sql(s, con)

print("Running Step 2 Assertions...")
assert q("SELECT COUNT(*) n FROM matches").n[0] == 1243, "Assertion 1 failed: total matches != 1243"
assert q("SELECT COUNT(*) n FROM matches WHERE season=2026").n[0] == 74, "Assertion 2 failed: 2026 matches != 74"
assert q("SELECT COUNT(DISTINCT match_id) n FROM matches").n[0] == 1243, "Assertion 3 failed: duplicate matches found"
assert len(q("""SELECT match_id, innings_no FROM deliveries WHERE is_super_over=0 GROUP BY 1,2 HAVING SUM(is_legal) > 120""")) == 0, "Assertion 4 failed: innings with >120 legal balls found"

print("[PASS] All initial assertions passed!\n")

print("--- 2026 Final ---")
print(q("SELECT * FROM matches WHERE stage='Final' AND season=2026")[["date","winner","by_wickets","potm"]])

print("\n--- Super Overs ---")
print(q("SELECT COUNT(*) super_overs FROM matches WHERE result='tie'"))

print("\n--- Top 3 Batters 2026 ---")
print(q("""SELECT batter, SUM(runs_batter) runs FROM deliveries d JOIN matches m USING(match_id) WHERE m.season=2026 AND d.is_super_over=0 GROUP BY 1 ORDER BY 2 DESC LIMIT 3"""))

print("\n--- Top 3 Bowlers 2026 ---")
print(q("""SELECT bowler, COUNT(*) wkts FROM deliveries d JOIN matches m USING(match_id) WHERE m.season=2026 AND d.is_wicket=1 AND d.is_super_over=0 AND d.wicket_kind NOT IN ('run out','retired hurt','retired out','obstructing the field') GROUP BY 1 ORDER BY 2 DESC LIMIT 3"""))

print("\n--- 2026 League Wins ---")
print(q("""SELECT winner, COUNT(*) wins FROM matches WHERE season=2026 AND stage='League' AND winner IS NOT NULL GROUP BY 1 ORDER BY 2 DESC"""))

print("\n--- MI vs CSK Head to Head ---")
print(q("""SELECT COUNT(*) m, SUM(winner='Mumbai Indians') mi, SUM(winner='Chennai Super Kings') csk FROM matches WHERE (team1='Mumbai Indians' AND team2='Chennai Super Kings') OR (team1='Chennai Super Kings' AND team2='Mumbai Indians')"""))

print("\n--- Additional Sanity Checks ---")
print("Kohli runs through 2025:", q("""SELECT SUM(runs_batter) runs FROM deliveries d JOIN matches m USING(match_id) WHERE batter='V Kohli' AND d.is_super_over=0 AND m.season <= 2025""").iloc[0,0])
print("Kohli runs through 2026:", q("""SELECT SUM(runs_batter) runs FROM deliveries d JOIN matches m USING(match_id) WHERE batter='V Kohli' AND d.is_super_over=0""").iloc[0,0])
print("Bravo career wickets:", q("""SELECT COUNT(*) wkts FROM deliveries d WHERE bowler='DJ Bravo' AND is_wicket=1 AND is_super_over=0 AND wicket_kind NOT IN ('run out','retired hurt','retired out','obstructing the field')""").iloc[0,0])
