import streamlit as st
import pandas as pd
import os
from data_preprocessing import standardize_columns 
from overall_analysis import generate_insights 
import matplotlib.pyplot as plt
from query import ask_about_dataframe 

st.title("Retail Data to Insight Agent")

col1, col2 = st.columns([2.2, 1])

with col1:
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

with col2:
    st.caption("Or load sample data:")
    c1, c2 = st.columns(2)
    with c1:
        sample1 = st.button("📂 Walmart", use_container_width=True)
    with c2:
        sample2 = st.button("📂 Retail's", use_container_width=True)




sample_dir = "data_sample"
sample_paths = {
    "walmart": os.path.join(sample_dir, "(sample1)Walmart.csv"),
    "retail": os.path.join(sample_dir, "(sample2)retaildata.csv")
}

if "df" not in st.session_state:
    st.session_state.df = None

if uploaded_file is not None:
    st.session_state.df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
elif sample1:
    st.session_state.df = pd.read_csv(sample_paths["walmart"])
    st.success("Loaded sample dataset: Walmart.csv")
elif sample2:
    st.session_state.df = pd.read_csv(sample_paths["retail"])
    st.success("Loaded sample dataset: RetailData.csv")

df = st.session_state.df

if df is not None:
    with st.spinner("Standardizing column names ......"):
        try:
            standardized_df = standardize_columns(df)
        except Exception as e:
            standardized_df = df  

    st.subheader("Data Overall Analysis")

    with st.spinner("Analyzing sales data ......"):
        try:
            insights, recommendations = generate_insights(standardized_df)

            # --- Insights ---
            with st.expander("Insights", expanded=True):
                clean_insights = [i for i in insights if i and i.strip()]
                if clean_insights:
                    for idx, i in enumerate(clean_insights, start=1):
                        st.markdown(f"**{idx}.** {i.strip()}")
                else:
                    st.info("No insights returned.")

            # --- Recommendations ---
            with st.expander("Recommendations", expanded=True):
                clean_recs = [r for r in recommendations if r and r.strip()]
                if clean_recs:
                    for idx, r in enumerate(clean_recs, start=1):
                        st.markdown(f"**{idx}.** {r.strip()}")
                else:
                    st.info("No recommendations returned.")

        except Exception as e:
            st.error(f"Error during analysis: {e}")
            


    st.subheader("💬 Ask a Question About Your Data")
    st.info("Try questions like: *'Which region had the highest sales last month?'*")

    user_query = st.text_input("Ask about your dataset here:")

    if user_query:
        with st.spinner("Thinking..."):
            answer = ask_about_dataframe(standardized_df, user_query)
        st.markdown("### 🧠 Answer:")
        st.markdown(answer)


    # st.subheader("Retail Sale Details")

    # st.subheader("Standardized Data Preview")
    # st.dataframe(standardized_df.head())

    # st.subheader("Sales Trend Overview")
    # trend_df = standardized_df.copy()
    # trend_df["Week"] = pd.to_datetime(trend_df["Week"], errors="coerce")

    # if "Sales" in trend_df.columns:
    #     sales_trend = trend_df.groupby("Week")["Sales"].sum().reset_index()

    #     fig, ax = plt.subplots(figsize=(8, 4))
    #     ax.plot(sales_trend["Week"], sales_trend["Sales"], marker="o", linewidth=1.5)
    #     ax.set_title("Weekly Total Sales Trend", fontsize=13)
    #     ax.set_xlabel("Week")
    #     ax.set_ylabel("Total Sales")
    #     ax.grid(alpha=0.3)

    #     st.pyplot(fig)

    #     st.markdown("#### Recent Weeks Data")
    #     st.dataframe(sales_trend.tail(8).reset_index(drop=True))
    # else:
    #     st.warning(" No 'Sales' column found — cannot plot trend.")
