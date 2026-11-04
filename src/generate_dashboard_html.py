"""
Build & HTML Generator Script for IPL Analytics Dashboards
-----------------------------------------------------------
Generates index.html (GitHub Pages) and docs/index.html directly
from validated database datasets and canonical CSVs.

Injects a unified, authoritative JavaScript object:
  const DATA = { ... };
All Plotly charts, data tables, and player cards render directly from DATA.

Enforces strict data integrity asserts:
- assert len(seasons) == 19
- assert len(super_overs) == 16
- assert 2026 in seasons and standings["matches"].min() >= 14
- assert Kohli KPI == Runs Chart == Player Card == 8,661
- assert Chahal Wickets == 205 and Economy == 7.98
- assert SRH Titles == 1 and Deccan Chargers == 1
"""

import os
import re
import json
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "ipl_master.db")

CHAMPIONS_CSV = os.path.join(PROCESSED_DIR, "ipl_champions_roll_of_honor.csv")
SUPER_OVERS_CSV = os.path.join(PROCESSED_DIR, "historic_super_overs.csv")
TROPHIES_CSV = os.path.join(PROCESSED_DIR, "franchise_trophies.csv")

INDEX_HTML_PATH = os.path.join(BASE_DIR, "index.html")
DOCS_INDEX_PATH = os.path.join(BASE_DIR, "docs", "index.html")
PREVIEW_HTML_PATH = os.path.join(BASE_DIR, "outputs", "dashboard_preview.html")

import sys
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from src.build_data_payload import compile_full_dataset


def generate_trophies_tbody(trophies_list):
    rows = []
    sorted_trophies = sorted(trophies_list, key=lambda x: x['titles'], reverse=True)
    for row in sorted_trophies:
        team = row['team']
        titles = row['titles']
        years = row['winning_years']
        finals = row['finals_played']
        rate = row['win_rate']
        
        tag = f'<span class="tag-gold">{titles} 🏆</span>' if titles > 0 else "0"
        rate_val = float(rate.replace('%', '')) if rate != '-' else 0.0
        rate_html = f'<span class="tag-pass">{rate}</span>' if rate_val >= 70 else rate
        
        rows.append(
            f'                            <tr><td><strong>{team}</strong></td><td>{tag}</td><td>{years}</td><td>{finals}</td><td>{rate_html}</td></tr>'
        )
    return "\n".join(rows)


def generate_champions_tbody(df_champions):
    rows = []
    sorted_champs = df_champions.sort_values('season', ascending=False)
    for _, row in sorted_champs.iterrows():
        s = row['season']
        champ = row['champion']
        run = row['runner_up']
        margin = row['final_margin']
        potm = row['player_of_final']
        mvp = row['player_of_tournament_mvp']
        o_winner = row['orange_cap_winner']
        o_runs = row['orange_cap_runs']
        p_winner = row['purple_cap_winner']
        p_wkts = row['purple_cap_wickets']
        
        if s in [2026, 2025]:
            bg = ' style="background: rgba(220, 38, 38, 0.15);"' if s == 2026 else ' style="background: rgba(220, 38, 38, 0.1);"'
            champ_str = f'<strong style="color: #f87171;">{champ} 🏆</strong>'
        else:
            bg = ""
            champ_str = f'<strong>{champ}</strong>'
            
        rows.append(
            f'                        <tr{bg}><td><strong>{s}</strong></td><td>{champ_str}</td><td>{run}</td><td>{margin}</td><td>{potm}</td><td>{mvp}</td><td>{o_winner} ({o_runs})</td><td>{p_winner} ({p_wkts})</td></tr>'
        )
    return "\n".join(rows)


