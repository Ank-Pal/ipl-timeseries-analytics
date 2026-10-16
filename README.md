# 🏏 IPL Enterprise Intelligence: Ball-by-Ball Analytics & Predictive Time-Series (2008–2026)

[![Live Interactive Dashboard](https://img.shields.io/badge/Live%20Demo-Interactive%20Dashboard-38bdf8?style=for-the-badge&logo=googlechrome&logoColor=white)](https://ank-pal.github.io/ipl-timeseries-analytics/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Database](https://img.shields.io/badge/SQL-SQLite%20Master%20DB-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Deliveries](https://img.shields.io/badge/Data-283k%2B%20Balls-success.svg)](https://cricsheet.org/)
[![Matches](https://img.shields.io/badge/Matches-1%2C193%20Matches-orange.svg)](https://www.kaggle.com/)
[![Time-Series](https://img.shields.io/badge/Model-Phase%20ARIMA-purple.svg)](https://www.statsmodels.org/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit%20Interactive-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)

The **Definitive IPL Sports Analytics & Econometric Forecasting Platform**, built on **283,000+ authentic ball-by-ball deliveries**, **1,193 genuine matches** across 18 seasons (2008–2025), and live **IPL 2026 season data**.

This repository answers every fundamental sports, economic, and tactical question about the Indian Premier League:
* **🏆 Season Champions & Trophy Cabinet**: Every champion, runner-up, final margin, MVP, Orange Cap, and Purple Cap from 2008 to 2026, plus franchise trophy rankings (MI: 5, CSK: 5, KKR: 3, SRH: 2, RR: 1, GT: 1).
* **⚡ All 15 Historic Super Overs**: Detailed breakdown of every tied thriller in IPL history, tied 20-over scores, super over scores, and hero POTM performances (including the legendary 2020 Double Super Over).
* **Player Dominance**: Most Player of the Match awards, Orange & Purple caps, and career phase strike rates across 788 profiled cricketers.
* **The Phase Revolution**: Econometric time-series modeling of **Powerplay (Overs 1–6)** vs **Death Overs (Overs 16–20)**, capturing the 2023–2026 **Impact Player rule explosion**.
* **The Real Toss & Dew Paradox**: Grounded in authentic day vs night dew data across India's iconic stadiums.
* **Franchise Rivalries**: Head-to-Head matrices (CSK vs MI, KKR vs RCB) and home ground fortress ratings.
* **IPL 2026 Live Season Hub**: Official standings, points table, top performers, and squad lists.

---

## 🏆 Key Records & Historical Leaderboards

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

* **The Impact Player Anomaly**: Introduced in 2023, the Impact Player rule allowed franchises to bat with 8 recognized hitters, causing death overs run-rates to shatter previous ceilings, surging from ~10.4 rpo to over **12.8+ rpo**.
* **ARIMA Projections**: Projects future phase boundaries with 95% Confidence Intervals.

---

## 🏗️ Repository Architecture

```
ipl-timeseries-analytics/
├── app.py                             # 🌟 Master 9-Tab Streamlit Dashboard (Live on port 8501)
├── data/
│   ├── raw/                           # Raw CricSheet & 2026 CSVs
│   └── processed/
│       ├── ipl_master.db              # High-performance SQLite warehouse (283k+ deliveries)
│       ├── ipl_champions_roll_of_honor.csv # All 18 champions, runners-up, MVPs, caps
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

### 3. Interactive Executive Dashboard
You have three easy ways to interact with the executive dashboard:
* **Option 1 (Online Live Demo)**: Click the **[Live Interactive Dashboard](https://ank-pal.github.io/ipl-timeseries-analytics/)** badge to view all interactive Plotly charts directly in your browser without installing anything.
* **Option 2 (Offline Standalone)**: Simply double-click [`outputs/dashboard_preview.html`](outputs/dashboard_preview.html) or `index.html` on your computer to open the interactive dashboard in any browser.
* **Option 3 (Local Streamlit Server)**: If running locally from the terminal:
  ```bash
  streamlit run app.py
  ```
  Then open your local browser to `http://localhost:8501` to explore all 9 tabs interactively!

---

## 🎙️ Elite Interview Talking Points

> *"For this project, I built an end-to-end sports intelligence and econometric forecasting platform analyzing over 283,000 official CricSheet deliveries across 1,193 matches from 2008 to the live 2026 season.*
>
> *I designed a multi-phase time-series architecture, evaluating Powerplay and Death Overs scoring trajectories independently. Using Augmented Dickey-Fuller and KPSS dual testing, I proved that death-over run-rates were non-stationary due to the 2023 Impact Player tactical disruption, requiring first-order differencing ($p < 0.0001$) before ARIMA fitting. Model residuals were verified as pure white noise ($p = 0.9997$ via Ljung-Box).*
>
> *On the business intelligence front, I developed a 7-tab interactive Streamlit application with live SQL querying, profiling 788 cricketers, tracking all 15 historic super overs, stadium chase biases, and franchise head-to-head rivalries like the CSK vs MI 'El Clásico'."*

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
