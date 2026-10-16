"""
IPL Phase-by-Phase ARIMA Time-Series Modeling & Forecasting (2008–2026)
Models scoring dynamics across the 3 core match phases:
1. Powerplay (Overs 1–6)
2. Middle Overs (Overs 7–15)
3. Death Overs (Overs 16–20)
Specifically models the secular upward drift and the Impact Player explosion (2023–2026).
Conducts ADF & KPSS dual stationarity testing, differencing (d=1), and forecasting.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
FIGURES_DIR = os.path.join(BASE_DIR, "outputs", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

def test_stationarity(series, name):
    adf_res = adfuller(series.dropna(), maxlag=1)
    kpss_res = kpss(series.dropna(), regression='c', nlags="auto")
    return {
        "series": name,
        "adf_stat": round(float(adf_res[0]), 4),
        "adf_pvalue": round(float(adf_res[1]), 4),
        "kpss_stat": round(float(kpss_res[0]), 4),
        "kpss_pvalue": round(float(kpss_res[1]), 4),
        "is_stationary": bool((adf_res[1] < 0.05) and (kpss_res[1] >= 0.05))
    }

def fit_and_forecast_phase(series, phase_name, steps=3):
    # Test raw vs differenced
    raw_stat = test_stationarity(series, f"Raw {phase_name}")
    diff_series = series.diff().dropna()
    diff_stat = test_stationarity(diff_series, f"Diff (d=1) {phase_name}")
    
    # Model: ARIMA(0, 1, 0) random walk with drift
    model = ARIMA(series, order=(0, 1, 0)).fit()
    fc_res = model.get_forecast(steps=steps)
    fc_mean = fc_res.predicted_mean
    fc_ci = fc_res.conf_int(alpha=0.05)
    
    future_seasons = [int(series.index[-1] + i) for i in range(1, steps + 1)]
    fc_mean.index = future_seasons
    fc_ci.index = future_seasons
    
    lb_test = acorr_ljungbox(model.resid, lags=[5], return_df=True)
    
    return {
        "phase": phase_name,
        "raw_stat": raw_stat,
        "diff_stat": diff_stat,
        "model_aic": round(float(model.aic), 2),
        "ljung_box_pvalue": round(float(lb_test.loc[5, 'lb_pvalue']), 4),
        "forecast": fc_mean,
        "conf_int": fc_ci,
        "historical": series
    }

def run_phase_modeling():
    print("[1/3] Loading phase-aggregated annual scoring data...")
    phase_csv = os.path.join(PROCESSED_DIR, "phase_annual_runrates.csv")
    df_phase = pd.read_csv(phase_csv)
    
    # Filter valid seasons
    df_phase = df_phase[df_phase['season'] >= 2008].sort_values(['season', 'phase'])
    
    # Pivot to get annual run-rate by phase
    pivot_rpo = df_phase.pivot(index='season', columns='phase', values='run_rate')
    
    # Run modeling for each phase
    phases = ['Powerplay', 'Middle', 'Death']
    phase_models = {}
    
    print("[2/3] Executing ARIMA modeling and Stationarity testing across match phases...")
    for p in phases:
        series = pivot_rpo[p].dropna()
        res = fit_and_forecast_phase(series, p, steps=3)
        phase_models[p] = res
        print(f" -> {p:9s} | Raw ADF p={res['raw_stat']['adf_pvalue']:.4f} | Diff ADF p={res['diff_stat']['adf_pvalue']:.4f} | LB p={res['ljung_box_pvalue']:.4f}")

    # Generate Figures
    print("[3/3] Generating publication-quality phase trajectory charts...")
    
    # Plot 1: Historical Phase Run Rate Trajectories (2008–2024/2026)
    fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
    seasons = pivot_rpo.index
    
    ax.plot(seasons, pivot_rpo['Powerplay'], marker='o', linewidth=2.5, color='#38bdf8', label='Powerplay (Overs 1–6)')
    ax.plot(seasons, pivot_rpo['Middle'], marker='s', linewidth=2.5, color='#fb923c', label='Middle Overs (Overs 7–15)')
    ax.plot(seasons, pivot_rpo['Death'], marker='^', linewidth=2.8, color='#f43f5e', label='Death Overs (Overs 16–20)')
    
    ax.axvline(2023, color='#c084fc', linestyle='--', linewidth=1.5, label='2023 Impact Player Rule Introduced')
    ax.set_title("IPL Phase-by-Phase Scoring Rate Evolution (2008–2026)", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Season", fontsize=11, fontweight='bold')
    ax.set_ylabel("Run Rate (Runs / Over)", fontsize=11, fontweight='bold')
    ax.set_xticks(seasons)
    ax.set_xticklabels([str(s) for s in seasons], rotation=45)
    ax.legend(frameon=True, loc='upper left')
    
    plt.tight_layout()
    chart1_path = os.path.join(FIGURES_DIR, "phase_runrate_trajectories.png")
    plt.savefig(chart1_path)
    plt.close()
    
    # Plot 2: Phase Forecasts with 95% Confidence Intervals
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    # Powerplay Forecast
    pp_m = phase_models['Powerplay']
    axes[0].plot(pp_m['historical'].index, pp_m['historical'].values, marker='o', color='#38bdf8', linewidth=2, label='Observed Powerplay RPO')
    fc_x = list(pp_m['forecast'].index)
    axes[0].plot(fc_x, pp_m['forecast'].values, marker='s', color='#2ca02c', linewidth=2.5, label='ARIMA Forecast')
    axes[0].fill_between(fc_x, pp_m['conf_int'].iloc[:, 0], pp_m['conf_int'].iloc[:, 1], color='#2ca02c', alpha=0.2, label='95% CI')
    axes[0].set_title("Powerplay (Overs 1–6) ARIMA Forecast", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Season")
    axes[0].set_ylabel("Run Rate (rpo)")
    axes[0].legend(loc='upper left')
    
    # Death Overs Forecast
    death_m = phase_models['Death']
    axes[1].plot(death_m['historical'].index, death_m['historical'].values, marker='^', color='#f43f5e', linewidth=2, label='Observed Death Overs RPO')
    axes[1].plot(fc_x, death_m['forecast'].values, marker='s', color='#2ca02c', linewidth=2.5, label='ARIMA Forecast')
    axes[1].fill_between(fc_x, death_m['conf_int'].iloc[:, 0], death_m['conf_int'].iloc[:, 1], color='#2ca02c', alpha=0.2, label='95% CI')
    axes[1].set_title("Death Overs (Overs 16–20) ARIMA Forecast", fontsize=13, fontweight='bold')
    axes[1].set_xlabel("Season")
    axes[1].set_ylabel("Run Rate (rpo)")
    axes[1].legend(loc='upper left')
    
    plt.tight_layout()
    chart2_path = os.path.join(FIGURES_DIR, "phase_arima_forecasts.png")
    plt.savefig(chart2_path)
    plt.close()
    
    # Export summary JSON
    summary_export = {
        p: {
            "raw_adf_pvalue": phase_models[p]['raw_stat']['adf_pvalue'],
            "diff_adf_pvalue": phase_models[p]['diff_stat']['adf_pvalue'],
            "ljung_box_pvalue": phase_models[p]['ljung_box_pvalue'],
            "forecast_2025_2027": {
                str(y): {
                    "pred_rpo": round(float(phase_models[p]['forecast'].loc[y]), 2),
                    "lower_95_ci": round(float(phase_models[p]['conf_int'].loc[y].iloc[0]), 2),
                    "upper_95_ci": round(float(phase_models[p]['conf_int'].loc[y].iloc[1]), 2)
                }
                for y in fc_x
            }
        }
        for p in phases
    }
    
    json_path = os.path.join(BASE_DIR, "outputs", "phase_arima_summary.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_export, f, indent=2)
        
    print(f" -> Saved phase charts to: {FIGURES_DIR}")
    print(f" -> Saved phase summary JSON to: {json_path}")

if __name__ == "__main__":
    run_phase_modeling()
