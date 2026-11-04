"""
IPL Master Analytics Platform: Unified Orchestrator
---------------------------------------------------
Executes end-to-end data pipeline:
  1. Ingestion of authentic CricSheet ball-by-ball deliveries & matches
  2. Building normalized player dimension (dim_players) and generating figures
  3. Validating and syncing official champions roll of honor & 16 super overs
  4. Building interactive HTML dashboards with strict build assertion checks
  5. Dynamically reporting database record counts
"""

import os
import sys
import subprocess
import time
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "ipl_master.db")

def run_step(step_name, script_path):
    print(f"\n{'='*70}")
    print(f">> STEP: {step_name}")
    print(f"   Executing: {os.path.basename(script_path)}")
    print(f"{'='*70}")
    
    start_time = time.time()
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    elapsed = time.time() - start_time
    
    if result.returncode != 0:
        print(f"[FAIL] Error during {step_name}:")
        print(result.stderr)
        sys.exit(1)
        
    print(result.stdout.strip())
    print(f"[OK] Completed in {elapsed:.2f}s")

def print_database_summary():
    if not os.path.exists(DB_PATH):
        return
    print("\n" + "="*70)
    print("       DATABASE RECORD COUNTS (LIVE FROM SQLITE)")
    print("="*70)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    for table in ["matches", "deliveries", "dim_players", "dim_ipl_champions", "fact_super_overs"]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            cnt = cur.fetchone()[0]
            print(f"  * {table:<25}: {cnt:,} rows")
        except Exception:
            pass
    con.close()
    print("="*70)

def main():
    print("======================================================================")
    print("      IPL MASTER ANALYTICS (2008-2026) UNIFIED PIPELINE               ")
    print("======================================================================")
    
    # 1. Ingest CricSheet data
    run_step("1. Ingesting Authentic CricSheet Deliveries & Matches",
             os.path.join(BASE_DIR, "src", "ingest_cricsheet.py"))
    
    # 2. Player Analytics & Figures
    run_step("2. Building Player Dimension & Generating Visualizations",
             os.path.join(BASE_DIR, "src", "player_analytics.py"))
    
    # 3. Champions & Super Overs Sync
    run_step("3. Synchronizing Champions Roll of Honor & Super Overs",
             os.path.join(BASE_DIR, "src", "load_champions_and_superovers.py"))
    
    # 4. Generate Dashboards with Assertions
    run_step("4. Generating Production HTML Dashboards with Build Asserts",
             os.path.join(BASE_DIR, "src", "generate_dashboard_html.py"))
    
    print_database_summary()
    print("\n[SUCCESS] Unified pipeline completed cleanly!")

if __name__ == "__main__":
    main()
