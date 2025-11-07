from dotenv import load_dotenv
import os
from ollama import Client

load_dotenv()

api_key = os.getenv("OLLAMA_API_KEY")

client = Client(
    host="https://ollama.com", headers={"Authorization": f"Bearer {api_key}"}
)

messages = [
    {
        "role": "user",
        "content": "Why is the sky blue?",
    },
]

for part in client.chat("gpt-oss:20b", messages=messages, stream=True):
    print(part["message"]["content"], end="", flush=True)
















import streamlit as st
import pandas as pd
import os
from data_preprocessing import standardize_columns 
from overall_analysis import generate_insights 
import matplotlib.pyplot as plt
from query import smart_dataframe_qa 

@st.cache_data
def load_csv(path_or_file):
    return pd.read_csv(path_or_file)

@st.cache_data
def preprocess_data(df):
    return standardize_columns(df)

@st.cache_data
def analyze_data(standardized_df):
    return generate_insights(standardized_df)


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


    st.subheader("Standardized Data Preview")
    st.dataframe(standardized_df.head())



    st.subheader("Data Overall Analysis")

    with st.spinner("Analyzing sales data ......"):
        try:
            insights, recommendations = generate_insights(standardized_df)

            # --- Insights ---
            with st.expander("Insights", expanded=True):
                st.markdown(insights)
                # clean_insights = [i for i in insights if i and i.strip()]
                # if clean_insights:
                #     for idx, i in enumerate(clean_insights, start=1):
                #         st.markdown(f"**{idx}.** {i.strip()}")
                # else:
                #     st.info("No insights returned.")

            # --- Recommendations ---
            with st.expander("Recommendations", expanded=True):
                st.markdown(recommendations)
                # clean_recs = [r for r in recommendations if r and r.strip()]
                # if clean_recs:
                #     for idx, r in enumerate(clean_recs, start=1):
                #         st.markdown(f"**{idx}.** {r.strip()}")
                # else:
                #     st.info("No recommendations returned.")

        except Exception as e:
            st.error(f"Error during analysis: {e}")
            


    # st.subheader("💬 Ask a Question About Your Data")
    # # st.info("Try questions like: *'Which region had the highest sales last month?'*")

    # user_query = st.text_input("Ask about your dataset here:")

    # st.markdown(
    #     "<p style='color:gray; font-style:italic; font-size:14px; margin-top:-5px;'>"
    #     "Try questions like: <b>'Which region had the highest sales last month?'</b>"
    #     "</p>",
    #     unsafe_allow_html=True
    # )

    # if user_query:
    #     with st.spinner("Thinking..."):
    #         answer = smart_dataframe_qa(standardized_df, user_query)
    #     st.markdown("### 💡 Answer:")
    #     st.markdown(answer)





