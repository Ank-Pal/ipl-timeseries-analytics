# 🏏 IPL Match Analytics & Phase Time-Series (2008–2026)

[![Live Interactive Dashboard](https://img.shields.io/badge/Live%20Demo-Interactive%20Dashboard-38bdf8?style=for-the-badge&logo=googlechrome&logoColor=white)](https://ank-pal.github.io/ipl-timeseries-analytics/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQL-SQLite%20Master%20DB-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Deliveries](https://img.shields.io/badge/Data-295k%2B%20Balls-success.svg)](https://cricsheet.org/)
[![Matches](https://img.shields.io/badge/Matches-1%2C243%20Ball--by--Ball-orange.svg)](https://cricsheet.org/)
[![Time-Series](https://img.shields.io/badge/Model-Phase%20ARIMA-purple.svg)](https://www.statsmodels.org/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit%20Interactive-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://ankur-pal-ipl-analytics.streamlit.app/)

> ℹ️ **Disclaimer & Non-Affiliation:** This is an independent, open-source data analytics and econometric research portfolio project built using public delivery data from CricSheet and tournament match reports. It is unofficial and is not affiliated with, endorsed by, or sponsored by the Board of Control for Cricket in India (BCCI) or the Indian Premier League (IPL).

> 📌 **Data Provenance & Lineage Notice:** The entire project data warehouse, SQL analytics, and statistical models are built on authentic **CricSheet** ball-by-ball delivery archives (`ipl_json.zip`, 1,243 matches, 295,732 deliveries) spanning all 19 seasons (2008–2026), downloaded in November 2026. The data is licensed under the [Open Data Commons Attribution License (ODC-By)](https://opendatacommons.org/licenses/by/1-0/). Automated ingestion is managed by `scripts/download_and_count_cricsheet.py` and `src/ingest_cricsheet.py`.

An end-to-end sports analytics platform and time-series forecasting pipeline analyzing **295,732 ball-by-ball deliveries** across **1,243 matches** spanning 19 editions (2008–2026):
* **2008–2026 (CricSheet Ball-by-Ball):** Complete coverage across all 19 seasons (1,243 matches with ball-by-ball logs). Exactly 8 matches across 2008, 2009, 2011, 2015, 2017, and 2024 were abandoned without a ball bowled (washouts), consistent with CricSheet's ball-by-ball scope.
* **16 Historic Super Overs:** Comprehensive ball-by-ball coverage and scorecard records of all 16 tied thrillers, from Cape Town 2009 to Lucknow 2026.
* **19 Season Champions:** Sourced from official tournament records, culminating in Royal Challengers Bengaluru defeating Gujarat Titans by 5 wickets in the 2026 Final (Virat Kohli POTM with 75* off 42).

---

## 🎯 Core Analytical Questions Investigated

1. **The Phase Scoring Shift & Impact Player Effect**:
   Scoring rates have drifted upward across tournament history, but the **2023 Impact Player rule** coincided with a marked shift in death-overs scoring (Overs 16–20), rising from an average of **10.11 RPO** (2019–2022, n=418 innings) to **10.92 RPO** (2023–2025, n=341 innings). A 10,000-iteration bootstrap confirms an observed difference of **+0.81 RPO** (95% CI: [0.40, 1.23] RPO). This shift coincides with deeper batting orders, pitch factors, and the 2022 franchise expansion.
2. **Empirical Toss Evaluation**:
   Testing toss outcomes across decided regular-season matches reveals **no detectable toss advantage; effects up to about 4 points cannot be excluded**:
   * **Overall**: Toss winners won the match **51.6%** of the time (95% Wilson CI: [48.7%, 54.5%]).
   * **Era Comparison**: Pre-2016 toss winners won at **50.0%**; Post-2016 toss winners won at **52.4%**. A two-proportion z-test yields $z = -0.95, p = 0.342$, showing no statistically significant era shift.
   * **Trend Logit Model**: Fitting a logistic regression $\text{Logit}(P(\text{MatchWin} \mid \text{TossWin})) \sim \text{Season}$ yields a coefficient of $+0.0018$ ($p = 0.870$), proving no secular trend.
3. **Venue Chase Bias & Multiple Testing Correction**:
   Testing venue-level chase proportions across major grounds:
   * **Unadjusted vs Family-Wise Correction**: While Sawai Mansingh Stadium, Jaipur exhibits an unadjusted chase rate of **64.1%** (raw $p \approx 0.03$), family-wise error rate correction across 13 major venues using the **Holm step-down procedure** yields an adjusted $p \approx 0.40$.
   * **Joint Heterogeneity Test**: A contingency chi-squared test across all major venues ($\chi^2 = 14.8, p = 0.25$) confirms that venue-to-venue chase variations are statistically consistent with chance and sampling variation.

---

## 🌧️ Abandoned Matches Accounting (The 8 Omitted CricSheet Matches)

CricSheet indexes ball-by-ball delivery records; fixtures abandoned without a ball bowled generate no delivery events. The 8 missing fixtures between official tournament schedules and ball-by-ball logs are:

1. **2008-05-18**: Delhi Daredevils vs Kolkata Knight Riders (Feroz Shah Kotla, Delhi) — Rain / Washout
2. **2009-04-21**: Delhi Daredevils vs Chennai Super Kings (Kingsmead, Durban) — Rain / Washout
3. **2011-04-19**: Kolkata Knight Riders vs Chennai Super Kings (Eden Gardens, Kolkata) — Rain / Washout
4. **2015-04-26**: Kolkata Knight Riders vs Rajasthan Royals (Eden Gardens, Kolkata) — Rain / Washout
5. **2017-04-25**: Royal Challengers Bangalore vs Sunrisers Hyderabad (M Chinnaswamy, Bengaluru) — Rain / Washout
6. **2024-05-13**: Gujarat Titans vs Kolkata Knight Riders (Narendra Modi Stadium, Ahmedabad) — Rain / Washout
7. **2024-05-16**: Sunrisers Hyderabad vs Gujarat Titans (Rajiv Gandhi Stadium, Hyderabad) — Rain / Washout
8. **2024-05-19**: Rajasthan Royals vs Kolkata Knight Riders (Barsapara Stadium, Guwahati) — Rain / Washout

*Scheduled totals (1,251) minus the 8 washouts equals exactly **1,243 ball-by-ball matches** in our SQLite warehouse.*

---

## 🏆 Tournament Roll of Honor & Leaderboards

### 1. Most Player of the Match (POTM) Awards in History
| Rank | Player Name | POTM Awards | Career Runs | Career Wickets |
| :---: | :--- | :---: | :---: | :---: |
| **1** | **AB de Villiers** | **25 🏅** | 5,162 | — |
| **2** | **Chris Gayle** | **22 🏅** | 4,965 | 18 |
| **3** | **Rohit Sharma** | **21 🏅** | 7,046 | 15 |
| **4** | **Virat Kohli** | **19 🏅** | 8,661 | 4 |
| **5** | **David Warner** | **18 🏅** | 6,565 | — |
| **6** | **MS Dhoni** | **18 🏅** | 5,439 | — |

### 2. All-Time Run Leaders (Settled Career Benchmark Through 2025 / 2026)
* **Virat Kohli**: **8,661 runs** through 2025 (9,336 all-time through 2026; 8 centuries, 58 fifties)
* **Rohit Sharma**: **7,046 runs** through 2025 (2 centuries, 44 fifties; 5-time championship captain)
* **Shikhar Dhawan**: **6,769 runs** (768 fours — all-time leading boundary hitter)
* **David Warner**: **6,565 runs** (3-time Orange Cap winner: 2015, 2017, 2019)
* **MS Dhoni**: **5,439 runs** (2,789 death-over runs; 5-time championship captain)

### 3. All-Time Leading Wicket Takers (Legitimate Bowler Wickets)
* **Yuzvendra Chahal**: **205 wickets** through 2024 (233 all-time through 2026; 7.98 Econ)
* **Piyush Chawla**: **192 wickets** (7.96 Econ)
* **Jasprit Bumrah**: **165 wickets** through 2024 (187 all-time through 2026; 7.49 Econ)
* **Dwayne Bravo**: **183 wickets** (Retired 2022; 8.38 Econ)
* **Bhuvneshwar Kumar**: **181 wickets** through 2024 (226 all-time through 2026; 7.55 Econ)
* **Sunil Narine**: **180 wickets** through 2024 (207 all-time through 2026; 6.73 Econ — best economy in tournament history)
* **Ravichandran Ashwin**: **180 wickets** through 2024 (187 all-time through 2026; 7.12 Econ)
* **Lasith Malinga**: **170 wickets** (19.8 bowling average)

### 4. 2026 Season Awards
* **Champions**: Royal Challengers Bengaluru (def. Gujarat Titans by 5 wickets in Ahmedabad)
* **Player of the Final**: Virat Kohli (75* off 42 balls)
* **Orange Cap (Most Runs)**: Vaibhav Sooryavanshi (Rajasthan Royals) — **776 runs**
* **Purple Cap (Most Wickets)**: Kagiso Rabada (Gujarat Titans) — **29 wickets**
* **Tournament MVP**: Vaibhav Sooryavanshi (RR)

---

## ⚡ Econometric Time-Series & Phase Diagnostics (ARIMA Backtest)

Rather than treating cricket as a single static run-rate, this platform models phase-level scoring rates and evaluates 1-step-ahead forecasts against standard baselines across expanding historical windows:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Expanding Window 1-Step-Ahead Forecast Evaluation (Hold-Out Evaluation)                │
├───────────────────────────────┬────────────────────────────┬───────────────────────────┤
│ Match Phase                   │ ARIMA(0,1,0) + Drift       │ Naive Baseline (Last Year)│
│                               │ MAE  /  RMSE               │ MAE  /  RMSE              │
├───────────────────────────────┼────────────────────────────┼───────────────────────────┤
│ Powerplay (Overs 1–6)         │ 0.340  /  0.420 (Slight)   │ 0.410  /  0.480           │
│ Middle Overs (Overs 7–15)     │ 0.310  /  0.380 (Tied)     │ 0.330  /  0.410           │
│ Death Overs (Overs 16–20)     │ 0.620  /  0.740            │ 0.510  /  0.610 (Best)    │
└───────────────────────────────┴────────────────────────────┴───────────────────────────┘
```

> **Model Evaluation Takeaway:**
> * **Death Overs Step Change**: The simple naive baseline outperforms ARIMA in death overs (MAE 0.51 vs 0.62). The 2023 Impact Player rule caused a structural step change that plateaued (2023: 10.49, 2024: 11.21, 2025: 10.96) rather than escalating continuously past 12.0 RPO.
> * **No Long-Range Predictive Drift**: In small annual samples ($N=19$), simple random-walk persistence provides a more robust benchmark than high-order polynomial extrapolation.

---

## 🏗️ Repository Architecture

```
ipl-timeseries-analytics/
├── app.py                             # 🌟 Master 9-Slide Interactive Dashboard & Executive Deck
├── index.html                         # 🚀 GitHub Pages production dashboard
├── docs/index.html                    # 🚀 Synchronized GitHub Pages doc source
├── data/
│   ├── raw/cricsheet/                 # 1,243 authentic CricSheet JSON match files
│   └── processed/
│       ├── ipl_master.db              # High-performance SQLite warehouse (295k+ deliveries, 1,243 matches)
│       ├── ipl_champions_roll_of_honor.csv # All 19 champions, runners-up, MVPs, caps
│       ├── historic_super_overs.csv   # All 16 tie matches, tied & SO scores, heroes
│       ├── franchise_trophies.csv     # Franchise trophy rankings & finals win conversion
│       └── ipl_2026_points_table.csv  # 2026 final standings (14 matches each)
├── src/
│   ├── venues.py                      # Canonical mapping of all 41 venue variations to 36 grounds
│   ├── ingest_cricsheet.py            # Production parser of 1,243 JSON matches & 295k deliveries
│   ├── build_data_payload.py          # Compiles single-source-of-truth DATA payload
│   ├── generate_dashboard_html.py     # Injects DATA and compiles index.html & docs/index.html
│   ├── player_analytics.py            # Computes dim_players, POTM, and death strike rates
│   └── load_champions_and_superovers.py # Ingests champions, trophies & super overs
├── scripts/
│   ├── download_and_count_cricsheet.py # Automated CricSheet archive downloader & verification
│   └── verify_step2_checks.py         # Step 2 Oracle verification suite
├── tests/
│   ├── test_dashboard_integrity.py    # Asserts HTML, DATA, KPI, and table consistency
│   └── test_streamlit_integrity.py    # Asserts Streamlit app and database coherence
├── requirements.txt                   # Python dependencies
└── README.md                          # Repository documentation
```

---

## 🚀 Quickstart & How to Run

### 1. Ingestion & Build Pipeline
```bash
python scripts/download_and_count_cricsheet.py
python src/ingest_cricsheet.py
python src/player_analytics.py
python src/load_champions_and_superovers.py
python src/generate_dashboard_html.py
python -m pytest tests/ -v
```

### 2. 🌐 Live Interactive Dashboards
* 🚀 **[Fast Web Dashboard (GitHub Pages)](https://ank-pal.github.io/ipl-timeseries-analytics/)** — Instant client-side interactive deck (100% uptime, zero cold starts)
* ⚡ **[Live Python Server (Streamlit Cloud)](https://ankur-pal-ipl-analytics.streamlit.app/)** — Interactive Python runtime with dynamic SQL queries & phase filters

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE). Ball-by-ball delivery records courtesy of [CricSheet](https://cricsheet.org/) under [ODC-By](https://opendatacommons.org/licenses/by/1-0/).
