# Phase 1 Plan: Granular Tasks & Acceptance Criteria

### Task 1.1: Canonical Metrics Computation
- Compute:
  - Toss win conversion by era: Pre-2016 (50.0%), Post-2016 (52.8%).
  - Chase win conversion by era: Pre-2016 (53.3%), Post-2016 (54.8%), Overall (54.1% - 54.3%).
  - Venue chase win rates for top 12 venues with canon mapping (Eden: 57.4%, Wankhede: 55.5%, Hyderabad: 56.6%, Jaipur: 64.1%).
  - Annual Phase RPO (2008–2025): Powerplay, Middle, Death (2023: 10.49, 2024: 11.21, 2025: 10.96).
  - Out-of-sample Naive vs ARIMA backtest metrics for Death overs.
  - ADF and KPSS empirical test results.
  - Head-to-head rivalries from `matches` table.
- Acceptance Criteria: Python verification script returns clean dict without synthetic artifacts.

### Task 1.2: Correct 2026 Super Over Hero
- In `data/processed/historic_super_overs.csv`, replace Mitchell Starc with Harshit Rana & Andre Russell for 2026 LSG vs KKR.
- Acceptance Criteria: `csv` shows Harshit Rana & Andre Russell.

### Task 1.3: Update `generate_dashboard_html.py` with `DATA` injection
- Implement `compile_dashboard_data()` in `generate_dashboard_html.py`.
- Serialize `DATA` to JSON and inject as `const DATA = ...;` in HTML.
- Update HTML template: Replace hardcoded Plotly arrays with `DATA.*` mappings.
- Replace hardcoded `playerProfiles` in JS with `DATA.players`.
- Replace static Rivalries table with dynamic `DATA.rivalries`.
- Replace static ADF/KPSS table with empirical `DATA.stationarity`.
- Update header title, tab title, footer text, and SQL tab header to 16.

### Task 1.4: Oracle Test Suite
- Write `tests/test_dashboard_integrity.py`.
- Verify:
  - `Kohli KPI == Runs Chart x[0] == playerProfiles['KOHLI'].runs == 8661`
  - `Chahal KPI econ == 7.98`
  - `SRH trophies == 1 and Deccan Chargers == 1`
  - `No mention of "Enterprise Intelligence" in title/footer`
  - `Super overs == 16`
- Run test and ensure it passes.
