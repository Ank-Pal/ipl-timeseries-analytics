"""
Oracle Verification Suite: Dashboard Data Integrity & Consistency
------------------------------------------------------------------
Parses index.html and docs/index.html to ensure complete data-driven
coherence between KPI cards, Plotly charts, data tables, and player cards.
"""

import os
import re
import json
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "index.html")
DOCS_INDEX_PATH = os.path.join(BASE_DIR, "docs", "index.html")


def extract_data_payload(html_content):
    match = re.search(r'const DATA = (\{.*?\});\s*// Dark theme', html_content, re.DOTALL)
    assert match is not None, "Failed to find 'const DATA = {...}' in HTML"
    data_str = match.group(1)
    return json.loads(data_str)


def test_dual_html_synchronization():
    """Ensure root index.html and docs/index.html exist and are identical."""
    assert os.path.exists(INDEX_PATH), "index.html missing"
    assert os.path.exists(DOCS_INDEX_PATH), "docs/index.html missing"
    
    with open(INDEX_PATH, 'r', encoding='utf-8') as f1:
        c1 = f1.read()
    with open(DOCS_INDEX_PATH, 'r', encoding='utf-8') as f2:
        c2 = f2.read()
        
    assert c1 == c2, "index.html and docs/index.html are not in sync!"


def test_kohli_tripartite_consistency():
    """
    Assert that the Kohli KPI card, the runs chart, and the player profile card
    display the exact same number (8,661).
    """
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    DATA = extract_data_payload(html)
    
    # 1. KPI Card
    kpi_match = re.search(r'All-Time Run King.*?<div class="kpi-val"[^>]*>([\d,]+)\s*Runs</div>', html, re.DOTALL)
    assert kpi_match is not None, "Kohli KPI card missing"
    kpi_runs = int(kpi_match.group(1).replace(',', ''))
    
    # 2. Runs Chart (Top run scorer in DATA payload)
    top_scorer = DATA['top_run_scorers'][0]
    assert top_scorer['player_name'] == "Virat Kohli", f"Expected Virat Kohli, got {top_scorer['player_name']}"
    chart_runs = int(top_scorer['runs'])
    
    # 3. Player Profile Card
    profile_runs_k = int(DATA['players']['KOHLI']['runs'].replace(',', ''))
    profile_runs_v = int(DATA['players']['VIRAT']['runs'].replace(',', ''))
    
    # Tripartite assertion
    assert kpi_runs == chart_runs == profile_runs_k == profile_runs_v == 8661, (
        f"Inconsistency in Kohli runs: KPI={kpi_runs}, Chart={chart_runs}, Profile={profile_runs_k}"
    )


def test_chahal_wicket_and_economy_consistency():
    """Verify Chahal 205 wickets and 7.98 economy across KPI, table, and DATA."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    DATA = extract_data_payload(html)
    
    # KPI Card
    kpi_match = re.search(r'All-Time Wicket King.*?<div class="kpi-val"[^>]*>(\d+)\s*Wickets</div>.*?<div class="kpi-sub">.*?([\d.]+)\s*Econ', html, re.DOTALL)
    assert kpi_match is not None, "Chahal KPI card missing"
    kpi_wkts = int(kpi_match.group(1))
    kpi_econ = float(kpi_match.group(2))
    
    assert kpi_wkts == 205
    assert kpi_econ == 7.98
    
    # Top wicket taker in DATA
    top_bowler = DATA['top_wicket_takers'][0]
    assert top_bowler['player_name'] == "Yuzvendra Chahal"
    assert top_bowler['wickets'] == 205
    assert top_bowler['economy'] == 7.98
    
    # Profile Card
    assert int(DATA['players']['CHAHAL']['wkts']) == 205
    assert float(DATA['players']['CHAHAL']['sr']) == 7.98


def test_trophies_srh_and_deccan_chargers():
    """Verify Deccan Chargers (1 Title) is separate from SRH (1 Title)."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    DATA = extract_data_payload(html)
    trophies = {t['team']: t['titles'] for t in DATA['trophies']}
    
    assert "Deccan Chargers" in trophies, "Deccan Chargers missing from trophies"
    assert trophies['Deccan Chargers'] == 1, "Deccan Chargers must have 1 title"
    assert trophies['Sunrisers Hyderabad'] == 1, "SRH must have strictly 1 title, not 2"


def test_no_enterprise_intelligence():
    """Verify title and footer do not contain stale 'Enterprise Intelligence'."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    title_match = re.search(r'<title>(.*?)</title>', html)
    assert "Enterprise Intelligence" not in title_match.group(1)
    
    footer_match = re.search(r'<footer>(.*?)</footer>', html, re.DOTALL)
    assert "Enterprise Intelligence" not in footer_match.group(1)


def test_super_overs_hero_line():
    """Verify 2026 super over hero lists Harshit Rana & Andre Russell, not Mitchell Starc."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    assert "Mitchell Starc & Harshit Rana" not in html, "Mitchell Starc incorrectly listed for KKR in 2026"
    assert "Harshit Rana & Andre Russell" in html, "2026 KKR Super Over heroes missing"
    assert "16 Historic Super Overs" in html


def test_arima_and_death_rpo():
    """Verify Death RPO values (2023: 10.49, 2024: 11.21, 2025: 10.96) and Naive backtest."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    DATA = extract_data_payload(html)
    seasons = DATA['phase_rpo']['seasons']
    death_rpo = DATA['phase_rpo']['death']
    rpo_dict = dict(zip(seasons, death_rpo))
    
    assert rpo_dict[2023] == 10.49
    assert rpo_dict[2024] == 11.21
    assert rpo_dict[2025] == 10.96
    
    # Backtest evaluation
    death_eval = [p for p in DATA['arima_evaluation']['phases'] if 'Death' in p['phase']][0]
    assert death_eval['naive_rmse'] < death_eval['arima_rmse'], "Naive should outperform ARIMA in death overs"


def test_rivalries_derived_from_matches():
    """Verify MI vs CSK rivalry has 41 encounters derived from matches (MI 21, CSK 20)."""
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
        
    DATA = extract_data_payload(html)
    mi_csk = [r for r in DATA['rivalries'] if r['matchup'] == 'MI vs CSK'][0]
    
    assert mi_csk['matches'] == 41
    assert mi_csk['w1'] == 21
    assert mi_csk['w2'] == 20


if __name__ == "__main__":
    test_dual_html_synchronization()
    test_kohli_tripartite_consistency()
    test_chahal_wicket_and_economy_consistency()
    test_trophies_srh_and_deccan_chargers()
    test_no_enterprise_intelligence()
    test_super_overs_hero_line()
    test_arima_and_death_rpo()
    test_rivalries_derived_from_matches()
    print("\n[ALL ORACLE VERIFICATION TESTS PASSED 100% GREEN!]")