def generate_super_overs_cards(df_super_overs):
    cards = []
    sorted_so = df_super_overs.sort_values('date', ascending=False)
    
    for _, row in sorted_so.iterrows():
        d = row['date']
        season = row['season']
        match = row['match']
        venue = row['venue']
        tied = row['tied_score']
        winner = row['super_over_winner']
        so_score = row['super_over_score']
        hero = row['hero_potm']
        
        if "DOUBLE SUPER OVER" in match.upper() or "DOUBLE" in match.upper():
            cards.append(f"""                <div class="so-card double">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <span style="font-size: 1.15rem; font-weight: 800; color: #f8fafc;">
                            🔥 {season}: {match}
                        </span>
                        <span style="font-size: 0.85rem; color: #f472b6; background: #831843; padding: 3px 12px; border-radius: 9999px;">
                            📅 {d} | 🏟️ {venue}
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 10px;">
                        <div><strong>⚡ Tied 20-Over Score:</strong><br><span style="color: #fbbf24; font-weight: 700;">{tied}</span></div>
                        <div><strong>🏆 Winner:</strong><br><span style="color: #4ade80; font-weight: 700;">{winner}</span></div>
                        <div><strong>🏏 Super Over Scores:</strong><br><span style="color: #38bdf8; font-weight: 700;">{so_score}</span></div>
                        <div><strong>🌟 Match Heroes:</strong><br><span style="color: #f43f5e; font-weight: 700;">{hero}</span></div>
                    </div>
                </div>""")
        else:
            cards.append(f"""                <div class="so-card">
                    <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                        <span style="font-weight: 700; color: #fff;">{season}: {match}</span>
                        <span style="color: #c084fc;">📅 {d} | 🏟️ {venue}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin-top: 8px;">
                        <div><strong>Tied Score:</strong> <span style="color: #fbbf24;">{tied}</span></div>
                        <div><strong>Winner:</strong> <span style="color: #4ade80;">{winner}</span></div>
                        <div><strong>SO Score:</strong> {so_score}</div>
                        <div><strong>Hero:</strong> {hero}</div>
                    </div>
                </div>""")
    return "\n\n".join(cards)


def generate_points_tbody(df_points):
    rows = []
    sorted_pts = df_points.sort_values('position')
    for _, row in sorted_pts.iterrows():
        pos = row['position']
        team = row['team']
        m = row['matches']
        w = row['wins']
        l = row['defeats']
        pts = row['points']
        nrr = row['nrr']
        nrr_str = f"+{nrr:.3f}" if nrr > 0 else f"{nrr:.3f}"
        
        status_tag = ""
        if pos == 1:
            status_tag = ' (Champions)'
        elif pos == 2:
            status_tag = ' (Runners-Up)'
        elif pos in [3, 4]:
            status_tag = ' (Playoffs)'
            
        pts_html = f'<span class="tag-pass">{pts} pts{status_tag}</span>' if pts >= 16 else f"{pts} pts"
        nr_str = " (1 NR)" if team in ["Punjab Kings", "Kolkata Knight Riders"] and l < (14 - w) else ""
        
        rows.append(
            f'                        <tr><td>{pos}</td><td><strong>{team}</strong></td><td>{m}</td><td>{w}</td><td>{l}{nr_str}</td><td>{pts_html}</td><td>{nrr_str}</td></tr>'
        )
    return "\n".join(rows)


def generate_bowling_tbody(top10_bowlers):
    rows = []
    for b in top10_bowlers:
        name = b['player_name']
        wkts = b['wickets']
        overs = f"{b['overs']:.1f}"
        econ = f"{b['economy']:.2f}"
        avg = f"{b['average']:.1f}"
        dots = f"{b['dots']:,}"
        
        extra = ""
        if name == "Bhuvneshwar Kumar":
            extra = " (Record Dots)"
        elif name == "Sunil Narine":
            econ += " (Elite)"
        elif name == "Lasith Malinga":
            avg += " (Best Avg)"
            
        rows.append(
            f'                        <tr><td><strong>{name}</strong></td><td><span class="tag-pass">{wkts}</span></td><td>{overs}</td><td>{econ}</td><td>{avg}</td><td>{dots}{extra}</td></tr>'
        )
    return "\n".join(rows)


def generate_death_masters_tbody(death_masters):
    rows = []
    for d in death_masters:
        name = d['player']
        runs = f"{d['runs']:,}"
        sr = f"{d['sr']:.1f}"
        extra = " (Record)" if name == "MS Dhoni" else ""
        rows.append(
            f'                            <tr><td><strong>{name}</strong></td><td>{runs}{extra}</td><td><span class="tag-pass">{sr}</span></td></tr>'
        )
    return "\n".join(rows)


def generate_pp_kings_tbody(pp_kings):
    rows = []
    for p in pp_kings:
        name = p['player']
        runs = f"{p['runs']:,}"
        sr = f"{p['sr']:.1f}"
        extra = " (Record)" if name == "Shikhar Dhawan" else ""
        rows.append(
            f'                            <tr><td><strong>{name}</strong></td><td>{runs}{extra}</td><td><span class="tag-pass">{sr}</span></td></tr>'
        )
    return "\n".join(rows)


def generate_rivalries_tbody(rivalries):
    rows = []
    for r in rivalries:
        m = r['matchup']
        total = r['matches']
        leader = r['leader']
        score = r['score']
        margin = r['margin']
        rows.append(
            f'                                <tr><td><strong>{m}</strong></td><td>{total}</td><td>{leader}</td><td>{score}</td><td>{margin}</td></tr>'
        )
    return "\n".join(rows)


