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


def standardize_columns(input: pd.DataFrame, retry=False, verbose=False) -> pd.DataFrame:
    """
    Use LLM (via Ollama) to automatically map dataset columns
    to standardized target field names for easier downstream analysis.
    Includes auto-retry safeguard if Region, Week, or Sales are missing.
    Optional verbose mode for debugging.
    """
    df = input.copy()

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
    1. Match columns based on **semantic meaning or common synonyms**, not exact names.
        - For "Region": match region, area, zone, territory, state, store, location, branch.
        - For "Week": match date, week, time, period, or any column indicating weekly timestamps.
        - For "Sales": match weekly_sales, total_sales, revenue, amount, sales_value.
        - For "Holiday": match holiday_flag, is_holiday, festival, holiday indicator.
        - For "temperature": match temp, temperature, weather_temp.
        - For "fuel_price": match fuel, gas_price, petrol_price.
        - For "cpi": match consumer_price_index, inflation, CPI.
        - For "unemployment": match unemployment_rate, jobless_rate, unemp.
        - For "Promotion_Flag": match promo, promotion_flag, discount_flag.
        - For "Category": match product_type, department, category_name.

    2. If no column matches, set its value to null.
    3. Special case for region mapping:
        - If there is no "region" column, map "store" (or similar) to "Region".
        - If both "region" and "store" exist, keep both by mapping:
            "Region": "region"
            "Store": "store"

    4. Return ONLY a valid JSON dictionary, no explanation or commentary.
    5. When detecting the column corresponding to "Week" or "Date":
        - If the date format looks like "05-02-2010" or "5-2-2010", assume it is in day-first format (%d-%m-%Y).
        - The output should ensure that this column can be converted to the standardized format "%Y-%m-%d" (YYYY-MM-DD).
        - The JSON key must still be "Week" (not "Date") in the final mapping.
    """

    messages = [{"role": "user", "content": prompt}]
    response_text = ""

    if verbose:
        print("Sending prompt to Ollama...")
        print("Prompt preview:\n", prompt[:500], "...\n")

    for part in client.chat("gpt-oss:20b", messages=messages, stream=True):
        response_text += part["message"]["content"]

    if verbose:
        print("Raw model response:\n", response_text, "\n")

    try:
        mapping = json.loads(response_text)
        if verbose:
            print("Parsed mapping JSON:\n", json.dumps(mapping, indent=2))
    except json.JSONDecodeError:
        print("Warning: model did not return valid JSON.")
        mapping = {}

    valid_map = {k: v for k, v in mapping.items() if v and v in df.columns}

    # Handle multiple targets mapping to same source (e.g. Region & Store -> Store)
    inverse_map = {}
    for k, v in valid_map.items():
        inverse_map.setdefault(v, []).append(k)

    for src_col, targets in inverse_map.items():
        if len(targets) == 1:
            df.rename(columns={src_col: targets[0]}, inplace=True)
        else:
            for tgt in targets:
                df[tgt] = df[src_col]
            if verbose:
                print(f"Duplicated '{src_col}' for multiple targets: {targets}")

    #df = df.rename(columns={v: k for k, v in valid_map.items()})

    if "Week" not in df.columns:
        possible_date_cols = [
            col for col in df.columns
            if any(x in col.lower() for x in ["date", "week", "time", "period","Week"])
        ]
        if possible_date_cols:
            if verbose:
                print(f"Fallback: Detected possible date column → {possible_date_cols[0]}")
            df.rename(columns={possible_date_cols[0]: "Week"}, inplace=True)

    if "Week" in df.columns:
        df["Week_parsed"] = pd.to_datetime(df["Week"], format="%d-%m-%Y", errors="coerce")

        mask = df["Week_parsed"].isna()
        if mask.any():
            df.loc[mask, "Week_parsed"] = pd.to_datetime(df.loc[mask, "Week"], format="%Y-%m-%d", errors="coerce")

        df["Week"] = df["Week_parsed"].dt.strftime("%Y-%m-%d")
        df.drop(columns=["Week_parsed"], inplace=True)

    if "Holiday" in df.columns:
        df["Holiday"] = df["Holiday"].replace(
            {True: 1, False: 0, "true": 1, "false": 0}
        ).astype(int)

    final_cols = [col for col in target_fields if col in df.columns]
    final_df = df[final_cols]

    print("\nFinal standardized columns:", final_df.columns.to_list())

    required_fields = {"Region", "Week", "Sales"}
    missing = required_fields - set(final_df.columns)

    if missing and not retry:
        print(f"Missing critical fields: {missing}. Retrying once...\n")
        return standardize_columns(input, retry=True, verbose=verbose)
    elif missing and retry:
        print(f"Retry failed. Still missing: {missing}. Please check column names manually.")

    return final_df
