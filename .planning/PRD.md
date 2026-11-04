# PRD: Single Source of Truth & Dual-Platform Architecture

## 1. Objective
Refactor and synchronize both the static GitHub Pages dashboard (`https://ank-pal.github.io/ipl-timeseries-analytics/`) and the interactive Streamlit Cloud application (`https://ankur-pal-ipl-analytics.streamlit.app/`). Eliminate all data discrepancies, resolve chart resizing/layout bugs across tab navigation, and ensure 100% adherence to verified CricSheet historical cricket data (2008–2026).

## 2. Requirements & Acceptance Criteria
1. **Database Warehouse Rectification**:
   - `fact_matches` in `data/processed/ipl_master.db` must include all 19 seasons (2008–2026), including all 60 matches from the 2010 season (previously misattributed to 2009).
   - Season count distribution: 2008 (58), 2009 (57), 2010 (60), 2011 (73), 2012 (74), 2013 (76), 2014 (60), 2015 (59), 2016 (60), 2017 (59), 2018 (60), 2019 (60), 2020 (60), 2021 (60), 2022 (74), 2023 (74), 2024 (71), 2025 (74), 2026 (25). Total: 1,194 matches.
2. **Chart Visibility & Layout Integrity**:
   - `openTab` slide switching in `index.html` must automatically invoke `Plotly.Plots.resize` on all visible charts via `setTimeout` / layout reflow, eliminating crushed or 0-width charts when navigating slides.
   - `chart-trophies` must only render champion franchises ($\ge 1$ titles) sorted cleanly with official franchise colors (MI, CSK, KKR, RCB, SRH, RR, GT, Deccan Chargers).
3. **Dual Deployment Synchronization**:
   - GitHub Pages (`index.html` and `docs/index.html`) must remain byte-for-byte identical.
   - Streamlit App (`app.py`) must be harmonized: update titles (remove legacy "Enterprise Intelligence"), reflect 19 Champions and 16 Super Overs, include the empirical ARIMA vs Naive backtest table, and frame career milestones transparently.
4. **Sports Researcher Data Integrity**:
   - Player career milestones: Virat Kohli (8,661 runs through 2025; 8,889 in 2026*), Rohit Sharma (7,046 runs through 2025; 7,183 in 2026*), Yuzvendra Chahal (205 wickets, 7.98 economy), Jasprit Bumrah (165 wickets, 7.49 economy), Bravo (183 wickets).
   - Deccan Chargers (2009, 1 Title) and Sunrisers Hyderabad (2016, 1 Title) separated.
   - 2026 Super Over hero: Harshit Rana & Andre Russell.
5. **Oracle Verification Suite**:
   - All tests in `tests/test_dashboard_integrity.py` and `tests/test_streamlit_integrity.py` must pass 100% green.
