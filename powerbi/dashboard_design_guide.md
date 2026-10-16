# Power BI Dashboard Design Guide: IPL Time-Series Analytics

This guide details the complete 3-page interactive report layout for Power BI Desktop.

---

## Global Report Theme & Formatting Standards
* **Color Palette**:
  * Primary Accent: Deep Cricket Blue (`#1E3A8A`)
  * Secondary Accent: Sunset Orange (`#EA580C`)
  * Chase Indicator (Green): `#16A34A`
  * Defend Indicator (Red/Amber): `#DC2626`
  * Background: Slate Light (`#F8FAFC`) with pure white visual containers (`#FFFFFF`).
* **Visual Styling**: Card visual corners rounded to `8px`, subtle drop shadow enabled, consistent padding.
* **Global Filter Pane**:
  * Season Slicer (Range slider: 2008–2024)
  * Era Slicer (Radio button: All / Pre-2016 / Post-2016)
  * Match Type Slicer (Buttons: Day / Night)

---

## Page 1: The Toss Paradox: Strategic Shift & Tactical Parity

### Objective
Showcase how the toss went from a statistically significant advantage (pre-2016) to coin-flip parity (post-2016) as teams prioritized fielding first.

### Visual Layout Grid (16:9 Canvas)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [HEADER]: IPL Toss Paradox & Strategic Chasing Analysis (2008–2024)                   │
├───────────────┬────────────────┬────────────────┬─────────────────────┬────────────────┤
│ [KPI CARD 1]  │ [KPI CARD 2]   │ [KPI CARD 3]   │ [KPI CARD 4]        │ [KPI CARD 5]   │
│ Total Matches │ Pre-2016 Toss% │ Post-2016 Toss%│ Dilution Delta      │ Field First %  │
│ 1,099         │ 55.1%          │ 52.6%          │ -2.5% (p > 0.05)    │ 46.4% -> 73.2% │
├───────────────┴────────────────┴────────────────┴─────────────────────┴────────────────┤
│ [VISUAL 1: Clustered Column Chart]              │ [VISUAL 2: Ribbon/Area Chart]        │
│ Title: Toss Win % vs Field Decision % by Era   │ Title: 3-Year Rolling Chase vs Toss  │
│ X-Axis: dim_seasons[era]                        │ X-Axis: dim_seasons[season_year]     │
│ Values:                                         │ Values:                              │
│  - [Toss-to-Win Conversion Rate %]              │  - [Rolling 3-Season Chase Win %]    │
│  - [Field First Decision %]                     │  - [Toss-to-Win Conversion Rate %]   │
│  - [Overall Chase Win %]                        │ Constant line at 50%                 │
├─────────────────────────────────────────────────┴──────────────────────────────────────┤
│ [VISUAL 3: Clustered Bar Chart - Venue Chase Bias]                                     │
│ Y-Axis: dim_venues[venue_name] | X-Axis: [Overall Chase Win %]                          │
│ Color scale: Red (<47%) -> Yellow (48-52%) -> Green (>53%)                             │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Page 2: Scoring Rate Trajectory & ARIMA Forecasting

### Objective
Present the secular upward trend in scoring rates, boundary contribution, and 200+ totals explosion alongside the ARIMA forecast.

### Visual Layout Grid

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [HEADER]: Time-Series Scoring Evolution & ARIMA Forecast Model                         │
├───────────────┬────────────────┬────────────────┬─────────────────────┬────────────────┤
│ [KPI CARD 1]  │ [KPI CARD 2]   │ [KPI CARD 3]   │ [KPI CARD 4]        │ [KPI CARD 5]   │
│ 2008 Mean RPO │ 2024 Mean RPO  │ RPO Delta YoY  │ 200+ Scores Total   │ 2025 ARIMA Fc  │
│ 7.75 rpo      │ 9.61 rpo       │ +1.86 rpo      │ 120+ (Impact Player)│ 9.61 rpo       │
├───────────────┴────────────────┴────────────────┴─────────────────────┴────────────────┤
│ [VISUAL 1: Line & Clustered Column Combo Chart]                                        │
│ Title: Innings Scoring Rate (RPO) & 200+ Score Frequency                               │
│ Shared X-Axis: dim_seasons[season_year]                                                │
│ Column Values: [200+ Scores Count]                                                     │
│ Line Values: [Mean Innings Run Rate]                                                   │
├─────────────────────────────────────────────────┬──────────────────────────────────────┤
│ [VISUAL 2: Forecast Area Chart]                 │ [VISUAL 3: Donut Chart]              │
│ Title: ARIMA(0,1,0) Projections & 95% Conf Int  │ Title: Boundary Run Composition      │
│ X-Axis: Season (Historical + Forecast)          │ Values: Fours Runs, Sixes Runs,      │
│ Series: Actual RPO, ARIMA Forecast, Upper/Lower │ Running between wickets              │
└─────────────────────────────────────────────────┴──────────────────────────────────────┘
```

---

## Page 3: Franchise & Venue Performance Matrix

### Objective
Deliver drill-through capability to analyze how individual franchises and venues perform when chasing vs defending.

### Visual Layout Grid

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [HEADER]: Franchise Chase Efficiency & Venue Advantage Matrix                          │
├─────────────────────────────────────────────────┬──────────────────────────────────────┤
│ [VISUAL 1: Scatter Plot - Franchise Quadrant]   │ [VISUAL 2: Matrix Table with Heatmap]│
│ X-Axis: [Overall Defend Win %]                  │ Rows: dim_teams[team_code]           │
│ Y-Axis: [Overall Chase Win %]                   │ Columns: match_type (Day / Night)    │
│ Size: [Total Matches]                           │ Values:                              │
│ Quadrants:                                      │  - [Total Matches]                   │
│  - Top-Right: Elite All-Round (CSK, MI)         │  - [Chase Win %]                     │
│  - Top-Left: Chase Specialists (KKR, RR)        │  - [Toss Win %]                      │
│  - Bottom-Right: Defend Specialists (SRH)       │ Conditional color formatting applied │
└─────────────────────────────────────────────────┴──────────────────────────────────────┘
```
