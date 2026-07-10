# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

from core.semantic_mapper import detect_target_metric_column, detect_entity_column


def is_single_record_dataset(df):
    """
    True when the dataset has exactly one row (one entity/record) but two or
    more numeric columns - e.g. a single day's stats, a single player's
    profile, a single company's KPIs pasted in as one line. Correlation and
    time-series math need multiple rows to mean anything, so this case needs
    its own variance-based analysis path instead of silently failing.
    """
    if df is None or df.empty:
        return False
    numeric_count = df.select_dtypes(include=[np.number]).shape[1]
    return len(df) == 1 and numeric_count >= 2


def process_single_record_variance(df, entity_col="Platform", metric_col=None):
    """
    Variance-based analysis for a single-row dataset.

    With only one record, there is no second row to correlate against, so
    this instead treats the row's own numeric columns as a small population
    and reports the classic descriptive-statistics set - mean, median,
    variance, standard deviation, and coefficient of variation - across
    those columns. This is the "report by variance" fallback: it lets the
    app return a meaningful, trustworthy summary for single-record uploads
    instead of returning nothing.
    """
    if df is None or df.empty:
        return None

    df_clean = df.copy()
    df_clean.columns = [str(c).lower().strip() for c in df_clean.columns]

    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) < 2:
        return None

    row = df_clean[numeric_cols].iloc[0].astype(float)
    values = row.values

    mean_val = float(np.mean(values))
    median_val = float(np.median(values))
    variance_val = float(np.var(values, ddof=0))
    std_val = float(np.std(values, ddof=0))
    coeff_variation = std_val / (abs(mean_val) + 1e-9)
    accuracy_score = max(0.0, min(1.0, 1.0 - coeff_variation))

    target_metric = str(metric_col).lower().strip() if metric_col else ""
    if target_metric in numeric_cols:
        actual_target = target_metric
    else:
        actual_target = detect_target_metric_column(df_clean) or numeric_cols[-1]
    remaining = [c for c in numeric_cols if c != actual_target]
    primary_driver = remaining[0] if remaining else actual_target

    if coeff_variation < 0.20:
        status_flag = "OPTIMAL"
        alignment_str = "Very consistent field values - low spread across this single record"
    elif coeff_variation < 0.50:
        status_flag = "STABLE"
        alignment_str = "Moderate spread across this single record's fields"
    else:
        status_flag = "VOLATILE"
        alignment_str = "Wide spread across this single record's fields"

    per_column = {col: float(val) for col, val in zip(numeric_cols, values)}
    sorted_cols = sorted(per_column.items(), key=lambda kv: kv[1], reverse=True)

    description = (
        f"=== HONEYPOT SINGLE-RECORD VARIANCE REPORT ===\n"
        f"Only one row was detected ({entity_col}), so correlation analysis does not\n"
        f"apply. Instead, the {len(numeric_cols)} numeric fields on this record were\n"
        f"treated as a small population for descriptive statistics:\n\n"
        f"• Mean across fields      : {mean_val:.4f}\n"
        f"• Median across fields    : {median_val:.4f}\n"
        f"• Variance across fields  : {variance_val:.4f}\n"
        f"• Std. Deviation          : {std_val:.4f}\n"
        f"• Coefficient of Variation: {coeff_variation:.4f} ({coeff_variation*100:.1f}%)\n\n"
        f"STATUS [{status_flag}]: {alignment_str}.\n"
        f"Highest field: {sorted_cols[0][0].title()} ({sorted_cols[0][1]:.2f})\n"
        f"Lowest field : {sorted_cols[-1][0].title()} ({sorted_cols[-1][1]:.2f})"
    )

    return {
        "mode": "single_record_variance",
        "connection_strength": round(1.0 - coeff_variation, 4),
        "fluke_chance": None,
        "accuracy_score": accuracy_score,
        "actual_target": actual_target,
        "primary_driver": primary_driver,
        "mean": mean_val,
        "median": median_val,
        "variance": variance_val,
        "std_dev": std_val,
        "coefficient_of_variation": coeff_variation,
        "status_flag": status_flag,
        "per_column_values": per_column,
        "numeric_columns": numeric_cols,
        "description": description,
    }


