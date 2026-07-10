# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def render_velocity_chart(frame, df, metric_col):
    """
    Renders a clean velocity vs SMA visualization.
    """
    fig, ax = plt.subplots(figsize=(5, 2), dpi=100)
    
    # Plot data
    ax.plot(df.index, df[metric_col], label="Raw Data", color="#10B981", alpha=0.6)
    ax.plot(df.index, df['SMA_7'], label="7-Day SMA", color="#F59E0B", linestyle="--")
    
    # Styling
    ax.set_title(f"Performance Velocity: {metric_col}", fontsize=10, color="white")
    ax.set_facecolor("#1E293B")
    fig.patch.set_facecolor("#0F172A")
    ax.tick_params(colors="white", labelsize=8)
    
    return FigureCanvasTkAgg(fig, master=frame)