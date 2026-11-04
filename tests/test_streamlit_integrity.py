"""
Oracle Verification Suite: Streamlit App & Database Integrity
-------------------------------------------------------------
Validates app.py text, queries, slide configurations, and database coherence.
"""

import os
import re
import sqlite3
import pytest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_PATH = os.path.join(BASE_DIR, "app.py")
DB_PATH = os.path.join(BASE_DIR, "data", "processed", "ipl_master.db")


def test_app_file_exists():
    assert os.path.exists(APP_PATH), "app.py does not exist!"


def test_no_legacy_branding_in_app():
    with open(APP_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    assert "IPL Enterprise Intelligence" not in text, "Legacy 'IPL Enterprise Intelligence' found in app.py"
    assert "18 Champions" not in text, "Legacy '18 Champions' found in app.py"
    assert "15 Super Overs" not in text, "Legacy '15 Super Overs' found in app.py"
    assert "Query 3: All 15 Historic Super Overs" not in text, "Old 15 Super Overs query header found in app.py"


def test_modern_branding_and_counts_in_app():
    with open(APP_PATH, 'r', encoding='utf-8') as f:
        text = f.read()
    assert "IPL Match Analytics & Phase Time-Series (2008–2026)" in text
    assert "19 Champions, 16 Super Overs" in text
    assert "Query 3: All 16 Historic Super Overs & Match Heroes" in text
    assert "Career Benchmark Framing" in text
    assert "Out-of-Sample Backtest: ARIMA vs. Naive Random Walk Benchmark" in text


def test_database_seasons_distribution():
    assert os.path.exists(DB_PATH), "ipl_master.db does not exist!"
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT season, COUNT(*) as c FROM fact_matches GROUP BY season ORDER BY season", conn)
    conn.close()

    seasons = dict(zip(df['season'], df['c']))
    assert 2010 in seasons, "Season 2010 missing from fact_matches in ipl_master.db!"
    assert seasons[2010] == 60, f"Expected 60 matches in 2010, got {seasons[2010]}"
    assert seasons[2009] == 57, f"Expected 57 matches in 2009, got {seasons[2009]}"
    assert seasons[2008] == 58, f"Expected 58 matches in 2008, got {seasons[2008]}"
    assert len(seasons) == 19, f"Expected 19 seasons (2008-2026), got {len(seasons)}"


def test_super_overs_table_count():
    conn = sqlite3.connect(DB_PATH)
    count = pd.read_sql("SELECT COUNT(*) as c FROM fact_super_overs", conn).iloc[0]['c']
    conn.close()
    assert count == 16, f"Expected 16 super overs, got {count}"


if __name__ == "__main__":
    test_app_file_exists()
    test_no_legacy_branding_in_app()
    test_modern_branding_and_counts_in_app()
    test_database_seasons_distribution()
    test_super_overs_table_count()
    print("\n[ALL STREAMLIT & DATABASE ORACLE VERIFICATION TESTS PASSED 100% GREEN!]")
