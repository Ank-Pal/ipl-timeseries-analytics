# Phase 1 Plan: Dual-Platform Synchronization

### Task 1: Database & Payload Rectification
- Verify `fact_matches` season counts (60 matches in 2010; 1,194 total).
- Re-run `build_data_payload.py` to compile the single-source-of-truth `DATA` payload.

### Task 2: HTML Generator Enhancement
- Update `src/generate_dashboard_html.py`:
  - Enhance `openTab` with deferred Plotly resize handler.
  - Refactor `chart-trophies` to display only champions with dedicated team colors.
  - Generate synchronized `index.html` and `docs/index.html`.

### Task 3: Streamlit Application Update
- Update `app.py` headers, super over counts, champions counts, Slide 6 backtest table, and Slide 9 query titles.

### Task 4: Oracle Tests & Verification
- Run `tests/test_dashboard_integrity.py` and `tests/test_streamlit_integrity.py`.
- Conduct CodeRabbit review.
