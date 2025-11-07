import io
import sys
import os
import pandas as pd
from dotenv import load_dotenv
from ollama import Client

# === Step 0: 初始化 ===
load_dotenv()
api_key = os.getenv("OLLAMA_API_KEY")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {api_key}"}
)

def smart_dataframe_qa(final_df: pd.DataFrame, question: str):
    df=final_df.copy()
    preview = df.head(5).to_string(index=False)

    prompt_code = f"""
You are a careful Python data analyst using pandas.
Here is a sample of the dataset (first 5 rows):

{preview}

The original DataFrame is called df, but please do not modify it.
Instead, always start with:
templatedf = df.copy()

Use templatedf for all analysis steps.

Question: "{question}"

Write Python code using pandas to answer the question.

Rules:
- Always create a copy: templatedf = df.copy()
- Always build an aggregated DataFrame named `summary_table` for the target metric
  (e.g., total Sales per Region for the last month) and print(summary_table)
- Set the top region id/name to a variable named `result_region`
- Set that region’s aggregated total to a variable named `result_value` (numeric)
- Always print(result_region) and print(result_value)
- If summary_table is empty, set result_region, result_value = None, None
- Do NOT assume or modify data types unless absolutely necessary
- Output only Python code, no explanations, no markdown
"""

    response = client.chat(
        "gpt-oss:120b",
        messages=[{"role": "user", "content": prompt_code}],
        stream=False
    )
    code = response["message"]["content"]

    clean_code = (
        code.replace("```python", "")
            .replace("```", "")
            .strip()
    )


    buf = io.StringIO()
    sys_stdout_backup = sys.stdout
    sys.stdout = buf

    exec_env = {
        "pd": pd,   
        "df": df   
    }

    try:
        exec(clean_code, exec_env)

        summary_table = exec_env.get("summary_table", None)
        result_region = exec_env.get("result_region")
        result_value  = exec_env.get("result_value")

        if (summary_table is None) or (hasattr(summary_table, "empty") and summary_table.empty):
            print("summary_table is empty — performing fallback aggregation...\n")

            fallback_df = df.copy()
            fallback_df["Week"] = pd.to_datetime(fallback_df["Week"], errors="coerce")
            fallback_df["YearMonth"] = fallback_df["Week"].dt.to_period("M")

            valid_months = (
                fallback_df.groupby("YearMonth")["Sales"].sum()
                .reset_index()
                .sort_values("YearMonth", ascending=False)
            )
            if not valid_months.empty:
                fallback_month = valid_months.iloc[0]["YearMonth"]
                df_fallback = fallback_df[fallback_df["YearMonth"] == fallback_month]
                summary_table = (
                    df_fallback.groupby("Region", as_index=False)["Sales"].sum()
                    .sort_values("Sales", ascending=False)
                )
                result_region = summary_table.iloc[0]["Region"]
                result_value = summary_table.iloc[0]["Sales"]
            else:
                result_region, result_value = None, None

    except Exception as e:
        sys.stdout = sys_stdout_backup
        print(f"Error executing code: {e}")
        return f"Execution Error: {e}"
    finally:
        sys.stdout = sys_stdout_backup


    internal_output = buf.getvalue().strip()

    # print("\nCode executed successfully.")
    # print("Internal print output:\n", internal_output)
    # print("result_region:", result_region)
    # print("result_value:", result_value)

    prompt_summary = f"""
You are a professional data analyst.

Question: {question}
Top region id/name: {result_region}
Top region total (numeric): {result_value}

Write the final answer as one clear, plain-English sentence.
Include the numeric value (rounded nicely, with unit if applicable), and do not mention any code.
Example style:
"Region 4 had the highest sales last month, with total sales of approximately $8.59 million."
"""

    summary_response = client.chat(
        "gpt-oss:20b",
        messages=[{"role": "user", "content": prompt_summary}],
        stream=False
    )
    final_answer = summary_response["message"]["content"].strip()

    return final_answer




