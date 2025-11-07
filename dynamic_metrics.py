from matplotlib.ticker import FuncFormatter
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def thousands_formatter(x, pos):
    return f"{x / 1000:.0f}"

def generate_time_series_region(filtered_region_df: pd.DataFrame):
    df=filtered_region_df.copy()
    if df.empty:
        return None, {"total_sales": 0, "avg_sales": 0, "records": 0}

    sales_trend = (
        df.groupby(["Week", "Region"])["Sales"]
        .sum()
        .reset_index()
        .sort_values("Week")
    )

    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(8, 4))

    colors = plt.cm.tab10.colors
    region_list = sales_trend["Region"].unique().tolist()

    for i, region in enumerate(region_list):
        group = sales_trend[sales_trend["Region"] == region]
        ax.plot(
            group["Week"],
            group["Sales"],
            linewidth=2.0,
            color=colors[i % len(colors)],
            alpha=0.8,
            label=str(region),
        )

    ax.set_title("Weekly Sales Trend by Region", fontsize=14, pad=10)
    ax.set_xlabel("Week", fontsize=11)
    ax.text(
        -0.08,
        0.96,
        "Sales (k)\n",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=11,
        fontweight="semibold",
    )


    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.grid(False)
    ax.legend(title="Region", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    plt.tight_layout()

    total_sales = sales_trend["Sales"].sum()
    avg_sales = sales_trend["Sales"].mean()

    summary = {
        "total_sales": total_sales,
        "avg_sales": avg_sales,
        "records": len(sales_trend),
    }

    return fig, summary


def compute_retail_metrics(filtered_df: pd.DataFrame):
    df = filtered_df.copy()
    df["Week"] = pd.to_datetime(df["Week"], errors="coerce")
    df = df.dropna(subset=["Week", "Sales"]).sort_values("Week")

    if df.empty:
        return (
            {
                "Weeks Covered": 0,
                "Total Sales": 0,
                "Avg Weekly Sales": 0,
                "WoW Growth %": np.nan,
                "MoM Growth %": np.nan,
                "QoQ Growth %": np.nan,
                "YoY Growth %": np.nan,
                "Anomaly Weeks": [],
            },
            pd.DataFrame(columns=["Region", "Total Sales", "Market Share %"]),
        )

    start_date, end_date = df["Week"].min(), df["Week"].max()
    period_days = (end_date - start_date).days
    period_weeks = period_days // 7
    total_sales = df["Sales"].sum()
    avg_sales = df["Sales"].mean()

    # === Week-over-Week Growth ===
    if len(df) >= 2:
        wow_growth = (df["Sales"].iloc[-1] - df["Sales"].iloc[-2]) / df["Sales"].iloc[-2]
    else:
        wow_growth = np.nan

    # === Month-over-Month Growth ===
    if period_weeks >= 8:
        df_monthly = df.set_index("Week").resample("M")["Sales"].sum().reset_index()
        mom_growth = (
            (df_monthly["Sales"].iloc[-1] - df_monthly["Sales"].iloc[-2])
            / df_monthly["Sales"].iloc[-2]
            if len(df_monthly) >= 2
            else np.nan
        )
    else:
        mom_growth = np.nan

    # === Quarter-over-Quarter Growth ===
    if period_weeks >= 24:
        df_quarterly = df.set_index("Week").resample("Q")["Sales"].sum().reset_index()
        qoq_growth = (
            (df_quarterly["Sales"].iloc[-1] - df_quarterly["Sales"].iloc[-2])
            / df_quarterly["Sales"].iloc[-2]
            if len(df_quarterly) >= 2
            else np.nan
        )
    else:
        qoq_growth = np.nan

    # === Year-over-Year Growth ===
    if period_weeks >= 52:
        df_yearly = df.set_index("Week").resample("Y")["Sales"].sum().reset_index()
        yoy_growth = (
            (df_yearly["Sales"].iloc[-1] - df_yearly["Sales"].iloc[-2])
            / df_yearly["Sales"].iloc[-2]
            if len(df_yearly) >= 2
            else np.nan
        )
    else:
        yoy_growth = np.nan

    # === simple anomaly detection：Z-score > 2 ===
    agg_sales = df.groupby("Week", as_index=False)["Sales"].sum().sort_values("Week")
    mean_sales = agg_sales["Sales"].mean()
    std_sales = agg_sales["Sales"].std(ddof=0)
    if std_sales > 0:
        agg_sales["z_score"] = (agg_sales["Sales"] - mean_sales) / std_sales
    else:
        agg_sales["z_score"] = 0
    anomaly_weeks = agg_sales.loc[agg_sales["z_score"] > 2, "Week"].dt.strftime("%Y-%m-%d").tolist()
    anomaly_weeks = sorted(list(set(anomaly_weeks)))

    
    summary = {
        "Weeks Covered": period_weeks,
        "Total Sales": total_sales,
        "Avg Weekly Sales": avg_sales,
        "WoW Growth %": wow_growth,
        "MoM Growth %": mom_growth,
        "QoQ Growth %": qoq_growth,
        "YoY Growth %": yoy_growth,
        "Anomaly Weeks": anomaly_weeks,
    }

    # ===  Top 3 Regions by Sales ===
    if "Region" in df.columns:
        region_sales = (
            df.groupby("Region", as_index=False)["Sales"]
            .sum()
            .rename(columns={"Sales": "Total Sales"})
        )
        region_sales["Market Share %"] = (
            region_sales["Total Sales"] / region_sales["Total Sales"].sum() * 100
        )
        top3_df = region_sales.sort_values("Total Sales", ascending=False).head(3)
        top3_df["Total Sales"] = top3_df["Total Sales"].round(2)
        top3_df["Market Share %"] = top3_df["Market Share %"].round(2)
    else:
        top3_df = pd.DataFrame(columns=["Region", "Total Sales", "Market Share %"])

    return summary, top3_df
