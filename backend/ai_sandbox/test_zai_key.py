from __future__ import annotations

import asyncio
import os

from zhipuai import ZhipuAI

from backend.src.core.config import settings

try:
    from .glm_client import GLMClient, ILMU_BASE_URL
except ImportError:  # pragma: no cover - supports direct script execution
    from glm_client import GLMClient, ILMU_BASE_URL


def mask(value: str) -> str:
    if not value:
        return "<missing>"
    return f"{value[:6]}...{value[-4:]}"


async def main() -> None:
    client = GLMClient()
    print("ZAI_API_KEY:", mask(os.getenv("ZAI_API_KEY", "").strip()))
    print("BASE_URL:", ILMU_BASE_URL)
    print("MODEL:", client.model)
    result = await client.generate_json(
        system_prompt="You are a connection test assistant.",
        user_prompt='Return JSON only: {"pong": true}',
        temperature=0.0,
    )
    print("GLMClient path OK:", result)

    scout_client = ZhipuAI(api_key=settings.zai_api_key, base_url=settings.zai_base_url)
    scout_response = await asyncio.to_thread(
        scout_client.chat.completions.create,
        model=settings.zai_model,
        messages=[
            {"role": "system", "content": "Return JSON only."},
            {"role": "user", "content": '{"scout": "pong"}'},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    print("Scout SDK path OK:", scout_response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())
