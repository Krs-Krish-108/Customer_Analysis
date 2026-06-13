# 🛍️ RetailIQ — AI-Powered Retail Customer Analytics Dashboard

> A portfolio-grade, full-stack analytics SaaS application built with Flask, trained ML models, SQLite, Bootstrap 5, and Chart.js. Powered by the UCI Online Retail Dataset.

![Python](https://img.shields.io/badge/Python-3.10%2B-3b82f6?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-10b981?style=flat-square&logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-f59e0b?style=flat-square&logo=scikit-learn)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-8b5cf6?style=flat-square&logo=bootstrap)

---

## 📌 Project Overview

RetailIQ is a production-style retail analytics platform that demonstrates end-to-end machine learning integration — from customer segmentation and churn prediction, to product recommendations and revenue forecasting — all surfaced through a sleek dark-mode SaaS dashboard.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Customer Segmentation** | KMeans (k=4) clustering on RFM features → VIP / Loyal / Regular / At Risk |
| **Churn Prediction** | Random Forest model with 5 features → Low / Medium / High risk + probability % |
| **Product Recommendations** | Apriori association rules → confidence + lift scores per product pair |
| **Demand Forecasting** | Prophet time-series → daily revenue forecast with confidence intervals |
| **Live Prediction** | Single-customer form → instant ML inference → SQLite storage |
| **Batch Upload** | Upload any UCI-format CSV → auto-compute RFM → batch predictions |
| **Prediction History** | Searchable, sortable prediction log backed by SQLite |
| **Dark SaaS Dashboard** | Glassmorphism cards, Chart.js charts, Bootstrap 5, Font Awesome 6 |

---

## 🏗️ Architecture

```
Browser
  ↓ HTTP
Flask (app.py)
  ├── utils/preprocessing.py   ← CSV loaders
  ├── utils/segmentation.py    ← KMeans + StandardScaler
  ├── utils/churn.py           ← Random Forest
  ├── utils/recommendation.py  ← Apriori rules lookup
  ├── utils/forecasting.py     ← Prophet CSV reader
  └── utils/database.py        ← SQLite CRUD
        ↓
    database/retail.db
```

---

## 📂 Folder Structure

```
Retail-Customer-Analytics/
├── app.py                    ← Flask application (routes only)
├── requirements.txt
├── README.md
├── .gitignore
│
├── models/
│   ├── kmeans.pkl            ← Trained KMeans model
│   ├── scaler.pkl            ← StandardScaler
│   ├── churn_model.pkl       ← Random Forest classifier
│   └── forecast_model.pkl    ← Prophet model (training artifact only)
│
├── data/
│   ├── customer_segments.csv
│   ├── customer_churn.csv
│   ├── recommendation_rules.csv
│   ├── sales_forecast.csv
│   ├── cluster_summary.csv
│   └── dashboard_summary.json
│
├── database/
│   └── retail.db             ← SQLite (auto-created)
│
├── docs/
│   └── architecture.md
│
├── notebooks/
│   └── retail_customer_analysis.ipynb
│
├── utils/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── segmentation.py
│   ├── churn.py
│   ├── recommendation.py
│   ├── forecasting.py
│   └── database.py
│
├── static/
│   ├── css/style.css
│   └── js/
│
└── templates/
    ├── base.html
    ├── index.html
    ├── dashboard.html
    ├── segmentation.html
    ├── churn.html
    ├── recommendations.html
    ├── forecasting.html
    ├── customer_entry.html
    ├── upload_dataset.html
    └── history.html
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/your-username/retail-customer-analytics.git
cd retail-customer-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Then open: **http://localhost:5000**

---

## 🚀 Usage

### Dashboard
Navigate to `/dashboard` to view the main KPI overview including total revenue, customers, orders, segment distribution, and a live forecast preview.

### Live Prediction (`/customer-entry`)
1. Enter: Customer ID, Recency, Frequency, Monetary, Total Revenue, Total Quantity, Unique Products
2. Click **Run Prediction**
3. System runs KMeans segmentation + Random Forest churn prediction
4. Results are stored to SQLite and displayed instantly

### Product Recommendations (`/recommendations`)
1. Select a product from the dropdown
2. View ranked recommendation cards with confidence and lift scores

### Demand Forecasting (`/forecasting`)
Toggle between 7-day, 30-day, or full forecast view. Confidence intervals shown.

### Batch Upload (`/upload-dataset`)
Upload a CSV with columns: `CustomerID, InvoiceDate, Quantity, UnitPrice`
The system computes RFM automatically and runs batch predictions.

### History (`/history`)
View all predictions with search, filter by risk level/segment, and column sorting.

---

## 📊 Dataset Information

**Source**: [UCI Machine Learning Repository — Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/online+retail)

- **Records**: ~541,909 transactions
- **Customers**: ~4,338 unique
- **Period**: December 2010 – December 2011
- **Geography**: United Kingdom (primarily)

---

## 🤖 ML Models Used

| Model | Library | Input Features | Output |
|---|---|---|---|
| **KMeans** (k=4) | scikit-learn | Recency, Frequency, Monetary | Cluster 0–3 → Segment |
| **StandardScaler** | scikit-learn | RFM | Scaled features |
| **Random Forest** | scikit-learn | Frequency, Monetary, TotalRevenue, TotalQuantity, UniqueProducts | Churn probability |
| **Apriori Rules** | mlxtend | Transaction data | antecedent → consequent + confidence + lift |
| **Prophet** | prophet | Daily revenue time series | yhat, yhat_lower, yhat_upper |

### Cluster Mapping (KMeans)
```python
{0: "Regular", 1: "At Risk", 2: "VIP", 3: "Loyal"}
```

### Churn Risk Thresholds
```python
probability >= 0.70 → "High Risk"
probability >= 0.40 → "Medium Risk"
probability  < 0.40 → "Low Risk"
```

---

## 🖼️ Screenshots

> _Add screenshots of your dashboard, customer entry, and recommendation pages here._

---

## 🔮 Future Improvements

- [ ] User authentication (Flask-Login)
- [ ] Email alerts for high-risk customers
- [ ] A/B test tracking per segment
- [ ] Customer 360 profile view
- [ ] REST API with JWT tokens
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Docker containerisation
- [ ] Real-time streaming predictions

---

## 📄 License

MIT License — see `LICENSE` for details.
