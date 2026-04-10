import base64
import json
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def analyser_image_llm(contenu_image: bytes) -> dict:
    image_base64 = base64.b64encode(contenu_image).decode("utf-8")
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        "Analyze this image of a tennis player and determine the stroke they are playing. "
        "The stroke must be exactly one of the following classes: 'backhand', 'forehand', 'ready_position', 'serve'. "
        "Respond in pure JSON format only with the following exact structure: "
        '{"classe": "value", "confiance": 0.95} '
        "where 'confiance' is a float between 0.0 and 1.0 representing your confidence score."
    )

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "response_format": {"type": "json_object"}
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30.0
        )
        response.raise_for_status()
        data = response.json()
        
    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    return {
        "classe": parsed.get("classe", "unknown"),
        "confiance": float(parsed.get("confiance", 0.0))
    }