def process_general_reliability(df, entity_col="Platform", metric_col="Impressions"):
    """
    Finalized Predictive Distribution Engine:
    Calculates the correlation matrix and density probability vectors 
    for the Honeypot Dashboard.

    Automatically detects dataset shape first: a normal multi-row dataset
    still goes through the correlation/density pipeline below, but a
    single-record dataset (one row, many columns) is routed to the
    variance-based report instead, since correlation is undefined for a
    single point.
    """
    if df is None or df.empty:
        return None

    if is_single_record_dataset(df):
        return process_single_record_variance(df, entity_col=entity_col, metric_col=metric_col)

    df_clean = df.copy()
    df_clean.columns = [str(c).lower().strip() for c in df_clean.columns]
    
    target_metric = str(metric_col).lower().strip()
    entity_segment = str(entity_col).lower().strip()

    # Identify numeric vectors
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None

    # Semantic column detection: an explicit caller-supplied metric_col is
    # always honored if it exists; otherwise the best-scoring "measurable
    # outcome" column (Total, Score, Amount Spent, Population...) is chosen
    # instead of blindly grabbing the last numeric column.
    if target_metric in df_clean.columns:
        actual_target = target_metric
    else:
        actual_target = detect_target_metric_column(df_clean) or numeric_cols[-1]

    if entity_segment not in df_clean.columns:
        entity_segment = detect_entity_column(df_clean, exclude={actual_target}) or entity_segment

    other_drivers = [c for c in numeric_cols if c != actual_target]
    if other_drivers:
        primary_driver = detect_target_metric_column(df_clean[other_drivers]) or other_drivers[0]
    else:
        primary_driver = actual_target

    preds = pd.to_numeric(df_clean[primary_driver], errors='coerce').fillna(0).values
    acts = pd.to_numeric(df_clean[actual_target], errors='coerce').fillna(0).values
    
    # Statistical Validation
    if len(preds) < 2 or np.std(preds) == 0 or np.std(acts) == 0:
        connection_strength = 0.0
        fluke_chance = 1.0
    else:
        connection_strength, fluke_chance = pearsonr(preds, acts)
    
    accuracy_score = 1.0 - abs(connection_strength)
    total_population = len(df_clean)

    # Probability Distribution Brackets
    bins = 10
    group_boundaries = np.linspace(0, 1, bins + 1)
    # Normalize data to 0-1 for plotting
    norm_acts = (acts - acts.min()) / (acts.max() - acts.min() + 1e-9)
    
    hist, _ = np.histogram(norm_acts, bins=bins, range=(0, 1))
    group_percentages = hist / total_population
    running_total_share = np.cumsum(hist) / total_population

    # Status Flagging
    if abs(connection_strength) > 0.8:
        status_flag = "OPTIMAL"
        alignment_str = "Strong predictive cohesion"
    elif abs(connection_strength) > 0.4:
        status_flag = "STABLE"
        alignment_str = "Moderate trend alignment"
    else:
        status_flag = "VOLATILE"
        alignment_str = "Weak structural correlation detected"

    description = (
        f"=== HONEYPOT SYSTEM ADVANCED PREDICTIVE COHESION REPORT ===\n"
        f"• Tracked Grid Scope    : [{entity_segment.upper()}] Rows Groupings\n"
        f"• Continuous Axes Setup : [{actual_target.upper()}] connected to [{primary_driver.upper()}]\n"
        f"• Connection Strength   : {connection_strength:.4f} (Directional trend index)\n"
        f"• Fluke Chance (p-val)  : {fluke_chance:.4e}\n"
        f"• System Accuracy Score : {accuracy_score:.4f} (Model trace report card)\n\n"
        f"=== OPERATIONAL DIAGNOSTIC INTERPRETATION ===\n"
        f"STATUS [{status_flag}]: {alignment_str}. Grid outputs show that variations \n"
        f"across your categories trace matching structural trend shifts rather than clean fluke behaviors.\n\n"
        f"• Distribution Breakdown Metrics:\n"
        f"  - Total Evaluated Ledger Records: N = {total_population}\n"
        f"  - Peak Bracket Cluster Load: {max(group_percentages)*100:.2f}% inside localized group percentages."
    )

    return {
        "connection_strength": connection_strength,
        "fluke_chance": fluke_chance,
        "group_boundaries": group_boundaries.tolist(),
        "group_percentages": group_percentages.tolist(),
        "running_total_share": running_total_share.tolist(),
        "accuracy_score": accuracy_score,
        "description": description,
        "primary_driver": primary_driver,
        "actual_target": actual_target,
        "classroom_diagnostics": compute_classroom_diagnostics(df, entity_col=entity_segment, metric_col=actual_target)
    }


