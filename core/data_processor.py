# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
import pandas as pd
import numpy as np

def calculate_realtime_metrics(df, metric_col):
    """
    Calculates dynamic velocity and trends for real-time dashboards.
    - Velocity: Percentage change between time steps.
    - SMA_7: 7-period moving average for smoothing noise.

    A single-row dataset has no "previous step" to compare against, so
    Velocity/SMA are left as 0 / the value itself rather than producing
    all-NaN columns that would look like a bug downstream.
    """
    # Ensure index is sorted for chronological math
    df = df.sort_index()

    if len(df) < 2:
        df['Velocity'] = 0.0
        df['SMA_7'] = df[metric_col]
        return df

    # Calculate % change (Velocity)
    df['Velocity'] = df[metric_col].pct_change() * 100
    
    # Calculate Moving Average
    df['SMA_7'] = df[metric_col].rolling(window=7).mean()
    
    return df

def identify_anomalies(df, metric_col):
    """
    Flags data points outside the standard Interquartile Range.
    With a single row there's no distribution to compute quartiles from, so
    nothing is flagged rather than raising a spurious anomaly.
    """
    if len(df) < 2:
        return pd.Series([False] * len(df), index=df.index)

    q1 = df[metric_col].quantile(0.25)
    q3 = df[metric_col].quantile(0.75)
    iqr = q3 - q1
    return (df[metric_col] < (q1 - 1.5 * iqr)) | (df[metric_col] > (q3 + 1.5 * iqr))

import pandas as pd

def auto_map_columns(df):
    """
    Intelligently identifies columns based on semantic similarity.
    Returns a dictionary mapping of system-critical roles.
    """
    mapping = {
        'target': None,     
        'engagement': [],   
        'category': None    
    }
    
    cols = [c.lower() for c in df.columns]
    
    for col in df.columns:
        c_lower = col.lower()
        if any(keyword in c_lower for keyword in ['impression', 'revenue', 'value', 'reach']):
            if mapping['target'] is None: # Pick the first relevant match as target
                mapping['target'] = col
        elif any(x in c_lower for x in ['like', 'share', 'comment', 'engagement']):
            mapping['engagement'].append(col)
        elif any(x in c_lower for x in ['type', 'category', 'platform']):
            mapping['category'] = col
            
    return mapping

def get_salient_columns(df, limit=8):
    """
    Ranks columns by their diagnostic value (Coefficient of Variation).
    Keeps high-entropy columns, discards static/noise columns.
    """
    # 1. Filter numeric data for variance analysis
    numeric_df = df.select_dtypes(include=[np.number])
    
    # 2. Calculate Coefficient of Variation (std / mean)
    # This identifies which columns have the most "action"
    cv = numeric_df.std() / (numeric_df.mean() + 1e-6)
    
    # 3. Sort by saliency and keep the top N
    top_cols = cv.nlargest(limit).index.tolist()
    
    # 4. Always ensure essential columns (like Content Type/Platform) stay
    essential = [c for c in df.columns if any(x in c.lower() for x in ['type', 'platform', 'date'])]
    
    final_cols = list(set(top_cols + essential))
    return final_cols[:limit]