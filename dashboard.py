import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from data_preprocessing import standardize_columns 
from overall_analysis import generate_insights 
from dynamic_metrics import generate_time_series_region, compute_retail_metrics

# ==============================
st.set_page_config(page_title="Data to Insight Agent", layout="wide")

# ==============================
@st.cache_data
def load_csv(path_or_file):
    """
    Load data from a CSV or Excel file and return a pandas DataFrame.
    If Excel file is uploaded, convert it to CSV-equivalent DataFrame.
    """
    file_name = (
        path_or_file.name
        if hasattr(path_or_file, "name")
        else str(path_or_file)
    )

    # Check file extension
    ext = os.path.splitext(file_name)[-1].lower()

    if ext in [".xls", ".xlsx"]:
        st.info("Excel file detected.")
        df = pd.read_excel(path_or_file)
    elif ext == ".csv":
        df = pd.read_csv(path_or_file)
    else:
        st.error("Unsupported file type. Please upload a .csv or .xlsx file.")
        return None

    return df


@st.cache_data
def preprocess_data(df):
    return standardize_columns(df)

@st.cache_data
def analyze_data(standardized_df):
    return generate_insights(standardized_df)

@st.cache_data
def time_series_analysis_all(filtered_df, start_date, end_date):
    return compute_retail_metrics(filtered_df, start_date, end_date)

# @st.cache_data
def time_series_analysis(filtered_region_df):
    return generate_time_series_region(filtered_region_df)


# ==============================
st.title("Retail Data to Insight Agent")

left_col, right_col = st.columns([3, 2], gap="large")

# ==============================
#Left
with left_col:
    st.subheader("📂 Upload or Load Sample Data")

    col1, col2 = st.columns([2.2, 1])
    with col1:
        uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx", "xls"])
    with col2:
        st.caption("Or load sample data:")
        c1, c2 = st.columns(2)
        with c1:
            sample1 = st.button("📂 Retail 1", use_container_width=True)
        with c2:
            sample2 = st.button("📂 Retail 2", use_container_width=True)


    sample_dir = "data_sample"
    sample_paths = {
        "walmart": os.path.join(sample_dir, "(sample1)Walmart.csv"),
        "retail": os.path.join(sample_dir, "(sample2)retaildata.csv")
    }

    if "df" not in st.session_state:
        st.session_state.df = None

    if uploaded_file is not None:
        st.session_state.df = load_csv(uploaded_file)
        st.success("File uploaded successfully!")
    elif sample1:
        st.session_state.df = load_csv(sample_paths["walmart"])
        st.success("Loaded sample dataset: Walmart.csv")
    elif sample2:
        st.session_state.df = load_csv(sample_paths["retail"])
        st.success("Loaded sample dataset: RetailData.csv")



    df = st.session_state.df

    if df is not None:
        with st.spinner("Standardizing column names ......"):
            try:
                standardized_df = preprocess_data(df)
            except Exception as e:
                standardized_df = df  

        st.subheader("📊 Standardized Data Preview")
        st.dataframe(standardized_df.head(3), use_container_width=True, hide_index=True)


        st.subheader("🔍 Data Overall Analysis")
        with st.spinner("Analyzing sales data ......"):
            try:
                insights, recommendations = analyze_data(standardized_df)
                with st.expander("Insights", expanded=True):
                    st.markdown(insights)
                with st.expander("Recommendations", expanded=True):
                    st.markdown(recommendations)
            except Exception as e:
                st.error(f"Error during analysis: {e}")

