from datetime import timedelta
import pandas as pd
from ollama import Client
import os
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv("OLLAMA_API_KEY")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {api_key}"}
)


def generate_insights(final_df: pd.DataFrame):
    """
    Generate business insights and recommendations from weekly retail sales data
    using LLM (Ollama).
    
    Input:
        final_df (pd.DataFrame): standardized DataFrame with at least columns:
            ["Region", "Week", "Sales", "Holiday", "temperature", 
             "fuel_price", "cpi", "unemployment"]
    
    Returns:
        insights (list[str]): extracted analytical insights
        recommendations (list[str]): actionable recommendations
    """

    df = final_df.copy()
    df["Week"] = pd.to_datetime(df["Week"], format="%Y-%m-%d")

    cutoff_date = df["Week"].max() - pd.DateOffset(years=1)
    recent_data = df[df["Week"] >= cutoff_date]

    latest_week = df["Week"].max()
    previous_week = latest_week - timedelta(days=7)
    quarter_start = latest_week - pd.DateOffset(months=3)

    two_weeks_data = df[df["Week"].between(previous_week - timedelta(days=7), latest_week)]
    quarter_data = df[df["Week"] >= quarter_start]

    summary = recent_data.describe().to_string()
    quarter_summary = (
        quarter_data.groupby("Region")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .to_string()
    )

    prompt = f"""
You are acting as an experienced retail data analyst with access to two years of weekly sales data.
Use the data summaries below to generate analytical insights.

Below is the summary of the most recent year’s sales data:
{summary}

Below is the summary of the most recent quarter's sales data:
{quarter_summary}

Below is the summary of the most two week's sales data: 
{two_weeks_data}

Columns:
- Region: store/region ID
- Week: week of observation
- Sales: weekly total revenue
- Holiday: whether week includes holiday (1=yes, 0=no)
- temperature, fuel_price, cpi, unemployment: macro factors

Your task:
1. Identify 3–5 key business insights from this data. 
   - At most 5 insights
   - Focus on trends, anomalies, or regional differences.
   - Example: “Region 3 showed a 10% increase in sales week-over-week.”
   - Short-term: Compare recent 2 weeks (e.g., “Region B’s revenue decreased by 12% week-over-week”)
   - Medium-term: Highlight best/worst performing regions in the last quarter (e.g., “Region D led the quarter with 15% growth”)
   - Long-term: Note any multi-year trends, seasonality, or correlation with macro factors.
   - **Important note:** Give *least priority* to unemployment rate analysis. 
     Only include unemployment-related insights if there is a *clear and significant* relationship with major sales fluctuations.
     If unemployment remains relatively stable or shows no correlation with sales, ignore it in the insights.

2. Provide 1–2 actionable business recommendations.
   - At most 2 recommendations.
   - Based on insights, suggest next steps (e.g., restocking, marketing push).

Output format (must be plain text): 
**Insights:** 
1. ...
2. ...
3. ...

**Recommendations:** 
1. ...
2. ...
"""

    response = ""
    for part in client.chat("gpt-oss:20b", messages=[{"role": "user", "content": prompt}], stream=True):
        response += part["message"]["content"]
        print(part["message"]["content"], end="", flush=True)

    insight_marker = "**Insights:**"
    recommend_marker = "**Recommendations:**"

    insights = ""
    recommendations = ""


    if insight_marker in response and recommend_marker in response:
        pattern = re.escape(insight_marker) + r"(.*?)" + re.escape(recommend_marker)
        match = re.search(pattern, response, flags=re.DOTALL)
        if match:
            insights = match.group(1).strip()
        
        recommendations = response.split(recommend_marker, 1)[1].strip()

    elif recommend_marker in response: 
        recommendations = response.split(recommend_marker, 1)[1].strip()

    elif insight_marker in response:  
        insights = response.split(insight_marker, 1)[1].strip()

    # insights, recommendations = [], []

    # if "**Insights:**" in response:
    #     insights_part = response.split("**Insights:**")[1].split("**Recommendations:**")[0].strip() \
    #         if "**Recommendations:**" in response else response.split("**Insights:**")[1].strip()
    #     for line in insights_part.splitlines():
    #         clean = line.strip()
    #         if len(clean) > 2 and (clean[0].isdigit() or clean.startswith("-") or clean.startswith("*")):
    #             insights.append(clean.lstrip("0123456789.-) ").strip())

    # if "**Recommendations:**" in response:
    #     rec_part = response.split("**Recommendations:**")[1].strip()
    #     for line in rec_part.splitlines():
    #         clean = line.strip()
    #         if len(clean) > 2 and (clean[0].isdigit() or clean.startswith("-") or clean.startswith("*")):
    #             recommendations.append(clean.lstrip("0123456789.-) ").strip())

    return insights, recommendations
