from dotenv import load_dotenv
import os
from ollama import Client
import pandas as pd

load_dotenv()

api_key = os.getenv("OLLAMA_API_KEY")

client = Client(
    host="https://ollama.com",
    headers={"Authorization": f"Bearer {api_key}"}
)


def ask_about_dataframe(df: pd.DataFrame, question: str) -> str:
    """
    Use an LLM (Ollama) to answer a natural language question about a DataFrame.
    
    Parameters:
        df (pd.DataFrame): the dataset to analyze
        question (str): a natural language question (e.g. "What is the profit growth this month vs last month?")
    
    Returns:
        str: model-generated answer
    """

    prompt = f"""
You are an intelligent data analyst with Python knowledge.

You will receive:
- a DataFrame preview
- a natural language question about it


Question: {question}

Please  answer the question based on the the dataset in clear, concise language.
If exact computation is not possible from this small sample, infer logically and explain the reasoning.
Output must be plain text, no code.
    """

    response_text = ""
    for part in client.chat("gpt-oss:20b", messages=[{"role": "user", "content": prompt}], stream=True):
        response_text += part["message"]["content"]
        print(part["message"]["content"], end="", flush=True)

    return response_text
