"""
# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
theme_manager.py

Single source of truth for Honeypot Analytics' visual skins.

Design goals:
- Exactly one place where colors live, so every screen (gateway, onboarding,
  dashboard, ingestion) stays visually consistent.
- The chosen skin persists locally on the user's machine (same folder the
  vault lives in) so it survives app restarts - no account/server needed.
- Adding a 4th, 5th... skin later is just adding a dict entry below.
"""

import json
import os

# Local, per-machine config home. Same folder auth_utils.py uses for the vault,
# so everything "that belongs to this install" lives in one tidy place.
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".honeypot_analytics")
CONFIG_FILE = os.path.join(CONFIG_DIR, "branding_config.json")

os.makedirs(CONFIG_DIR, exist_ok=True)

DEFAULT_THEME = "midnight_sovereign"

THEMES = {
    "midnight_sovereign": {
        "label": "Midnight Sovereign",
        "emoji": "🌙",
        "appearance": "dark",
        "bg_main": "#0F172A",
        "bg_panel": "#1E293B",
        "bg_card": "#111524",
        "text_color": "#F1F5F9",
        "muted_text": "#94A3B8",
        "accent": "#38BDF8",
        "accent_hover": "#0284C7",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "honey": "#F59E0B",
        "honey_hover": "#D97706",
        "honey_text": "#1F1300",
        "border": "#334155",
        "swatch": "#0F172A",
    },
    "honeycomb_gold": {
        "label": "Honeycomb Gold",
        "emoji": "🍯",
        "appearance": "light",
        "bg_main": "#FFFBEB",
        "bg_panel": "#FEF3C7",
        "bg_card": "#FDE68A",
        "text_color": "#451A03",
        "muted_text": "#92400E",
        "accent": "#D97706",
        "accent_hover": "#B45309",
        "success": "#16A34A",
        "warning": "#EA580C",
        "danger": "#DC2626",
        "honey": "#F59E0B",
        "honey_hover": "#B45309",
        "honey_text": "#1F1300",
        "border": "#FBBF24",
        "swatch": "#F59E0B",
    },
    "arctic_frost": {
        "label": "Arctic Frost",
        "emoji": "❄️",
        "appearance": "light",
        "bg_main": "#F8FAFC",
        "bg_panel": "#FFFFFF",
        "bg_card": "#EFF6FF",
        "text_color": "#0F172A",
        "muted_text": "#64748B",
        "accent": "#2563EB",
        "accent_hover": "#1D4ED8",
        "success": "#059669",
        "warning": "#F59E0B",
        "danger": "#DC2626",
        "honey": "#F59E0B",
        "honey_hover": "#D97706",
        "honey_text": "#1F1300",
        "border": "#DBEAFE",
        "swatch": "#2563EB",
    },
}


def _load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_config(updates: dict):
    config = _load_config()
    config.update(updates)
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except OSError:
        pass
    return config


def list_themes():
    """Returns [(key, theme_dict), ...] in a stable, deliberate display order."""
    order = ["midnight_sovereign", "honeycomb_gold", "arctic_frost"]
    return [(key, THEMES[key]) for key in order if key in THEMES]


def get_active_theme_name():
    config = _load_config()
    name = config.get("theme", DEFAULT_THEME)
    return name if name in THEMES else DEFAULT_THEME


def get_active_theme():
    return THEMES[get_active_theme_name()]


def set_active_theme(name: str):
    if name not in THEMES:
        name = DEFAULT_THEME
    _save_config({"theme": name})
    return THEMES[name]


def get_theme(name: str = None):
    if name is None:
        return get_active_theme()
    return THEMES.get(name, THEMES[DEFAULT_THEME])
