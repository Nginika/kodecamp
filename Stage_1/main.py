import sys
from dotenv import load_dotenv
import requests
import os

load_dotenv()

def call(prompt):
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME")

    if not OPENROUTER_API_KEY:
        raise ValueError("Missing OPENROUTER_API_KEY")
    if not MODEL_NAME:
        raise ValueError("Missing MODEL_NAME")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        json={
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    data = response.json()

    if "choices" not in data:
        print("API Error:", data)
        return None

    return data["choices"][0]["message"]["content"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your prompt here\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    result = call(prompt)

    if result:
        print(result)
