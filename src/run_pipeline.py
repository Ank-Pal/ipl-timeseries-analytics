"""
IPL Master Analytics Platform: One-Click End-to-End Orchestrator
Executes:
1. Ingestion of 283,000+ CricSheet deliveries, 1,193 matches & 2026 season stats
2. Player Hall of Fame, POTM leaderboard & Franchise Rivalry computation
3. Phase-by-Phase ARIMA Modeling (Powerplay vs Death overs) with ADF/KPSS testing
"""

import os
import sys
import subprocess
import time

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
        
    print(result.stdout)
    print(f"[OK] Completed in {elapsed:.2f}s")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("======================================================================")
    print("      IPL MASTER ANALYTICS (2008-2026) FULL PIPELINE                 ")
    print("======================================================================")
    
    # 1. Real Ingestion
    ingest_script = os.path.join(base_dir, "src", "ingest_real_data.py")
    run_step("1. Ingesting Real CricSheet Ball-by-Ball & 2026 Season Datasets", ingest_script)
    
    # 2. Player Analytics & Rivalries
    player_script = os.path.join(base_dir, "src", "player_analytics.py")
    run_step("2. Computing Player Hall of Fame, POTM Awards & Head-to-Head Matrices", player_script)
    
    # 3. Phase ARIMA
    phase_script = os.path.join(base_dir, "src", "phase_arima_forecasting.py")
    run_step("3. Phase-by-Phase ARIMA Time-Series Modeling (Powerplay vs Death)", phase_script)
    
    print("\n" + "="*70)
    print("[OK] MASTER PIPELINE COMPLETE! ALL DATABASE TABLES & CHARTS READY.")
    print("======================================================================")
    print("Key Deliverables:")
    print(f" * Master Database:        {os.path.join(base_dir, 'data', 'processed', 'ipl_master.db')}")
    print(f" * Master SQL Suite:       {os.path.join(base_dir, 'sql', 'master_queries.sql')}")
    print(f" * Live Streamlit App:     http://localhost:8501")
    print(f" * High-Res Visuals:       {os.path.join(base_dir, 'outputs', 'figures')}")
    print("======================================================================")

if __name__ == "__main__":
    main()
