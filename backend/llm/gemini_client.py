import requests
from backend import config
from backend.llm.prompts import build_prompt

API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{config.MODEL_PATH}:generateContent?key={config.GOOGLE_API_KEY}"

def classify_message(text: str) -> dict:
    try:
        prompt = build_prompt(text)
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return {"verdict": "error", "reasoning": response.text, "category": "unknown", "raw_response": ""}

        result = response.json()
        generated_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Parse structured output
        lines = generated_text.strip().split("\n")
        verdict = lines[0].replace("Verdict:", "").strip().lower()
        reasoning = lines[1].replace("Reasoning:", "").strip()
        category = "unknown"
        if len(lines) > 2:
            category = lines[2].replace("Category:", "").strip().lower()

        return {"verdict": verdict, "reasoning": reasoning, "category": category, "raw_response": result}

    except Exception as e:
        return {"verdict": "error", "reasoning": str(e), "category": "unknown", "raw_response": ""}
