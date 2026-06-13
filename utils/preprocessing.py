"""
utils/preprocessing.py
=======================
Data loading and preprocessing utilities.

All CSV paths are resolved relative to the project root so that
the module works regardless of the working directory.
"""

import os
import re
import json

import pandas as pd

# ── Path helpers ───────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")


def _data(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


# ── Frozenset string cleaner (for Apriori rules CSV) ──────────────────────

def _clean_frozenset(val) -> str:
    """Convert a frozenset-string representation to a plain product name."""
    if pd.isna(val):
        return ""
    val = str(val)
    val = re.sub(r"frozenset\(\{?", "", val)
    val = re.sub(r"\}?\)", "", val)
    val = val.replace('"', "").replace("'", "").strip(", ").strip()
    return val


# ── Loaders ───────────────────────────────────────────────────────────────

def load_customer_segments() -> pd.DataFrame:
    """Load the customer segments CSV and normalise column names."""
    try:
        df = pd.read_csv(_data("customer_segments.csv"))
        df.columns = [c.strip() for c in df.columns]
        if "Segments" in df.columns:
            df.rename(columns={"Segments": "Segment"}, inplace=True)
        df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
        df.dropna(subset=["CustomerID"], inplace=True)
        df["CustomerID"] = df["CustomerID"].astype(int)
        return df
    except FileNotFoundError:
        return pd.DataFrame(
            columns=["CustomerID", "Recency", "Frequency", "Monetary", "Cluster", "Segment"]
        )


def load_churn_data() -> pd.DataFrame:
    """Load the customer churn dataset."""
    try:
        df = pd.read_csv(_data("customer_churn.csv"))
        df.columns = [c.strip() for c in df.columns]
        df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")
        df.dropna(subset=["CustomerID"], inplace=True)
        df["CustomerID"] = df["CustomerID"].astype(int)
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def load_recommendation_rules() -> pd.DataFrame:
    """Load Apriori association rules and clean frozenset strings."""
    try:
        df = pd.read_csv(_data("recommendation_rules.csv"))
        df.columns = [c.strip() for c in df.columns]
        df["antecedents_clean"] = df["antecedents"].apply(_clean_frozenset)
        df["consequents_clean"] = df["consequents"].apply(_clean_frozenset)
        # Keep only single-product antecedent rules (easier to search)
        df = df[df["antecedents_clean"].str.len() > 0].reset_index(drop=True)
        return df
    except FileNotFoundError:
        return pd.DataFrame()


def load_forecast_data() -> pd.DataFrame:
    """Load the Prophet sales forecast CSV."""
    try:
        df = pd.read_csv(_data("sales_forecast.csv"))
        df.columns = [c.strip() for c in df.columns]
        df["ds"] = pd.to_datetime(df["ds"])
        # Clip negative lower bounds to 0
        df["yhat_lower"] = df["yhat_lower"].clip(lower=0)
        df["yhat"] = df["yhat"].clip(lower=0)
        return df.sort_values("ds").reset_index(drop=True)
    except FileNotFoundError:
        return pd.DataFrame()


def load_cluster_summary() -> pd.DataFrame:
    """Load the cluster centroid summary."""
    try:
        return pd.read_csv(_data("cluster_summary.csv"))
    except FileNotFoundError:
        return pd.DataFrame()


def load_dashboard_summary() -> dict:
    """Load pre-computed KPI summary from JSON, or derive from CSV data."""
    summary_path = _data("dashboard_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, "r") as f:
            return json.load(f)

    # Fallback: derive from segments CSV
    df = load_customer_segments()
    churn_df = load_churn_data()
    if df.empty:
        return {
            "total_revenue": 0,
            "total_customers": 0,
            "total_orders": 0,
            "total_products": 0,
        }

    revenue = float(df["Monetary"].sum()) if "Monetary" in df.columns else 0
    orders = int(churn_df["Frequency"].sum()) if not churn_df.empty and "Frequency" in churn_df.columns else 0
    products = int(churn_df["UniqueProducts"].sum()) if not churn_df.empty and "UniqueProducts" in churn_df.columns else 0

    return {
        "total_revenue": round(revenue, 2),
        "total_customers": len(df),
        "total_orders": orders,
        "total_products": products,
    }


def compute_rfm_from_upload(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given an uploaded CSV with basic transaction columns, compute RFM features.

    Expects columns: CustomerID, InvoiceDate, Quantity, UnitPrice
    Returns DataFrame with: CustomerID, Recency, Frequency, Monetary
    """
    required = {"CustomerID", "InvoiceDate", "Quantity", "UnitPrice"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.copy()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df = df[df["Revenue"] > 0].dropna(subset=["CustomerID", "InvoiceDate"])

    snapshot = df["InvoiceDate"].max()

    rfm = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        Frequency=("InvoiceDate", "count"),
        Monetary=("Revenue", "sum"),
        TotalRevenue=("Revenue", "sum"),
        TotalQuantity=("Quantity", "sum"),
        UniqueProducts=("Revenue", "count"),
    ).reset_index()

    return rfm
