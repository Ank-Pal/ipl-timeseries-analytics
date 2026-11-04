# Implementation Roadmap: Dashboard Data Architecture & Oracle Verification

## Phase 1: Data Pipeline Extraction & Metric Harmonization
- Extract canonical metrics from `ipl_master.db` (matches, deliveries, dim_players, dim_franchise_trophies, fact_super_overs).
- Calculate canonical Toss & Venue chase stats (using `src/venues.py` canonical mappings).
- Calculate empirical Phase Run Rates (Powerplay, Middle, Death) through 2025.
- Compute ARIMA vs Naive out-of-sample backtest table and stationarity diagnostics.
- Fix 2026 super over hero line in `historic_super_overs.csv`.

## Phase 2: Centralized Injection Script (`generate_dashboard_html.py`)
- Define the canonical `build_data_payload()` returning `DATA` dictionary.
- Inject `const DATA = { ... };` directly into `index.html` and `docs/index.html`.
- Update static text (SQL tab query title to 16, page title and footer removing "Enterprise Intelligence").

## Phase 3: Client JavaScript Refactoring
- Refactor Plotly charts (`chart-trophies`, `chart-potm`, `chart-runs`, `chart-toss-paradox`, `chart-venue-chase`, `chart-phase-trajectories`, `chart-arima-evaluation`) to read directly from `DATA`.
- Refactor `playerProfiles` and card explorer functions to read directly from `DATA.players`.
- Ensure all charts, tables, cards, and KPI cards share the exact same numbers.

## Phase 4: Oracle Verification & GitHub Deployment
- Implement `tests/test_dashboard_integrity.py` asserting consistency between KPI cards, Plotly charts, and player profile cards.
- Run tests and verify 100% green pass.
- Commit and push to `origin/main`.
- Verify GitHub Actions deployment status.
