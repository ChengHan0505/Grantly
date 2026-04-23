import os
from dotenv import load_dotenv
from openai import OpenAI

BASE_URL = "https://api.ilmu.ai/v1"

def mask(s: str) -> str:
    if not s:
        return "<missing>"
    return f"{s[:6]}...{s[-4:]}"

def main():
    load_dotenv()
    key = os.getenv("ZAI_API_KEY", "").strip()

    print("ZAI_API_KEY:", mask(key))
    print("BASE_URL:", BASE_URL)

    if not key:
        raise SystemExit("❌ ZAI_API_KEY missing in .env")

    client = OpenAI(
        api_key=key,
        base_url=BASE_URL,
    )

    try:
        resp = client.chat.completions.create(
            model="ilmu-glm-5.1",
            messages=[{"role": "user", "content": "Reply with: pong"}],
            temperature=0.1,
        )
        print("✅ ilmu auth OK")
        print("Model reply:", resp.choices[0].message.content)
    except Exception as e:
        print("❌ ilmu auth/call failed")
        print(type(e).__name__, str(e))

if __name__ == "__main__":
    main()