def compute_classroom_diagnostics(df, entity_col="Platform", metric_col="Impressions", top_n=5, pass_threshold=None):
    """
    "Classroom Diagnostic" package for any multi-row dataset (student grades,
    platform stats, sensor logs, sales reps - anything with multiple rows
    and a numeric metric). Deliberately context-aware rather than a
    black-box trend model: everything here measures how each row sits
    relative to the group's OWN baseline (its mean/std), never assumes a
    trend, and stays interpretable even to a non-technical reader.

    Produces: Top/Bottom N performers, Performance Gap, Z-Score
    Benchmarking (top/bottom 10%), Pass/Fail Distribution, Class Variance,
    Difficulty Analysis (relative standing of numeric columns/"subjects"),
    and a conditional-formatting flag per row for the UI to color-code.
    """
    if df is None or df.empty:
        return None

    df_clean = df.copy()
    df_clean.columns = [str(c).lower().strip() for c in df_clean.columns]
    metric = str(metric_col).lower().strip()
    entity = str(entity_col).lower().strip()

    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None
    if metric not in numeric_cols:
        metric = detect_target_metric_column(df_clean) or numeric_cols[-1]

    values = pd.to_numeric(df_clean[metric], errors="coerce").dropna()
    if len(values) < 2:
        return None

    labels = (
        df_clean.loc[values.index, entity].astype(str)
        if entity in df_clean.columns
        else pd.Series([f"Row {i+1}" for i in values.index], index=values.index)
    )

    mean_val = float(values.mean())
    median_val = float(values.median())
    std_val = float(values.std(ddof=0))
    variance_val = float(values.var(ddof=0))

    # --- Top N / Bottom N performers by row ---
    ranked = pd.DataFrame({"entity": labels.values, "value": values.values}).sort_values(
        "value", ascending=False
    ).reset_index(drop=True)
    n = min(top_n, len(ranked))
    top_performers = ranked.head(n).to_dict("records")
    bottom_performers = ranked.tail(n).sort_values("value").to_dict("records")

    # --- Performance Gap: how far apart the best is from the worst ---
    highest_value = float(ranked["value"].iloc[0])
    lowest_value = float(ranked["value"].iloc[-1])
    performance_gap = highest_value - lowest_value

    # --- Z-Score Benchmarking: identify top/bottom 10% ---
    safe_std = std_val if std_val > 1e-9 else 1e-9
    z_scores = (values - mean_val) / safe_std
    percentile_ranks = values.rank(pct=True) * 100
    bench_table = pd.DataFrame({
        "entity": labels.values, "value": values.values,
        "z_score": z_scores.values, "percentile": percentile_ranks.values
    })
    top_10_percent = bench_table[bench_table["percentile"] >= 90].sort_values("value", ascending=False).to_dict("records")
    bottom_10_percent = bench_table[bench_table["percentile"] <= 10].sort_values("value").to_dict("records")

    # --- Pass/Fail Distribution: baseline "success rate", default threshold = class mean ---
    threshold = pass_threshold if pass_threshold is not None else mean_val
    pass_count = int((values >= threshold).sum())
    fail_count = int((values < threshold).sum())
    total = len(values)
    pass_rate = (pass_count / total) * 100 if total else 0.0

    # --- Difficulty Analysis: relative standing across numeric columns ("subjects") ---
    difficulty = []
    for col in numeric_cols:
        col_vals = pd.to_numeric(df_clean[col], errors="coerce").dropna()
        if col_vals.empty:
            continue
        col_std = float(col_vals.std(ddof=0))
        difficulty.append({
            "column": col,
            "mean": float(col_vals.mean()),
            "std_dev": col_std,
            "coefficient_of_variation": col_std / (abs(float(col_vals.mean())) + 1e-9),
        })
    difficulty_sorted = sorted(difficulty, key=lambda d: d["mean"])  # lowest average = hardest/weakest area
    hardest_column = difficulty_sorted[0] if difficulty_sorted else None
    easiest_column = difficulty_sorted[-1] if difficulty_sorted else None

    # --- Conditional-formatting flag per row (drives color-coding in the UI/PDF) ---
    def _flag_for(z):
        if z >= 1.0:
            return "EXCELS", "#22C55E"      # green
        elif z <= -1.0:
            return "NEEDS ATTENTION", "#EF4444"  # red
        else:
            return "ON TRACK", "#F59E0B"    # amber

    row_flags = []
    for ent, val, z in zip(labels.values, values.values, z_scores.values):
        flag_label, flag_color = _flag_for(z)
        row_flags.append({
            "entity": ent, "value": float(val), "z_score": float(z),
            "flag": flag_label, "color": flag_color
        })

    return {
        "metric": metric,
        "entity": entity,
        "class_mean": mean_val,
        "class_median": median_val,
        "class_std_dev": std_val,
        "class_variance": variance_val,
        "top_performers": top_performers,
        "bottom_performers": bottom_performers,
        "performance_gap": performance_gap,
        "highest_value": highest_value,
        "lowest_value": lowest_value,
        "top_10_percent": top_10_percent,
        "bottom_10_percent": bottom_10_percent,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "pass_rate": pass_rate,
        "pass_threshold": threshold,
        "difficulty_analysis": difficulty_sorted,
        "hardest_column": hardest_column,
        "easiest_column": easiest_column,
        "row_flags": row_flags,
    }

