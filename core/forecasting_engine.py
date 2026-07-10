"""
forecasting_engine.py

Real implementations of generic, domain-agnostic time-series diagnostics:
state-space smoothing, entropy rate, Lyapunov exponent estimate, phase-space
embedding, ergodicity check, empirical-Bayes hierarchical shrinkage, and a
martingale fairness test.

Design note on scope: Physics-Informed Neural Networks require a known
governing equation (a specific PDE) to be meaningful - there is no generic
"PINN for any dataset". Rather than fake that, this module routes physical-
looking data and behavioral-looking data through the SAME state-space /
Bayesian machinery, just with different framing text. If a real governing
equation is ever supplied for a specific physical system, a true PINN branch
can be added on top of this.
"""

# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
import numpy as np
import pandas as pd
from scipy import stats


def is_single_record(df):
    """
    Shared shape-check used across the forecast engine: True when the
    dataset is a single row with two or more numeric columns. Every
    diagnostic in this module (Kalman smoothing, entropy, Lyapunov,
    ergodicity, martingale fairness) needs a *sequence* of observations to
    mean anything - a single row has no sequence, so those tools are
    skipped and a variance-based summary is used instead.
    """
    if df is None or df.empty:
        return False
    numeric_count = df.select_dtypes(include=[np.number]).shape[1]
    return len(df) == 1 and numeric_count >= 2


def run_variance_summary(df, metric_col=None):
    """
    Forecast-tab counterpart to process_single_record_variance() in
    analytics_engine.py. When only one record exists, there is no time
    axis to forecast along, so this reports the same descriptive-statistics
    package (mean, median, variance, std, coefficient of variation) computed
    across that record's numeric fields, plus a simple per-field ranking so
    the forecast tab still has something concrete and honest to show.
    """
    if df is None or df.empty:
        return None

    df_clean = df.copy()
    df_clean.columns = [str(c).lower().strip() for c in df_clean.columns]
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return None

    values = df_clean[numeric_cols].iloc[0].astype(float).values
    mean_val = float(np.mean(values))
    median_val = float(np.median(values))
    variance_val = float(np.var(values, ddof=0))
    std_val = float(np.std(values, ddof=0))
    coeff_variation = std_val / (abs(mean_val) + 1e-9)

    per_column = {col: float(val) for col, val in zip(numeric_cols, values)}
    ranked = sorted(per_column.items(), key=lambda kv: kv[1], reverse=True)

    target = str(metric_col).lower().strip() if metric_col else ""
    focus_field = target if target in numeric_cols else numeric_cols[-1]
    focus_value = per_column.get(focus_field, mean_val)
    deviation_from_mean = focus_value - mean_val

    summary = (
        f"Single record detected - {len(numeric_cols)} numeric fields analyzed by variance "
        f"instead of a time series.\n"
        f"Mean = {mean_val:.4f}, Median = {median_val:.4f}, Variance = {variance_val:.4f}, "
        f"Std Dev = {std_val:.4f} (CoV = {coeff_variation*100:.1f}%).\n"
        f"Focus field '{focus_field}' = {focus_value:.4f} "
        f"({'above' if deviation_from_mean >= 0 else 'below'} the record's own average by {abs(deviation_from_mean):.4f})."
    )

    return {
        "mode": "single_record_variance",
        "mean": mean_val,
        "median": median_val,
        "variance": variance_val,
        "std_dev": std_val,
        "coefficient_of_variation": coeff_variation,
        "per_column_values": per_column,
        "ranked_fields": ranked,
        "numeric_columns": numeric_cols,
        "focus_field": focus_field,
        "focus_value": focus_value,
        "summary": summary,
    }


