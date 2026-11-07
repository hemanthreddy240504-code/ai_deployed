import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test():
    key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    url = (
        f"https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent?key={key}"
    )

    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(
            url,
            json={
                "contents": [
                    {"parts": [{"text": "Say hello"}]}
                ]
            }
        )

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

asyncio.run(test())