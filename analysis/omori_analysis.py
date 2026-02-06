#!/usr/bin/env python3
"""
Omori's Law Analysis for Earthquake Aftershocks
Author: Edward Xiong
Diamond Bar High School, 11th Grade
NHSJS Research Project: Mathematics of Earthquake Aftershocks

Omori's Law (1894): n(t) = K / (c + t)^p
- n(t): aftershock rate at time t after mainshock
- K: productivity parameter (amplitude)
- c: characteristic time delay (typically 0.01-0.5 days)
- p: decay exponent (typically 0.9-1.5)

This script fits Omori's Law to aftershock sequences and analyzes
how parameters vary with mainshock characteristics.
"""

import json
import numpy as np
import pandas as pd
from scipy import optimize
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Publication-quality figure settings
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16


class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types."""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


# =============================================================================
# OMORI'S LAW MODELS
# =============================================================================

def omori_original(t, K, c):
    """
    Original Omori's Law (1894): n(t) = K / (c + t)
    Fixed p = 1
    """
    return K / (c + t)


def omori_modified(t, K, c, p):
    """
    Modified Omori-Utsu Law: n(t) = K / (c + t)^p
    The most commonly used form.
    """
    return K / np.power(c + t, p)


def omori_exponential(t, K, tau):
    """
    Exponential decay model for comparison: n(t) = K * exp(-t/tau)
    Not typically used for aftershocks but useful for comparison.
    """
    return K * np.exp(-t / tau)


# =============================================================================
# MODEL FITTING
# =============================================================================

def prepare_data_for_fitting(aftershocks, time_unit='hours'):
    """
    Prepare aftershock data for Omori fitting.
    Uses cumulative count method for more robust fitting.
    """
    if not aftershocks:
        return None, None

    # Get times
    if time_unit == 'hours':
        times = np.array([a['hours_after_mainshock'] for a in aftershocks])
    else:
        times = np.array([a['days_after_mainshock'] for a in aftershocks])

    times = np.sort(times)

    # For rate calculation, bin the data
    if len(times) < 20:
        return None, None

    # Use logarithmic binning for better fit at early times
    t_min = max(0.1, times[0])  # Avoid t=0
    t_max = times[-1]

    n_bins = min(30, len(times) // 3)
    bin_edges = np.logspace(np.log10(t_min), np.log10(t_max), n_bins + 1)

    counts, _ = np.histogram(times, bins=bin_edges)
    bin_widths = np.diff(bin_edges)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Calculate rate (events per unit time)
    rates = counts / bin_widths

    # Filter out zero-rate bins
    mask = rates > 0
    t_data = bin_centers[mask]
    rate_data = rates[mask]

    return t_data, rate_data


def fit_omori_modified(t_data, rate_data):
    """Fit the modified Omori-Utsu law to data."""
    if t_data is None or len(t_data) < 5:
        return None

    # Initial guesses based on typical values
    K_init = rate_data[0] * t_data[0]  # Estimate from first point
    c_init = 0.1
    p_init = 1.0

    try:
        # Fit in log space for better numerical stability
        def log_residuals(params):
            K, c, p = params
            if K <= 0 or c <= 0 or p <= 0:
                return 1e10
            predicted = omori_modified(t_data, K, c, p)
            log_pred = np.log10(predicted + 1e-10)
            log_obs = np.log10(rate_data + 1e-10)
            return np.sum((log_pred - log_obs) ** 2)

        result = optimize.minimize(
            log_residuals,
            x0=[K_init, c_init, p_init],
            bounds=[(0.01, 1e6), (0.001, 10), (0.1, 3)],
            method='L-BFGS-B'
        )

        if not result.success:
            return None

        K, c, p = result.x

        # Calculate goodness of fit
        predicted = omori_modified(t_data, K, c, p)

        # R-squared in log space
        log_pred = np.log10(predicted)
        log_obs = np.log10(rate_data)
        ss_res = np.sum((log_obs - log_pred) ** 2)
        ss_tot = np.sum((log_obs - np.mean(log_obs)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # RMSE
        rmse = np.sqrt(np.mean((rate_data - predicted) ** 2))

        return {
            'K': K,
            'c': c,
            'p': p,
            'r_squared': r_squared,
            'rmse': rmse,
            'success': True
        }

    except Exception as e:
        print(f"    Fitting error: {e}", flush=True)
        return None


def fit_omori_original(t_data, rate_data):
    """Fit original Omori's Law (p=1)."""
    if t_data is None or len(t_data) < 5:
        return None

    try:
        popt, _ = optimize.curve_fit(
            omori_original,
            t_data, rate_data,
            p0=[rate_data[0] * t_data[0], 0.1],
            bounds=([0, 0.001], [1e6, 10]),
            maxfev=5000
        )

        K, c = popt
        predicted = omori_original(t_data, K, c)

        log_pred = np.log10(predicted + 1e-10)
        log_obs = np.log10(rate_data + 1e-10)
        ss_res = np.sum((log_obs - log_pred) ** 2)
        ss_tot = np.sum((log_obs - np.mean(log_obs)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            'K': K,
            'c': c,
            'p': 1.0,  # Fixed
            'r_squared': r_squared,
            'success': True
        }

    except Exception:
        return None


# =============================================================================
# ANALYSIS
# =============================================================================

def analyze_sequence(sequence: dict) -> dict:
    """Analyze a single aftershock sequence."""
    mainshock = sequence['mainshock']
    aftershocks = sequence['aftershocks']

    result = {
        'mainshock_id': mainshock['id'],
        'mainshock_magnitude': mainshock['magnitude'],
        'mainshock_depth': mainshock['depth_km'],
        'mainshock_lat': mainshock['latitude'],
        'mainshock_lon': mainshock['longitude'],
        'mainshock_place': mainshock['place'],
        'mainshock_time': mainshock['time'],
        'total_aftershocks': len(aftershocks)
    }

    # Prepare data
    t_data, rate_data = prepare_data_for_fitting(aftershocks, time_unit='hours')

    if t_data is None:
        result['fit_success'] = False
        return result

    result['t_data'] = t_data.tolist()
    result['rate_data'] = rate_data.tolist()

    # Fit modified Omori's Law
    fit_result = fit_omori_modified(t_data, rate_data)

    if fit_result and fit_result['success']:
        result['fit_success'] = True
        result['K'] = fit_result['K']
        result['c'] = fit_result['c']
        result['p'] = fit_result['p']
        result['r_squared'] = fit_result['r_squared']
        result['rmse'] = fit_result['rmse']
    else:
        result['fit_success'] = False

    # Also fit original Omori for comparison
    original_fit = fit_omori_original(t_data, rate_data)
    if original_fit:
        result['original_K'] = original_fit['K']
        result['original_c'] = original_fit['c']
        result['original_r_squared'] = original_fit['r_squared']

    return result


def create_visualizations(results: list, output_dir: str):
    """Create publication-quality figures."""
    os.makedirs(output_dir, exist_ok=True)

    good_results = [r for r in results if r.get('fit_success') and r.get('r_squared', 0) > 0.5]

    if len(good_results) < 3:
        print("Not enough good fits for visualization", flush=True)
        return

    # 1. Example Omori fit plot
    best_result = max(good_results, key=lambda x: x.get('r_squared', 0))

    fig, ax = plt.subplots(figsize=(10, 7))

    t_data = np.array(best_result['t_data'])
    rate_data = np.array(best_result['rate_data'])

    # Plot data points
    ax.scatter(t_data, rate_data, s=80, c='red', zorder=5, label='Observed rates', edgecolors='black')

    # Plot fitted curve
    t_smooth = np.logspace(np.log10(t_data[0]), np.log10(t_data[-1]), 100)
    K, c, p = best_result['K'], best_result['c'], best_result['p']
    rate_fit = omori_modified(t_smooth, K, c, p)
    ax.plot(t_smooth, rate_fit, 'b-', linewidth=2.5,
            label=f"Omori fit: n(t) = {K:.1f}/(t+{c:.2f})^{p:.2f}\nR² = {best_result['r_squared']:.3f}")

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Time after mainshock (hours)')
    ax.set_ylabel('Aftershock rate (events/hour)')
    ax.set_title(f"Omori's Law Fit: M{best_result['mainshock_magnitude']:.1f} {best_result['mainshock_place'][:40]}")
    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'example_omori_fit.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Distribution of p values
    p_values = [r['p'] for r in good_results if 'p' in r]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(p_values, bins=15, color='steelblue', edgecolor='black', alpha=0.8)
    ax.axvline(x=np.mean(p_values), color='red', linestyle='--', linewidth=2,
               label=f'Mean p = {np.mean(p_values):.2f}')
    ax.axvline(x=1.0, color='green', linestyle=':', linewidth=2,
               label='Classical Omori (p=1)')
    ax.set_xlabel('Decay exponent p')
    ax.set_ylabel('Number of sequences')
    ax.set_title("Distribution of Omori's Law Decay Exponent (p)")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'p_value_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. p vs mainshock magnitude
    mags = [r['mainshock_magnitude'] for r in good_results]
    p_vals = [r['p'] for r in good_results]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(mags, p_vals, s=100, c='coral', edgecolors='black', alpha=0.8)

    # Linear fit
    slope, intercept, r_value, p_value, std_err = stats.linregress(mags, p_vals)
    x_fit = np.linspace(min(mags), max(mags), 100)
    y_fit = slope * x_fit + intercept
    ax.plot(x_fit, y_fit, 'b--', linewidth=2,
            label=f'Linear fit (r={r_value:.2f}, p={p_value:.3f})')

    ax.set_xlabel('Mainshock Magnitude')
    ax.set_ylabel('Decay Exponent (p)')
    ax.set_title("Relationship Between Mainshock Magnitude and Omori's p")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'p_vs_magnitude.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 4. R² distribution
    r2_values = [r['r_squared'] for r in good_results]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(r2_values, bins=15, color='forestgreen', edgecolor='black', alpha=0.8)
    ax.axvline(x=np.mean(r2_values), color='red', linestyle='--', linewidth=2,
               label=f'Mean R² = {np.mean(r2_values):.3f}')
    ax.set_xlabel('R² (Goodness of fit)')
    ax.set_ylabel('Number of sequences')
    ax.set_title("Distribution of Omori's Law Fit Quality")
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'r_squared_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Comparison: Original vs Modified Omori
    original_r2 = [r.get('original_r_squared', 0) for r in good_results if 'original_r_squared' in r]
    modified_r2 = [r['r_squared'] for r in good_results if 'original_r_squared' in r]

    if original_r2 and modified_r2:
        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(2)
        means = [np.mean(original_r2), np.mean(modified_r2)]
        stds = [np.std(original_r2), np.std(modified_r2)]

        bars = ax.bar(x, means, yerr=stds, capsize=5, color=['#3498db', '#e74c3c'], edgecolor='black')
        ax.set_xticks(x)
        ax.set_xticklabels(['Original Omori\n(p=1 fixed)', 'Modified Omori\n(p fitted)'])
        ax.set_ylabel('Average R²')
        ax.set_title('Comparison of Original vs Modified Omori Law')
        ax.set_ylim(0, 1)

        for bar, val in zip(bars, means):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=12)

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'original_vs_modified.png'), dpi=300, bbox_inches='tight')
        plt.close()

    print(f"Visualizations saved to: {output_dir}", flush=True)


