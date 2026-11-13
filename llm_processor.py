import json

from config import API_KEY, MODEL, SYSTEM_PROMPT

from openrouter import OpenRouter

def analyze_text(text):
    if not API_KEY:
        raise ValueError('Не найден OR_API_KEY в .env')

    prompt = SYSTEM_PROMPT + '\n' + text

    with OpenRouter(api_key=API_KEY) as client:
        response = client.chat.send(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

    result = response.choices[0].message.content

    result = result.strip()

    if result.startswith("```json"):
        result = result[7:]

    if result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    result = result.strip()

    return json.loads(result)