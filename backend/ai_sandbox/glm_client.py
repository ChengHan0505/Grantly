"""Asynchronous JSON client with Claude, Gemini, and GLM provider fallbacks.

The rest of the Grantly AI agents still import ``GLMClient``. The class name is
kept as a compatibility shim, but calls now go through Claude Sonnet first,
OpenRouter-hosted Gemini second, direct Gemini third, and Z.ai GLM last.
"""

from __future__ import annotations

import asyncio
from email.utils import parsedate_to_datetime
import json
import logging
import os
import random
import re
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from dotenv import load_dotenv

log = logging.getLogger(__name__)

_DEFAULT_MAX_ATTEMPTS = 2
_BASE_DELAY_S = 2.0
_JITTER_S = 0.5
_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

DEFAULT_CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_FALLBACK_MODELS = ("gemini-2.5-flash-lite",)
DEFAULT_OPENROUTER_MODEL = "google/gemini-2.5-flash"
DEFAULT_OPENROUTER_FALLBACK_MODELS = ("google/gemini-2.5-flash-lite",)
DEFAULT_ZAI_MODEL = "ilmu-glm-5.1"
CLAUDE_BASE_URL = "https://api.anthropic.com/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
ZAI_BASE_URL = "https://api.ilmu.ai/v1"
PROJECT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]

