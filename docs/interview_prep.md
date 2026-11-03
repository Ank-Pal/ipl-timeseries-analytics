# IPL Analytics Interview Talking Points (Private Notes)

> Personal talking points for data analyst & sports analytics interviews. Not part of the public project deliverable.

### 30-Second Elevator Pitch
"For this project, I built an end-to-end sports analytics and time-series forecasting platform analyzing over 283,000 official CricSheet deliveries across 1,194 matches from 2008 through the 2026 season.

I designed a multi-phase time-series architecture evaluating Powerplay (Overs 1–6) and Death Overs (Overs 16–20) scoring trajectories independently. Using Augmented Dickey-Fuller (ADF) and KPSS dual stationarity testing, I demonstrated that death-over run-rates became non-stationary following the 2023 Impact Player tactical shift, requiring first-order differencing ($d=1, p < 0.0001$) before ARIMA fitting. Model residuals were verified as white noise ($p = 0.9997$ via Ljung-Box).

On the user-facing side, I developed an interactive Streamlit application with live SQL querying, profiling 788 cricketers, tracking all 15 historic super overs, stadium chase biases, and franchise head-to-head records."

### Key Technical Questions & Answers

#### Q1: Why model match phases separately instead of overall run rate?
In modern T20 cricket, aggregate run-rate obscures critical tactical shifts. Powerplay scoring is constrained by field restrictions (2 fielders outside the 30-yard circle), while Death Overs scoring is high-variance boundary hitting with wickets in hand. Modeling them separately reveals that the 2023 Impact Player rule caused an acute structural break in Death Overs scoring (surging from ~10.4 to over 12.8 RPO), while middle-overs run rates grew at a much steadier pace.

#### Q2: How did you handle stationarity for ARIMA?
Time-series models like ARIMA assume weak stationarity (constant mean and autocovariance). I applied dual tests:
1. **Augmented Dickey-Fuller (ADF)**: Null hypothesis of a unit root ($H_0$). Rejected for differenced series ($p < 0.05$).
2. **KPSS Test**: Null hypothesis of trend/level stationarity ($H_0$). Verified consistency.
First-order differencing ($d=1$) was required for the death-overs series to achieve stationarity before fitting $(p, d, q)$ parameters chosen via AIC grid search.

#### Q3: What is the "Toss & Dew Paradox"?
Historically (2008–2015), winning the toss conferred a measurable win advantage (~54.2% match conversion). However, post-2016 data shows this advantage has flattened to ~50.2% nationally (statistically indistinguishable from a coin toss). Teams overwhelmingly choose to field first (~74% of tosses post-2016 vs ~45% historically) to capitalize on second-innings dew and known target chases at venues like Wankhede and Chinnaswamy, but defensive death bowling and higher par totals have neutralized the raw toss advantage at other venues.
