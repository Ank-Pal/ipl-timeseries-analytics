# 🏏 IPL Ball-by-Ball Analytics & Predictive Phase Time-Series (2008–2026)

[![Live Interactive Dashboard](https://img.shields.io/badge/Live%20Demo-Interactive%20Dashboard-38bdf8?style=for-the-badge&logo=googlechrome&logoColor=white)](https://ank-pal.github.io/ipl-timeseries-analytics/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQL-SQLite%20Master%20DB-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Deliveries](https://img.shields.io/badge/Data-283k%2B%20Balls-success.svg)](https://cricsheet.org/)
[![Matches](https://img.shields.io/badge/Matches-1%2C194%20Matches-orange.svg)](https://www.kaggle.com/)
[![Time-Series](https://img.shields.io/badge/Model-Phase%20ARIMA-purple.svg)](https://www.statsmodels.org/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit%20Interactive-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://ankur-pal-ipl-analytics.streamlit.app/)

An end-to-end sports analytics platform and time-series forecasting pipeline built on **283,000+ ball-by-ball deliveries** across **1,194 matches** spanning 19 tournament editions (2008–2026):
* **2008–2024 (Official Ground Truth):** 17 completed official seasons sourced from [CricSheet](https://cricsheet.org/) (260,000+ deliveries, 1,095 matches).
* **2025–2026 (Predictive Simulation Hub):** Forward tournament simulations and prospective playoff modeling built on post-auction squad rosters and phase scoring distributions.

---

## 🎯 Core Analytical Questions Investigated

1. **The Phase Scoring Shift (Powerplay vs Death Overs)**:
   Scoring rates have drifted upward across tournament history, but the **2023 Impact Player rule** coincided with an unprecedented structural break in death-overs scoring (Overs 16–20), surging from a ~10.4 RPO ceiling to over **12.8+ RPO** as teams bat with 8 recognized hitters.
2. **The Modern Toss & Chase Paradox**:
   Between 2008 and 2015, winning the toss conferred a noticeable match-win edge (~54.2%). In the modern era, despite teams choosing to field first in ~74% of matches to capitalize on second-innings dew proxies, the toss-to-win correlation has flattened to ~50.2% (statistically indistinguishable from a coin flip).
3. **Phase-Specific Strike Rate Titans**:
   Isolated phase-level leaderboards reveal extreme specialization: death-overs monsters like **AB de Villiers (232.5 SR)**, **Liam Livingstone (227.8 SR)**, and **Andre Russell (206.8 SR)** convert late-inning balls into runs at double the rate of standard middle-overs anchors.

---

## 🏆 Tournament Roll of Honor & Leaderboards

> **Data Classification Note:** Champions from 2008 to 2024 represent official verified BCCI tournament results. 2025 and 2026 reflect forward simulated tournament outcomes modeled from prospective squad compositions and phase metrics.

### 1. Most Player of the Match (POTM) Awards in History
| Rank | Player Name | POTM Awards | Career Runs | Career Wickets |
| :---: | :--- | :---: | :---: | :---: |
| **1** | **AB de Villiers** | **25 🏅** | 5,162 | — |
| **2** | **Chris Gayle** | **22 🏅** | 4,965 | 18 |
| **3** | **Rohit Sharma** | **19 🏅** | 6,628 | 15 |
| **4** | **Virat Kohli** | **18 🏅** | 8,004 | 4 |
| **5** | **David Warner** | **18 🏅** | 6,565 | — |
| **6** | **MS Dhoni** | **17 🏅** | 5,243 | — |

### 2. All-Time Orange Cap Titans (Most Runs)
* **Virat Kohli**: 8,000+ runs (Avg: 38.6, SR: 131.9, 8 Centuries, 55 Fifties)
* **Shikhar Dhawan**: 6,769 runs (Avg: 35.3, SR: 127.1, 2 Centuries, 51 Fifties)
* **Rohit Sharma**: 6,628 runs (Avg: 29.7, SR: 131.1, 2 Centuries, 43 Fifties)
* **David Warner**: 6,565 runs (Avg: 40.5, SR: 139.7, 4 Centuries, 62 Fifties)

### 3. All-Time Purple Cap Titans (Most Wickets)
* **Yuzvendra Chahal**: 205+ wickets (Econ: 7.68)
* **Dwayne Bravo**: 183 wickets (Econ: 8.38)
* **Bhuvneshwar Kumar**: 181 wickets (Econ: 7.55)
* **Sunil Narine**: 180 wickets (Econ: 6.73 — Best economy in tournament history)
* **Jasprit Bumrah**: 165+ wickets (Econ: 7.30)

### 4. Phase Specialists: Death Overs Monsters (Overs 16–20)
*(Highest strike rates in tournament history with min 300 death overs runs)*
* **Liam Livingstone**: **227.8 SR**
* **AB de Villiers**: **232.5 SR**
* **Andre Russell**: **206.8 SR**
* **Heinrich Klaasen**: **205.2 SR**
* **Dinesh Karthik**: **189.4 SR**
* **MS Dhoni**: **185.8 SR** (Most death overs runs in IPL history: 2,700+ runs)

---

## ⚡ Econometric Time-Series & Phase Forecasting (ARIMA)

Rather than treating cricket as a single static run-rate, this platform isolates match phases to model tactical modernization:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Phase Time Series (2008–2026) ──► Stationarity Testing (ADF & KPSS) ──► ARIMA Modeling │
├───────────────────────────────┬──────────────────────────────────┬─────────────────────┤
│ Match Phase                   │ Stationarity Proof (Diff d=1)    │ Ljung-Box Residuals │
├───────────────────────────────┼──────────────────────────────────┼─────────────────────┤
│ Powerplay (Overs 1–6)         │ ADF: p = 0.0435 (Stationary)     │ p = 0.9985 (White)  │
│ Middle Overs (Overs 7–15)     │ ADF: p = 0.0285 (Stationary)     │ p = 0.9996 (White)  │
│ Death Overs (Overs 16–20)     │ ADF: p = 0.0000 (Stationary)     │ p = 0.9997 (White)  │
└───────────────────────────────┴──────────────────────────────────┴─────────────────────┘
```

* **The Impact Player Anomaly**: Introduced in 2023, the Impact Player rule coincided with death overs run-rates surging from ~10.4 RPO to over **12.8+ RPO** as teams fielded extended batting lineups.
* **ARIMA Projections**: Projects future phase boundaries with 95% Confidence Intervals.
* **Methodology Caveat**: With $N=19$ annual aggregated data points, the ARIMA model serves as an exploratory macro-level trend projection across tournament eras rather than an asymptotic micro-level proof.

---

## 🏗️ Repository Architecture

```
ipl-timeseries-analytics/
├── app.py                             # 🌟 Master 9-Slide Interactive Dashboard & Executive Deck
├── data/
│   ├── raw/                           # Raw CricSheet & 2026 CSVs
│   └── processed/
│       ├── ipl_master.db              # High-performance SQLite warehouse (283k+ deliveries)
│       ├── ipl_champions_roll_of_honor.csv # All 19 champions, runners-up, MVPs, caps
│       ├── historic_super_overs.csv   # All 15 tie matches, tied & SO scores, heroes
│       ├── franchise_trophies.csv     # Franchise trophy rankings & finals win conversion
│       ├── player_career_stats.csv    # Career batting, bowling, POTM profiles for 788 players
│       ├── phase_annual_runrates.csv  # Powerplay, Middle, Death overs annual run-rates
│       └── h2h_rivalry_records.csv    # All franchise head-to-head records
├── sql/
│   └── master_queries.sql             # 12 production SQL queries answering all IPL questions
├── src/
│   ├── ingest_real_data.py            # Cleans and ingests 283k balls & 2026 stats
│   ├── load_champions_and_superovers.py # Ingests champions, trophies & super overs
│   ├── player_analytics.py            # Computes POTM, Orange/Purple caps, Death strike rates
│   ├── phase_arima_forecasting.py     # Dual stationarity tests, ARIMA grid search & forecast
│   └── run_pipeline.py                # Automated one-click pipeline runner
├── powerbi/
│   ├── data_model_architecture.md     # Star Schema specifications
│   ├── dax_measures.dax               # 30+ copy-paste production DAX measures
│   └── dashboard_design_guide.md      # Multi-page layout wireframes
├── outputs/
│   ├── figures/                       # Publication plots (POTM, Death SR, Phase ARIMA)
│   ├── phase_arima_summary.json       # Forecast metrics & test statistics
│   └── dashboard_preview.html         # Standalone client-side interactive HTML dashboard
├── requirements.txt                   # Python dependencies
└── README.md                          # Repository documentation
```

---

## 🖼️ Publication Figures & Analytical Visualizations

All figures are automatically generated in publication quality (300 DPI) inside `outputs/figures/`:

### 1. Econometric Time-Series & Phase Forecasting (ARIMA)
| Overall Tournament Run-Rate Forecast | Phase Scoring Trajectories (Powerplay vs Death) |
| :---: | :---: |
| <img src="outputs/figures/arima_runrate_forecast.png" alt="ARIMA Run Rate Forecast" width="460" /> | <img src="outputs/figures/phase_runrate_trajectories.png" alt="Phase Run Rate Trajectories" width="460" /> |
| *ARIMA forecasting IPL scoring inflation past 9.5 RPO* | *Impact Player rule exploding death overs to 12.8+ RPO* |

### 2. Player Dominance & Strike Rate Titans
| Top Player of the Match (POTM) Awards | Death Overs Strike Rate Kings (Overs 16–20) |
| :---: | :---: |
| <img src="outputs/figures/top_potm_awards.png" alt="Top POTM Awards" width="460" /> | <img src="outputs/figures/death_overs_strike_rate_kings.png" alt="Death Overs Strike Rate Kings" width="460" /> |
| *AB de Villiers (25) & Chris Gayle (22) leading history* | *Livingstone (228 SR) & De Villiers (233 SR) death dominance* |

### 3. Tactical Insights: Toss Paradox & Venue Chase Bias
| The Toss & Dew Paradox (Day vs Night Shifts) | Stadium Chase Bias & Win Probability |
| :---: | :---: |
| <img src="outputs/figures/toss_paradox_era_shift.png" alt="Toss Paradox Era Shift" width="460" /> | <img src="outputs/figures/venue_chase_bias.png" alt="Venue Chase Bias" width="460" /> |
| *Evolution of toss advantage across modern IPL eras* | *Chinnaswamy & Wankhede second-innings chase advantage* |

---

## 🚀 Quickstart & How to Run

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/Ank-Pal/ipl-timeseries-analytics.git
cd ipl-timeseries-analytics
pip install -r requirements.txt
```

### 2. Run the Ingestion & Analytics Pipeline
```bash
python src/run_pipeline.py
python src/load_champions_and_superovers.py
```

### 3. 🌐 Live Interactive Dashboards
Launch the full interactive sports intelligence deck directly in your browser with zero installation:

* 🚀 **[Fast Web Dashboard (GitHub Pages)](https://ank-pal.github.io/ipl-timeseries-analytics/)** — Instant client-side interactive deck (100% uptime, zero cold starts)
* ⚡ **[Live Python Server (Streamlit Cloud)](https://ankur-pal-ipl-analytics.streamlit.app/)** — Interactive Python runtime with dynamic SQL queries & phase filters

> **Explore all 9 Interactive Modules**:
> * 🏆 **Champions & Trophies**: All 19 champions & RCB back-to-back 2025–2026 title defense
> * ⚡ **Historic Super Overs**: Complete archive of all 15 tied thrillers & super over scores
> * 👑 **Player Hall of Fame**: Full career scorecards & phase strike rates for 788 cricketers
> * 🏟️ **Toss & Venues**: Stadium chase biases, dew analysis & 1,194 searchable match records
> * 📊 **Phase Velocity**: Powerplay vs Death-overs run-rates & Impact Player surge
> * 📈 **ARIMA Forecasts**: Time-series econometric models with ADF/KPSS diagnostics
> * ⚔️ **Franchise Rivalries**: Head-to-Head matrices (CSK vs MI El Clásico) & fortress ratings
> * 🏏 **IPL 2026 Season Hub**: Live standings, points table, squad lists & award leaders
> * 🗄️ **Interactive SQL Studio**: Run live SQL queries on 283,000+ CricSheet deliveries

### 4. 💻 Running Locally with Streamlit (Optional)
If running locally from your terminal:
```bash
streamlit run app.py
```
Then open your local browser to `http://localhost:8501`.

---

## 📚 Technical Interview Preparation

Structured talking points, econometric stationarity proofs, and sample Q&A for data analyst & sports analytics interviews are documented in [`docs/interview_prep.md`](docs/interview_prep.md).

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
