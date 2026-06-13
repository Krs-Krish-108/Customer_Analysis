"""
utils/churn.py  (updated)
==========================
Churn prediction — with retailer-friendly risk labels.

Fixed feature order (MUST NOT change):
  [Frequency, Monetary, TotalRevenue, TotalQuantity, UniqueProducts]
"""

import os
import warnings

import joblib
import numpy as np

warnings.filterwarnings("ignore")

ROOT       = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, "models")

CHURN_FEATURES = ["Frequency", "Monetary", "TotalRevenue", "TotalQuantity", "UniqueProducts"]

# Retailer-friendly risk labels
RISK_LABEL_MAP: dict[str, str] = {
    "High Risk":   "High Retention Risk",
    "Medium Risk": "Medium Retention Risk",
    "Low Risk":    "Low Retention Risk",
}

RISK_ACTIONS: dict[str, list[str]] = {
    "High Retention Risk":   ["Send loyalty offer immediately", "Run re-engagement campaign", "Contact top inactive customers directly"],
    "Medium Retention Risk": ["Send a personalised check-in", "Offer a product recommendation", "Invite to upcoming sale"],
    "Low Retention Risk":    ["Continue regular engagement", "Reward with occasional offers", "Ask for product feedback"],
}


def _load_churn_model():
    try:
        return joblib.load(os.path.join(MODELS_DIR, "churn_model.pkl"))
    except Exception as exc:
        print(f"[churn] Model load failed: {exc}")
        return None


_CHURN_MODEL = _load_churn_model()


def model_loaded() -> bool:
    return _CHURN_MODEL is not None


def _classify_risk(probability: float) -> str:
    if probability >= 0.70:
        return "High Risk"
    elif probability >= 0.40:
        return "Medium Risk"
    return "Low Risk"


def _risk_badge_class(friendly_risk: str) -> str:
    return {
        "High Retention Risk":   "badge-risk",
        "Medium Retention Risk": "badge-warn",
        "Low Retention Risk":    "badge-safe",
    }.get(friendly_risk, "badge-safe")


def predict_churn(
    frequency: float,
    monetary: float,
    total_revenue: float,
    total_quantity: float,
    unique_products: float,
) -> dict:
    """
    Returns dict with:
      churn_probability (float 0-1)
      churn_risk        (ML label: "High Risk" etc.)
      retention_risk    (friendly: "High Retention Risk" etc.)
      churn_pct         ("XX%")
      badge_class
      actions           (list[str])
    """
    if not model_loaded():
        raise RuntimeError("Churn model is not loaded.")

    features_list = [frequency, monetary, total_revenue, total_quantity, unique_products]
    for i, val in enumerate(features_list):
        if val is None or (isinstance(val, float) and np.isnan(val)):
            raise ValueError(f"Feature '{CHURN_FEATURES[i]}' has invalid value: {val}")

    features      = np.array([features_list], dtype=float)
    probability   = float(_CHURN_MODEL.predict_proba(features)[0][1])
    ml_risk       = _classify_risk(probability)
    friendly_risk = RISK_LABEL_MAP.get(ml_risk, ml_risk)

    return {
        "churn_probability": round(probability, 4),
        "churn_risk":        ml_risk,
        "retention_risk":    friendly_risk,
        "churn_pct":         f"{probability * 100:.1f}%",
        "badge_class":       _risk_badge_class(friendly_risk),
        "actions":           RISK_ACTIONS.get(friendly_risk, []),
    }
