# Retail Data to Insight Agent

A **lightweight AI prototype** that reads structured retail datasets (CSV or Excel) and automatically generates **business insights**, **trend analyses**, and **data-driven recommendations**.
It combines automated data preprocessing, key sales KPI tracking, and LLM-powered recommendations through the Ollama API.

---
## 🧠  Problem Statement & Goal

The client currently reviews weekly sales data manually to detect performance trends and anomalies.  
This project builds a **Streamlit-based AI Data Analyst** that automates the process by:

- Reading structured datasets (CSV / Excel)
- Standardizing columns and validating schema
- Detecting key sales trends and anomalies
- Generating concise business insights and recommended actions using LLMs (via **Ollama API**)

**Example Insight:**  
> “Region 4’s weekly revenue rose by 13% in the last quarter, outperforming Region 20 by 4M USD.”

---

## ⚙️ System Workflow & Design

###  Overview
The system follows a **three-stage modular workflow**:

1. **Data Ingestion & Preprocessing**  
   - User uploads or selects a sample dataset.  
   - Columns are standardized using a schema-matching LLM (`standardize_columns()`).
   - Data is validated and parsed into a uniform format (`Region`, `Week`, `Sales`, `Holiday`, etc.).

2. **Dynamic KPI Computation**  
   - Time-based aggregations (weekly, monthly, quarterly).  
   - KPIs: Total Sales, Average Weekly Sales, Volatility Index, Momentum.  
   - Detects anomalies via z-score > 2 and highlights outlier periods.

3. **Insight Generation (AI Layer)**  
   - Summarizes regional performance trends.  
   - Identifies sales growth/decline and recommends next actions.  
   - Uses LLM (Ollama) for natural-language insight generation.

---

## 🧰 Technical Workflow Diagram

```
+-----------------------------+
|  Upload CSV / Excel File    |
+-------------+---------------+
              |
              v
+-----------------------------+
|  Data Standardization       |
|  (LLM-based column mapping) |
+-------------+---------------+
              |
              v
+-----------------------------+
|  Dynamic KPI Computation    |
|  (Sales, Growth, Volatility)|
+-------------+---------------+
              |
              v
+-----------------------------+
|  Insight Generation (LLM)   |
|  - Trend summaries          |
|  - Anomaly detection        |
|  - Recommendations          |
+-----------------------------+
              |
              v
+-----------------------------+
|  Interactive Streamlit App  |
|  Visualization + KPI Cards  |
+-----------------------------+
```

---
### 📊 Dashboard Key Outputs

The dashboard automatically computes and visualizes key retail performance metrics, with **interactive controls** to select **custom date ranges** and **specific regions**.

#### Core Metrics
-  **Total Sales** — total revenue within the selected time frame  
-  **Average Weekly Sales** — mean weekly revenue over the selected range  
-  **Growth Metrics:**  
  - **Week-over-Week Growth** — short-term performance change  
  - **Month-over-Month Growth** — medium-term sales trend  
  - **Quarter-over-Quarter Growth** — quarterly comparison for performance evaluation  
  - **Year-over-Year Growth** — long-term trend accounting for seasonality  
- **Anomaly Weeks (Z-score > 2)** — automatically highlights unusual spikes or drops in weekly sales  
- **Top 3 Regions by Total Sales** — ranks highest-performing regions by total revenue share  

---
## 🚀 How to Run the Project

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/Retail-Data-to-Insight-Agent.git
cd Retail-Data-to-Insight-Agent
```

---

### 2. Set up your environment (Makefile)

Use the provided **Makefile** for fast and consistent setup:

```bash
make install
```

Once finished, you’ll see:
```
Setup complete!
```

---

### 3. Configure your environment variables

Before running the app, set up your environment file:

```bash
cp .env.example .env
```

Then open `.env` and add your **Ollama API key**:

```bash
OLLAMA_API_KEY=your_api_key_here
```

> ⚠️ `.env` is ignored by Git to protect your credentials.  
> Example `.env.example` is included for reference.

---

### 6. One-step setup & run

You can install dependencies **and** start the dashboard in a single command:

```bash
make all
```

Or run them separately:

```bash
make install
make run
```

Once started, Streamlit will open automatically in your browser at:  
 [http://localhost:8501](http://localhost:8501)

---

## 🧩 Project structure

```bash
Retail-Data-to-Insight-Agent/
├── .venv/                 # Virtual environment (ignored by git)
├── .env.example           # Template for environment variables
├── .gitignore
├── Makefile               # Automates setup & run
├── requirements.txt       # Dependencies
├── dashboard.py           # Main Streamlit dashboard
├── data_preprocessing.py  # Data cleaning & standardization
├── dynamic_metrics.py     # KPI and time-series analysis
├── overall_analysis.py    # Analytical insights generation
├── test                   # Testing sample
└── data_sample/           # Local demo datasets
```

---
