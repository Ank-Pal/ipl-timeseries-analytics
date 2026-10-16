# Power BI Data Model Architecture: IPL Time-Series Analytics

## 1. Dimensional Architecture Overview

The data model follows an enterprise **Star Schema** designed for Power BI Desktop. The model optimizes query performance by eliminating many-to-many ambiguity, maintaining unidirectional 1-to-many (`1:*`) relationships, and separating high-cardinality numerical facts from low-cardinality descriptive dimensions.

```
       ┌────────────────────────┐
       │      dim_seasons       │
       │────────────────────────│
       │ * season_year (PK)     │
       │   era                  │
       │   impact_player_active │
       └───────────┬────────────┘
                   │ 1
                   │
                   │ *
       ┌───────────▼────────────┐        1 ┌────────────────────────┐
       │      fact_matches      │◄─────────┤       dim_venues       │
       │────────────────────────│          │────────────────────────│
       │ * match_id (PK)        │          │ * venue_name (PK)      │
       │   season (FK)          │          │   city                 │
       │   venue_name (FK)      │          │   chase_bias_category  │
       │   bat_first_team       │          └────────────────────────┘
       │   field_first_team     │
       │   toss_winner          │        1 ┌────────────────────────┐
       │   toss_decision        │◄─────────┤       dim_teams        │
       │   winner               │          │────────────────────────│
       │   toss_match_winner    │          │ * team_code (PK)       │
       │   won_batting_second   │          │   team_name            │
       │   inn1_runs            │          │   active_status        │
       │   inn2_runs            │          └────────────────────────┘
       │   match_total_runs     │
       └───────────┬────────────┘
                   │ 1
                   │
                   │ *
       ┌───────────▼────────────┐
       │  fact_innings_summary  │
       │────────────────────────│
       │ * innings_id (PK)      │
       │   match_id (FK)        │
       │   season (FK)          │
       │   innings_num          │
       │   run_rate             │
       │   powerplay_runs       │
       │   death_runs           │
       │   fours, sixes         │
       └────────────────────────┘
```

---

## 2. Table Specifications & Relationships

| Source Table | Key Field | Target Table | Foreign Key | Cardinality | Cross Filter | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `dim_seasons` | `season_year` | `fact_matches` | `season` | `1 : *` | Single | Season slicing & Era grouping |
| `dim_venues` | `venue_name` | `fact_matches` | `venue_name` | `1 : *` | Single | Venue & city performance analysis |
| `dim_teams` | `team_code` | `fact_matches` | `winner` | `1 : *` | Single (Inactive for team1/team2) | Franchise win slicing |
| `fact_matches` | `match_id` | `fact_innings_summary` | `match_id` | `1 : *` | Single | Grain expansion to innings & overs |

---

## 3. Power Query (M) Data Ingestion Guidelines

1. **Source Connection**:
   - In Power BI Desktop: `Get Data` -> `More` -> `ODBC` / `SQLite ODBC Driver` (or directly import `data/raw/matches.csv` and `data/raw/deliveries_summary.csv`).
2. **Data Type Enforcement**:
   - `match_id`, `season`, `inn1_runs`, `inn2_runs`: `Int64.Type`
   - `match_date`: `type date`
   - `run_rate`, `overs`: `type number`
   - `toss_match_winner`, `won_batting_second`: `type logical` (or `Int64.Type` 0/1)
3. **Sort By Column Configurations**:
   - Set `dim_seasons[season_year]` as the default numerical sort.
   - For custom time series or month names, ensure explicit `Sort by Column` indexing.
