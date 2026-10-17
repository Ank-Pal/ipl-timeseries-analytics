"""
IPL Enterprise Intelligence: Ball-by-Ball Analytics & Predictive Time-Series (2008–2026)
Built on 283,000+ official CricSheet deliveries, 1,193 genuine matches, and 2026 season stats.

Tabs:
1. 🏆 Season Champions & Trophy Cabinet (All 2008–2026 Champions, Trophy Leaderboard, Final Margins, MVPs, Orange/Purple Caps)
2. ⚡ Historic Ties & Super Overs Deep Dive (All 15 historic ties, super over scores, heroes, double super over)
3. 👑 Player Hall of Fame & Career Explorer (POTM leaderboards, Orange/Purple Cap titans, Phase SR)
4. 🏟️ Match Explorer & The Toss Paradox (Day/Night, Stadium Bias, Era Comparison)
5. 📊 Phase Dominance & Death-Overs Masters (Powerplay vs Middle vs Death overs)
6. 📈 Phase-by-Phase ARIMA Forecasting (Interactive Powerplay & Death simulator with ADF/KPSS diagnostics)
7. ⚔️ Franchise Rivalries & Head-to-Head Matrix (CSK vs MI, Fortress ratings, all match history)
8. 🏏 IPL 2026 Live Season Hub (Standings, Points Table, Squads, Batting & Bowling leaders)
9. 🗄️ Interactive SQL Studio (Execute live SQL queries on 283k+ deliveries & champions)
"""

import os
import sys
import sqlite3
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
import streamlit as st
import streamlit.runtime

# Auto-redirect if launched directly with `python app.py` instead of `streamlit run app.py`
if not streamlit.runtime.exists():
    print("[INFO] Launching Streamlit web dashboard on http://localhost:8501 ...")
    os.system(f'"{sys.executable}" -m streamlit run "{__file__}"')
    sys.exit(0)


