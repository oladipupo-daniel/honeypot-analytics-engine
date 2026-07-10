# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
"""
semantic_mapper.py

Single source of truth for "which column actually matters here?" - the
question every screen in Honeypot Analytics used to answer differently
(and often wrongly, e.g. "just grab the last numeric column" or "just grab
the first text column"). That's how the app ended up analyzing an ID
column, a row-index, or an arbitrary numeric field instead of the real
performance metric.

This module scores column NAMES against known real-world vocabularies -
"Total"/"Score"/"Amount Spent" as measurable outcomes, "Credit Card"/
"Country"/"Student"/"Class" as the entity a row is about - so that whatever
sheet gets uploaded (grades, payments, population, sales, sports, sensors),
the app targets the column a human would actually pick by eye.

Examples this is built to get right:
- Student/Class sheet     -> entity = Student/Class,   metric = Total/Score
- Payments/Credit Card     -> entity = Credit Card,      metric = Amount/Total Spent
- Country/Population       -> entity = Country,          metric = Population
"""

import re
import numpy as np
import pandas as pd

# Columns that represent a MEASURABLE OUTCOME worth analyzing/forecasting -
# the "target metric". Longer/more specific phrases are listed too so a
# column like "Amount Spent" or "Total Score" scores higher than a vague
# generic numeric column.
METRIC_KEYWORDS = [
    "total score", "total scores", "final score", "amount spent", "total spent",
    "total", "score", "scores", "performance", "amount", "spent", "spend",
    "population", "revenue", "sales", "value", "reach", "profit", "impressions",
    "balance", "grade", "grades", "gpa", "sum", "count", "engagement",
    "conversion", "rating", "growth", "quantity", "cost", "price", "income",
    "expense", "attendance", "output", "yield", "volume", "points", "goals",
    "transaction", "transactions", "views", "clicks", "sessions",
]

# Numeric-looking columns that are actually IDENTIFIERS, not metrics, and
# should never be picked as the analysis target even though they're numbers.
ID_KEYWORDS = [
    "id", "code", "number", "ssn", "security number", "card number",
    "account number", "phone", "zip", "postal", "index", "key", "uuid",
    "reference", "barcode",
]

# Columns that represent the ENTITY / "who or what is this row about" -
# the grouping/label column, as opposed to the metric being measured.
ENTITY_KEYWORDS = [
    "name", "platform", "category", "type", "country", "class", "student",
    "team", "region", "department", "product", "credit card", "card",
    "customer", "client", "employee", "player", "subject", "branch",
    "store", "channel", "campaign", "school", "company", "vendor", "merchant",
]


def _clean(col_name):
    """Lowercase, de-underscore a column name for keyword matching."""
    return re.sub(r"[_\-]+", " ", str(col_name).strip().lower())


def _score(col_clean, keywords):
    """
    Counts how many vocabulary phrases appear in the column name. Multi-word
    phrases (e.g. 'amount spent') are checked as substrings; single words are
    checked as whole words so 'id' doesn't match inside 'video'.
    """
    total = 0
    for kw in keywords:
        if " " in kw:
            if kw in col_clean:
                total += 2  # a specific multi-word match is a stronger signal
        elif re.search(r"\b" + re.escape(kw) + r"\b", col_clean):
            total += 1
    return total


def is_identifier_column(col_name):
    """True for columns that are clearly IDs/codes, not metrics to analyze."""
    return _score(_clean(col_name), ID_KEYWORDS) > 0


def detect_target_metric_column(df, preferred=None):
    """
    Picks the numeric column that best represents a measurable outcome -
    Total, Score, Amount Spent, Population, Revenue, etc. - instead of
    defaulting to "the last numeric column", which is how the wrong field
    kept getting analyzed. ID-like numeric columns are always excluded
    unless there is truly nothing else to work with.

    `preferred`, if given and present/numeric/non-ID, is always honored -
    this keeps any explicit user or caller choice in charge.
    """
    if df is None or df.empty:
        return None

    if preferred and preferred in df.columns and pd.api.types.is_numeric_dtype(df[preferred]) \
            and not is_identifier_column(preferred):
        return preferred

    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if not is_identifier_column(c)]
    if not numeric_cols:
        # Nothing but ID-like numeric columns exist - better to analyze one
        # of those than to return nothing at all.
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return None

    scored = sorted(
        ((_score(_clean(c), METRIC_KEYWORDS), c) for c in numeric_cols),
        key=lambda t: t[0], reverse=True
    )
    if scored[0][0] > 0:
        return scored[0][1]

    # No column name matched any known metric vocabulary (e.g. an unlabeled
    # export) - the highest-variance numeric column is a far better default
    # than an arbitrary positional pick.
    variances = df[numeric_cols].var()
    return variances.idxmax()


def detect_entity_column(df, preferred=None, exclude=None):
    """
    Picks the best "who/what is this row about" column - Student, Country,
    Credit Card, Platform, Class - rather than defaulting to "the first text
    column" regardless of what it actually is.
    """
    if df is None or df.empty:
        return None

    exclude = set(exclude or [])

    if preferred and preferred in df.columns and preferred not in exclude:
        return preferred

    candidate_cols = [c for c in df.columns if c not in exclude]
    non_numeric = [c for c in candidate_cols if not pd.api.types.is_numeric_dtype(df[c])]

    # Prefer columns whose name matches known entity vocabulary; a date/time/
    # URL-looking column is deprioritized since it isn't really a group label.
    def _is_junk(c):
        cl = _clean(c)
        return any(tok in cl for tok in ["date", "time", "url", "link", "timestamp"])

    usable_non_numeric = [c for c in non_numeric if not _is_junk(c)] or non_numeric

    if usable_non_numeric:
        scored = sorted(
            ((_score(_clean(c), ENTITY_KEYWORDS), c) for c in usable_non_numeric),
            key=lambda t: t[0], reverse=True
        )
        if scored[0][0] > 0:
            return scored[0][1]
        return usable_non_numeric[0]

    # No text/category column at all - an ID-like numeric column can still
    # serve as a row label (e.g. "Student ID", "Account Number").
    id_like = [c for c in candidate_cols if is_identifier_column(c)]
    if id_like:
        return id_like[0]

    return None  # caller should fall back to synthetic "Row N" labels


def detect_target_and_entity(df, metric_hint=None, entity_hint=None):
    """Convenience wrapper: resolves both the metric and entity column in one call."""
    metric_col = detect_target_metric_column(df, preferred=metric_hint)
    entity_col = detect_entity_column(df, preferred=entity_hint, exclude={metric_col} if metric_col else None)
    return metric_col, entity_col
