"""
utils/segmentation.py  (updated)
=================================
KMeans customer segmentation.

Internal ML values are translated to retailer-friendly labels before display.
"""

import os
import warnings

import joblib
import numpy as np

warnings.filterwarnings("ignore")

ROOT       = os.path.dirname(os.path.dirname(__file__))
MODELS_DIR = os.path.join(ROOT, "models")

# ── Internal cluster → ML segment ─────────────────────────────────────────
CLUSTER_MAP: dict[int, str] = {
    0: "Regular",
    1: "At Risk",
    2: "VIP",
    3: "Loyal",
}

# ── ML segment → Retailer-friendly label ──────────────────────────────────
SEGMENT_LABEL_MAP: dict[str, str] = {
    "VIP":     "Best Customers",
    "Loyal":   "Repeat Customers",
    "Regular": "Standard Customers",
    "At Risk": "Customers You May Lose",
}

# ── Reverse map (friendly → ML) ───────────────────────────────────────────
FRIENDLY_TO_ML: dict[str, str] = {v: k for k, v in SEGMENT_LABEL_MAP.items()}

# ── Colours keyed by FRIENDLY label ───────────────────────────────────────
SEGMENT_COLORS: dict[str, str] = {
    "Best Customers":        "#10b981",
    "Repeat Customers":      "#3b82f6",
    "Standard Customers":    "#64748b",
    "Customers You May Lose":"#ef4444",
    # Also keep ML names as fallback
    "VIP":     "#10b981",
    "Loyal":   "#3b82f6",
    "Regular": "#64748b",
    "At Risk": "#ef4444",
}

SEGMENT_BADGE_CLASS: dict[str, str] = {
    "Best Customers":        "badge-vip",
    "Repeat Customers":      "badge-loyal",
    "Standard Customers":    "badge-regular",
    "Customers You May Lose":"badge-risk",
    "VIP":     "badge-vip",
    "Loyal":   "badge-loyal",
    "Regular": "badge-regular",
    "At Risk": "badge-risk",
}

# Suggested business actions per segment
SEGMENT_ACTIONS: dict[str, list[str]] = {
    "Best Customers":        ["Send VIP loyalty rewards", "Offer early access to new products", "Request testimonials or referrals"],
    "Repeat Customers":      ["Offer a subscription or bundle deal", "Send personalised thank-you messages", "Provide exclusive member discounts"],
    "Standard Customers":    ["Send product recommendations", "Run promotional campaigns", "Invite to loyalty programme"],
    "Customers You May Lose":["Send re-engagement offers", "Follow up with a personal call", "Provide a win-back discount"],
}


def _load_models():
    try:
        kmeans = joblib.load(os.path.join(MODELS_DIR, "kmeans.pkl"))
        scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.pkl"))
        return kmeans, scaler
    except Exception as exc:
        print(f"[segmentation] Model load failed: {exc}")
        return None, None


_KMEANS, _SCALER = _load_models()


def models_loaded() -> bool:
    return _KMEANS is not None and _SCALER is not None


def predict_segment(recency: float, frequency: float, monetary: float) -> dict:
    """
    Returns dict with:
      cluster (int), segment (ML label), customer_category (friendly label),
      color, badge_class, actions (list[str])
    """
    if not models_loaded():
        raise RuntimeError("Segmentation models are not loaded.")

    features = np.array([[recency, frequency, monetary]], dtype=float)
    scaled   = _SCALER.transform(features)
    cluster  = int(_KMEANS.predict(scaled)[0])
    segment  = CLUSTER_MAP.get(cluster, "Regular")
    category = SEGMENT_LABEL_MAP.get(segment, segment)

    return {
        "cluster":           cluster,
        "segment":           segment,
        "customer_category": category,
        "color":             SEGMENT_COLORS.get(category, "#64748b"),
        "badge_class":       SEGMENT_BADGE_CLASS.get(category, "badge-regular"),
        "actions":           SEGMENT_ACTIONS.get(category, []),
    }
