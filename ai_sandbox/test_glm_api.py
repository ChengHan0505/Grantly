"""Small ZhipuAI smoke test using the API key from local .env files."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from zhipuai import ZhipuAI


DEFAULT_MODEL = "ilmu-glm-5.1"


def load_env() -> None:
    """Load env vars from ai_sandbox/.env first, then Grantly/.env."""

    current_dir = Path(__file__).resolve().parent
    env_candidates = [
        current_dir / ".env",
        current_dir.parent / ".env",
    ]

    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(env_path, override=False)


def main() -> None:
    load_env()

    api_key = os.getenv("ZAI_API_KEY") or os.getenv("ILMU_API_KEY")
    model = os.getenv("GLM_MODEL", DEFAULT_MODEL)
    if not api_key:
        raise RuntimeError(
            "No API key found. Set ZAI_API_KEY or ILMU_API_KEY in "
            "Grantly/.env or Grantly/ai_sandbox/.env."
        )

    client = ZhipuAI(api_key=api_key)
    print("Using model:", model)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": 'Reply with exactly: {"ok": true}',
            }
        ],
        temperature=0,
    )

    print("Request succeeded.")
    print("Response:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
