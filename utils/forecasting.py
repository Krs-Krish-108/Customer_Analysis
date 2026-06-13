"""
utils/forecasting.py
=====================
Demand forecast data loader.

Source: data/sales_forecast.csv (Prophet output — never use forecast_model.pkl at runtime)
forecast_model.pkl is kept only as a training artifact in the models/ directory.

CSV columns: ds, yhat, yhat_lower, yhat_upper
"""

import pandas as pd
from utils.preprocessing import load_forecast_data


def get_forecast_series(days: int | None = None) -> list[dict]:
    """
    Return forecast data as a list of JSON-serialisable dicts.

    Parameters
    ----------
    days : int or None
        If provided, return only the last `days` rows from the CSV.
        None returns the full dataset.

    Each dict contains: date, forecast, lower, upper
    """
    df = load_forecast_data()
    if df.empty:
        return []

    if days is not None:
        df = df.tail(days)

    return [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "forecast": round(float(row["yhat"]), 2),
            "lower": round(float(row["yhat_lower"]), 2),
            "upper": round(float(row["yhat_upper"]), 2),
        }
        for _, row in df.iterrows()
    ]


def get_forecast_summary(days: int | None = None) -> dict:
    """
    Return summary KPIs for the forecast series.

    Returns dict with: max_forecast, avg_forecast, min_lower, max_upper,
    start_date, end_date, total_points
    """
    df = load_forecast_data()
    if df.empty:
        return {}

    if days is not None:
        df = df.tail(days)

    return {
        "max_forecast": round(float(df["yhat"].max()), 2),
        "avg_forecast": round(float(df["yhat"].mean()), 2),
        "min_lower": round(float(df["yhat_lower"].min()), 2),
        "max_upper": round(float(df["yhat_upper"].max()), 2),
        "start_date": df["ds"].min().strftime("%Y-%m-%d"),
        "end_date": df["ds"].max().strftime("%Y-%m-%d"),
        "total_points": len(df),
    }