# Add these to C:\Local_Projects\project_honeypot\core\analytics_engine.py

def get_weighted_stability(df):
    target, _ = get_universal_metrics(df)
    if not target: return 0.0
    data = pd.to_numeric(df[target], errors='coerce').fillna(0)
    return data.mean() / (data.std() + 1) # Resilience index

def detect_regime_shift(df):
    target, _ = get_universal_metrics(df)
    if not target: return False, []
    data = pd.to_numeric(df[target], errors='coerce').fillna(0)
    return data.std() > data.mean(), []

def get_universal_metrics(df):
    """Dynamically find the best numeric and categorical columns."""
    df_clean = df.copy()
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) == 0: return None, None
    
    # Heuristic: Pick the column with the highest variance as the target
    target = numeric_cols[np.argmax(df_clean[numeric_cols].var())]
    
    # Pick the first non-numeric column as the category
    cat_cols = [c for c in df.columns if c not in numeric_cols]
    category = cat_cols[0] if cat_cols else None
    
    return target, category

def get_attribution_map(df):
    target, category = get_universal_metrics(df)
    if not target or not category: return pd.Series(dtype=float)
    return df.groupby(category)[target].mean().nlargest(8)

def compute_universal_stability(df):
    target, _ = get_universal_metrics(df)
    if not target: return 0.0
    
    data = pd.to_numeric(df[target], errors='coerce').fillna(0)
    # Stability = Mean / (StdDev + 1) -> Higher value is more stable
    return data.mean() / (data.std() + 1)

def get_attribution_map(df):
    """
    Schema-aware: Ignores unique IDs and groups by relevant categories.
    """
    df_clean = df.copy()
    df_clean.columns = df_clean.columns.str.strip().str.lower()
    
    # 1. Dynamically find numeric and categorical columns
    numeric_col = df_clean.select_dtypes(include=[np.number]).columns[0]
    
    # 2. Heuristic: Avoid columns with 'id' or 'name' (these are unique)
    cat_cols = [c for c in df_clean.columns if c not in numeric_col and 'id' not in c and 'name' not in c]
    
    if not cat_cols:
        cat_cols = [c for c in df_clean.columns if c != numeric_col] # Fallback
    
    category = cat_cols[0]
    return df_clean.groupby(category)[numeric_col].mean().nlargest(8)