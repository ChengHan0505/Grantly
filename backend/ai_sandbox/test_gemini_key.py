from __future__ import annotations

import asyncio
import os

try:
    from .glm_client import (
        CLAUDE_BASE_URL,
        DEFAULT_CLAUDE_MODEL,
        DEFAULT_MODEL,
        DEFAULT_OPENROUTER_MODEL,
        DEFAULT_ZAI_MODEL,
        GEMINI_BASE_URL,
        GLMClient,
        OPENROUTER_BASE_URL,
        ZAI_BASE_URL,
    )
except ImportError:  # pragma: no cover - supports direct script execution
    from glm_client import (
        CLAUDE_BASE_URL,
        DEFAULT_CLAUDE_MODEL,
        DEFAULT_MODEL,
        DEFAULT_OPENROUTER_MODEL,
        DEFAULT_ZAI_MODEL,
        GEMINI_BASE_URL,
        GLMClient,
        OPENROUTER_BASE_URL,
        ZAI_BASE_URL,
    )


def mask(value: str) -> str:
    if not value:
        return "<missing>"
    return f"{value[:6]}...{value[-4:]}"


async def main() -> None:
    client = GLMClient()
    claude_api_key = (
        os.getenv("CLAUDE_SONNET_API_KEY", "").strip()
        or os.getenv("ANTHROPIC_API_KEY", "").strip()
    )
    api_key = os.getenv("GOOGLE_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY", "").strip()
    openrouter_api_key = (
        os.getenv("OPENROUTER_GEMINI_API_KEY", "").strip()
        or os.getenv("OPENROUTER_API_KEY", "").strip()
    )
    zai_api_key = (
        os.getenv("ZAI_API_KEY", "").strip()
        or os.getenv("Z_AI_API_KEY", "").strip()
        or os.getenv("ZHIPUAI_API_KEY", "").strip()
        or os.getenv("ILMU_API_KEY", "").strip()
    )
    print("CLAUDE_SONNET_API_KEY:", mask(claude_api_key))
    print("GOOGLE_API_KEY:", mask(api_key))
    print("OPENROUTER_API_KEY:", mask(openrouter_api_key))
    print("ZAI_API_KEY:", mask(zai_api_key))
    print("CLAUDE_BASE_URL:", os.getenv("CLAUDE_SONNET_BASE_URL") or os.getenv("ANTHROPIC_BASE_URL") or CLAUDE_BASE_URL)
    print("BASE_URL:", os.getenv("GEMINI_BASE_URL") or GEMINI_BASE_URL)
    print("OPENROUTER_BASE_URL:", os.getenv("OPENROUTER_BASE_URL") or OPENROUTER_BASE_URL)
    print("ZAI_BASE_URL:", os.getenv("ZAI_BASE_URL") or os.getenv("GLM_BASE_URL") or ZAI_BASE_URL)
    print("CLAUDE_MODEL:", client.claude_model or DEFAULT_CLAUDE_MODEL)
    print("MODEL:", client.model or DEFAULT_MODEL)
    print("OPENROUTER_MODEL:", client.openrouter_model or DEFAULT_OPENROUTER_MODEL)
    print("ZAI_MODEL:", client.zai_model or DEFAULT_ZAI_MODEL)
    result = await client.generate_json(
        system_prompt="You are a connection test assistant.",
        user_prompt='Return JSON only: {"pong": true}',
        temperature=0.0,
    )
    print("Claude primary / OpenRouter Gemini / direct Gemini / Z.ai fallback path OK:", result)


if __name__ == "__main__":
    asyncio.run(main())