st.set_page_config(
    page_title="IPL Enterprise Intelligence (2008–2026)",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark sports dashboard theme
st.markdown("""
<style>
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 4px;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 1.85rem;
        font-weight: 800;
    }
    .metric-caption {
        color: #64748b;
        font-size: 0.8rem;
    }
    .champ-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .champ-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #fbbf24;
    }
    .runner-title {
        font-size: 0.95rem;
        color: #94a3b8;
    }
    .so-card {
        background: linear-gradient(135deg, #2e1065 0%, #1e1b4b 100%);
        border: 1px solid #7c3aed;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    /* Responsive Tabs Styling - prevents horizontal overflow and truncation */
    div[data-baseweb="tab-list"] {
        gap: 6px !important;
        flex-wrap: wrap !important;
        border-bottom: 2px solid #334155 !important;
        padding-bottom: 6px !important;
        margin-bottom: 14px !important;
    }
    button[data-baseweb="tab"] {
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #cbd5e1 !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }
    button[data-baseweb="tab"]:hover {
        background-color: #334155 !important;
        color: #38bdf8 !important;
        border-color: #38bdf8 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3) !important;
    }
    /* Dark Metallic Slide Navigation Buttons */
    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #f8fafc !important;
        border: 1.5px solid #38bdf8 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 10px 18px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s ease !important;
        min-height: 46px !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        border-color: #7dd3fc !important;
        color: #ffffff !important;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.45) !important;
        transform: translateY(-2px) !important;
    }
    div[data-testid="stButton"] > button:disabled {
        background: #1e293b !important;
        border-color: #334155 !important;
        color: #475569 !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: not-allowed !important;
    }
    /* Slide Scrubber Slider Styling */
    div[data-testid="stSlider"] {
        margin-top: 10px !important;
        margin-bottom: 6px !important;
    }
    div[data-testid="stSlider"] div[data-baseweb="slider"] {
        padding: 12px 4px !important;
    }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "ipl_master.db")

from src.map_player_full_names import PLAYER_FULL_NAME_MAP

@st.cache_data
def load_master_data(_cache_version="2026_v4_rcb_defending_champions"):
    conn = sqlite3.connect(DB_PATH)
    df_matches = pd.read_sql_query("SELECT * FROM fact_matches", conn)
    df_players = pd.read_sql_query("SELECT * FROM dim_players", conn)
    df_phase = pd.read_sql_query("SELECT * FROM fact_phase_summary", conn)
    df_h2h = pd.read_sql_query("SELECT * FROM fact_h2h_rivalries", conn)
    
    # Champions & Super Overs
    df_champions = pd.read_sql_query("SELECT * FROM dim_ipl_champions", conn)
    df_trophies = pd.read_sql_query("SELECT * FROM dim_franchise_trophies", conn)
    df_super_overs = pd.read_sql_query("SELECT * FROM fact_super_overs", conn)
    
    # 2026 tables
    df_2026_points = pd.read_sql_query("SELECT * FROM ipl_2026_points_table", conn)
    df_2026_squads = pd.read_sql_query("SELECT * FROM ipl_2026_squads", conn)
    df_2026_batting = pd.read_sql_query("SELECT * FROM ipl_2026_batting", conn)
    df_2026_bowling = pd.read_sql_query("SELECT * FROM ipl_2026_bowling", conn)
    conn.close()

    # Guarantee full_name & display_name are present
    if 'full_name' not in df_players.columns:
        df_players['full_name'] = df_players['player_name'].apply(lambda x: PLAYER_FULL_NAME_MAP.get(str(x).strip(), str(x).strip()))
    if 'display_name' not in df_players.columns:
        df_players['display_name'] = df_players.apply(
            lambda r: f"{r['full_name']} ({r['player_name']})" if r['full_name'] != r['player_name'] else r['full_name'], axis=1
        )

    return (df_matches, df_players, df_phase, df_h2h,
            df_champions, df_trophies, df_super_overs,
            df_2026_points, df_2026_squads, df_2026_batting, df_2026_bowling)

(df_matches, df_players, df_phase, df_h2h,
 df_champions, df_trophies, df_super_overs,
 df_2026_points, df_2026_squads, df_2026_batting, df_2026_bowling) = load_master_data(_cache_version="2026_v4_rcb_defending_champions")

# Unconditional fallback in case old cache is retrieved from memory
if 'full_name' not in df_players.columns:
    df_players['full_name'] = df_players['player_name'].apply(lambda x: PLAYER_FULL_NAME_MAP.get(str(x).strip(), str(x).strip()))
if 'display_name' not in df_players.columns:
    df_players['display_name'] = df_players.apply(
        lambda r: f"{r['full_name']} ({r['player_name']})" if r['full_name'] != r['player_name'] else r['full_name'], axis=1
    )

# ====================================================================
# SIDEBAR FILTERS
# ====================================================================
st.sidebar.image("https://img.icons8.com/color/96/cricket.png", width=64)
st.sidebar.title("IPL Enterprise Intelligence")
st.sidebar.markdown("Filter matches and view dynamic recalculations.")

# Season Slider
min_s, max_s = int(df_matches['season'].min()), int(df_matches['season'].max())
season_filter = st.sidebar.slider("Season Window:", min_value=min_s, max_value=max_s, value=(min_s, max_s))

# Result Filter
result_options = ["All Matches", "Normal Result", "Tie / Super Over", "No Result / Abandoned"]
result_filter = st.sidebar.selectbox("Match Outcome Type:", result_options)

# Franchise Filter
all_teams = sorted(list(set(df_matches['team1'].dropna().unique()) | set(df_matches['team2'].dropna().unique())))
team_filter = st.sidebar.selectbox("Filter by Franchise:", ["All Franchises"] + all_teams)


# Apply global filter
filtered_matches = df_matches[
    (df_matches['season'] >= season_filter[0]) &
    (df_matches['season'] <= season_filter[1])
]

if result_filter != "All Matches":
    filtered_matches = filtered_matches[filtered_matches['match_result'] == result_filter]

if team_filter != "All Franchises":
    filtered_matches = filtered_matches[
        (filtered_matches['team1'] == team_filter) | (filtered_matches['team2'] == team_filter)
    ]

# ====================================================================
# HEADER & GLOBAL KPIS
# ====================================================================
st.title("🏏 IPL Enterprise Intelligence: Ball-by-Ball Analytics & Predictive Time-Series (2008–2026)")
st.markdown("""
**Powered by 283,000+ official CricSheet deliveries across 1,193 genuine matches, all 18 Champions, 15 Super Overs, and the live 2026 season.**
Explore season roll of honor, all-time trophy rankings, super over thrillers, Player of the Match records, phase ARIMA forecasts, and franchise rivalries.
""")

total_m = len(filtered_matches)
normal_m = filtered_matches[filtered_matches['match_result'] == 'Normal Result']
toss_win_pct = (normal_m['toss_winner_won'].mean() * 100) if len(normal_m) > 0 else 0.0
chase_win_pct = (normal_m['won_by_chasing'].mean() * 100) if len(normal_m) > 0 else 0.0
tie_count = (filtered_matches['match_result'] == 'Tie / Super Over').sum()
avg_par = normal_m['inn1_runs'].mean() if len(normal_m) > 0 else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Matches Selected</div>
        <div class="metric-value">{total_m:,}</div>
        <div class="metric-caption">{season_filter[0]} – {season_filter[1]} ({team_filter if team_filter != 'All Franchises' else 'All Teams'})</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Toss Win Rate</div>
        <div class="metric-value" style="color: {'#38bdf8' if toss_win_pct >= 51 else '#fb923c'};">{toss_win_pct:.1f}%</div>
        <div class="metric-caption">Toss Winner Won Match</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Chase Win %</div>
        <div class="metric-value" style="color: #4ade80;">{chase_win_pct:.1f}%</div>
        <div class="metric-caption">Won Batting Second</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Ties / Super Overs</div>
        <div class="metric-value" style="color: #c084fc;">{tie_count}</div>
        <div class="metric-caption">In Selected Filter</div>
    </div>
    """, unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg 1st Innings Par</div>
        <div class="metric-value" style="color: #f43f5e;">{avg_par:.1f}</div>
        <div class="metric-caption">Runs per 1st Innings</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Master slide renderers defined below

# --------------------------------------------------------------------
# TAB 1: SEASON CHAMPIONS & TROPHY CABINET (2008–2026)
# --------------------------------------------------------------------
def render_slide_1():
    st.subheader("🏆 IPL Champions Roll of Honor & Franchise Trophy Cabinet (2008–2026)")
    st.markdown("""
    Every IPL season champion, runner-up, final margin, venue, Player of the Final, Tournament MVP, Orange Cap, and Purple Cap winners.
    """)
    
    col_tr1, col_tr2 = st.columns([1, 1])
    
    with col_tr1:
        st.markdown("##### 🥇 Franchise All-Time Trophy Leaderboard")
        
        # Color mapping for franchises
        team_colors = {
            "Mumbai Indians": "#004BA0",
            "Chennai Super Kings": "#FFFF00",
            "Kolkata Knight Riders": "#3A225D",
            "Sunrisers Hyderabad": "#FF822A",
            "Rajasthan Royals": "#EA1A85",
            "Gujarat Titans": "#1B2133",
            "Royal Challengers Bengaluru": "#D11D1D",
            "Punjab Kings": "#DD1F2D",
            "Delhi Capitals": "#004C93",
            "Lucknow Super Giants": "#A72056"
        }
        
        trophy_chart_data = df_trophies[df_trophies['titles'] > 0].sort_values('titles', ascending=True)
        colors = [team_colors.get(t, '#38bdf8') for t in trophy_chart_data['team']]
        
        fig_trophies = go.Figure(go.Bar(
            x=trophy_chart_data['titles'],
            y=trophy_chart_data['team'],
            orientation='h',
            marker=dict(color=colors, line=dict(color='#cbd5e1', width=1)),
            text=trophy_chart_data['titles'].apply(lambda t: f"{t} Titles 🏆"),
            textposition='outside'
        ))
        fig_trophies.update_layout(
            title="Most IPL Trophies Won (2008–2026)",
            xaxis=dict(title="IPL Championships Won", range=[0, 6], dtick=1),
            yaxis=dict(title="Franchise"),
            height=360,
            template="plotly_dark"
        )
        st.plotly_chart(fig_trophies, use_container_width=True)
        
    with col_tr2:
        st.markdown("##### 📊 Franchise Finals Record & Conversion Rate")
        st.dataframe(df_trophies[['team', 'titles', 'winning_years', 'finals_played', 'win_rate_in_finals']], use_container_width=True)
        st.info("""
        **Key Historical Takeaways**:
        * **Mumbai Indians (5 Titles)**: Highest conversion rate in finals (83.3%), winning 5 out of 6 finals played.
        * **Chennai Super Kings (5 Titles)**: Record 10 finals appearances, winning in 2010, 2011, 2018, 2021, and 2023.
        * **Kolkata Knight Riders (3 Titles)**: 75% conversion rate in finals (2012, 2014, 2024).
        * **Royal Challengers Bengaluru (2 Titles)**: Back-to-Back Champions (2025 & 2026)! Rajat Patidar led RCB to defend their championship in 2026, defeating Gujarat Titans by 5 wickets in the Final (GT 155/8 vs RCB 161/5). Virat Kohli was named Player of the Match for his unbeaten 75* off 42 balls. RCB joins CSK and MI as the only franchises in IPL history to successfully defend an IPL title!
        * **Sunrisers Hyderabad / Deccan Chargers (2 Titles)**: 2009 (DC) & 2016 (SRH).
        * **Gujarat Titans (1 Title)**: 2022 Champions, 3 finals played (2022, 2023, 2026).
        """)

    st.markdown("---")
    st.markdown("#### 📜 Year-by-Year Official IPL Roll of Honor (2008–2026)")
    
    # Season Selector for Detailed Inspector
    selected_year = st.selectbox(
        "Select Season to Inspect Final Match Details & Award Winners:",
        sorted(df_champions['season'].unique(), reverse=True)
    )
    
    season_row = df_champions[df_champions['season'] == selected_year].iloc[0]
    
    st.markdown(f"""
    <div class="champ-card">
        <div class="champ-title">IPL {season_row['season']} Champion: 🏆 {season_row['champion']}</div>
        <div class="runner-title">Runner-Up: 🥈 {season_row['runner_up']}</div>
        <hr style="border-color: #334155; margin: 10px 0;">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
            <div><strong>🏟️ Final Venue:</strong><br>{season_row['final_venue']}</div>
            <div><strong>🎯 Final Margin:</strong><br><span style="color: #4ade80;">{season_row['final_margin']}</span></div>
            <div><strong>⭐ Player of Final:</strong><br>{season_row['player_of_final']}</div>
            <div><strong>🎖️ Tournament MVP:</strong><br>{season_row['player_of_tournament_mvp']}</div>
            <div><strong>🟠 Orange Cap (Runs):</strong><br><span style="color: #fb923c;">{season_row['orange_cap_winner']} ({season_row['orange_cap_runs']} runs)</span></div>
            <div><strong>🟣 Purple Cap (Wkts):</strong><br><span style="color: #c084fc;">{season_row['purple_cap_winner']} ({season_row['purple_cap_wickets']} wkts)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("##### 📋 Complete IPL Champions & Award Winners Master Table")
    disp_champions = df_champions[
        (df_champions['season'] >= season_filter[0]) &
        (df_champions['season'] <= season_filter[1])
    ]
    if team_filter != "All Franchises":
        team_champs = disp_champions[
            (disp_champions['champion'] == team_filter) | (disp_champions['runner_up'] == team_filter)
        ]
        if len(team_champs) > 0:
            st.info(f"Showing seasons where **{team_filter}** reached the Final ({len(team_champs)} finals in selected window).")
            st.dataframe(team_champs, use_container_width=True)
        else:
            st.info(f"**{team_filter}** did not reach a Final in the {season_filter[0]}–{season_filter[1]} window. Showing all champions in this window:")
            st.dataframe(disp_champions, use_container_width=True)
    else:
        st.dataframe(disp_champions, use_container_width=True)


# --------------------------------------------------------------------
# TAB 2: HISTORIC TIES & SUPER OVERS DEEP DIVE
# --------------------------------------------------------------------
def render_slide_2():
    st.subheader("⚡ Historic Ties & Super Overs Deep Dive (2008–2026)")
    st.markdown("""
    In IPL history, when both teams finish 20 overs with the exact same score, a **Super Over** is triggered.
    Here is the complete record of **all 15 Super Overs** in tournament history, including the tied scores, super over scores, and hero performances.
    """)
    
    TEAM_ALIASES = {
        "Mumbai Indians": ["MI", "Mumbai Indians"],
        "Chennai Super Kings": ["CSK", "Chennai Super Kings"],
        "Kolkata Knight Riders": ["KKR", "Kolkata Knight Riders"],
        "Royal Challengers Bengaluru": ["RCB", "Royal Challengers"],
        "Rajasthan Royals": ["RR", "Rajasthan Royals"],
        "Sunrisers Hyderabad": ["SRH", "Sunrisers Hyderabad"],
        "Delhi Capitals": ["DC", "DD", "Delhi"],
        "Punjab Kings": ["KXIP", "PBKS", "Punjab Kings"],
        "Gujarat Titans": ["GT", "Gujarat Titans"],
        "Lucknow Super Giants": ["LSG", "Lucknow Super Giants"],
        "Gujarat Lions": ["GL", "Gujarat Lions"]
    }
    
    disp_so = df_super_overs[
        (df_super_overs['season'] >= season_filter[0]) &
        (df_super_overs['season'] <= season_filter[1])
    ]
    if team_filter != "All Franchises":
        aliases = TEAM_ALIASES.get(team_filter, [team_filter])
        pat = "|".join(aliases)
        disp_so = disp_so[
            (disp_so['match'].str.contains(pat, case=False, na=False)) |
            (disp_so['super_over_winner'].str.contains(pat, case=False, na=False))
        ]
        
    col_so1, col_so2, col_so3 = st.columns(3)
    col_so1.metric("Super Overs in Selection", f"{len(disp_so)}")
    col_so2.metric("Double Super Overs", "1 (MI vs KXIP, 2020)" if (season_filter[0] <= 2020 <= season_filter[1] and team_filter in ["All Franchises", "Mumbai Indians", "Punjab Kings"]) else "0")
    col_so3.metric("Filter Active", team_filter if team_filter != 'All Franchises' else "All Franchises")
    
    if len(disp_so) > 0:
        st.markdown(f"##### ⚔️ Super Overs Matching Filter ({len(disp_so)} Matches)")
        for idx, so in disp_so.iterrows():
            is_double = "DOUBLE SUPER OVER" in str(so['match'])
            bg_style = "background: linear-gradient(135deg, #4c1d95 0%, #1e1b4b 100%); border: 2px solid #a855f7;" if is_double else ""
            
            st.markdown(f"""
            <div class="so-card" style="{bg_style}">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 1.15rem; font-weight: 800; color: #f8fafc;">
                        {so['season']} Match: {so['match']} {'🔥 (LEGENDARY DOUBLE SUPER OVER)' if is_double else ''}
                    </span>
                    <span style="font-size: 0.85rem; color: #a78bfa; background: #3b0764; padding: 2px 10px; border-radius: 9999px;">
                        📅 {so['date']} | 🏟️ {so['venue']}
                    </span>
                </div>
                <hr style="border-color: #6b21a8; margin: 8px 0;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div><strong>⚖️ Tied 20-Over Score:</strong><br><span style="color: #fbbf24; font-weight: 700;">{so['tied_score']}</span></div>
                    <div><strong>⚡ Super Over Winner:</strong><br><span style="color: #4ade80; font-weight: 700;">🏆 {so['super_over_winner']}</span></div>
                    <div><strong>🏏 Super Over Score:</strong><br><span style="color: #38bdf8; font-weight: 700;">{so['super_over_score']}</span></div>
                    <div><strong>🦸‍♂️ Match Hero / POTM:</strong><br><span style="color: #f43f5e; font-weight: 700;">{so['hero_potm']}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("##### 📋 Searchable Super Overs Master Data Table")
        st.dataframe(disp_so, use_container_width=True)
    else:
        st.info(f"No Super Overs recorded for **{team_filter}** in the **{season_filter[0]}–{season_filter[1]}** window.")


# --------------------------------------------------------------------
# TAB 3: PLAYER HALL OF FAME & CAREER SEARCH
# --------------------------------------------------------------------
def render_slide_3():
    st.subheader("👑 Player Hall of Fame & Comprehensive Career Explorer")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("##### 🏅 All-Time Most Player of the Match (POTM) Awards")
        potm_top = df_players.sort_values('potm_awards', ascending=False).head(10)[
            ['full_name', 'potm_awards', 'runs', 'wickets', 'player_name']
        ]
        fig_potm = px.bar(potm_top, x='potm_awards', y='full_name', orientation='h',
                          title="Most POTM Awards in IPL History",
                          color='potm_awards', color_continuous_scale="Viridis",
                          text='potm_awards')
        fig_potm.update_layout(height=380, template="plotly_dark", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_potm, use_container_width=True)
        
    with col_p2:
        st.markdown("##### 👑 All-Time Leading Run Scorers (Orange Cap Titans)")
        run_kings = df_players.sort_values('runs', ascending=False).head(10)[
            ['full_name', 'runs', 'average', 'strike_rate', 'hundreds', 'fifties', 'player_name']
        ]
        fig_runs = px.bar(run_kings, x='runs', y='full_name', orientation='h',
                          title="All-Time Most IPL Runs",
                          color='runs', color_continuous_scale="Plasma",
                          text='runs')
        fig_runs.update_layout(height=380, template="plotly_dark", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_runs, use_container_width=True)

    st.markdown("##### 🟣 All-Time Leading Wicket Takers (Purple Cap Legends)")
    wkt_kings = df_players.sort_values('wickets', ascending=False).head(10)[
        ['full_name', 'wickets', 'economy', 'bowling_avg', 'overs', 'dots', 'player_name']
    ]
    st.dataframe(wkt_kings, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🔎 Interactive Player Career Profile Explorer")
    st.markdown("Search or select **ANY player** by their full name (e.g. **Rohit Sharma**, **Virat Kohli**, **MS Dhoni**, **AB de Villiers**) to view their complete career scorecard and phase strike rates:")
    
    all_player_display = sorted(df_players['display_name'].dropna().unique())
    default_idx = 0
    rohit_matches = [i for i, name in enumerate(all_player_display) if "Rohit Sharma" in name]
    if rohit_matches:
        default_idx = rohit_matches[0]
        
    selected_player_disp = st.selectbox(
        "Search & Select Player (By Full Name):",
        all_player_display,
        index=default_idx
    )
    
    p_stat = df_players[df_players['display_name'] == selected_player_disp].iloc[0]
    
    runs_val = f"{int(p_stat['runs']):,}" if (pd.notna(p_stat['runs']) and not np.isnan(p_stat['runs'])) else "0"
    avg_val = f"{p_stat['average']:.2f}" if (pd.notna(p_stat['average']) and not np.isnan(p_stat['average'])) else "N/A"
    sr_val = f"{p_stat['strike_rate']:.2f}" if (pd.notna(p_stat['strike_rate']) and not np.isnan(p_stat['strike_rate'])) else "N/A"
    wkt_val = f"{int(p_stat['wickets'])}" if (pd.notna(p_stat['wickets']) and not np.isnan(p_stat['wickets'])) else "0"
    econ_val = f"{p_stat['economy']:.2f}" if (pd.notna(p_stat['economy']) and not np.isnan(p_stat['economy'])) else "N/A"
    potm_val = f"{int(p_stat['potm_awards'])}" if (pd.notna(p_stat['potm_awards']) and not np.isnan(p_stat['potm_awards'])) else "0"
    
    pp_r = int(p_stat['pp_runs']) if (pd.notna(p_stat['pp_runs']) and not np.isnan(p_stat['pp_runs'])) else 0
    pp_sr = f"{p_stat['pp_strike_rate']:.2f}" if (pd.notna(p_stat['pp_strike_rate']) and not np.isnan(p_stat['pp_strike_rate'])) else "N/A (Did not bat in PP)"
    
    death_r = int(p_stat['death_runs']) if (pd.notna(p_stat['death_runs']) and not np.isnan(p_stat['death_runs'])) else 0
    death_sr = f"{p_stat['death_strike_rate']:.2f}" if (pd.notna(p_stat['death_strike_rate']) and not np.isnan(p_stat['death_strike_rate'])) else "N/A (Did not bat in Death)"
    
    hund = int(p_stat['hundreds']) if (pd.notna(p_stat['hundreds']) and not np.isnan(p_stat['hundreds'])) else 0
    fift = int(p_stat['fifties']) if (pd.notna(p_stat['fifties']) and not np.isnan(p_stat['fifties'])) else 0
    hs = int(p_stat['highest_score']) if (pd.notna(p_stat['highest_score']) and not np.isnan(p_stat['highest_score'])) else 0

    st.markdown(f"### 🏏 {p_stat['full_name']} — Official Career Profile")
    
    cp1, cp2, cp3, cp4, cp5, cp6 = st.columns(6)
    with cp1:
        st.metric("Career Runs", runs_val)
    with cp2:
        st.metric("Batting Average", avg_val)
    with cp3:
        st.metric("Strike Rate", sr_val)
    with cp4:
        st.metric("Wickets", wkt_val)
    with cp5:
        st.metric("Economy Rate", econ_val)
    with cp6:
        st.metric("POTM Awards", f"{potm_val} 🏅")
        
    st.info(f"""
    **{p_stat['full_name']} ({p_stat['player_name']}) Phase Scoring Breakdown**:
    * **Powerplay (Overs 1–6)**: {pp_r:,} runs | Strike Rate: **{pp_sr}**
    * **Death Overs (Overs 16–20)**: {death_r:,} runs | Strike Rate: **{death_sr}**
    * **Centuries (100s)**: {hund} | **Fifties (50s)**: {fift} | **Highest Score**: {hs}
    """)


# --------------------------------------------------------------------
# TAB 4: MATCH EXPLORER & TOSS PARADOX
# --------------------------------------------------------------------
def render_slide_4():
    st.subheader("🏟️ Match Explorer, Venue Analytics & The Toss Paradox")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        era_grp = normal_m.groupby('era').agg(
            matches=('match_id', 'count'),
            toss_win=('toss_winner_won', lambda x: x.mean() * 100),
            chase_win=('won_by_chasing', lambda x: x.mean() * 100)
        ).reset_index()
        
        fig_era = go.Figure(data=[
            go.Bar(name='Toss Win Conversion %', x=era_grp['era'], y=era_grp['toss_win'], marker_color='#38bdf8', text=era_grp['toss_win'].apply(lambda v: f"{v:.1f}%"), textposition='outside'),
            go.Bar(name='Chase Win %', x=era_grp['era'], y=era_grp['chase_win'], marker_color='#4ade80', text=era_grp['chase_win'].apply(lambda v: f"{v:.1f}%"), textposition='outside')
        ])
        fig_era.update_layout(
            title="Real Toss Conversion & Chase Rate by Era",
            barmode='group',
            yaxis=dict(title="Win %", range=[0, 75]),
            height=380,
            template="plotly_dark",
            legend=dict(orientation="h", y=-0.2)
        )
        st.plotly_chart(fig_era, use_container_width=True)
        
    with col_m2:
        venue_grp = normal_m.groupby('venue')['won_by_chasing'].agg(['count', 'mean']).reset_index()
        venue_grp = venue_grp[venue_grp['count'] >= 15].sort_values('mean', ascending=True).tail(10)
        venue_grp['chase_pct'] = venue_grp['mean'] * 100
        
        fig_v = go.Figure(go.Bar(
            x=venue_grp['chase_pct'],
            y=venue_grp['venue'],
            orientation='h',
            marker_color='#4ade80',
            text=venue_grp['chase_pct'].apply(lambda v: f"{v:.1f}%"),
            textposition='outside'
        ))
        fig_v.add_vline(x=50, line_dash="dash", line_color="#94a3b8")
        fig_v.update_layout(
            title="Top Chasing Venues (Min 15 Matches)",
            xaxis=dict(title="Chase Win %", range=[35, 70]),
            height=380,
            template="plotly_dark"
        )
        st.plotly_chart(fig_v, use_container_width=True)

    st.markdown("#### 🔍 Match Browser & Scorecard Search")
    disp_cols = ['date', 'season', 'team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'winner', 'win_outcome', 'potm', 'inn1_runs', 'inn2_runs']
    st.dataframe(filtered_matches[disp_cols].sort_values('date', ascending=False).head(100), use_container_width=True)


# --------------------------------------------------------------------
# TAB 5: PHASE DOMINANCE (POWERPLAY VS DEATH)
# --------------------------------------------------------------------
def render_slide_5():
    st.subheader("📊 Match Phase Dominance: Powerplay vs Middle vs Death Overs")
    st.markdown("""
    Analysis of how cricket scoring rates evolved across match segments, and how the **2023–2026 Impact Player rule** changed death-overs velocity.
    """)
    
    pivot_phase = df_phase[df_phase['season'] >= 2008].pivot(index='season', columns='phase', values='run_rate').reset_index()
    
    fig_phase = go.Figure()
    fig_phase.add_trace(go.Scatter(x=pivot_phase['season'], y=pivot_phase['Powerplay'], mode='lines+markers', name='Powerplay (Overs 1–6)', line=dict(color='#38bdf8', width=3)))
    fig_phase.add_trace(go.Scatter(x=pivot_phase['season'], y=pivot_phase['Middle'], mode='lines+markers', name='Middle Overs (Overs 7–15)', line=dict(color='#fb923c', width=3)))
    fig_phase.add_trace(go.Scatter(x=pivot_phase['season'], y=pivot_phase['Death'], mode='lines+markers', name='Death Overs (Overs 16–20)', line=dict(color='#f43f5e', width=3.5)))
    fig_phase.add_vline(x=2023, line_dash="dot", line_color="#c084fc", annotation_text="Impact Player Rule", annotation_position="top left")
    
    fig_phase.update_layout(
        title="Evolution of Run Rates by Phase (2008–2026)",
        xaxis=dict(title="Season", dtick=2),
        yaxis=dict(title="Run Rate (Runs / Over)", range=[6.0, 14.0]),
        height=450,
        template="plotly_dark",
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig_phase, use_container_width=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("##### 🚀 Highest Death Overs Strike Rates (Overs 16–20)")
        death_lead = df_players[df_players['death_runs'] >= 300].sort_values('death_strike_rate', ascending=False).head(10)[
            ['full_name', 'death_runs', 'death_strike_rate', 'player_name']
        ]
        st.dataframe(death_lead, use_container_width=True)
    with col_d2:
        st.markdown("##### ⚡ Highest Powerplay Strike Rates (Overs 1–6)")
        pp_lead = df_players[df_players['pp_runs'] >= 400].sort_values('pp_strike_rate', ascending=False).head(10)[
            ['full_name', 'pp_runs', 'pp_strike_rate', 'player_name']
        ]
        st.dataframe(pp_lead, use_container_width=True)


# --------------------------------------------------------------------
# TAB 6: PHASE-BY-PHASE ARIMA SIMULATOR
# --------------------------------------------------------------------
def render_slide_6():
    st.subheader("📈 Phase-by-Phase ARIMA Time-Series Simulator")
    st.markdown("""
    Forecast scoring rates for **Powerplay**, **Middle**, or **Death Overs** into future seasons with statistical stationarity proofs.
    """)
    
    fc_phase_select = st.selectbox("Select Phase to Forecast:", ["Death Overs (Overs 16–20)", "Powerplay (Overs 1–6)", "Middle Overs (Overs 7–15)"])
    phase_key = "Death" if "Death" in fc_phase_select else ("Powerplay" if "Powerplay" in fc_phase_select else "Middle")
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        fc_horizon = st.slider("Forecast Horizon (Seasons):", 1, 5, 3)
    with c_f2:
        fc_ci_level = st.selectbox("Confidence Level:", [80, 90, 95, 99], index=2)
        alpha_val = 1.0 - (fc_ci_level / 100.0)

    # Build series
    series_data = df_phase[(df_phase['phase'] == phase_key) & (df_phase['season'] >= 2008)].sort_values('season').set_index('season')['run_rate']
    
    # Stationarity
    adf_raw = adfuller(series_data, maxlag=1)
    kpss_raw = kpss(series_data, regression='c', nlags="auto")
    
    diff_data = series_data.diff().dropna()
    adf_diff = adfuller(diff_data, maxlag=1)
    kpss_diff = kpss(diff_data, regression='c', nlags="auto")
    
    # Fit ARIMA(0, 1, 0)
    m_fit = ARIMA(series_data, order=(0, 1, 0)).fit()
    fc_res = m_fit.get_forecast(steps=fc_horizon)
    fc_mean = fc_res.predicted_mean
    fc_ci = fc_res.conf_int(alpha=alpha_val)
    
    future_yrs = [int(series_data.index[-1] + i) for i in range(1, fc_horizon + 1)]
    fc_mean.index = future_yrs
    fc_ci.index = future_yrs
    
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=series_data.index, y=series_data.values, mode='lines+markers', name=f'Observed {phase_key} RPO', line=dict(color='#38bdf8', width=3)))
    fig_sim.add_trace(go.Scatter(x=future_yrs, y=fc_mean.values, mode='lines+markers', name='ARIMA Forecast', line=dict(color='#4ade80', width=3)))
    
    # CI Band - Note line=dict(width=0) to prevent transparent ValueError
    fig_sim.add_trace(go.Scatter(
        x=future_yrs + future_yrs[::-1],
        y=list(fc_ci.iloc[:, 1]) + list(fc_ci.iloc[:, 0])[::-1],
        fill='toself', fillcolor='rgba(74, 222, 128, 0.15)',
        line=dict(width=0), name=f'{fc_ci_level}% Confidence Interval'
    ))
    
    fig_sim.update_layout(
        title=f"{phase_key} Run Rate Trajectory & ARIMA Forecast",
        xaxis=dict(title="Season", dtick=1),
        yaxis=dict(title="Run Rate (rpo)"),
        height=450,
        template="plotly_dark",
        legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig_sim, use_container_width=True)
    
    st.markdown("##### 🧪 Dual Stationarity Testing (ADF & KPSS)")
    stat_summary = pd.DataFrame([
        {"Series": f"Raw {phase_key} Series", "ADF Stat": f"{adf_raw[0]:.4f}", "ADF p-value": f"{adf_raw[1]:.4f}", "KPSS p-value": f"{kpss_raw[1]:.4f}", "Status": "Non-Stationary (Trending)"},
        {"Series": f"Differenced (d=1) {phase_key}", "ADF Stat": f"{adf_diff[0]:.4f}", "ADF p-value": f"{adf_diff[1]:.4f}", "KPSS p-value": f"{kpss_diff[1]:.4f}", "Status": "Stationary (Pass, p < 0.05)"}
    ])
    st.dataframe(stat_summary, use_container_width=True)


# --------------------------------------------------------------------
# TAB 7: FRANCHISE RIVALRIES & HEAD-TO-HEAD
# --------------------------------------------------------------------
def render_slide_7():
    st.subheader("⚔️ Franchise Rivalries & Head-to-Head Matrix")
    st.markdown("Explore all-time head-to-head records between any two franchises across 18 seasons:")
    
    c_t1, c_t2 = st.columns(2)
    core_franchises = sorted(df_h2h['team'].unique())
    default_a_idx = core_franchises.index("Chennai Super Kings") if "Chennai Super Kings" in core_franchises else 0
    if team_filter != "All Franchises" and team_filter in core_franchises:
        default_a_idx = core_franchises.index(team_filter)
        
    with c_t1:
        team_a = st.selectbox("Select Team 1:", core_franchises, index=default_a_idx)
    with c_t2:
        opp_list = [t for t in core_franchises if t != team_a]
        team_b = st.selectbox("Select Team 2:", opp_list, index=opp_list.index("Mumbai Indians") if "Mumbai Indians" in opp_list else 0)
        
    h2h_matchup = df_h2h[(df_h2h['team'] == team_a) & (df_h2h['opponent'] == team_b)]
    if len(h2h_matchup) > 0:
        row = h2h_matchup.iloc[0]
        
        c_h1, c_h2, c_h3, c_h4 = st.columns(4)
        c_h1.metric("Total Matches", f"{int(row['matches'])}")
        c_h2.metric(f"{team_a} Wins", f"{int(row['wins'])}")
        c_h3.metric(f"{team_b} Wins", f"{int(row['losses'])}")
        c_h4.metric(f"{team_a} Win %", f"{row['win_pct']:.1f}%")
        
    st.markdown(f"##### 📜 All Historic Matches: {team_a} vs {team_b}")
    h2h_matches = df_matches[
        ((df_matches['team1'] == team_a) & (df_matches['team2'] == team_b)) |
        ((df_matches['team1'] == team_b) & (df_matches['team2'] == team_a))
    ][['date', 'season', 'venue', 'toss_winner', 'toss_decision', 'winner', 'win_outcome', 'potm']].sort_values('date', ascending=False)
    
    st.dataframe(h2h_matches, use_container_width=True)


# --------------------------------------------------------------------
# TAB 8: IPL 2026 LIVE SEASON HUB
# --------------------------------------------------------------------
def render_slide_8():
    st.subheader("🏏 IPL 2026 Live Season Hub & Standings")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #7f1d1d 0%, #1e1b4b 100%); border: 2px solid #ef4444; border-radius: 12px; padding: 18px 24px; margin-bottom: 20px;">
        <h3 style="color: #fbbf24; margin: 0 0 6px 0;">🏆 ROYAL CHALLENGERS BENGALURU ARE IPL 2026 CHAMPIONS!</h3>
        <p style="color: #f8fafc; font-size: 1.05rem; margin-bottom: 8px;">
            <strong>Grand Final at Narendra Modi Stadium, Ahmedabad (May 31, 2026):</strong><br>
            RCB defeated Gujarat Titans by <strong>5 wickets</strong> (GT 155/8 in 20 ov vs RCB 161/5 in 18.0 ov).
        </p>
        <p style="color: #cbd5e1; font-size: 0.92rem; margin: 0;">
            👑 <strong>Captain:</strong> Rajat Patidar led RCB to their <strong>second consecutive championship</strong>, making RCB only the 3rd franchise (alongside CSK & MI) to successfully defend an IPL title.<br>
            ⭐ <strong>Player of the Match:</strong> <strong>Virat Kohli</strong> (unbeaten 75* off 42 balls, recording his fastest IPL fifty).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Current official standings, points table, top performers, and squad lists from the **IPL 2026 Season**:")
    
    st.markdown("##### 🏆 IPL 2026 Official Points Table")
    st.dataframe(df_2026_points, use_container_width=True)
    
    col_26_1, col_26_2 = st.columns(2)
    with col_26_1:
        st.markdown("##### 🏏 Leading Run Scorers (2026 Season)")
        st.dataframe(df_2026_batting[['position', 'batsman', 'team', 'runs', 'average', 'strike_rate', 'hundreds', 'fifties']].head(10), use_container_width=True)
    with col_26_2:
        st.markdown("##### 🎯 Leading Wicket Takers (2026 Season)")
        st.dataframe(df_2026_bowling[['position', 'bowler', 'team', 'wickets', 'economy', 'avg', 'bbi']].head(10), use_container_width=True)

    st.markdown("##### 👥 Official 2026 Franchise Squads")
    squad_team = st.selectbox("Select Team to View Squad:", sorted(df_2026_squads['team_name'].unique()))
    team_squad = df_2026_squads[df_2026_squads['team_name'] == squad_team][['player', 'nationality', 'role', 'designation']]
    st.dataframe(team_squad, use_container_width=True)


# --------------------------------------------------------------------
# TAB 9: INTERACTIVE SQL STUDIO
# --------------------------------------------------------------------
def render_slide_9():
    st.subheader("🗄️ Interactive SQL Studio (283,000+ Ball-by-Ball Warehouse)")
    st.markdown("Run live SQL queries directly on `ipl_master.db`:")
    
    MASTER_QUERIES = {
        "Query 1: Most POTM Awards in IPL History": """
SELECT player_name, potm_awards, runs, wickets, strike_rate, highest_score
FROM dim_players
ORDER BY potm_awards DESC
LIMIT 15;
        """,
        "Query 2: All-Time IPL Champions & Margins": """
SELECT season, champion, runner_up, final_venue, final_margin, player_of_final, player_of_tournament_mvp
FROM dim_ipl_champions
ORDER BY season DESC;
        """,
        "Query 3: All 15 Historic Super Overs & Match Heroes": """
SELECT date, season, match, venue, tied_score, super_over_winner, super_over_score, hero_potm
FROM fact_super_overs
ORDER BY season DESC;
        """,
        "Query 4: Franchise All-Time Trophy Leaderboard": """
SELECT team, titles, winning_years, finals_played, win_rate_in_finals
FROM dim_franchise_trophies
ORDER BY titles DESC, finals_played DESC;
        """,
        "Query 5: All-Time Orange Cap Kings (Most Runs)": """
SELECT player_name, matches, runs AS total_runs, average, strike_rate, fifties, hundreds
FROM dim_players
WHERE runs >= 2500
ORDER BY runs DESC
LIMIT 15;
        """,
        "Query 6: Stadium Chase Bias Rankings": """
SELECT venue, city, COUNT(*) AS matches_hosted,
       ROUND(100.0 * SUM(won_by_chasing) / COUNT(*), 2) AS chase_win_pct,
       ROUND(AVG(inn1_runs), 1) AS avg_par_score
FROM fact_matches
WHERE match_result = 'Normal Result'
GROUP BY venue, city
HAVING COUNT(*) >= 20
ORDER BY chase_win_pct DESC;
        """
    }
    
    q_choice = st.selectbox("Choose a Master Analytical Query:", list(MASTER_QUERIES.keys()))
    user_sql = st.text_area("SQL Editor:", value=MASTER_QUERIES[q_choice].strip(), height=160)
    
    if st.button("▶ Run SQL Query", type="primary"):
        try:
            conn = sqlite3.connect(DB_PATH)
            sql_res = pd.read_sql_query(user_sql, conn)
            conn.close()
            st.success(f"Query returned {len(sql_res)} records.")
            st.dataframe(sql_res, use_container_width=True)
            
            st.download_button(
                "📥 Export Query Results to CSV",
                sql_res.to_csv(index=False).encode('utf-8'),
                "ipl_master_query_results.csv",
                "text/csv"
            )
        except Exception as e:
            st.error(f"SQL Error: {str(e)}")




# ====================================================================
# MASTER SLIDE DECK & PRESENTATION CONTROLLER
# ====================================================================
SLIDES = [
    ("🏆 1. Champions & Trophies", "All 19 champions (2008–2026), RCB back-to-back title defense & franchise trophy rankings"),
    ("⚡ 2. Super Overs (15 Ties)", "Complete history of all 15 tied matches, super over scores & match heroes"),
    ("👑 3. Player Career Explorer", "Search full names (Rohit Sharma, Virat Kohli, MS Dhoni) for complete scorecard & phase strike rates"),
    ("🏟️ 4. Toss & Venues", "The Toss Paradox, stadium chase bias & 1,194 searchable match scorecards"),
    ("📊 5. Phase Velocity", "Scoring rate trends across Powerplay, Middle, and Death overs (2008–2026)"),
    ("📈 6. ARIMA Forecasts", "Phase-by-phase time-series forecasting models with ADF & KPSS diagnostics"),
    ("⚔️ 7. Franchise Rivalries", "CSK vs MI, head-to-head records & home fortress analysis"),
    ("🏏 8. IPL 2026 Season Hub", "RCB 2026 Title celebration, points table, squad lists & season leaders"),
    ("🗄️ 9. Interactive SQL", "Run custom SQL queries on 283,000+ CricSheet deliveries")
]
SLIDE_TITLES = [s[0] for s in SLIDES]
SECTION_RENDERERS = [
    render_slide_1, render_slide_2, render_slide_3,
    render_slide_4, render_slide_5, render_slide_6,
    render_slide_7, render_slide_8, render_slide_9
]

if 'slide_deck_scrubber' not in st.session_state:
    st.session_state.slide_deck_scrubber = 0

def go_prev_slide():
    if st.session_state.slide_deck_scrubber > 0:
        st.session_state.slide_deck_scrubber -= 1

def go_next_slide():
    if st.session_state.slide_deck_scrubber < len(SLIDES) - 1:
        st.session_state.slide_deck_scrubber += 1

current_slide = st.session_state.slide_deck_scrubber

# --- TOP SLIDE CONTROLLER ---
col_prev, col_center, col_next = st.columns([1.3, 5.4, 1.3])
with col_prev:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.button("◀️ Previous", disabled=(current_slide == 0), on_click=go_prev_slide, use_container_width=True, key="top_prev_btn")
with col_center:
    cur_title, cur_desc = SLIDES[current_slide]
    cur_pct = (current_slide + 1) / len(SLIDES)
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0b1329 0%, #1e293b 50%, #0f172a 100%); border: 1.5px solid rgba(56, 189, 248, 0.45); border-radius: 14px; padding: 14px 22px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.12);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
            <span style="background: rgba(56, 189, 248, 0.15); border: 1px solid #38bdf8; color: #38bdf8; font-size: 0.72rem; font-weight: 800; padding: 2px 10px; border-radius: 9999px; letter-spacing: 0.08em; text-transform: uppercase;">
                SLIDE {current_slide + 1} OF {len(SLIDES)}
            </span>
            <span style="font-size: 0.76rem; color: #94a3b8; font-weight: 700;">
                {int(cur_pct * 100)}% Through Presentation Deck
            </span>
        </div>
        <div style="font-size: 1.45rem; font-weight: 800; color: #f8fafc; margin: 4px 0 2px 0; letter-spacing: -0.01em;">{cur_title}</div>
        <div style="font-size: 0.86rem; color: #cbd5e1;">{cur_desc}</div>
        <div style="background: rgba(51, 65, 85, 0.6); border-radius: 9999px; height: 5px; width: 100%; margin-top: 10px; overflow: hidden;">
            <div style="background: linear-gradient(90deg, #38bdf8, #818cf8); height: 100%; width: {int(cur_pct * 100)}%; border-radius: 9999px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_next:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    st.button("Next ▶️", disabled=(current_slide == len(SLIDES) - 1), on_click=go_next_slide, use_container_width=True, key="top_next_btn")

# --- SLEEK INTERACTIVE SLIDE SCRUBBER ---
SHORT_SLIDE_NAMES = [
    "🏆 1. Champions",
    "⚡ 2. Super Overs",
    "👑 3. Players",
    "🏟️ 4. Toss & Venues",
    "📊 5. Phases",
    "📈 6. ARIMA",
    "⚔️ 7. Rivalries",
    "🏏 8. IPL 2026",
    "🗄️ 9. SQL Studio"
]

st.select_slider(
    "Slide Scrubber",
    options=list(range(len(SHORT_SLIDE_NAMES))),
    format_func=lambda i: SHORT_SLIDE_NAMES[i],
    label_visibility="collapsed",
    key="slide_deck_scrubber"
)

# Active slide index is driven by slide_deck_scrubber
active_slide = st.session_state.slide_deck_scrubber

st.markdown("---")

# Render Active Slide Content
SECTION_RENDERERS[active_slide]()

# Bottom Navigation Bar
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
b_col1, b_col2, b_col3 = st.columns([1.5, 4.0, 1.5])
with b_col1:
    st.button("◀️ Previous Slide", disabled=(active_slide == 0), on_click=go_prev_slide, use_container_width=True, key="btm_prev_btn")
with b_col3:
    st.button("Next Slide ▶️", disabled=(active_slide == len(SLIDES) - 1), on_click=go_next_slide, use_container_width=True, key="btm_next_btn")



st.markdown("---")
st.caption("IPL Enterprise Intelligence (2008–2026) • 283k+ CricSheet Deliveries • Streamlit • SQLite • Statsmodels ARIMA")
