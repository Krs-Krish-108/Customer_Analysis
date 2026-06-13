# RetailIQ User Flow Documentation

This document explains the step-by-step user journey through the RetailIQ platform and how data flows through the system.

## 1. Authentication Flow
- **Entry**: The user lands on the Home Page (`/`). If not authenticated, they only see marketing copy and Call-to-Action buttons.
- **Login/Register**: Users access `/login` or `/register`.
- **Demo Access**: For demonstration purposes, users can click **One-Click Demo Login** to automatically log in as `testuser`.
- **Session**: Once authenticated, a secure Flask session is created, granting access to the CRM dashboard.

## 2. Onboarding & Data Import
When an authenticated user logs in for the first time with an empty database:
- **Empty State**: The dashboard displays a "No Customer Data Found" state.
- **Action**: The user clicks **Generate Demo Data** (or Upload Dataset).
- **Processing**: The `/api/generate-demo-data` endpoint creates dummy customers and transactions, mimicking a real import.
- **Onboarding Card**: Upon refresh, the user sees an onboarding card directing them to the four core modules. This card is dismissed and saved to `localStorage`.

## 3. CRM Workflows

### A. Exploring the Dashboard
- **Top Metrics**: Total Revenue, Total Customers, Total Orders, and At-Risk count are immediately visible.
- **Charts**: Users toggle between Customer Count, Revenue, and Average Spending within the Categories donut chart. Clicking a chart slice deep-links to the filtered Customer Directory.

### B. Searching for Customers
- **Global Search**: Users type in the top-navigation search bar. This queries `/api/search-customers` with the input (Name, ID, or Phone) and displays instant autocomplete results.
- **Directory Search**: On the `/customers` page, users filter the paginated table by Category (e.g., "Best Customers"), Retention Risk, or text query.

### C. Viewing Customer Profiles
- **Profile View (`/customer/<id>`)**: When a specific customer is selected, the application queries the SQLite database for:
  - Personal Details
  - Lifetime Value & Order History
  - AI Recommended Products (frequently bought together)
  - Next Expected Purchase Date
- **Action**: Retailers use this view when a customer calls or enters the store, immediately seeing if they are VIP, what to cross-sell, and if they are at risk of churning.

### D. Entering New Transactions
- **Customer Entry (`/add`)**: 
  - The retailer selects "New Customer" or "Returning Customer".
  - They input the purchase amount, product categories, and date.
  - The system dynamically updates the customer's RFM (Recency, Frequency, Monetary) metrics.
  - *Data Flow*: Form -> `POST /add` -> Insert into `transactions` table -> Background ML Pipeline (optional) -> UI Update.

## 4. Machine Learning Integration
The CRM is uniquely powered by background Machine Learning models that transform raw data into actionable business intelligence:

### A. Customer Segmentation (KMeans)
- **What it does**: Groups customers based on their RFM (Recency, Frequency, Monetary) metrics.
- **UI Mapping**: Raw cluster IDs (0, 1, 2, 3) are mapped to business terms ("Best Customers", "Repeat Customers", "Standard Customers", "At Risk").
- **Where it appears**: These labels are rendered as color-coded badges (`badge-vip` green, `badge-loyal` blue, etc.) on the Dashboard donut chart, the Customer Directory table, and Individual Customer Profiles.
- **User Flow**: Retailers use these visual badges to instantly identify high-value clients and tailor their communication strategy.

### B. Churn Prediction (Random Forest)
- **What it does**: Calculates the probability (0.0 to 1.0) of a customer not returning.
- **UI Mapping**: The raw probability score is bucketed into "Retention Risk" levels. A score >0.7 becomes "High Risk" (red alert), >0.4 is "Medium Risk" (amber warning), and the rest are "Low Risk".
- **Where it appears**: Displayed prominently on the Dashboard's "Customers You May Lose" widget. In the Customer Profile, it triggers an actionable "Next Steps" card suggesting a retention campaign if the risk is High.
- **User Flow**: Retailers click on high-risk profiles to intervene, using the UI prompts to send targeted discount codes.

### C. Product Recommendations (Apriori)
- **What it does**: Discovers association rules between products (e.g., "Customers who bought X also bought Y").
- **UI Mapping**: The raw rules (antecedents -> consequents) along with Confidence and Lift scores are parsed into "Frequently Bought Together" product cards.
- **Where it appears**: Shown on the `/recommendations` page as a searchable grid. On individual customer profiles, the UI checks the customer's purchase history and suggests matching consequents.
- **User Flow**: Sales staff use the cross-sell section of a customer profile while a customer is viewing an item to suggest highly relevant additions, increasing average order value.

### D. Demand Forecasting (Prophet)
- **What it does**: Analyzes historical transaction volume to predict future revenue.
- **UI Mapping**: The model's output dataframe (containing `ds`, `yhat`, `yhat_lower`, `yhat_upper`) is serialized into JSON. The UI uses Chart.js to render these as a multi-line graph: a solid purple line for expected sales, and dashed/shaded lines for confidence intervals.
- **Where it appears**: Displayed as a 30-day "Expected Sales" interactive chart on the main Dashboard and a detailed view on the `/forecasting` page.
- **User Flow**: Store managers review the Chart.js visual timeline to plan inventory, staffing levels, and financial projections for the upcoming month.

## 5. Theme & Preferences Flow
- **Theme Switcher**: Users click the top-right monitor icon to select Light, Dark, or System theme.
- **Storage**: The preference is saved in `localStorage`.
- **Render**: The JavaScript immediately sets `data-theme="light"` or `dark` on the `<html>` element. CSS variables adapt, and Chart.js instances are forcefully re-rendered to match the new text colors.
