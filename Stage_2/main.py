import sys
from dotenv import load_dotenv
import requests
import os
from pathlib import Path

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


def load_prompt(path):
    return Path(path).read_text(encoding="utf-8")

def prompt_chain(user_complaint):

    def run_prompt(filename, **kwargs):
        template = load_prompt(filename)
        prompt = template.format(**kwargs)
        return call(prompt)

    step1Response = run_prompt("prompts/1_intent.txt", user_complaint=user_complaint)
    print (step1Response)

    prompt_2_template = load_prompt("prompts/2_possible_categories.txt")
    prompt_2 = prompt_2_template.format(
    step1Response=step1Response,
    user_complaint=user_complaint
    )
    step2Response = call(prompt_2)
    if step2Response is None:
     raise RuntimeError("Step 2 failed")
    print (step2Response)

    prompt_3_template = load_prompt("prompts/3_best_category.txt")
    prompt_3 = prompt_3_template.format(
    step2Response=step2Response,
    user_complaint=user_complaint
    )
    step3Response = call(prompt_3)
    if step3Response is None:
     raise RuntimeError("Step 3 failed")
    print (step3Response)

    prompt_4_template = load_prompt("prompts/4_extra_info.txt")
    prompt_4 = prompt_4_template.format(
    step1Response=step1Response,
    step3Response=step3Response,
    user_complaint=user_complaint
    )
    step4Response = call(prompt_4)
    if step4Response is None:
     raise RuntimeError("Step 4 failed")
    print (step4Response)

    prompt_5_template = load_prompt("prompts/5_produce_reply.txt")
    prompt_5 = prompt_5_template.format(
    step4Response=step4Response,
    step3Response=step3Response,
    user_complaint=user_complaint
    )
    step5Response = call(prompt_5)

    return step5Response





if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py \"your prompt here\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    result = prompt_chain(prompt)

    if result:
        print(result)