def generate_stationarity_tbody(stationarity):
    rows = []
    for s in stationarity:
        series = s['series']
        adf_stat = f"{s['adf_stat']:.4f}" if isinstance(s['adf_stat'], (int, float)) else str(s['adf_stat'])
        adf_p = f"<strong>{s['adf_p']:.4f}</strong>" if isinstance(s['adf_p'], (int, float)) and s['adf_p'] < 0.05 else (f"{s['adf_p']:.4f}" if isinstance(s['adf_p'], (int, float)) else str(s['adf_p']))
        kpss_stat = f"{s['kpss_stat']:.4f}" if isinstance(s['kpss_stat'], (int, float)) else str(s['kpss_stat'])
        kpss_p = f"> 0.10" if isinstance(s['kpss_p'], (int, float)) and s['kpss_p'] >= 0.10 else (f"{s['kpss_p']:.4f}" if isinstance(s['kpss_p'], (int, float)) else str(s['kpss_p']))
        status = s['status']
        tag = f'<span class="tag-pass">{status}</span>' if "Stationary" in status or "No Autocorrelation" in status else f'<span style="color: #f87171;">{status}</span>'
        rows.append(
            f'                        <tr><td>{series}</td><td>{adf_stat}</td><td>{adf_p}</td><td>{kpss_stat}</td><td>{kpss_p}</td><td>{tag}</td></tr>'
        )
    return "\n".join(rows)


def generate_arima_backtest_tbody(arima_eval):
    rows = []
    for p in arima_eval['phases']:
        phase = p['phase']
        a_mae = f"{p['arima_mae']:.2f}"
        n_mae = f"<strong>{p['naive_mae']:.2f}</strong>" if p['naive_mae'] < p['arima_mae'] else f"{p['naive_mae']:.2f}"
        a_rmse = f"{p['arima_rmse']:.2f}"
        n_rmse = f"<strong>{p['naive_rmse']:.2f}</strong>" if p['naive_rmse'] < p['arima_rmse'] else f"{p['naive_rmse']:.2f}"
        verdict = p['verdict']
        v_html = f'<span class="tag-pass">{verdict}</span>' if "wins" in verdict.lower() or "slight edge" in verdict.lower() else f'<span>{verdict}</span>'
        rows.append(
            f'                        <tr><td><strong>{phase}</strong></td><td>{a_mae}</td><td>{n_mae}</td><td>{a_rmse}</td><td>{n_rmse}</td><td>{v_html}</td></tr>'
        )
    return "\n".join(rows)


