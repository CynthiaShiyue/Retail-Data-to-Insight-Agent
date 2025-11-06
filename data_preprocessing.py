from dotenv import load_dotenv
import os
from ollama import Client
import json
import pandas as pd

load_dotenv()  

api_key = os.getenv("OLLAMA_API_KEY")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {api_key}"}
)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Use LLM (via Ollama) to automatically map dataset columns
    to standardized target field names for easier downstream analysis.
    """

    target_fields = [
        "Region", "Week", "Sales", "Holiday",
        "temperature", "fuel_price", "cpi", "unemployment",
        "Promotion_Flag", "Category"
    ]

    prompt = f"""
    You are a data preprocessing assistant.

    Your task:
    Given the dataset columns: {list(df.columns)},
    map each target field from this list: {target_fields}
    to the most appropriate column name from the dataset.

    Mapping rules:
    1. Match based on semantic meaning (e.g., "weekly_sales" → "Sales", "holiday_flag" → "Holiday").
    2. If no column matches, set its value to null.
    3. Special case for region mapping:
       - If there is no "region" column, map "store" (or similar) to "Region".
       - If both "region" and "store" exist, keep both by mapping:
           "Region": "region"
           "Store": "store"
         (add "Store" as an extra field in output if needed).
    4. Return ONLY a valid JSON dictionary, no explanation or commentary.

    Example output:
    {{
      "Region": "region",
      "Store": "store",
      "Week": "date", in "%Y-%m-%d" format
      "Sales": "weekly_sales",
      "Holiday": "holiday_flag",
      "temperature": "temperature",
      "fuel_price": "fuel_price",
      "cpi": "cpi",
      "unemployment": "unemployment",
      "Promotion_Flag": null,
      "Category": "product_type"
    }}
    """

    messages = [{"role": "user", "content": prompt}]
    response_text = ""

    for part in client.chat("gpt-oss:20b", messages=messages, stream=True):
        response_text += part["message"]["content"]

    try:
        mapping = json.loads(response_text)
    except json.JSONDecodeError:
        print("Warning: model did not return valid JSON.")
        mapping = {}

    valid_map = {k: v for k, v in mapping.items() if v and v in df.columns}

    df = df.rename(columns={v: k for k, v in valid_map.items()})

    if "Week" in df.columns:
        df["Week"] = pd.to_datetime(df["Week"], dayfirst=True, errors="coerce")
        df["Week"] = df["Week"].dt.strftime("%Y-%m-%d")


    if "Holiday" in df.columns:
        df["Holiday"] = df["Holiday"].replace(
            {True: 1, False: 0, "true": 1, "false": 0}
        )
        df["Holiday"] = df["Holiday"].astype(int)

    final_cols = [col for col in target_fields if col in df.columns]
    final_df = df[final_cols]

    print("\nFinal standardized columns:", final_df.columns.to_list())
    return final_df
