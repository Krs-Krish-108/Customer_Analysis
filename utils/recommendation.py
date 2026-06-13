"""
utils/recommendation.py
========================
Product recommendation engine using Apriori association rules.

Source: data/recommendation_rules.csv (canonical — never use duplicates)
"""

import pandas as pd


def get_all_products(rules_df: pd.DataFrame) -> list[str]:
    """Return a sorted list of all unique antecedent products."""
    if rules_df.empty or "antecedents_clean" not in rules_df.columns:
        return []
    products = rules_df["antecedents_clean"].dropna().unique().tolist()
    return sorted([p for p in products if p.strip()])


def get_recommendations(rules_df: pd.DataFrame, product: str) -> list[dict]:
    """
    Find all recommendations for a given product (exact antecedent match).

    Returns a list of dicts ordered by lift (descending), each containing:
      rank, product, lift, conf, conf_pct, support
    """
    if rules_df.empty or not product:
        return []

    matching = (
        rules_df[rules_df["antecedents_clean"] == product.strip()]
        .copy()
        .sort_values("lift", ascending=False)
        .reset_index(drop=True)
    )

    results = []
    for i, (_, row) in enumerate(matching.iterrows()):
        results.append(
            {
                "rank": i + 1,
                "product": row["consequents_clean"],
                "lift": f"{row['lift']:.2f}",
                "lift_float": round(float(row["lift"]), 2),
                "conf": f"{row['confidence']:.1%}",
                "conf_pct": round(float(row["confidence"]) * 100, 1),
                "support": f"{row['support']:.4f}",
            }
        )
    return results


def get_overview(rules_df: pd.DataFrame) -> dict:
    """Return summary statistics for the rule set."""
    if rules_df.empty:
        return {"total": 0, "max_lift": "—", "avg_conf": "—", "products": 0}
    return {
        "total": len(rules_df),
        "max_lift": f"{rules_df['lift'].max():.2f}",
        "avg_conf": f"{rules_df['confidence'].mean():.1%}",
        "products": rules_df["antecedents_clean"].nunique(),
    }
