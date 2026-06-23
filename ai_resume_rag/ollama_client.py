import requests


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
CHAT_MODEL = "llama3.2:latest"


def chat_with_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json={
                "model": CHAT_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "stream": False,
                "options": {
                    "temperature": 0.1,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["message"]["content"]
    except Exception as e:
        print(f"Failed to connect: {e}")
        return ""