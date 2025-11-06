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