def compute_comparative_benchmarking(df, metric_col, entity_col=None):
    """
    Context-aware benchmarking for the Forecast page: rather than fitting a
    trend model, this measures how each row's value compares to the GROUP'S
    OWN mean/median via a z-score and a percentile rank. This is the
    general-purpose stand-in for the old physics-flavored diagnostics - it
    never mistakes ordinary spread/noise for a "regime shift", it simply
    shows, plainly, where each entry stands relative to its peers.
    """
    if df is None or df.empty or metric_col not in df.columns:
        return None

    values = pd.to_numeric(df[metric_col], errors="coerce").dropna()
    if values.empty:
        return None

    mean_val = float(values.mean())
    median_val = float(values.median())
    std_val = float(values.std(ddof=0))
    safe_std = std_val if std_val > 1e-9 else 1e-9

    if entity_col and entity_col in df.columns:
        labels = df.loc[values.index, entity_col].astype(str)
    else:
        labels = pd.Series([f"Row {i+1}" for i in values.index], index=values.index)

    z_scores = (values - mean_val) / safe_std
    percentile_ranks = values.rank(pct=True) * 100

    benchmark_table = pd.DataFrame({
        "entity": labels.values,
        "value": values.values,
        "z_score": z_scores.values,
        "percentile": percentile_ranks.values,
    }).sort_values("value", ascending=False).reset_index(drop=True)

    top_10_percent = benchmark_table[benchmark_table["percentile"] >= 90]
    bottom_10_percent = benchmark_table[benchmark_table["percentile"] <= 10]

    return {
        "mean": mean_val,
        "median": median_val,
        "std_dev": std_val,
        "benchmark_table": benchmark_table,
        "top_10_percent": top_10_percent,
        "bottom_10_percent": bottom_10_percent,
    }


def compute_subject_mean_variance_penetration(df, metric_col, entity_col=None):
    """
    "Subject-to-Mean Variance Penetration" - shows exactly where one entry
    (a student, a platform, a sensor node...) stands inside the group, in
    two complementary units:
      - z_score: how many standard deviations above/below the mean
      - penetration_pct: the same distance rescaled against the single most
        extreme entry in the dataset, so it reads as an intuitive
        -100%..+100% "how deep into the pack" position.
    This is the deliberately simple, always-interpretable replacement for
    black-box "chaos"/"regime" style diagnostics.
    """
    if df is None or df.empty or metric_col not in df.columns:
        return None

    values = pd.to_numeric(df[metric_col], errors="coerce").dropna()
    if values.empty:
        return None

    mean_val = float(values.mean())
    std_val = float(values.std(ddof=0))
    safe_std = std_val if std_val > 1e-9 else 1e-9
    deviations = values - mean_val
    max_abs_dev = float(deviations.abs().max()) or 1e-9

    if entity_col and entity_col in df.columns:
        labels = df.loc[values.index, entity_col].astype(str)
    else:
        labels = pd.Series([f"Row {i+1}" for i in values.index], index=values.index)

    z_scores = deviations / safe_std
    penetration_pct = (deviations / max_abs_dev) * 100

    table = pd.DataFrame({
        "entity": labels.values,
        "value": values.values,
        "z_score": z_scores.values,
        "penetration_pct": penetration_pct.values,
    }).sort_values("penetration_pct", ascending=False).reset_index(drop=True)

    return {
        "mean": mean_val,
        "std_dev": std_val,
        "table": table,
    }


def detect_data_flavor(df, metric_col):
    """
    Heuristic-only router: looks at column names to decide whether to frame
    results as 'physical system' or 'behavioral/market system' language.
    This does NOT change the underlying math - both paths use the same
    state-space/Bayesian tools, just narrated differently, since there is no
    generic way to auto-derive physics equations from arbitrary columns.
    """
    cols_lower = [str(c).lower() for c in df.columns]
    physical_signals = ["temp", "pressure", "voltage", "sensor", "velocity",
                         "rpm", "humidity", "flow", "vibration", "current_amp"]
    behavioral_signals = ["price", "sales", "click", "engagement", "revenue",
                           "impressions", "conversion", "spend", "rating"]

    physical_hits = sum(any(sig in c for sig in physical_signals) for c in cols_lower)
    behavioral_hits = sum(any(sig in c for sig in behavioral_signals) for c in cols_lower)

    if physical_hits > behavioral_hits:
        return "physical"
    return "behavioral"  # default assumption when ambiguous