# ==============================
# Right
with right_col:
    if "df" in st.session_state and st.session_state.df is not None:
        st.subheader("📈 Custom Data Query")

        # ----------- Step 1:  -----------
        st.markdown("### Step 1: Select Date Range")

        weeks = pd.to_datetime(standardized_df["Week"], errors="coerce").dropna()
        if weeks.empty:
            st.warning("No valid dates found in 'Week' column.")
            st.stop()

        date_min, date_max = weeks.min(), weeks.max()

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date:", value=date_min, min_value=date_min, max_value=date_max)
        with col2:
            end_date = st.date_input("End Date:", value=date_max, min_value=date_min, max_value=date_max)

        run_overall = st.button("Run Overall Analysis")

        if run_overall:
            with st.spinner("Computing overall retail metrics..."):
                df_all = standardized_df.copy()
                df_all["Week"] = pd.to_datetime(df_all["Week"], errors="coerce")

                filtered_df = df_all[
                    (df_all["Week"] >= pd.to_datetime(start_date))
                    & (df_all["Week"] <= pd.to_datetime(end_date))
                ].sort_values("Week")

                if filtered_df.empty:
                    st.warning(f"No data found between {start_date} and {end_date}.")
                else:

                    st.session_state.summary_all = compute_retail_metrics(filtered_df)

        if "summary_all" in st.session_state:
            summary_all, top3_df = st.session_state.summary_all


            # === Growth Data ===
            col1, col2 = st.columns(2)
            
            with col1:
                if pd.notna(summary_all['WoW Growth %']):
                    st.metric("Week-over-Week Growth", f"{summary_all['WoW Growth %']:,.2%}")
            with col2:
                if pd.notna(summary_all['MoM Growth %']):
                    st.metric("Month-over-Month Growth", f"{summary_all['MoM Growth %']:,.2%}")

            col3, col4 = st.columns(2)
            with col3:
                if pd.notna(summary_all['QoQ Growth %']):
                    st.metric("Quarter-over-Quarter Growth", f"{summary_all['QoQ Growth %']:,.2%}")
            with col4:
                if pd.notna(summary_all['YoY Growth %']):
                    st.metric("Year-over-Year Growth", f"{summary_all['YoY Growth %']:,.2%}")

            st.divider()

            # === Anomaly Weeks ===
            if summary_all.get("Anomaly Weeks"):
                st.subheader("⚠️ Anomaly Weeks (Z-score > 2)")
                st.markdown(
                    ", ".join(summary_all["Anomaly Weeks"])
                    if len(summary_all["Anomaly Weeks"]) > 0
                    else "No significant anomalies detected."
                )
            else:
                st.subheader("⚠️ Anomaly Weeks")
                st.markdown("No significant anomalies detected.")


            # === Top 3 Regions ===
            if not top3_df.empty:
                st.subheader("🏆 Top 3 Regions by Total Sales")
                st.dataframe(top3_df, use_container_width=True, hide_index=True)
            else:
                st.subheader("🏆 Top 3 Regions by Total Sales")
                st.info("No region-level data available.")

        st.divider()

        # ----------- Step 2: -----------
        st.markdown("### Step 2: Region-Level Analysis")

        regions = standardized_df["Region"].dropna().unique().tolist()
        selected_regions = st.multiselect("Select Region(s):", regions, default=regions[:1])

        run_region = st.button("Run Regional Analysis")

        if run_region:
            with st.spinner("Generating region-level time series..."):
                df_region = standardized_df.copy()
                df_region["Week"] = pd.to_datetime(df_region["Week"], errors="coerce")

                filtered_region_df = df_region[
                    (df_region["Region"].isin(selected_regions))
                    & (df_region["Week"] >= pd.to_datetime(start_date))
                    & (df_region["Week"] <= pd.to_datetime(end_date))
                ].sort_values("Week")

                if filtered_region_df.empty:
                    st.warning(f"No sales data found for selected regions between {start_date} and {end_date}.")
                else:
                    fig_region, summary_region = time_series_analysis(filtered_region_df)
                    if fig_region is None:
                        st.warning("No valid data to plot.")
                    else:
                        st.pyplot(fig_region, use_container_width=True)
                        st.markdown(f"**📅 Period:** {start_date} → {end_date}")
                        st.markdown(f"**💰 Total Sales:** ${summary_region['total_sales']:,.2f}")
                        st.markdown(f"**📊 Avg Weekly Sales:** ${summary_region['avg_sales']:,.2f}")
