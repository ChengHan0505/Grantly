"""Asynchronous client for the Z.ai / Zhipu GLM chat-completions API.

Uses the official ``zhipuai`` SDK's ``AsyncZhipuAI`` so we inherit the
dynamic JWT authentication the service requires, while keeping a
JSON-in / JSON-out method surface for the rest of the Grant Copilot.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from zhipuai import ZhipuAI
from zhipuai.core._errors import APIStatusError

log = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3
_BASE_DELAY_S = 2.0
_JITTER_S = 0.5
_RETRYABLE_STATUS_CODES = {502, 503, 504}

DEFAULT_MODEL = "ilmu-glm-5.1"
ILMU_BASE_URL = "https://api.ilmu.ai/v1"
PROJECT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]

_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*(?P<body>.*?)\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)


class GLMClientError(RuntimeError):
    """Raised when the GLM API call fails or its response can't be parsed."""


class GLMClient:
    """Minimal async client for GLM chat completions returning JSON."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str | None = None,
    ) -> None:
        load_dotenv(PROJECT_DIR / ".env")
        load_dotenv(BACKEND_DIR / ".env", override=False)
        resolved_key = api_key or os.getenv("ZAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "ZAI_API_KEY is not set. Add it to your .env file or pass api_key= explicitly."
            )

        self.api_key = resolved_key
        self.model = model or os.getenv("ZAI_MODEL") or os.getenv("GLM_MODEL") or DEFAULT_MODEL
        self.client = ZhipuAI(api_key=self.api_key, base_url=ILMU_BASE_URL, timeout=20.0, max_retries=0)

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Send a chat completion and return the model's JSON content as a dict."""

        hardened_system_prompt = (
            system_prompt.rstrip()
            + "\n\nYou MUST respond with a single valid JSON object and nothing else. "
            "Do not wrap the JSON in Markdown code fences or add commentary."
        )

        messages = [
            {"role": "system", "content": hardened_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        last_exc: Exception | None = None
        for attempt in range(1, _MAX_ATTEMPTS + 1):
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                break
            except APIStatusError as exc:
                if exc.status_code not in _RETRYABLE_STATUS_CODES:
                    raise GLMClientError(f"GLM API call failed: {exc}") from exc
                last_exc = exc
            except (TimeoutError, OSError) as exc:
                last_exc = exc

            if attempt < _MAX_ATTEMPTS:
                delay = _BASE_DELAY_S * (2 ** (attempt - 1)) + random.uniform(-_JITTER_S, _JITTER_S)
                delay = max(0.1, delay)
                log.warning(
                    "GLM API error. Retrying in %.1fs... (Attempt %d/%d)",
                    delay, attempt + 1, _MAX_ATTEMPTS,
                )
                print(f"GLM API error. Retrying in {delay:.1f}s... (Attempt {attempt + 1}/{_MAX_ATTEMPTS})")
                await asyncio.sleep(delay)
            else:
                raise GLMClientError(
                    f"GLM API call failed after {_MAX_ATTEMPTS} attempts: {last_exc}"
                ) from last_exc

        try:
            content: str = response.choices[0].message.content
        except (AttributeError, IndexError, TypeError) as exc:
            raise GLMClientError(
                f"Unexpected GLM response shape: {response!r}"
            ) from exc

        return self._parse_json_content(content)

    @staticmethod
    def _parse_json_content(content: str) -> dict[str, Any]:
        """Parse the assistant message as JSON, tolerating Markdown fences."""

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        fence_match = _JSON_FENCE_RE.match(content)
        if fence_match:
            stripped = fence_match.group("body")
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                pass

        first = content.find("{")
        last = content.rfind("}")
        if first != -1 and last != -1 and last > first:
            candidate = content[first : last + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError as exc:
                raise GLMClientError(
                    f"Could not parse JSON from GLM response: {content[:500]}"
                ) from exc

        raise GLMClientError(
            f"GLM response contained no parseable JSON object: {content[:500]}"
        )


async def _ping() -> None:
    client = GLMClient()
    result = await client.generate_json(
        system_prompt=(
            "You are a connection-test assistant for the Grantly."
        ),
        user_prompt=(
            'Return a JSON object with a single key "greeting" whose value is '
            'a short friendly hello message.'
        ),
    )
    print("GLM ping OK ->", result)


if __name__ == "__main__":
    asyncio.run(_ping())
