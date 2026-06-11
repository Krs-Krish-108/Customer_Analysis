# Smart Retail Customer Behavior Analytics Platform

A professional web application built with Flask, Bootstrap 5, and Plotly to analyze customer behavior, RFM (Recency, Frequency, Monetary) metrics, and market-basket recommendations.

## Features

- **Executive Dashboard**: High-level KPI metrics, segment distributions (VIP, Regular, At-Risk), and revenue insights.
- **Customer Insights**: Deep dive into individual customer RFM profiles with detailed radar charts and percentile rankings.
- **Product Recommendations**: Market-basket association rules with lift and confidence scoring for targeted upselling.
- **Analytics**: Deep-dive visualisations of purchasing patterns across segments using histograms, box plots, and treemaps.

## Tech Stack

- **Backend**: Python, Flask, Pandas, Joblib
- **Frontend**: HTML5, CSS3, Bootstrap 5, Custom Glassmorphism Theme
- **Data Visualisation**: Plotly (Python) & Plotly.js

## Project Structure

```
.
├── app.py                   # Main Flask application and routing
├── customer_segments.csv    # Customer RFM data and clusters
├── recommendation_rules.csv # Apriori/FP-Growth association rules
├── kmeans_model.pkl         # Trained KMeans clustering model
├── static/
│   └── css/style.css        # Custom dark theme and animations
└── templates/
    ├── base.html            # Base layout with sidebar and topbar
    ├── dashboard.html       # Executive dashboard view
    ├── insights.html        # Customer lookup and profiling
    ├── recommendations.html # Product recommendations view
    └── analytics.html       # Tabbed analytics charts
```

## Running Locally

1. **Clone the repository** (or download the files).
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```
3. **Activate the virtual environment**:
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Run the application**:
   ```bash
   python app.py
   ```
6. **View the app**: Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.