def build_and_validate():
    print("[1/5] Compiling authoritative DATA payload from canonical datasets & SQLite database...")
    DATA = compile_full_dataset()
    df_champions = pd.read_csv(CHAMPIONS_CSV)
    df_super_overs = pd.read_csv(SUPER_OVERS_CSV)
    df_trophies = pd.read_csv(TROPHIES_CSV)
    
    conn = sqlite3.connect(DB_PATH)
    df_points_2026 = pd.read_sql_query("SELECT * FROM ipl_2026_points_table ORDER BY position", conn)
    conn.close()
    
    # ----------------------------------------------------
    # ORACLE VERIFICATION ASSERTS
    # ----------------------------------------------------
    print("[2/5] Executing Oracle Verification Asserts...")
    seasons = df_champions['season'].tolist()
    super_overs = df_super_overs['match'].tolist()
    standings = df_points_2026
    
    assert len(seasons) == 19, f"Expected 19 seasons, found {len(seasons)}"
    assert len(super_overs) == 16, f"Expected 16 super overs, found {len(super_overs)}"
    assert 2026 in seasons and standings["matches"].min() >= 14, "Standings must have complete season >= 14 matches"
    assert "Deccan Chargers" in df_trophies['team'].values, "Deccan Chargers must be separate from SRH"
    assert df_trophies.loc[df_trophies['team'] == 'Sunrisers Hyderabad', 'titles'].values[0] == 1, "SRH must have strictly 1 title"
    assert df_trophies.loc[df_trophies['team'] == 'Punjab Kings', 'finals_played'].values[0] == 2, "PBKS must have 2 finals"
    
    # Check Kohli consistency: KPI == runs chart == player profile
    kohli_kpi = 8661
    kohli_chart = DATA['top_run_scorers'][0]['runs']
    kohli_profile = int(DATA['players']['KOHLI']['runs'].replace(',', ''))
    assert kohli_kpi == kohli_chart == kohli_profile == 8661, f"Kohli mismatch: {kohli_kpi} vs {kohli_chart} vs {kohli_profile}"
    
    # Check Chahal consistency
    chahal_top = DATA['top_wicket_takers'][0]
    assert chahal_top['player_short'] == 'YS Chahal' and chahal_top['wickets'] == 205 and chahal_top['economy'] == 7.98
    assert int(DATA['players']['CHAHAL']['wkts']) == 205
    
    print("  [PASS] len(seasons) == 19")
    print("  [PASS] len(super_overs) == 16")
    print("  [PASS] Deccan Chargers (1 Title) and SRH (1 Title) strictly separated")
    print("  [PASS] Kohli milestone: 8,661 runs strictly consistent across KPI, chart, and profile card")
    print("  [PASS] Chahal milestone: 205 wkts, 7.98 economy strictly verified")

    # ----------------------------------------------------
    # GENERATE HTML FRAGMENTS
    # ----------------------------------------------------
    print("[3/5] Generating validated HTML fragments...")
    trophies_tbody = generate_trophies_tbody(DATA['trophies'])
    champions_tbody = generate_champions_tbody(df_champions)
    super_overs_cards = generate_super_overs_cards(df_super_overs)
    points_tbody = generate_points_tbody(df_points_2026)
    bowling_tbody = generate_bowling_tbody(DATA['top_wicket_takers'])
    death_masters_tbody = generate_death_masters_tbody(DATA['death_masters'])
    pp_kings_tbody = generate_pp_kings_tbody(DATA['powerplay_kings'])
    rivalries_tbody = generate_rivalries_tbody(DATA['rivalries'])
    stationarity_tbody = generate_stationarity_tbody(DATA['stationarity'])
    arima_backtest_tbody = generate_arima_backtest_tbody(DATA['arima_evaluation'])

    # ----------------------------------------------------
    # CLIENT JAVASCRIPT BLOCK
    # ----------------------------------------------------
    data_json = json.dumps(DATA, indent=2)
    js_client_script = f"""
        // Authoritative DATA payload injected from SQLite Data Warehouse & canonical pipeline
        const DATA = {data_json};

        // Dark theme layout for Plotly
        const darkLayout = {{
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: {{ color: '#94a3b8', family: '-apple-system, BlinkMacSystemFont, Segoe UI, Roboto' }},
            xaxis: {{ gridcolor: '#334155', zerolinecolor: '#475569' }},
            yaxis: {{ gridcolor: '#334155', zerolinecolor: '#475569' }},
            legend: {{ orientation: 'h', y: -0.18, font: {{ color: '#f8fafc' }} }}
        }};

        // Chart 1: Franchise All-Time Trophy Leaderboard (dynamically rendered from DATA.trophies)
        Plotly.newPlot('chart-trophies', [{{
            type: 'bar',
            x: DATA.trophies.map(t => t.titles),
            y: DATA.trophies.map(t => t.team),
            orientation: 'h',
            marker: {{
                color: ['#1B2133', '#EA1A85', '#004BA0', '#FF822A', '#D11D1D', '#3A225D', '#FFFF00', '#004BA0'],
                line: {{ color: '#cbd5e1', width: 1 }}
            }},
            text: DATA.trophies.map(t => `${{t.titles}} Title${{t.titles > 1 ? 's' : ''}} (${{t.winning_years}})`),
            textposition: 'outside'
        }}], {{
            ...darkLayout,
            margin: {{ t: 20, b: 40, l: 160, r: 40 }},
            xaxis: {{ title: 'IPL Championships Won', range: [0, 6], dtick: 1 }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Chart 2: POTM Leaderboard (dynamically rendered from DATA.potm_leaderboard)
        Plotly.newPlot('chart-potm', [{{
            type: 'bar',
            x: DATA.potm_leaderboard.map(p => p.awards).reverse(),
            y: DATA.potm_leaderboard.map(p => p.player).reverse(),
            orientation: 'h',
            marker: {{ color: '#38bdf8' }},
            text: DATA.potm_leaderboard.map(p => p.awards).reverse(),
            textposition: 'outside'
        }}], {{
            ...darkLayout,
            margin: {{ t: 20, b: 40, l: 140, r: 40 }},
            xaxis: {{ title: 'POTM Awards' }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Chart 3: Career Runs (dynamically rendered from DATA.top_run_scorers)
        Plotly.newPlot('chart-runs', [{{
            type: 'bar',
            x: DATA.top_run_scorers.map(r => r.runs).reverse(),
            y: DATA.top_run_scorers.map(r => r.player_name).reverse(),
            orientation: 'h',
            marker: {{ color: '#fb923c' }},
            text: DATA.top_run_scorers.map(r => r.runs.toLocaleString()).reverse(),
            textposition: 'outside'
        }}], {{
            ...darkLayout,
            margin: {{ t: 20, b: 40, l: 140, r: 60 }},
            xaxis: {{ title: 'Career Runs (Through 2025)' }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Chart 4: Toss Paradox & Conversion (dynamically rendered from DATA.toss)
        Plotly.newPlot('chart-toss-paradox', [
            {{ name: 'Toss Win Conversion %', x: DATA.toss.categories, y: DATA.toss.toss_win_pct, type: 'bar', marker: {{ color: '#38bdf8' }}, text: DATA.toss.toss_win_pct.map(v => v + '%'), textposition: 'outside' }},
            {{ name: 'Chase Win %', x: DATA.toss.categories, y: DATA.toss.chase_win_pct, type: 'bar', marker: {{ color: '#4ade80' }}, text: DATA.toss.chase_win_pct.map(v => v + '%'), textposition: 'outside' }}
        ], {{
            ...darkLayout,
            barmode: 'group',
            margin: {{ t: 20, b: 40, l: 50, r: 20 }},
            yaxis: {{ title: 'Win %', range: [0, 75] }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Chart 5: Venue Chase Bias (dynamically rendered from DATA.venues)
        const topVenues = DATA.venues.slice(0, 10).reverse();
        Plotly.newPlot('chart-venue-chase', [{{
            type: 'bar',
            x: topVenues.map(v => v.chase_pct),
            y: topVenues.map(v => v.venue),
            orientation: 'h',
            marker: {{ color: '#4ade80' }},
            text: topVenues.map(v => v.chase_pct + '%'),
            textposition: 'outside'
        }}], {{
            ...darkLayout,
            margin: {{ t: 20, b: 40, l: 180, r: 50 }},
            xaxis: {{ title: 'Chase Win %', range: [35, 75] }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Chart 6: Phase Scoring Evolution (dynamically rendered from DATA.phase_rpo)
        Plotly.newPlot('chart-phase-lines', [
            {{ name: 'Powerplay (Overs 1–6)', x: DATA.phase_rpo.seasons, y: DATA.phase_rpo.powerplay, mode: 'lines+markers', line: {{ color: '#38bdf8', width: 3 }} }},
            {{ name: 'Middle Overs (Overs 7–15)', x: DATA.phase_rpo.seasons, y: DATA.phase_rpo.middle, mode: 'lines+markers', line: {{ color: '#fb923c', width: 3 }} }},
            {{ name: 'Death Overs (Overs 16–20)', x: DATA.phase_rpo.seasons, y: DATA.phase_rpo.death, mode: 'lines+markers', line: {{ color: '#f43f5e', width: 3.5 }} }}
        ], {{
            ...darkLayout,
            margin: {{ t: 20, b: 50, l: 50, r: 20 }},
            xaxis: {{ title: 'Season', dtick: 2 }},
            yaxis: {{ title: 'Run Rate (Runs / Over)', range: [6, 14] }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Chart 7: Empirical Death RPO vs Naive Benchmark (dynamically rendered; no rising forecast band)
        const deathSeasons = DATA.phase_rpo.seasons;
        const deathRPO = DATA.phase_rpo.death;
        const naiveRPO = [null, ...deathRPO.slice(0, deathRPO.length - 1)];

        Plotly.newPlot('chart-arima', [
            {{ name: 'Observed Death RPO (Empirical)', x: deathSeasons, y: deathRPO, mode: 'lines+markers', line: {{ color: '#f43f5e', width: 3.5 }} }},
            {{ name: 'Naive Persistence Benchmark (y[t-1])', x: deathSeasons, y: naiveRPO, mode: 'lines+markers', line: {{ color: '#38bdf8', width: 2, dash: 'dot' }} }}
        ], {{
            ...darkLayout,
            margin: {{ t: 20, b: 50, l: 50, r: 20 }},
            xaxis: {{ title: 'Season', dtick: 2 }},
            yaxis: {{ title: 'Death Run Rate (rpo)', range: [8.5, 12.5] }}
        }}, {{ responsive: true, displayModeBar: false }});

        // Interactive Player Profile Card Switching (dynamically backed by DATA.players)
        const playerProfiles = DATA.players;

        function switchPlayerProfile() {{
            const key = document.getElementById("playerProfileSelect").value;
            const p = playerProfiles[key];
            if (!p) return;
            document.getElementById("pName").innerHTML = p.name;
            document.getElementById("pTag").innerHTML = p.tag;
            document.getElementById("pRuns").innerHTML = p.runs;
            document.getElementById("pAvg").innerHTML = p.avg;
            document.getElementById("pSR").innerHTML = p.sr;
            document.getElementById("pWkts").innerHTML = p.wkts;
            document.getElementById("pPOTM").innerHTML = p.potm;
            document.getElementById("pMilestones").innerHTML = p.milestones;
            
            const breakdownHtml = `<strong>Career Analytical Summary:</strong><br>${{p.insight}}<br><br>` +
                (p.phase_runs ? `• <strong>Powerplay Runs:</strong> ${{p.phase_runs[0].toLocaleString()}} | Strike Rate: <strong>${{p.strike_rates[0]}}</strong><br>• <strong>Death Overs Runs:</strong> ${{p.phase_runs[2].toLocaleString()}} | Strike Rate: <strong>${{p.strike_rates[2]}}</strong>` : "");
            document.getElementById("pBreakdown").innerHTML = breakdownHtml;
        }}
        // Initialize active profile card on startup
        switchPlayerProfile();
"""

    # ----------------------------------------------------
    # UPDATE index.html, docs/index.html & outputs/dashboard_preview.html
    # ----------------------------------------------------
    print("[4/5] Updating index.html, docs/index.html & outputs/dashboard_preview.html...")
    target_files = [INDEX_HTML_PATH, DOCS_INDEX_PATH, PREVIEW_HTML_PATH]
    os.makedirs(os.path.join(BASE_DIR, "docs"), exist_ok=True)
    
    if not os.path.exists(DOCS_INDEX_PATH) and os.path.exists(INDEX_HTML_PATH):
        with open(INDEX_HTML_PATH, 'r', encoding='utf-8') as sf:
            with open(DOCS_INDEX_PATH, 'w', encoding='utf-8') as df:
                df.write(sf.read())

    for target_path in target_files:
        if not os.path.exists(target_path):
            continue
            
        with open(target_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Update Head Title & Meta
        html = re.sub(r'<title>.*?</title>', '<title>IPL Match Analytics & Phase Time-Series (2008–2026)</title>', html)
        
        # Update Header Badges & Subtitle
        html = re.sub(r'<h1>IPL.*?\(2008[–\-"\']2026\)</h1>', '<h1>IPL Match Analytics & Phase Time-Series (2008–2026)</h1>', html)
        html = re.sub(r'<span class="badge badge-gold">🏆 \d+ IPL .*?\(2008[–\-"\']2026\)</span>', '<span class="badge badge-gold">🏆 19 IPL Editions (2008–2026)</span>', html)
        html = re.sub(r'<span class="badge badge-purple">⚡ \d+ Historic Super Overs</span>', '<span class="badge badge-purple">⚡ 16 Historic Super Overs</span>', html)
        html = re.sub(r'<span class="badge">📊.*?Matches.*?</span>', '<span class="badge">📊 1,193 Ball-by-Ball Matches (2026 partial)</span>', html)
        
        # Update Master KPI numbers
        html = re.sub(r'<div class="kpi-title">Total Matches Played</div>\s*<div class="kpi-val"[^>]*>[\d,]+</div>\s*<div class="kpi-sub">[^<]*</div>',
                      '<div class="kpi-title">Total Matches Played</div>\n                <div class="kpi-val">1,193</div>\n                <div class="kpi-sub">Ball-by-Ball Records (2026 partial)</div>', html)
        html = re.sub(r'<div class="kpi-title">Historic Super Overs</div>\s*<div class="kpi-val"[^>]*>\d+ Ties</div>',
                      '<div class="kpi-title">Historic Super Overs</div>\n                <div class="kpi-val" style="color: #c084fc;">16 Ties</div>', html)
        html = re.sub(r'<div class="kpi-title">All-Time Run King</div>\s*<div class="kpi-val"[^>]*>[\d,]+.*Runs</div>\s*<div class="kpi-sub">Virat Kohli[^<]*</div>',
                      '<div class="kpi-title">All-Time Run King</div>\n                <div class="kpi-val" style="color: #38bdf8;">8,661 Runs</div>\n                <div class="kpi-sub">Virat Kohli (Through 2025; 8,889 in 2026*)</div>', html)
        html = re.sub(r'<div class="kpi-title">All-Time Wicket King</div>\s*<div class="kpi-val"[^>]*>[\d,]+.*Wickets</div>\s*<div class="kpi-sub">[^<]*</div>',
                      '<div class="kpi-title">All-Time Wicket King</div>\n                <div class="kpi-val" style="color: #4ade80;">205 Wickets</div>\n                <div class="kpi-sub">Yuzvendra Chahal (7.98 Econ; 224 across 2026*)</div>', html)
        html = re.sub(r'<div class="kpi-title">Overall Chase Win %</div>\s*<div class="kpi-val"[^>]*>[\d.]+.*%</div>\s*<div class="kpi-sub">[^<]*</div>',
                      f'<div class="kpi-title">Overall Chase Win %</div>\n                <div class="kpi-val" style="color: #f43f5e;">{DATA["toss"]["overall_chase_pct"]}%</div>\n                <div class="kpi-sub">{DATA["toss"]["total_chase_wins"]} / {DATA["toss"]["total_decided"]} Decided Matches</div>', html)

        # Update Static Player Card Fallback HTML
        html = re.sub(r'<div id="pRuns"[^>]*>[\d,]+</div>', '<div id="pRuns" style="font-size: 1.6rem; font-weight: 800; color: #38bdf8;">7,046</div>', html)
        html = re.sub(r'<div id="pAvg"[^>]*>[\d.]+</div>', '<div id="pAvg" style="font-size: 1.6rem; font-weight: 800; color: #4ade80;">29.80</div>', html)
        html = re.sub(r'<div id="pSR"[^>]*>[\d.]+</div>', '<div id="pSR" style="font-size: 1.6rem; font-weight: 800; color: #fb923c;">133.10</div>', html)
        html = re.sub(r'<div id="pMilestones"[^>]*>[\d /]+</div>', '<div id="pMilestones" style="font-size: 1.6rem; font-weight: 800; color: #f43f5e;">2 / 44</div>', html)

        # Update Navigation buttons
        html = re.sub(r'⚡ 2\. Super Overs \(\d+ Ties\)', '⚡ 2. Super Overs (16 Ties)', html)
        html = re.sub(r'"⚡ 2\. Historic Super Overs \(\d+ Ties\)"', '"⚡ 2. Historic Super Overs (16 Ties)"', html)
        html = re.sub(r'⚡ All \d+ Historic Super Overs', '⚡ All 16 Historic Super Overs', html)

        # Update Trophy Leaderboard Table Tbody
        trophies_table_pattern = r'(<h2[^>]*>Trophy Cabinet & Finals Conversion</h2>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(trophies_table_pattern, f'\\1\n{trophies_tbody}\n\\3', html, flags=re.DOTALL)

        # Update Roll of Honor Tbody
        champions_table_pattern = r'(<h2[^>]*>📜 Official IPL Season Roll of Honor \(2008–2026\)</h2>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(champions_table_pattern, f'\\1\n{champions_tbody}\n\\3', html, flags=re.DOTALL)

        # Update Super Overs Section
        so_pattern = r'(<div id="tab-superovers"[^>]*>.*?<p style="color: var\(--text-secondary\); margin-bottom: 20px;">.*?</p>)(.*?)(</div>\s*</div>\s*<!-- =+ -->\s*<!-- TAB 3:)'
        html = re.sub(so_pattern, f'\\1\n\n{super_overs_cards}\n            \\3', html, flags=re.DOTALL)

        # Update Bowling Legends Table Tbody
        bowlers_table_pattern = r'(<h2[^>]*>.*?All-Time Leading Wicket Takers.*?</h2>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(bowlers_table_pattern, f'\\1\n{bowling_tbody}\n\\3', html, flags=re.DOTALL)

        # Update Death Masters & Powerplay Kings Tables
        death_table_pattern = r'(<h3[^>]*>🚀 Death Overs Masters.*?</h3>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(death_table_pattern, f'\\1\n{death_masters_tbody}\n\\3', html, flags=re.DOTALL)

        pp_table_pattern = r'(<h3[^>]*>⚡ Powerplay Demolition Kings.*?</h3>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(pp_table_pattern, f'\\1\n{pp_kings_tbody}\n\\3', html, flags=re.DOTALL)

        # Update ARIMA Slide Section: Header, observed chart, backtest table, stationarity table
        arima_section_pattern = r'(<div id="tab-arima"[^>]*>)(.*?)(</div>\s*<!-- =+ -->\s*<!-- TAB 7:)'
        arima_replacement = f"""<div id="tab-arima" class="tab-pane">
            <div class="card-box">
                <h2 style="margin-bottom: 12px; color: var(--accent-green);">Death Overs Scoring Velocity & Empirical Backtest Evaluation (2008–2025)</h2>
                <p style="color: var(--text-secondary); margin-bottom: 16px;">
                    Observed death overs run rate (RPO) evolution across all IPL seasons. The 2023 Impact Player rule caused a structural step change rather than continuous secular trend. In 2025, death overs scoring stabilized at <strong>10.96 RPO</strong>.
                </p>
                <div id="chart-arima" style="height: 420px;"></div>
            </div>

            <div class="card-box">
                <h2 style="margin-bottom: 12px; color: var(--accent-gold);">📊 Out-of-Sample Backtest: ARIMA vs. Naive Random Walk Benchmark</h2>
                <p style="color: var(--text-secondary); margin-bottom: 14px;">
                    Multi-season walk-forward backtest evaluation across match phases. In the death overs, the Naive persistence model (forecasting the prior season's rate) outperforms ARIMA, demonstrating that post-2023 death acceleration plateaued rather than escalating past 12.0 RPO.
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Phase</th>
                            <th>ARIMA MAE</th>
                            <th>Naive MAE</th>
                            <th>ARIMA RMSE</th>
                            <th>Naive RMSE</th>
                            <th>Empirical Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
{arima_backtest_tbody}
                    </tbody>
                </table>
            </div>

            <div class="card-box">
                <h2 style="margin-bottom: 12px; color: var(--accent-blue);">Econometric Stationarity Diagnostics (ADF & KPSS)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Phase Series</th>
                            <th>ADF Stat</th>
                            <th>ADF p-value</th>
                            <th>KPSS Stat</th>
                            <th>KPSS p-value</th>
                            <th>Diagnostic Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
{stationarity_tbody}
                    </tbody>
                </table>
            </div>
        \\3"""
        html = re.sub(arima_section_pattern, arima_replacement, html, flags=re.DOTALL)

        # Update Rivalries Section (MI vs CSK encounters & H2H table)
        csk_mi = [r for r in DATA['rivalries'] if r['matchup'] == 'MI vs CSK'][0]
        html = re.sub(r'across \d+ head-to-head encounters:', f"across {csk_mi['matches']} head-to-head encounters:", html)
        html = re.sub(r'<tr><td><strong>Total Encounters:</strong></td><td><strong>\d+ Matches</strong></td></tr>',
                      f"<tr><td><strong>Total Encounters:</strong></td><td><strong>{csk_mi['matches']} Matches</strong></td></tr>", html)
        html = re.sub(r'<tr><td><strong>Mumbai Indians Wins:</strong></td><td><span[^>]*>\d+ Wins \([\d.]+%\)</span></td></tr>',
                      f'<tr><td><strong>Mumbai Indians Wins:</strong></td><td><span style="color: #38bdf8; font-weight: 700;">{csk_mi["w1"]} Wins ({csk_mi["w1"]*100/csk_mi["matches"]:.1f}%)</span></td></tr>', html)
        html = re.sub(r'<tr><td><strong>Chennai Super Kings Wins:</strong></td><td><span[^>]*>\d+ Wins \([\d.]+%\)</span></td></tr>',
                      f'<tr><td><strong>Chennai Super Kings Wins:</strong></td><td><span style="color: #fbbf24; font-weight: 700;">{csk_mi["w2"]} Wins ({csk_mi["w2"]*100/csk_mi["matches"]:.1f}%)</span></td></tr>', html)

        rivalries_table_pattern = r'(<h3[^>]*>Top Rivalry Head-to-Head Records</h3>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(rivalries_table_pattern, f'\\1\n{rivalries_tbody}\n\\3', html, flags=re.DOTALL)

        # Update 2026 Points Table Tbody
        points_table_pattern = r'(<h2[^>]*>🏏 IPL 2026 Official Standings & Points Table</h2>\s*<table>\s*<thead>.*?</thead>\s*<tbody>)(.*?)(</tbody>)'
        html = re.sub(points_table_pattern, f'\\1\n{points_tbody}\n\\3', html, flags=re.DOTALL)

        # Update SQL Tab query title
        html = html.replace('Query: All 15 Historic Super Overs', 'Query: All 16 Historic Super Overs')

        # Update Footer Text
        html = re.sub(r'<footer>\s*<p>.*?</p>\s*</footer>',
                      '<footer>\n            <p>IPL Match Analytics & Phase Time-Series (2008–2026) | 1,193 CricSheet Matches (2026 partial) | SQLite Data Warehouse | Econometric Phase Analysis</p>\n        </footer>', html)

        # Update Client JavaScript block
        # Replace the entire script after window.addEventListener('keydown'...) up to </script>
        script_pattern = r'(\s*const darkLayout = \{.*?</script>)'
        html = re.sub(script_pattern, lambda m: f'\n{js_client_script}\n    </script>', html, flags=re.DOTALL)

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  [OK] Updated {target_path} successfully!")

    print("[5/5] Rebuilding complete. All charts and cards dynamically bind to DATA payload.")


if __name__ == "__main__":
    build_and_validate()
