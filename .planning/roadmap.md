# Implementation Roadmap: Dual-Platform Synchronization & Sports Data Integrity

## Phase 1: Database Rectification & Pipeline Verification
- Fix 2010 season bug in `fact_matches` and `ingest_real_data.py`.
- Verify all 19 seasons (2008–2026) across `fact_matches`, `matches`, and `fact_phase_summary`.
- Re-run `build_data_payload.py` to produce updated, verified metrics.

## Phase 2: GitHub Pages Dashboard Refactor
- Refactor `src/generate_dashboard_html.py`:
  - Enhance `openTab` slide transition script with `setTimeout` + `Plotly.Plots.resize` on visible elements to eliminate crushed charts.
  - Fix `chart-trophies` to render only title winners ($\ge 1$ titles) with canonical franchise colors.
  - Maintain 100% synchronization between `index.html`, `docs/index.html`, and `outputs/dashboard_preview.html`.

## Phase 3: Streamlit Application Harmonization
- Update `app.py`:
  - Replace legacy "Enterprise Intelligence" branding with "IPL Match Analytics & Phase Time-Series (2008–2026)".
  - Update mentions to 19 Champions and 16 Super Overs (including Query 3 header in Slide 9).
  - Enhance Slide 6 with empirical ARIMA vs Naive backtest table and stationarity proof.
  - Add career milestone framing note to Slide 3.
  - Bump cache key in `load_master_data`.

## Phase 4: Oracle Verification & CodeRabbit Review
- Update `tests/test_dashboard_integrity.py` and create `tests/test_streamlit_integrity.py`.
- Run full test suite to 100% green pass.
- Conduct CodeRabbit review for correctness, security, and edge cases.
- Commit and push to `origin/main`.