# version1

    # 假设 standardized_df 已经存在
    st.subheader("📊 Custom Data Query")

    # 1️⃣ 选择 Region
    regions = standardized_df["Region"].dropna().unique().tolist()
    selected_region = st.selectbox("Select a Region:", regions)

    # 2️⃣ 日期选择范围（自动从 df 取 min/max）
    date_min = pd.to_datetime(standardized_df["Week"]).min()
    date_max = pd.to_datetime(standardized_df["Week"]).max()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date:", value=date_min, min_value=date_min, max_value=date_max)
    with col2:
        end_date = st.date_input("End Date:", value=date_max, min_value=date_min, max_value=date_max)

    # 3️⃣ 执行函数按钮
    if st.button("Run Analysis", type="primary"):
        with st.spinner("Generating time trend chart..."):
            try:
                # 筛选指定区域和日期范围
                df_region = standardized_df.copy()
                df_region["Week"] = pd.to_datetime(df_region["Week"], errors="coerce")
                
                filtered_df = df_region[
                    (df_region["Region"] == selected_region)
                    & (df_region["Week"] >= pd.to_datetime(start_date))
                    & (df_region["Week"] <= pd.to_datetime(end_date))
                ].sort_values("Week")

                # 检查是否有数据
                if filtered_df.empty:
                    st.warning(f"No sales data found for {selected_region} between {start_date} and {end_date}.")
                else:
                    # 计算 Weekly Sales 趋势
                    sales_trend = filtered_df.groupby("Week")["Sales"].sum().reset_index()

                    # --- 绘图 ---
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.plot(sales_trend["Week"], sales_trend["Sales"], marker="o", linewidth=2)
                    ax.set_title(f"Weekly Sales Trend for {selected_region}", fontsize=14)
                    ax.set_xlabel("Week")
                    ax.set_ylabel("Sales")
                    ax.grid(alpha=0.3)

                    st.pyplot(fig)

                    # 附加统计结果
                    total_sales = sales_trend["Sales"].sum()
                    avg_sales = sales_trend["Sales"].mean()
                    st.markdown(f"**📅 Period:** {start_date} → {end_date}")
                    st.markdown(f"**💰 Total Sales:** ${total_sales:,.2f}")
                    st.markdown(f"**📈 Average Weekly Sales:** ${avg_sales:,.2f}")

            except Exception as e:
                st.error(f"Error during analysis: {e}")





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








# version 2
import streamlit as st
import pandas as pd
import os
from data_preprocessing import standardize_columns 
from overall_analysis import generate_insights 
import matplotlib.pyplot as plt
from query import smart_dataframe_qa 
from dynamic_metrics import generate_time_series

# ==============================
@st.cache_data
def load_csv(path_or_file):
    return pd.read_csv(path_or_file)

@st.cache_data
def preprocess_data(df):
    return standardize_columns(df)

@st.cache_data
def analyze_data(standardized_df):
    return generate_insights(standardized_df)

@st.cache_data
def time_series_analysis(filtered_df):
    return generate_time_series(filtered_df)

# ==============================

st.set_page_config(
    page_title="Retail Data to Insight Agent",
    layout="wide",       
    initial_sidebar_state="expanded"  
)

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


# ==============================
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


# ==============================
if df is not None:
    with st.spinner("Standardizing column names ......"):
        try:
            standardized_df = preprocess_data(df)
        except Exception as e:
            standardized_df = df  

    st.subheader("Standardized Data Preview")
    st.dataframe(standardized_df.head())

    # --- Overall Analysis ---
    st.subheader("Data Overall Analysis")

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
    st.subheader("📈 Custom Data Query")

    regions = standardized_df["Region"].dropna().unique().tolist()
    selected_regions = st.multiselect("Select Region(s):", regions, default=regions[:1])


    date_min = pd.to_datetime(standardized_df["Week"]).min()
    date_max = pd.to_datetime(standardized_df["Week"]).max()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date:", value=date_min, min_value=date_min, max_value=date_max)
    with col2:
        end_date = st.date_input("End Date:", value=date_max, min_value=date_min, max_value=date_max)

    if st.button("Run Analysis", type="primary"):
        with st.spinner("Generating time trend chart..."):
            df_region = standardized_df.copy()
            df_region["Week"] = pd.to_datetime(df_region["Week"], errors="coerce")

            filtered_df = df_region[
                (df_region["Region"].isin(selected_regions))
                & (df_region["Week"] >= pd.to_datetime(start_date))
                & (df_region["Week"] <= pd.to_datetime(end_date))
            ].sort_values("Week")

            if filtered_df.empty:
                st.warning(f"No sales data found for selected regions between {start_date} and {end_date}.")
            else:
                fig, summary = time_series_analysis(filtered_df)

                if fig is None:
                    st.warning("No valid data to plot.")
                else:
                    st.pyplot(fig)
                    st.markdown(f"**📅 Period:** {start_date} → {end_date}")
                    st.markdown(f"**💰 Total Sales:** ${summary['total_sales']:,.2f}")
                    st.markdown(f"**📊 Average Weekly Sales:** ${summary['avg_sales']:,.2f}")