def kalman_filter_smooth(series, process_var=1e-4, measurement_var=None):
    """
    Univariate Kalman filter (constant-level model). Returns filtered estimate
    and one-step-ahead forecast. Pure linear state-space math - no training,
    no assumptions about domain.
    """
    values = pd.to_numeric(series, errors="coerce").ffill().fillna(0).values.astype(float)
    n = len(values)
    if n == 0:
        return np.array([]), np.array([])

    if measurement_var is None:
        measurement_var = max(np.var(values) * 0.1, 1e-6)

    x_est = values[0]
    p_est = 1.0
    filtered = np.zeros(n)

    for i, z in enumerate(values):
        # Predict
        p_pred = p_est + process_var
        # Update
        k_gain = p_pred / (p_pred + measurement_var)
        x_est = x_est + k_gain * (z - x_est)
        p_est = (1 - k_gain) * p_pred
        filtered[i] = x_est

    # Simple one-step forecast extension (constant-level assumption)
    forecast_steps = max(1, n // 10)
    forecast = np.full(forecast_steps, filtered[-1])

    return filtered, forecast


def compute_entropy_rate(series, bins=10):
    """
    Approximate entropy rate via Shannon entropy of the discretized
    first-difference distribution. Higher = more new information/unpredictability
    being injected into the system at each step.
    """
    values = pd.to_numeric(series, errors="coerce").dropna().values
    if len(values) < 3:
        return 0.0

    diffs = np.diff(values)
    hist, _ = np.histogram(diffs, bins=bins, density=True)
    hist = hist[hist > 0]
    bin_width = (diffs.max() - diffs.min()) / bins if diffs.max() != diffs.min() else 1
    probs = hist * bin_width
    probs = probs / probs.sum()
    entropy = -np.sum(probs * np.log2(probs + 1e-12))
    return float(entropy)


def estimate_lyapunov_exponent(series, embedding_dim=3, delay=1, max_iter=20):
    """
    Rosenstein-style estimate of the largest Lyapunov exponent: tracks how fast
    nearby trajectories in phase space diverge. Positive = chaotic sensitivity
    to initial conditions; near zero or negative = stable/predictable system.
    """
    values = pd.to_numeric(series, errors="coerce").dropna().values
    n = len(values)
    embed_n = n - (embedding_dim - 1) * delay
    if embed_n < max_iter + 2:
        return 0.0, "insufficient data"

    embedded = np.array([
        values[i: i + embedding_dim * delay: delay]
        for i in range(embed_n)
    ])

    divergences = []
    for i in range(len(embedded) - max_iter):
        dists = np.linalg.norm(embedded - embedded[i], axis=1)
        dists[i] = np.inf
        nearest_idx = np.argmin(dists)
        if dists[nearest_idx] == 0 or not np.isfinite(dists[nearest_idx]):
            continue

        d0 = dists[nearest_idx]
        steps_available = min(max_iter, len(embedded) - max(i, nearest_idx) - 1)
        if steps_available <= 0:
            continue

        dk = np.linalg.norm(embedded[i + steps_available] - embedded[nearest_idx + steps_available])
        if dk > 0:
            divergences.append(np.log(dk / d0) / steps_available)

    if not divergences:
        return 0.0, "could not estimate"

    lyap = float(np.mean(divergences))
    verdict = "chaotic (sensitive to initial conditions)" if lyap > 0.05 else \
              "stable/contractive" if lyap < -0.05 else "near-neutral / borderline"
    return lyap, verdict


def phase_space_embedding(series, embedding_dim=3, delay=1):
    """
    Takens' time-delay embedding: reconstructs the underlying attractor shape
    from a single observed variable. Generic - works on any scalar series.
    """
    values = pd.to_numeric(series, errors="coerce").dropna().values
    n = len(values)
    embed_n = n - (embedding_dim - 1) * delay
    if embed_n <= 0:
        return np.empty((0, embedding_dim))

    embedded = np.array([
        values[i: i + embedding_dim * delay: delay]
        for i in range(embed_n)
    ])
    return embedded


def ergodicity_check(series, n_windows=5):
    """
    Compares the long-run time average to several windowed (ensemble-proxy)
    averages. Large spread = system likely non-ergodic, meaning past data may
    not reliably predict future states.
    """
    values = pd.to_numeric(series, errors="coerce").dropna().values
    n = len(values)
    if n < n_windows * 2:
        return {"is_likely_ergodic": None, "time_average": None,
                "window_averages": [], "spread": None}

    time_average = float(np.mean(values))
    window_size = n // n_windows
    window_averages = [
        float(np.mean(values[i * window_size:(i + 1) * window_size]))
        for i in range(n_windows)
    ]
    spread = float(np.std(window_averages))
    relative_spread = spread / (abs(time_average) + 1e-9)

    is_likely_ergodic = relative_spread < 0.25  # heuristic threshold
    return {
        "is_likely_ergodic": is_likely_ergodic,
        "time_average": time_average,
        "window_averages": window_averages,
        "spread": spread,
        "relative_spread": relative_spread,
    }


def martingale_fairness_test(series):
    """
    Tests whether the series' increments behave like a martingale (zero
    expected drift given the past) - i.e. whether the process looks "fair" in
    the sense that knowing the current value gives no edge in predicting the
    next move's direction. Uses a one-sample t-test on first differences
    against zero mean, the standard empirical proxy for this property.
    """
    values = pd.to_numeric(series, errors="coerce").dropna().values
    if len(values) < 3:
        return {"t_stat": 0.0, "p_value": 1.0, "is_fair": None, "mean_drift": 0.0}

    diffs = np.diff(values)
    t_stat, p_value = stats.ttest_1samp(diffs, 0.0)
    is_fair = p_value > 0.05  # cannot reject "zero drift" null hypothesis

    return {
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "is_fair": bool(is_fair),
        "mean_drift": float(np.mean(diffs)),
    }


def bayesian_hierarchical_shrinkage(df, entity_col, metric_col):
    """
    Empirical-Bayes (James-Stein style) hierarchical shrinkage: pulls each
    group's noisy sample mean toward the overall (grand) mean, weighted by
    how much data that group has. This is a real, closed-form Bayesian
    hierarchical estimator - general purpose, works on any grouped numeric
    data (not specific to any one domain like rainfall).
    """
    work = df[[entity_col, metric_col]].dropna()
    if work.empty:
        return pd.DataFrame(columns=[entity_col, "raw_mean", "shrunk_estimate", "n"])

    group_stats = work.groupby(entity_col)[metric_col].agg(["mean", "var", "count"]).reset_index()
    group_stats.rename(columns={"mean": "raw_mean", "var": "raw_var", "count": "n"}, inplace=True)
    group_stats["raw_var"] = group_stats["raw_var"].fillna(0)

    grand_mean = work[metric_col].mean()
    between_group_var = group_stats["raw_mean"].var() if len(group_stats) > 1 else 0
    within_group_var = (group_stats["raw_var"] * group_stats["n"]).sum() / group_stats["n"].sum() \
        if group_stats["n"].sum() > 0 else 1e-6

    # Shrinkage weight per group: more data / lower noise -> trust raw mean more
    if between_group_var <= 0:
        group_stats["shrunk_estimate"] = grand_mean
    else:
        group_stats["shrinkage_weight"] = between_group_var / (
            between_group_var + (within_group_var / group_stats["n"].replace(0, 1))
        )
        group_stats["shrunk_estimate"] = (
            group_stats["shrinkage_weight"] * group_stats["raw_mean"]
            + (1 - group_stats["shrinkage_weight"]) * grand_mean
        )

    return group_stats[[entity_col, "raw_mean", "shrunk_estimate", "n"]]


def run_forecasting_suite(df, metric_col):
    if is_single_record(df):
        variance_result = run_variance_summary(df, metric_col)
        if variance_result is not None:
            return variance_result

    series = df[metric_col]

    flavor = detect_data_flavor(df, metric_col)
    filtered, forecast = kalman_filter_smooth(series)
    entropy = compute_entropy_rate(series)
    lyap, lyap_verdict = estimate_lyapunov_exponent(series)
    embedding = phase_space_embedding(series)
    ergodic = ergodicity_check(series)
    fairness = martingale_fairness_test(series)
    shrinkage = bayesian_hierarchical_shrinkage(df, entity_col="entity", metric_col=metric_col)

    return {
        "flavor": flavor,
        "kalman": {"filtered": filtered, "forecast": forecast},
        "entropy": entropy,
        "lyapunov": {"value": lyap, "verdict": lyap_verdict},
        "embedding_shape": embedding.shape,
        "ergodicity": ergodic,
        "fairness": fairness,
        "shrinkage": shrinkage,
        "summary": f"""
        Data flavor: {flavor.upper()} system.
        Kalman smoothing shows stable level at {filtered[-1]:.2f}.
        Entropy rate = {entropy:.2f} → {'high unpredictability' if entropy > 2 else 'stable information flow'}.
        Lyapunov exponent = {lyap:.3f} ({lyap_verdict}).
        Ergodicity check: {'likely ergodic' if ergodic['is_likely_ergodic'] else 'non-ergodic'}.
        Martingale fairness: {'fair process' if fairness['is_fair'] else 'biased drift'}.
        Shrinkage estimates applied for group-level accuracy.
        """
    }

from statsmodels.tsa.arima.model import ARIMA

def get_arima_insight(series):
    """
    Computes ARIMA forecast and returns a verdict based on trend.
    """
    try:
        # ARIMA(1,1,1) is a robust starting point for general datasets
        model = ARIMA(series, order=(1, 1, 1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=1)
        
        current_val = series.iloc[-1]
        forecast_val = forecast.iloc[0]
        
        status = "encouraging" if forecast_val > current_val else "cautious"
        return status, forecast_val
    except:
        return "neutral", series.iloc[-1]
    
def get_weighted_stability(df):
    """Sentiment-Weighted Stability: Weights interactions by depth."""
    # Weights: Shares=3, Comments=2, Likes=1.5, Passive Impressions=0.1
    df['weighted_score'] = (df['Shares']*3 + df['Comments']*2 + df['Likes']*1.5 + df['Impressions']*0.1)
    return df['weighted_score'].mean()

def detect_regime_shift(df, threshold=3.0):
    """Jump-Diffusion Detection: Flags spikes that exceed standard deviation."""
    z_scores = (df['Impressions'] - df['Impressions'].mean()) / df['Impressions'].std()
    jumps = z_scores[z_scores > threshold]
    return len(jumps) > 0, jumps

def get_attribution_map(df):
    """Feature Attribution: Identifies which Content Type generates the most Resilience."""
    return df.groupby('Content Type')['Impressions'].mean().sort_values(ascending=False)

def run_arima_forecast(df):
    """
    Automatically indexes by date for accurate forecasting.
    """
    df_clean = df.copy()
    
    # 1. Detect and set Date Index
    date_col = next((c for c in df_clean.columns if 'date' in c.lower()), None)
    if date_col:
        df_clean[date_col] = pd.to_datetime(df_clean[date_col])
        df_clean = df_clean.sort_values(date_col).set_index(date_col)
    
    # 2. Extract numeric metric
    numeric_col = df_clean.select_dtypes(include=[np.number]).columns[0]
    series = df_clean[numeric_col].resample('M').mean().fillna(0)
    
    # 3. Forecast
    model = ARIMA(series, order=(1, 1, 1))
    return model.fit().forecast(steps=1).iloc[0]