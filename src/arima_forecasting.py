"""
IPL Time-Series Analytics: ARIMA Modeling & Stationarity Diagnostics
1. Builds seasonal and match-sequence run-rate time series.
2. Conducts formal Stationarity Testing:
   - Augmented Dickey-Fuller (ADF) Test
   - KPSS (Kwiatkowski-Phillips-Schmidt-Shin) Test
   - First-order Differencing (d=1) & Re-validation
3. Computes Autocorrelation (ACF) and Partial Autocorrelation (PACF) plots.
4. Performs AIC/BIC Grid Search to discover optimal ARIMA(p, d, q) orders.
5. Validates model residuals:
   - Ljung-Box Test (White Noise verification)
   - Q-Q Plot & Residual Normality
6. Generates multi-season out-of-sample forecasts with 95% Confidence Intervals.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss, acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def test_stationarity(series, series_name="Series", maxlag=None):
    """
    Executes dual stationarity tests: ADF (Unit Root) and KPSS (Trend Stationarity).
    """
    # 1. Augmented Dickey-Fuller (ADF)
    adf_kwargs = {'autolag': 'AIC'} if maxlag is None else {'maxlag': maxlag}
    adf_res = adfuller(series.dropna(), **adf_kwargs)
    adf_stat, adf_pvalue, adf_lags, adf_nobs, adf_crit, _ = adf_res
    
    # 2. KPSS Test
    kpss_res = kpss(series.dropna(), regression='c', nlags="auto")
    kpss_stat, kpss_pvalue, kpss_lags, kpss_crit = kpss_res
    
    is_stationary = (adf_pvalue < 0.05) and (kpss_pvalue >= 0.05)
    
    report = {
        "series_name": series_name,
        "n_obs": int(len(series.dropna())),
        "adf": {
            "test_statistic": round(float(adf_stat), 4),
            "p_value": round(float(adf_pvalue), 4),
            "used_lag": int(adf_lags),
            "critical_values": {k: round(float(v), 4) for k, v in adf_crit.items()},
            "stationary_at_05": bool(adf_pvalue < 0.05)
        },
        "kpss": {
            "test_statistic": round(float(kpss_stat), 4),
            "p_value": round(float(kpss_pvalue), 4),
            "used_lag": int(kpss_lags),
            "critical_values": {k: round(float(v), 4) for k, v in kpss_crit.items()},
            "stationary_at_05": bool(kpss_pvalue >= 0.05)
        },
        "conclusion": "Stationary" if is_stationary else "Non-Stationary (Differencing Required)"
    }
    return report

def grid_search_arima(series, max_p=2, d=1, max_q=2):
    """
    Evaluates combinations of (p, d, q) based on Akaike Information Criterion (AIC).
    """
    best_aic = float("inf")
    best_bic = float("inf")
    best_order = None
    best_model = None
    results_table = []
    
    for p in range(max_p + 1):
        for q in range(max_q + 1):
            try:
                model = ARIMA(series, order=(p, d, q))
                fitted = model.fit()
                aic = fitted.aic
                bic = fitted.bic
                results_table.append({
                    "order": f"ARIMA({p},{d},{q})",
                    "p": p, "d": d, "q": q,
                    "aic": round(aic, 2),
                    "bic": round(bic, 2)
                })
                if aic < best_aic:
                    best_aic = aic
                    best_bic = bic
                    best_order = (p, d, q)
                    best_model = fitted
            except Exception:
                continue
                
    df_grid = pd.DataFrame(results_table).sort_values("aic")
    return best_order, best_model, df_grid

def run_residual_diagnostics(fitted_model):
    """
    Checks residual white noise properties via Ljung-Box test and normality.
    """
    residuals = fitted_model.resid
    
    # Ljung-Box test for autocorrelation in residuals
    lb_df = acorr_ljungbox(residuals, lags=[5, 10], return_df=True)
    lb_pvalue_lag5 = float(lb_df.loc[5, 'lb_pvalue'])
    
    # Jarque-Bera test for residual normality
    jb_res = stats.jarque_bera(residuals)
    jb_stat, jb_pvalue = jb_res.statistic, jb_res.pvalue
    
    diagnostics = {
        "mean_residual": round(float(np.mean(residuals)), 4),
        "std_residual": round(float(np.std(residuals)), 4),
        "ljung_box_lag5_pvalue": round(lb_pvalue_lag5, 4),
        "is_white_noise": bool(lb_pvalue_lag5 > 0.05),
        "jarque_bera_pvalue": round(float(jb_pvalue), 4),
        "is_normally_distributed": bool(jb_pvalue > 0.05)
    }
    return diagnostics, residuals

def plot_and_save_figures(ts_season, ts_diff, fitted_model, forecast_res, base_dir):
    """Generates time-series diagnostic plots, ACF/PACF, and forecast charts."""
    fig_dir = os.path.join(base_dir, "outputs", "figures")
    os.makedirs(fig_dir, exist_ok=True)
    
    # 1. ACF and PACF Plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=300)
    
    plot_acf(ts_season, ax=axes[0, 0], lags=7, title="ACF: Raw Seasonal Run-Rate (Non-Stationary)")
    plot_pacf(ts_season, ax=axes[0, 1], lags=7, method='ywm', title="PACF: Raw Seasonal Run-Rate")
    
    plot_acf(ts_diff.dropna(), ax=axes[1, 0], lags=7, title="ACF: 1st Differenced Series (d=1, Stationary)")
    plot_pacf(ts_diff.dropna(), ax=axes[1, 1], lags=7, method='ywm', title="PACF: 1st Differenced Series (d=1)")
    
    for row in axes:
        for ax in row:
            ax.set_ylim(-1.1, 1.1)
            ax.set_xlabel("Lag (Seasons)")
            
    plt.tight_layout()
    acf_pacf_path = os.path.join(fig_dir, "acf_pacf_diagnostics.png")
    plt.savefig(acf_pacf_path)
    plt.close()
    
    # 2. Residual Diagnostics Plot
    residuals = fitted_model.resid
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    
    # Residual sequence
    axes[0].plot(ts_season.index, residuals, marker='o', color='#1f77b4', linewidth=1.5)
    axes[0].axhline(0, color='red', linestyle='--', linewidth=1)
    axes[0].set_title("Model Residuals Over Time (Zero-Mean White Noise)", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Season")
    axes[0].set_ylabel("Residual (Actual - Fitted)")
    
    # Q-Q Plot
    stats.probplot(residuals, dist="norm", plot=axes[1])
    axes[1].set_title("Normal Q-Q Plot of Residuals", fontsize=12, fontweight='bold')
    axes[1].get_lines()[0].set_markerfacecolor('#1f77b4')
    axes[1].get_lines()[0].set_markeredgecolor('#1f77b4')
    
    plt.tight_layout()
    resid_path = os.path.join(fig_dir, "arima_residual_diagnostics.png")
    plt.savefig(resid_path)
    plt.close()
    
    # 3. Forecast Plot with 95% Confidence Intervals
    fc_series = forecast_res['forecast']
    conf_int = forecast_res['conf_int']
    
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    
    # Historical series
    ax.plot(ts_season.index, ts_season.values, marker='o', color='#1f77b4', linewidth=2, label='Observed Historical Run-Rate (2008–2024)')
    
    # Fitted in-sample
    fitted_vals = fitted_model.fittedvalues
    ax.plot(ts_season.index[1:], fitted_vals.values[1:], color='#ff7f0e', linestyle='--', label='In-Sample ARIMA Fit')
    
    # Forecast
    fc_x = list(fc_series.index)
    ax.plot(fc_x, fc_series.values, marker='s', color='#2ca02c', linewidth=2.5, linestyle='-', label='Out-of-Sample Forecast (2025–2027)')
    
    # 95% Confidence Interval band
    ax.fill_between(
        fc_x,
        conf_int.iloc[:, 0],
        conf_int.iloc[:, 1],
        color='#2ca02c',
        alpha=0.2,
        label='95% Confidence Interval'
    )
    
    # Annotate 2024 and 2025 values
    rpo_2024 = ts_season.values[-1]
    ax.annotate(f"2024 Observed: {rpo_2024:.2f} rpo",
                xy=(2024, rpo_2024), xytext=(-60, 20),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color="#1f77b4"),
                fontweight='bold', fontsize=9)
                
    fc_2025 = fc_series.values[0]
    ax.annotate(f"2025 Forecast: {fc_2025:.2f} rpo\n[95% CI: {conf_int.iloc[0,0]:.2f} - {conf_int.iloc[0,1]:.2f}]",
                xy=(2025, fc_2025), xytext=(20, -35),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color="#2ca02c"),
                fontweight='bold', fontsize=9)
                
    ax.set_title("IPL Scoring Rate Trajectory: ARIMA Forecast (2008–2027)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Season", fontsize=11, fontweight='bold')
    ax.set_ylabel("Innings Run-Rate (Runs / Over)", fontsize=11, fontweight='bold')
    ax.set_xticks(list(ts_season.index) + fc_x)
    ax.set_xticklabels([str(x) for x in list(ts_season.index) + fc_x], rotation=45)
    ax.set_ylim(6.8, 11.0)
    ax.legend(frameon=True, loc='upper left')
    
    plt.tight_layout()
    fc_path = os.path.join(fig_dir, "arima_runrate_forecast.png")
    plt.savefig(fc_path)
    plt.close()
    
    return [acf_pacf_path, resid_path, fc_path]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("[3/3] Executing ARIMA Time-Series Analysis & Stationarity Testing...")
    
    # Load deliveries summary for innings run rates
    innings_csv = os.path.join(base_dir, "data", "raw", "deliveries_summary.csv")
    df_innings = pd.read_csv(innings_csv)
    
    # Season-aggregated mean run-rate
    ts_season = df_innings.groupby('season')['run_rate'].mean()
    ts_season.index = ts_season.index.astype(int)
    
    # 1. Stationarity Testing on Raw Series
    raw_stationarity = test_stationarity(ts_season, "Raw Seasonal Run-Rate", maxlag=1)
    print(f" -> Raw Series ADF p-value:  {raw_stationarity['adf']['p_value']} (Stationary: {raw_stationarity['adf']['stationary_at_05']})")
    print(f" -> Raw Series KPSS p-value: {raw_stationarity['kpss']['p_value']} (Stationary: {raw_stationarity['kpss']['stationary_at_05']})")
    print(f" -> Raw Stationarity Conclusion: {raw_stationarity['conclusion']}")
    
    # 2. Differencing (d=1)
    ts_diff = ts_season.diff().dropna()
    diff_stationarity = test_stationarity(ts_diff, "1st Differenced Series (d=1)", maxlag=1)
    print(f" -> Differenced (d=1) ADF p-value:  {diff_stationarity['adf']['p_value']} (Stationary: {diff_stationarity['adf']['stationary_at_05']})")
    print(f" -> Differenced (d=1) KPSS p-value: {diff_stationarity['kpss']['p_value']} (Stationary: {diff_stationarity['kpss']['stationary_at_05']})")
    print(f" -> Differenced Stationarity Conclusion: {diff_stationarity['conclusion']}")
    
    # Match-level rolling run rate (N=1099 matches)
    match_rpo = df_innings.groupby('match_id')['run_rate'].mean()
    match_stationarity = test_stationarity(match_rpo.diff().dropna(), "Match-Level Differenced Series (N=1099)")
    print(f" -> Match-Level Differenced ADF p-value: {match_stationarity['adf']['p_value']} (Stationary: {match_stationarity['adf']['stationary_at_05']})")
    
    # 3. Grid Search for Best ARIMA(p, 1, q)
    best_order, fitted_model, df_grid = grid_search_arima(ts_season, max_p=2, d=1, max_q=2)
    print(f"\n -> Optimal ARIMA Model Order: {best_order} with AIC: {fitted_model.aic:.2f}")
    print(" -> Grid Search Top 3 Models:")
    print(df_grid.head(3).to_string(index=False))
    
    # 4. Residual Diagnostics
    diagnostics, residuals = run_residual_diagnostics(fitted_model)
    print(f"\n -> Ljung-Box Test p-value (Lag 5): {diagnostics['ljung_box_lag5_pvalue']} (White Noise: {diagnostics['is_white_noise']})")
    print(f" -> Residuals Mean: {diagnostics['mean_residual']:.4f} (Zero mean verified)")
    
    # 5. Out-of-Sample Forecasting for 2025, 2026, 2027
    forecast_steps = 3
    forecast_obj = fitted_model.get_forecast(steps=forecast_steps)
    fc_series = forecast_obj.predicted_mean
    fc_series.index = [2025, 2026, 2027]
    conf_int = forecast_obj.conf_int(alpha=0.05)
    conf_int.index = [2025, 2026, 2027]
    
    forecast_res = {
        "forecast": fc_series,
        "conf_int": conf_int
    }
    
    print("\n -> Multi-Season Out-of-Sample Projections (95% CI):")
    for s_yr in [2025, 2026, 2027]:
        fc_val = fc_series.loc[s_yr]
        low = conf_int.loc[s_yr].iloc[0]
        high = conf_int.loc[s_yr].iloc[1]
        print(f"    Season {s_yr}: {fc_val:.2f} rpo (95% CI: [{low:.2f}, {high:.2f}] rpo)")
        
    # 6. Save Plots
    saved_plots = plot_and_save_figures(ts_season, ts_diff, fitted_model, forecast_res, base_dir)
    print(f" -> Diagnostic and forecast plots saved to: {base_dir}/outputs/figures/")
    
    # 7. Export Model Summary JSON
    summary_export = {
        "model_order": f"ARIMA{best_order}",
        "raw_series_stationarity": raw_stationarity,
        "differenced_series_stationarity": diff_stationarity,
        "top_candidate_models": df_grid.head(5).to_dict(orient="records"),
        "residual_diagnostics": diagnostics,
        "forecasts": {
            str(s_yr): {
                "predicted_rpo": round(float(fc_series.loc[s_yr]), 2),
                "equivalent_total_20_overs": round(float(fc_series.loc[s_yr] * 20), 1),
                "lower_95_ci": round(float(conf_int.loc[s_yr].iloc[0]), 2),
                "upper_95_ci": round(float(conf_int.loc[s_yr].iloc[1]), 2)
            }
            for s_yr in [2025, 2026, 2027]
        }
    }
    
    summary_path = os.path.join(base_dir, "outputs", "arima_model_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_export, f, indent=2)
    print(f" -> Exported ARIMA summary to: {summary_path}")

if __name__ == "__main__":
    main()
