# PRD: Single Source of Truth & Data-Driven Dashboard Architecture

## 1. Objective
Refactor the IPL Match Analytics & Phase Time-Series dashboard from static/hard-coded JavaScript arrays to a fully data-driven pipeline architecture. Eliminate all discrepancies between database queries, KPI summary cards, interactive charts, and player profile modals by injecting a centralized canonical `DATA` JSON payload generated directly from `ipl_master.db`.

## 2. Requirements & Acceptance Criteria
1. **Centralized Data Injection (`const DATA = ...;`)**:
   - `generate_dashboard_html.py` queries `ipl_master.db` and canonical CSVs to assemble a comprehensive `DATA` dictionary.
   - The dictionary is JSON-serialized and injected into `/*DATA*/` in `index.html` and `docs/index.html`.
2. **Dynamic Chart & UI Rendering**:
   - **Toss Conversion**: Pre-2016 vs Post-2016 (50.0% vs 52.8%) rendered from `DATA.toss`.
   - **Chase Win Rates**: Overall chase win rate (54.3%) and era rates rendered from `DATA.toss`.
   - **Venue Chase %**: Eden Gardens (57.4%), Wankhede (55.1%), Hyderabad (56.6%), Jaipur (64.1%) rendered from `DATA.venues`.
   - **Phase Run Rates**: Powerplay, Middle, and Death RPO trajectories through 2025 (2023: 10.49, 2024: 11.21, 2025: 10.96) rendered from `DATA.phase_rpo`.
   - **ARIMA vs Naive Backtest**: Observed Death RPO through 2025 (no rising forecast to 13.4, no 95% band) plus an empirical backtest evaluation table demonstrating ARIMA vs Naive performance.
   - **Career Runs**: Chart and profile cards read directly from `DATA.top_run_scorers` and `DATA.players` (Kohli: 8,661 thru 2025; Rohit: 7,046).
   - **Career Wickets**: Wickets chart and profile cards read directly from `DATA.top_wicket_takers` and `DATA.players` (Chahal: 205 wkts, 7.98 Econ; Bumrah: 165; Bravo: 183; Mishra: 174; Jadeja: 160).
   - **POTM Consistency**: Aligned single source across chart and cards (Kohli: 19, Rohit: 21 through 2025).
   - **Trophy Chart**: SRH strictly 1 title (2016) and Deccan Chargers 1 title (2009), rendered from `DATA.trophies`.
   - **Rivalries**: Head-to-head records derived dynamically from `matches` table (MI vs CSK: 39 matches, 21-18).
3. **Copy & Text Fixes**:
   - SQL tab: Update query header from 15 to 16 Historic Super Overs.
   - Title & footer: Remove "Enterprise Intelligence", replace with "IPL Match Analytics & Phase Time-Series (2008–2026)".
   - 2026 Super Over hero: Replace Mitchell Starc with Harshit Rana & Andre Russell.
4. **Oracle Verification Test Suite**:
   - Create `tests/test_dashboard_integrity.py` asserting that the Kohli KPI card, the runs chart data, and the Kohli player profile card display the exact same number (8,661).
   - Assert consistency across all rendered metrics.
