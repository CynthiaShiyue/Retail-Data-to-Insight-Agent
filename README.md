# Data to Insight Agent  

A **Streamlit-based AI data analysis tool** for retail managers that automatically transforms weekly sales data into **business insights**, **performance metrics**, and **actionable recommendations**.  
It integrates automated data preparation, dynamic KPI tracking, and LLM-powered narrative generation via the Ollama API.  

---

## 🧠 Problem & Objective  

Retail teams often spend hours manually reviewing weekly sales to detect performance trends or irregularities.  
This project delivers an **AI Data Analyst prototype** that automates this process by:    

- Reading structured retail datasets (CSV / Excel)  
- Standardizing inconsistent column names automatically  
- Computing core KPIs and growth metrics  
- Detecting significant sales pattern changes  
- Generating concise insights and recommended business actions using LLM reasoning  

**Example Insight:**  
> Region 4’s revenue increased 13 % in Q3, outperforming Region 20 by USD 4 million.

---
## 💭 Assumptions  

- The uploaded dataset represents **weekly aggregated retail sales** — not customer-level transactions.  
- Each dataset must contain **Region**, **Week (date)**, and **Sales** as core fields for analysis.  
- Optional supporting variables may include **Holiday**, **temperature**, **fuel_price**, **CPI**, **unemployment**, and **promotion_flag**.  
- The target user is a **mid-size retail organization**, where sales performance is tracked at the **regional or store level** rather than by individual customers.  
- Time periods are assumed to be **continuous and comparable week-over-week**, enabling temporal trend detection and KPI computation.  
---
## 💡 Key Features

- **Automated Column Mapping** — Standardizes inconsistent column names using LLM reasoning, minimizing manual data cleaning.  
- **Interactive Filters** — Enables users to focus analysis by selecting **custom date ranges** and **specific regions**.  
- **Multi-Period Growth Analysis** — Computes and compares **Week-over-Week**, **Month-over-Month**, **Quarter-over-Quarter**, and **Year-over-Year** growth.  
- **Anomaly Detection (Z-score > 2)** — Detects and highlights **unusual sales patterns**, helping managers quickly spot unusual performance shifts.  
- **Narrative Insights & Recommendations** — Summarizes trends and provides **clear, data-driven business actions** in natural language.  

---

## ⚙️ System Design  

### Workflow  

1. **Data Ingestion & Preprocessing**  
   - Upload or select a sample dataset.  
   - Columns are standardized through an LLM-based schema matcher (`standardize_columns`).  
   - Data is validated and formatted into a consistent structure (`Region`, `Week`, `Sales`, `Holiday`, etc.).  

2. **KPI Computation & Anomaly Detection**  
   - Enables users to **filter results by custom date ranges and regions** for focused trend analysis.  
   - Performs time-based aggregations (weekly, monthly, quarterly, yearly).  
   - Calculates key KPIs:  
     - **Total Sales**  
     - **Average Weekly Sales**  
     - **Growth Metrics:** Week-over-Week, Month-over-Month, Quarter-over-Quarter, Year-over-Year  
   - **Detects anomalies using Z-score > 2** and highlights **abnormal sales periods**, helping managers quickly spot shifts in demand or operational performance.  

3. **Insight Generation (LLM Layer)**  
   - Summarizes recent and quarterly trends across regions.  
   - Highlights top- and bottom-performing markets.  
   - Provides 1–2 data-driven recommendations aligned with observed trends.  

---

## 📊 Dashboard Overview  

The interactive dashboard consolidates sales insights into an accessible management view:  

| Output | Description |
|---------|-------------|
| **Total Sales & Average Weekly Sales** | Core revenue indicators for the selected period |
| **Growth Metrics** | Week-over-week to year-over-year performance trends |
| **Abnormal Sales Periods (Z > 2)** | Automatically flags unusually high or low sales weeks |
| **Top 3 Regions by Sales** | Lists leading regions by total sales and market share |
| **Regional Trend Plot** | Visualizes weekly sales trajectories by region |

Managers can interactively refine **date ranges** and **regions** to focus on specific operational periods or market segments.

### Sample Output
![Dashboard Overview](sample_output/dashboardsample1.png)
![Regional Analysis](sample_output/dashboardsample1_2.png)

### Sample Input
- Dataset 1: https://www.kaggle.com/datasets/rutuspatel/walmart-dataset-retail  
- Dataset 2: https://www.kaggle.com/datasets/manjeetsingh/retaildataset

---

## 🧩 Architecture Diagram  

```
Upload CSV / Excel
        │
        ▼
Data Standardization (LLM)
        │
        ▼
Insight Generation (LLM)
        │
        ▼
KPI & Anomaly Computation
        │
        ▼
Interactive Dashboard (Streamlit)

```

---


## 🚀 Setup & Run  

### 1. Clone the repository  
```bash
git clone https://github.com/yourusername/Retail-Data-to-Insight-Agent.git
cd Retail-Data-to-Insight-Agent
```
### 2. Install dependencies

Use the provided **Makefile** for fast and consistent setup:

```bash
make install
```

Once finished, you’ll see:
```
Setup complete!
```


### 3. Configure your environment variables

Before running the app, set up your environment file:

```bash
cp .env.example .env
```

Then open `.env` and add your **Ollama API key**:

```bash
OLLAMA_API_KEY=your_api_key_here
```
> Example `.env.example` is included for reference.


### 4. Launch the dashboard

```bash
make run
```

Once started, Streamlit will open automatically in your browser at: [http://localhost:8501](http://localhost:8501)

---

## 📁 Project structure

```bash
Retail-Data-to-Insight-Agent/
├── dashboard.py           # Main Streamlit interface
├── data_preprocessing.py  # LLM-based column standardization
├── dynamic_metrics.py     # KPI & anomaly computation
├── overall_analysis.py    # Insight and recommendation generation
├── sample_input/           # Example datasets
├── sample_output/          # Screenshots of dashboard
├── requirements.txt
├── Makefile
└── .env.example

```
---
# 🔍 Future Enhancements

- Integrate **machine learning–based anomaly detection** (e.g., Isolation Forest) for deeper pattern recognition.
- Add **natural-language query support**, enabling conversational analytics (e.g., “Which region grew fastest last quarter?”).
- Incorporate **predictive sales forecasting** for proactive demand planning and marketing optimization.

---
