# System Architecture — RetailIQ Analytics Dashboard

## Overview

RetailIQ is a modular Flask application that integrates four trained ML models into a unified retail analytics platform. The architecture follows a clean separation between data loading, ML inference, persistence, and presentation.

---

## System Architecture Diagram

```mermaid
graph TD
    A[Browser] -->|HTTP Request| B[Flask app.py]

    B --> C{Route Handler}

    C --> D[/dashboard]
    C --> E[/segmentation]
    C --> F[/churn]
    C --> G[/recommendations]
    C --> H[/forecasting]
    C --> I[/customer-entry]
    C --> J[/upload-dataset]
    C --> K[/history]
    C --> L[/api/predict]

    D --> M[utils/preprocessing.py]
    E --> M
    F --> M
    G --> N[utils/recommendation.py]
    H --> O[utils/forecasting.py]
    I --> P[utils/segmentation.py]
    I --> Q[utils/churn.py]
    I --> R[utils/database.py]
    J --> M
    J --> P
    J --> Q
    J --> R
    K --> R
    L --> P
    L --> Q
    L --> R

    M --> S[(data/customer_segments.csv)]
    M --> T[(data/customer_churn.csv)]
    M --> U[(data/recommendation_rules.csv)]
    M --> V[(data/sales_forecast.csv)]
    M --> W[(data/dashboard_summary.json)]

    P --> X[(models/kmeans.pkl)]
    P --> Y[(models/scaler.pkl)]
    Q --> Z[(models/churn_model.pkl)]
    O --> V

    R --> AA[(database/retail.db)]

    B --> BB[Jinja2 Templates]
    BB --> CC[Bootstrap 5 + Chart.js Frontend]
```

---

## Data Flow Description

### 1. Dashboard KPI Flow
```
data/dashboard_summary.json
        ↓
utils/preprocessing.load_dashboard_summary()
        ↓
app.py /dashboard route
        ↓
templates/dashboard.html → Chart.js render
```

### 2. Live Prediction Flow
```
User submits form (customer_entry.html)
        ↓
app.py POST /customer-entry
        ↓
utils/database.save_customer(data)
        ↓
utils/segmentation.predict_segment(R, F, M)
   ├── scaler.transform([[R, F, M]])
   └── kmeans.predict(scaled)[0]
        ↓
utils/churn.predict_churn(F, M, TR, TQ, UP)
   └── churn_model.predict_proba(features)[0][1]
        ↓
utils/database.save_prediction(result)
        ↓
Render result card with badges + progress bar
```

### 3. Recommendation Flow
```
User selects product (recommendations.html)
        ↓
app.py POST /recommendations
        ↓
utils/recommendation.get_recommendations(rules_df, product)
   └── filter: antecedents_clean == product → sort by lift DESC
        ↓
Render recommendation cards + lift chart
```

### 4. Forecast Flow
```
data/sales_forecast.csv (Prophet output)
        ↓
utils/forecasting.get_forecast_series(days=N)
        ↓
app.py GET /forecasting
        ↓
templates/forecasting.html → Chart.js line chart
   └── Period tabs: 7d / 30d / Full
```

---

## Module Descriptions

| Module | Responsibility |
|---|---|
| `utils/preprocessing.py` | Load all CSV files, clean frozenset strings, derive RFM from uploads |
| `utils/segmentation.py` | Load KMeans + Scaler, predict_segment(R,F,M) → {cluster, segment} |
| `utils/churn.py` | Load churn RF model, predict_churn(F,M,TR,TQ,UP) → {probability, risk} |
| `utils/recommendation.py` | Filter association rules by antecedent, return ranked cards |
| `utils/forecasting.py` | Slice sales_forecast.csv by day count, return JSON series + summary |
| `utils/database.py` | SQLite init, save_customer, save_prediction, get_all_predictions |

---

## Database Schema

### `customers`
```sql
CREATE TABLE customers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id     TEXT    NOT NULL,
    recency         REAL,
    frequency       REAL,
    monetary        REAL,
    total_revenue   REAL,
    total_quantity  REAL,
    unique_products REAL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `predictions`
```sql
CREATE TABLE predictions (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id       TEXT    NOT NULL,
    segment           TEXT,
    cluster           INTEGER,
    churn_probability REAL,
    churn_risk        TEXT,
    prediction_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `forecast_logs`
```sql
CREATE TABLE forecast_logs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    forecast_date     TEXT,
    predicted_revenue REAL,
    lower_bound       REAL,
    upper_bound       REAL
);
```

---

## Route Map

| Route | Method | Template | Description |
|---|---|---|---|
| `/` | GET | `index.html` | Landing page with hero + stats |
| `/dashboard` | GET | `dashboard.html` | KPI cards + charts |
| `/segmentation` | GET | `segmentation.html` | Cluster analysis |
| `/churn` | GET | `churn.html` | Churn metrics + at-risk table |
| `/recommendations` | GET/POST | `recommendations.html` | Product recommendation engine |
| `/forecasting` | GET | `forecasting.html` | Demand forecast chart |
| `/customer-entry` | GET/POST | `customer_entry.html` | Live ML prediction form |
| `/upload-dataset` | GET/POST | `upload_dataset.html` | Batch CSV processing |
| `/history` | GET | `history.html` | SQLite prediction log |
| `/api/predict` | POST | JSON | API prediction endpoint |
| `/api/forecast` | GET | JSON | Forecast data API |
| `/api/dashboard-stats` | GET | JSON | KPI metrics API |

---

## ML Model Notes

> **Important**: Models are **NEVER** retrained inside Flask. They are loaded once at module import time and used only for inference.

| Model | File | Load strategy |
|---|---|---|
| KMeans | `models/kmeans.pkl` | `joblib.load()` at `utils/segmentation.py` import |
| StandardScaler | `models/scaler.pkl` | `joblib.load()` at `utils/segmentation.py` import |
| Random Forest | `models/churn_model.pkl` | `joblib.load()` at `utils/churn.py` import |
| Prophet | `models/forecast_model.pkl` | **Not loaded at runtime** — training artifact only |

Forecast data is served exclusively from `data/sales_forecast.csv`.