_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*(?P<body>.*?)\s*```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def _csv_env(name: str, default: tuple[str, ...]) -> list[str]:
    raw_value = os.getenv(name)
    if raw_value is None:
        return list(default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() not in {"0", "false", "no", "off"}


def _is_rate_limit_error(exc: Exception | None) -> bool:
    return isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 429


def _retry_after_seconds(exc: Exception | None) -> float | None:
    if not isinstance(exc, httpx.HTTPStatusError):
        return None

    header_value = exc.response.headers.get("retry-after")
    if header_value:
        if header_value.isdigit():
            return float(header_value)
        try:
            retry_at = parsedate_to_datetime(header_value)
            return max(0.0, retry_at.timestamp() - time.time())
        except (TypeError, ValueError, OverflowError):
            pass

    try:
        body = exc.response.json()
    except ValueError:
        return None

    details = body.get("error", {}).get("details", [])
    for detail in details if isinstance(details, list) else []:
        retry_delay = detail.get("retryDelay") if isinstance(detail, dict) else None
        if not isinstance(retry_delay, str):
            continue
        match = re.fullmatch(r"(?P<seconds>\d+(?:\.\d+)?)s", retry_delay.strip())
        if match:
            return float(match.group("seconds"))
    return None


class GLMClientError(RuntimeError):
    """Raised when provider calls fail or their responses can't be parsed."""


class GeminiRateLimitError(GLMClientError):
    """Raised when Gemini rate limits all configured model attempts."""


class GLMClient:
    """Compatibility client for Gemini-first JSON generation with GLM fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str | None = None,
        claude_api_key: Optional[str] = None,
        claude_model: str | None = None,
        openrouter_api_key: Optional[str] = None,
        openrouter_model: str | None = None,
        zai_api_key: Optional[str] = None,
        zai_model: str | None = None,
    ) -> None:
        load_dotenv(PROJECT_DIR / ".env")
        load_dotenv(BACKEND_DIR / ".env", override=False)
        resolved_claude_key = claude_api_key or os.getenv("CLAUDE_SONNET_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        gemini_api_keys = _dedupe(
            [
                key
                for key in [
                    api_key,
                    os.getenv("GOOGLE_API_KEY"),
                    os.getenv("GEMINI_API_KEY"),
                    *_csv_env("GEMINI_FALLBACK_API_KEYS", tuple()),
                    *_csv_env("GOOGLE_FALLBACK_API_KEYS", tuple()),
                ]
                if key
            ]
        )
        resolved_openrouter_key = (
            openrouter_api_key
            or os.getenv("OPENROUTER_GEMINI_API_KEY")
            or os.getenv("OPENROUTER_API_KEY")
        )
        resolved_zai_key = (
            zai_api_key
            or os.getenv("ZAI_API_KEY")
            or os.getenv("Z_AI_API_KEY")
            or os.getenv("ZHIPUAI_API_KEY")
            or os.getenv("ILMU_API_KEY")
        )
        if not resolved_claude_key and not gemini_api_keys and not resolved_openrouter_key and not resolved_zai_key:
            raise ValueError(
                "No AI API key is set. Add CLAUDE_SONNET_API_KEY, "
                "OPENROUTER_GEMINI_API_KEY/OPENROUTER_API_KEY, GOOGLE_API_KEY, "
                "or ZAI_API_KEY to your .env file."
            )

        self.claude_api_key = resolved_claude_key
        self.claude_model = (
            claude_model
            or os.getenv("CLAUDE_SONNET_MODEL")
            or os.getenv("ANTHROPIC_MODEL")
            or DEFAULT_CLAUDE_MODEL
        )
        self.claude_base_url = os.getenv("CLAUDE_SONNET_BASE_URL") or os.getenv("ANTHROPIC_BASE_URL") or CLAUDE_BASE_URL
        self.claude_timeout_seconds = float(os.getenv("CLAUDE_SONNET_TIMEOUT_SECONDS", "30"))
        self.claude_max_tokens = int(os.getenv("CLAUDE_SONNET_MAX_TOKENS", "8192"))
        self.claude_max_attempts = max(1, int(os.getenv("CLAUDE_SONNET_MAX_ATTEMPTS", "2")))
        self.claude_enabled = _bool_env("CLAUDE_SONNET_ENABLED", True)
        self.api_keys = gemini_api_keys
        self.api_key = gemini_api_keys[0] if gemini_api_keys else None
        self.model = model or os.getenv("GEMINI_MODEL") or os.getenv("GOOGLE_MODEL") or DEFAULT_MODEL
        fallback_models = _csv_env("GEMINI_FALLBACK_MODELS", DEFAULT_FALLBACK_MODELS)
        self.models = _dedupe([self.model, *fallback_models]) if self.api_keys else []
        self.base_url = os.getenv("GEMINI_BASE_URL") or GEMINI_BASE_URL
        self.timeout_seconds = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))
        self.max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "8192"))
        self.max_attempts = max(1, int(os.getenv("GEMINI_MAX_ATTEMPTS", str(_DEFAULT_MAX_ATTEMPTS))))
        self.max_retry_delay_seconds = max(0.5, float(os.getenv("GEMINI_MAX_RETRY_DELAY_SECONDS", "8")))
        self.openrouter_api_key = resolved_openrouter_key
        self.openrouter_model = (
            openrouter_model
            or os.getenv("OPENROUTER_MODEL")
            or os.getenv("OPENROUTER_GEMINI_MODEL")
            or DEFAULT_OPENROUTER_MODEL
        )
        openrouter_fallback_models = _csv_env(
            "OPENROUTER_FALLBACK_MODELS",
            DEFAULT_OPENROUTER_FALLBACK_MODELS,
        )
        self.openrouter_models = (
            _dedupe([self.openrouter_model, *openrouter_fallback_models])
            if self.openrouter_api_key
            else []
        )
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL") or OPENROUTER_BASE_URL
        self.openrouter_timeout_seconds = float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", str(self.timeout_seconds)))
        self.openrouter_max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", str(self.max_output_tokens)))
        self.openrouter_max_attempts = max(1, int(os.getenv("OPENROUTER_MAX_ATTEMPTS", "2")))
        self.openrouter_fallback_enabled = _bool_env("OPENROUTER_FALLBACK_ENABLED", True)
        self.openrouter_referer = os.getenv("OPENROUTER_HTTP_REFERER") or os.getenv("OPENROUTER_SITE_URL")
        self.openrouter_title = os.getenv("OPENROUTER_APP_TITLE") or "Grantly"
        self.zai_api_key = resolved_zai_key
        self.zai_model = zai_model or os.getenv("ZAI_MODEL") or os.getenv("GLM_MODEL") or DEFAULT_ZAI_MODEL
        self.zai_base_url = os.getenv("ZAI_BASE_URL") or os.getenv("GLM_BASE_URL") or ZAI_BASE_URL
        self.zai_timeout_seconds = float(os.getenv("ZAI_TIMEOUT_SECONDS", str(self.timeout_seconds)))
        self.zai_max_tokens = int(os.getenv("ZAI_MAX_TOKENS", str(self.max_output_tokens)))
        self.zai_max_attempts = max(1, int(os.getenv("ZAI_MAX_ATTEMPTS", "2")))
        self.zai_fallback_enabled = _bool_env("ZAI_FALLBACK_ENABLED", True)

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Send a provider request and return the generated JSON content as a dict."""

        return await asyncio.to_thread(
            self.generate_json_sync,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
        )

    def generate_json_sync(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Synchronous variant used by non-async flows such as Scout."""

        hardened_system_prompt = (
            system_prompt.rstrip()
            + "\n\nYou MUST respond with a single valid JSON object and nothing else. "
            "Do not wrap the JSON in Markdown code fences or add commentary."
        )

        gemini_payload = {
            "systemInstruction": {
                "parts": [{"text": hardened_system_prompt}],
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_prompt}],
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
                "maxOutputTokens": self.max_output_tokens,
            },
        }

        messages = [
            {"role": "system", "content": hardened_system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        provider_errors: list[tuple[str, Exception]] = []
        if self.claude_api_key and self.claude_enabled:
            try:
                return self._generate_json_via_claude(
                    system_prompt=hardened_system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                )
            except GLMClientError as exc:
                provider_errors.append(("Claude Sonnet", exc))

        if self.openrouter_models and self.openrouter_fallback_enabled:
            if provider_errors:
                log.warning(
                    "Claude Sonnet generation failed; falling back to OpenRouter Gemini: %s",
                    self._format_provider_errors(provider_errors),
                )
            try:
                return self._generate_json_via_openrouter(messages, temperature)
            except GLMClientError as exc:
                provider_errors.append(("OpenRouter Gemini", exc))

        if self.models:
            if provider_errors:
                log.warning(
                    "Claude/OpenRouter provider paths failed; falling back to direct Gemini: %s",
                    self._format_provider_errors(provider_errors),
                )
            try:
                return self._generate_json_via_gemini(gemini_payload)
            except GLMClientError as exc:
                provider_errors.append(("Gemini", exc))

        if self.zai_api_key and self.zai_fallback_enabled:
            if provider_errors:
                log.warning(
                    "Claude/Gemini provider paths failed; falling back to Z.ai GLM: %s",
                    self._format_provider_errors(provider_errors),
                )
            try:
                return self._generate_json_via_zai(messages, temperature)
            except GLMClientError as exc:
                provider_errors.append(("Z.ai GLM", exc))

        if provider_errors:
            raise self._provider_chain_error(provider_errors)

        if self.claude_api_key and not self.claude_enabled:
            raise GLMClientError(
                "CLAUDE_SONNET_API_KEY is set, but CLAUDE_SONNET_ENABLED=false and no fallback provider is available."
            )

        if self.openrouter_api_key and not self.openrouter_fallback_enabled:
            raise GLMClientError(
                "OPENROUTER_GEMINI_API_KEY/OPENROUTER_API_KEY is set, but "
                "OPENROUTER_FALLBACK_ENABLED=false and no fallback provider is available."
            )

        if self.zai_api_key and not self.zai_fallback_enabled:
            raise GLMClientError(
                "ZAI_API_KEY is set, but ZAI_FALLBACK_ENABLED=false and no Gemini provider is available."
            )

        raise GLMClientError(
            "No enabled AI provider is configured. Set CLAUDE_SONNET_API_KEY for Claude, "
            "OPENROUTER_GEMINI_API_KEY/OPENROUTER_API_KEY for OpenRouter Gemini, "
            "GOOGLE_API_KEY for direct Gemini, or ZAI_API_KEY for the GLM fallback."
        )

    def _generate_json_via_claude(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
    ) -> dict[str, Any]:
        payload = {
            "model": self.claude_model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": temperature,
            "max_tokens": self.claude_max_tokens,
        }

        last_exc: Exception | None = None
        for attempt in range(1, self.claude_max_attempts + 1):
            try:
                response_payload = self._post_claude_message(payload)
                content = self._extract_claude_text_content(response_payload)
                return self._parse_json_content(content, provider="Claude Sonnet")
            except GLMClientError:
                raise
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                    raise GLMClientError(
                        f"Claude Sonnet API call failed: {self._summarize_http_error(exc)}"
                    ) from exc
                last_exc = exc
            except (httpx.HTTPError, TimeoutError, OSError) as exc:
                last_exc = exc

            if attempt < self.claude_max_attempts:
                delay = self._retry_delay_seconds(last_exc, attempt)
                log.warning(
                    "Claude Sonnet API error. Retrying in %.1fs... (Attempt %d/%d)",
                    delay, attempt + 1, self.claude_max_attempts,
                )
                print(
                    f"Claude Sonnet API error. Retrying in {delay:.1f}s... "
                    f"(Attempt {attempt + 1}/{self.claude_max_attempts})"
                )
                time.sleep(delay)

        raise GLMClientError(
            "Claude Sonnet API call failed after configured retry attempts: "
            f"{self._summarize_exception(last_exc)}"
        ) from last_exc

    def _generate_json_via_gemini(self, payload: dict[str, Any]) -> dict[str, Any]:
        last_exc: Exception | None = None
        exhausted_pairs: list[str] = []
        total_keys = len(self.api_keys)
        for key_index, api_key in enumerate(self.api_keys, start=1):
            for model_name in self.models:
                for attempt in range(1, self.max_attempts + 1):
                    try:
                        response_payload = self._post_generate_content(payload, model_name, api_key)
                        content = self._extract_text_content(response_payload)
                        return self._parse_json_content(content, provider="Gemini")
                    except GLMClientError:
                        raise
                    except httpx.HTTPStatusError as exc:
                        if exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                            raise GLMClientError(
                                f"Gemini API call failed: {self._summarize_http_error(exc)}"
                            ) from exc
                        last_exc = exc
                    except (httpx.HTTPError, TimeoutError, OSError) as exc:
                        last_exc = exc

                    if attempt < self.max_attempts:
                        delay = self._retry_delay_seconds(last_exc, attempt)
                        log.warning(
                            "Gemini API error for %s (key %d/%d). Retrying in %.1fs... (Attempt %d/%d)",
                            model_name, key_index, total_keys, delay, attempt + 1, self.max_attempts,
                        )
                        print(
                            f"Gemini API error for {model_name} (key {key_index}/{total_keys}). "
                            f"Retrying in {delay:.1f}s... (Attempt {attempt + 1}/{self.max_attempts})"
                        )
                        time.sleep(delay)

                exhausted_pairs.append(f"{model_name}@key{key_index}")
                if model_name != self.models[-1]:
                    log.warning("Gemini model %s exhausted on key %d/%d; trying fallback model.", model_name, key_index, total_keys)
            if key_index != total_keys:
                log.warning("Gemini key %d/%d exhausted; trying next configured key.", key_index, total_keys)

        if _is_rate_limit_error(last_exc):
            models = ", ".join(exhausted_pairs)
            raise GeminiRateLimitError(
                "Gemini rate limit reached for configured models "
                f"({models}). The app can retry later, use deterministic fallback, "
                "or set GEMINI_MODEL=gemini-2.5-flash-lite to reduce pressure."
            ) from last_exc

        raise GLMClientError(
            "Gemini API call failed after configured retry attempts: "
            f"{self._summarize_exception(last_exc)}"
        ) from last_exc

    def _generate_json_via_openrouter(
        self,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> dict[str, Any]:
        last_exc: Exception | None = None
        exhausted_models: list[str] = []
        for model_name in self.openrouter_models:
            payload = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": self.openrouter_max_tokens,
                "stream": False,
                "response_format": {"type": "json_object"},
            }
            for attempt in range(1, self.openrouter_max_attempts + 1):
                try:
                    response_payload = self._post_openrouter_chat_completion(payload)
                    content = self._extract_chat_completion_content(
                        response_payload,
                        provider="OpenRouter Gemini",
                    )
                    return self._parse_json_content(content, provider="OpenRouter Gemini")
                except GLMClientError:
                    raise
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                        raise GLMClientError(
                            f"OpenRouter Gemini API call failed: {self._summarize_http_error(exc)}"
                        ) from exc
                    last_exc = exc
                except (httpx.HTTPError, TimeoutError, OSError) as exc:
                    last_exc = exc

                if attempt < self.openrouter_max_attempts:
                    delay = self._retry_delay_seconds(last_exc, attempt)
                    log.warning(
                        "OpenRouter Gemini API error for %s. Retrying in %.1fs... (Attempt %d/%d)",
                        model_name, delay, attempt + 1, self.openrouter_max_attempts,
                    )
                    print(
                        f"OpenRouter Gemini API error for {model_name}. Retrying in {delay:.1f}s... "
                        f"(Attempt {attempt + 1}/{self.openrouter_max_attempts})"
                    )
                    time.sleep(delay)

            exhausted_models.append(model_name)
            if model_name != self.openrouter_models[-1]:
                log.warning("OpenRouter model %s exhausted; trying fallback model.", model_name)

        models = ", ".join(exhausted_models)
        raise GLMClientError(
            "OpenRouter Gemini API call failed after configured retry attempts "
            f"for models ({models}): {self._summarize_exception(last_exc)}"
        ) from last_exc

    def _generate_json_via_zai(
        self,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> dict[str, Any]:
        payload = {
            "model": self.zai_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": self.zai_max_tokens,
            "stream": False,
            "response_format": {"type": "json_object"},
        }

        last_exc: Exception | None = None
        for attempt in range(1, self.zai_max_attempts + 1):
            try:
                response_payload = self._post_zai_chat_completion(payload)
                content = self._extract_chat_completion_content(response_payload, provider="Z.ai GLM")
                return self._parse_json_content(content, provider="Z.ai GLM")
            except GLMClientError:
                raise
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in _RETRYABLE_STATUS_CODES:
                    raise GLMClientError(
                        f"Z.ai GLM API call failed: {self._summarize_http_error(exc)}"
                    ) from exc
                last_exc = exc
            except (httpx.HTTPError, TimeoutError, OSError) as exc:
                last_exc = exc

            if attempt < self.zai_max_attempts:
                delay = self._retry_delay_seconds(last_exc, attempt)
                log.warning(
                    "Z.ai GLM API error. Retrying in %.1fs... (Attempt %d/%d)",
                    delay, attempt + 1, self.zai_max_attempts,
                )
                print(
                    f"Z.ai GLM API error. Retrying in {delay:.1f}s... "
                    f"(Attempt {attempt + 1}/{self.zai_max_attempts})"
                )
                time.sleep(delay)

        raise GLMClientError(
            "Z.ai GLM API call failed after configured retry attempts: "
            f"{self._summarize_exception(last_exc)}"
        ) from last_exc

    def _post_claude_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = f"{self.claude_base_url.rstrip('/')}/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.claude_api_key,
            "anthropic-version": os.getenv("CLAUDE_SONNET_API_VERSION", "2023-06-01"),
        }
        with httpx.Client(timeout=self.claude_timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _post_generate_content(self, payload: dict[str, Any], model_name: str, api_key: str) -> dict[str, Any]:
        endpoint = f"{self.base_url.rstrip('/')}/models/{model_name}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _post_openrouter_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = self._openrouter_chat_completions_url()
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        if self.openrouter_referer:
            headers["HTTP-Referer"] = self.openrouter_referer
        if self.openrouter_title:
            headers["X-Title"] = self.openrouter_title
        with httpx.Client(timeout=self.openrouter_timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _openrouter_chat_completions_url(self) -> str:
        base_url = self.openrouter_base_url.rstrip("/")
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    def _post_zai_chat_completion(self, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = self._zai_chat_completions_url()
        headers = {
            "Authorization": f"Bearer {self.zai_api_key}",
            "Content-Type": "application/json",
        }
        with httpx.Client(timeout=self.zai_timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()

    def _zai_chat_completions_url(self) -> str:
        base_url = self.zai_base_url.rstrip("/")
        if base_url.endswith("/chat/completions"):
            return base_url
        return f"{base_url}/chat/completions"

    def _retry_delay_seconds(self, exc: Exception | None, attempt: int) -> float:
        hinted_delay = _retry_after_seconds(exc)
        if hinted_delay is None:
            hinted_delay = _BASE_DELAY_S * (2 ** (attempt - 1)) + random.uniform(-_JITTER_S, _JITTER_S)
        return min(self.max_retry_delay_seconds, max(0.1, hinted_delay))

    @staticmethod
    def _extract_text_content(response_payload: dict[str, Any]) -> str:
        try:
            candidates = response_payload["candidates"]
            candidate = candidates[0]
            parts = candidate["content"]["parts"]
        except (KeyError, IndexError, TypeError) as exc:
            prompt_feedback = response_payload.get("promptFeedback")
            raise GLMClientError(
                f"Unexpected Gemini response shape: prompt_feedback={prompt_feedback!r}"
            ) from exc

        text = "".join(str(part.get("text", "")) for part in parts if isinstance(part, dict))
        if text.strip():
            return text

        finish_reason = candidate.get("finishReason")
        raise GLMClientError(f"Gemini response contained no text. finish_reason={finish_reason!r}")

    @staticmethod
    def _extract_claude_text_content(response_payload: dict[str, Any]) -> str:
        try:
            parts = response_payload["content"]
        except (KeyError, TypeError) as exc:
            raise GLMClientError(
                f"Unexpected Claude Sonnet response shape: {response_payload!r}"
            ) from exc

        text = "".join(
            str(part.get("text", ""))
            for part in parts
            if isinstance(part, dict) and part.get("type") == "text"
        )
        if text.strip():
            return text

        stop_reason = response_payload.get("stop_reason")
        raise GLMClientError(f"Claude Sonnet response contained no text. stop_reason={stop_reason!r}")

    @staticmethod
    def _extract_chat_completion_content(response_payload: dict[str, Any], provider: str) -> str:
        try:
            content = response_payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GLMClientError(
                f"Unexpected {provider} response shape: {response_payload!r}"
            ) from exc
        if isinstance(content, list):
            content = "".join(
                str(part.get("text", "")) if isinstance(part, dict) else str(part)
                for part in content
            )
        if not str(content).strip():
            raise GLMClientError(f"{provider} response contained no text.")
        return str(content)

    @staticmethod
    def _summarize_http_error(exc: httpx.HTTPStatusError) -> str:
        try:
            body = exc.response.json()
        except ValueError:
            body = exc.response.text[:500]
        return f"HTTP {exc.response.status_code}: {body}"

    @staticmethod
    def _summarize_exception(exc: Exception | None) -> str:
        if isinstance(exc, httpx.HTTPStatusError):
            return GLMClient._summarize_http_error(exc)
        return str(exc)[:500] if exc else "unknown error"

    @staticmethod
    def _format_provider_errors(provider_errors: list[tuple[str, Exception]]) -> str:
        return "; ".join(
            f"{provider}: {GLMClient._summarize_exception(exc)}"
            for provider, exc in provider_errors
        )

    def _provider_chain_error(
        self,
        provider_errors: list[tuple[str, Exception]],
    ) -> GLMClientError:
        return GLMClientError(
            "All configured AI providers failed. "
            f"{self._format_provider_errors(provider_errors)}"
        )

    @staticmethod
    def _parse_json_content(content: str, provider: str = "model") -> dict[str, Any]:
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
                    f"Could not parse JSON from {provider} response: {content[:500]}"
                ) from exc

        raise GLMClientError(
            f"{provider} response contained no parseable JSON object: {content[:500]}"
        )


async def _ping() -> None:
    client = GLMClient()
    result = await client.generate_json(
        system_prompt="You are a connection-test assistant for Grantly.",
        user_prompt=(
            'Return a JSON object with a single key "greeting" whose value is '
            'a short friendly hello message.'
        ),
    )
    print("AI provider ping OK ->", result)


if __name__ == "__main__":
    asyncio.run(_ping())
