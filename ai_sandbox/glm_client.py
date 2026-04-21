"""Asynchronous client for the Z.ai GLM chat-completions API.

Wraps httpx so the rest of the Grant Copilot can request strict JSON
responses from GLM without each caller re-implementing error handling,
Markdown-fence stripping, and payload shaping.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from typing import Any, Optional

import httpx
from dotenv import load_dotenv


DEFAULT_ENDPOINT = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
DEFAULT_MODEL = "glm-4"

_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*(?P<body>.*?)\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)


class GLMClientError(RuntimeError):
    """Raised when the GLM API call fails or its response can't be parsed."""


class GLMClient:
    """Minimal async client for Z.ai GLM chat completions returning JSON."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout: float = 60.0,
    ) -> None:
        load_dotenv()
        resolved_key = api_key or os.getenv("ZAI_API_KEY")
        if not resolved_key:
            raise ValueError(
                "ZAI_API_KEY is not set. Add it to your .env file or pass api_key= explicitly."
            )

        self._api_key = resolved_key
        self._model = model
        self._endpoint = endpoint
        self._timeout = timeout

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

        payload: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": hardened_system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    self._endpoint, json=payload, headers=headers
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500] if exc.response is not None else "<no body>"
            raise GLMClientError(
                f"GLM API returned HTTP {exc.response.status_code}: {body}"
            ) from exc
        except httpx.HTTPError as exc:
            raise GLMClientError(f"GLM API transport error: {exc}") from exc

        try:
            envelope = response.json()
        except json.JSONDecodeError as exc:
            raise GLMClientError(
                f"GLM API returned non-JSON envelope: {response.text[:500]}"
            ) from exc

        try:
            content: str = envelope["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GLMClientError(
                f"Unexpected GLM response shape: {envelope!r}"
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
            "You are a connection-test assistant for the Malaysia SME Grant Copilot."
        ),
        user_prompt=(
            'Return a JSON object with a single key "greeting" whose value is '
            'a short friendly hello message.'
        ),
    )
    print("GLM ping OK ->", result)


if __name__ == "__main__":
    asyncio.run(_ping())