def main():
    """Main analysis function."""
    print("=" * 60, flush=True)
    print("OMORI'S LAW ANALYSIS", flush=True)
    print("NHSJS Research Project - Edward Xiong", flush=True)
    print("=" * 60, flush=True)

    # Load data
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'earthquake_data.json')

    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}", flush=True)
        print("Please run collect_earthquake_data.py first.", flush=True)
        return

    with open(data_path) as f:
        data = json.load(f)

    sequences = data.get('sequences', [])
    print(f"Loaded {len(sequences)} aftershock sequences", flush=True)

    # Analyze each sequence
    results = []
    for i, seq in enumerate(sequences):
        ms = seq['mainshock']
        print(f"\n[{i+1}/{len(sequences)}] Analyzing M{ms['magnitude']:.1f} - {ms['place'][:30]}...", flush=True)

        result = analyze_sequence(seq)
        results.append(result)

        if result.get('fit_success'):
            print(f"    K={result['K']:.2f}, c={result['c']:.3f}, p={result['p']:.2f}, R²={result['r_squared']:.3f}", flush=True)
        else:
            print("    Fitting failed", flush=True)

    # Save results
    output_path = os.path.join(os.path.dirname(__file__), 'analysis_results.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to: {output_path}", flush=True)

    # Create visualizations
    fig_dir = os.path.join(os.path.dirname(__file__), '..', 'figures')
    create_visualizations(results, fig_dir)

    # Summary statistics
    good_fits = [r for r in results if r.get('fit_success') and r.get('r_squared', 0) > 0.5]

    print("\n" + "=" * 60, flush=True)
    print("ANALYSIS SUMMARY", flush=True)
    print("=" * 60, flush=True)
    print(f"Total sequences analyzed: {len(results)}", flush=True)
    print(f"Successful fits (R² > 0.5): {len(good_fits)}", flush=True)

    if good_fits:
        p_values = [r['p'] for r in good_fits]
        r2_values = [r['r_squared'] for r in good_fits]

        print(f"\nOmori's Law Parameters (n={len(good_fits)}):", flush=True)
        print(f"  p (decay exponent): {np.mean(p_values):.2f} ± {np.std(p_values):.2f}", flush=True)
        print(f"  p range: [{min(p_values):.2f}, {max(p_values):.2f}]", flush=True)
        print(f"  Average R²: {np.mean(r2_values):.3f}", flush=True)

        # Compare to literature values
        print(f"\nComparison to literature:", flush=True)
        print(f"  Our mean p = {np.mean(p_values):.2f} vs. literature p ≈ 1.0-1.3", flush=True)


if __name__ == "__main__":
    main()
