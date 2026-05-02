"""Per-provider API key ping test for Grantly.

Tests each configured provider individually, then runs the full fallback
chain to confirm end-to-end JSON generation works.
"""

from __future__ import annotations

import sys
import time

try:
    from .glm_client import GLMClient, GLMClientError
except ImportError:
    from glm_client import GLMClient, GLMClientError


def mask(value: str | None) -> str:
    if not value or len(value) < 10:
        return "<missing>"
    return f"{value[:6]}...{value[-4:]}"


def _ping_provider(label: str, call):
    """Run a single synchronous provider call and report pass/fail."""
    start = time.time()
    try:
        result = call()
        elapsed = time.time() - start
        print(f"  [{label}] PASS ({elapsed:.1f}s) -> {result}")
        return True
    except Exception as exc:
        elapsed = time.time() - start
        short = str(exc)[:200]
        print(f"  [{label}] FAIL ({elapsed:.1f}s) -> {short}")
        return False


def _build_gemini_payload(system_prompt: str, user_prompt: str, max_output_tokens: int) -> dict:
    hardened = (
        system_prompt
        + "\n\nYou MUST respond with a single valid JSON object and nothing else. "
        "Do not wrap the JSON in Markdown code fences or add commentary."
    )
    return {
        "systemInstruction": {"parts": [{"text": hardened}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": 0.0,
            "responseMimeType": "application/json",
            "maxOutputTokens": max_output_tokens,
        },
    }


def _ping_gemini_key_slot(client: GLMClient, slot_index: int, payload: dict) -> bool:
    if slot_index >= len(client.api_keys):
        print(f"  [Gemini Key Slot {slot_index + 1}] SKIP (not configured)")
        return False
    api_key = client.api_keys[slot_index]
    model_name = client.models[0] if client.models else None
    if not model_name:
        print(f"  [Gemini Key Slot {slot_index + 1}] SKIP (no Gemini model configured)")
        return False

    def _call():
        response_payload = client._post_generate_content(payload, model_name, api_key)
        content = client._extract_text_content(response_payload)
        return client._parse_json_content(content, provider=f"Gemini key slot {slot_index + 1}")

    return _ping_provider(f"Gemini Key Slot {slot_index + 1}", _call)


def main() -> None:
    client = GLMClient()

    claude_key = client.claude_api_key
    openrouter_key = client.openrouter_api_key
    gemini_key = client.api_key
    zai_key = client.zai_api_key

    print("=" * 60)
    print("Grantly API Key Ping Test")
    print("=" * 60)
    print(f"  CLAUDE_SONNET_API_KEY : {mask(claude_key)}")
    print(f"  OPENROUTER_API_KEY   : {mask(openrouter_key)}")
    print(f"  GOOGLE_API_KEY       : {mask(gemini_key)}")
    print(f"  GEMINI_FALLBACK_KEYS : {max(0, len(client.api_keys) - 1)} configured")
    print(f"  ZAI_API_KEY          : {mask(zai_key)}")
    print()

    system_prompt = "You are a connection test assistant."
    user_prompt = 'Return JSON only: {"pong": true}'
    gemini_payload = _build_gemini_payload(system_prompt, user_prompt, client.max_output_tokens)
    hardened = gemini_payload["systemInstruction"]["parts"][0]["text"]
    messages = [
        {"role": "system", "content": hardened},
        {"role": "user", "content": user_prompt},
    ]

    results: dict[str, bool] = {}

    print("[1/4] Claude Sonnet")
    if claude_key and client.claude_enabled:
        results["Claude"] = _ping_provider("Claude", lambda: client._generate_json_via_claude(
            system_prompt=hardened, user_prompt=user_prompt, temperature=0.0,
        ))
    else:
        print("  [Claude] SKIP (no key or disabled)")
        results["Claude"] = False

    print("[2/4] OpenRouter Gemini")
    if client.openrouter_models:
        results["OpenRouter"] = _ping_provider("OpenRouter", lambda: client._generate_json_via_openrouter(
            messages=messages, temperature=0.0,
        ))
    else:
        print("  [OpenRouter] SKIP (no key)")
        results["OpenRouter"] = False

    print("[3/4] Direct Gemini")
    if client.models:
        results["Gemini"] = _ping_provider("Gemini", lambda: client._generate_json_via_gemini(gemini_payload))
    else:
        print("  [Gemini] SKIP (no key)")
        results["Gemini"] = False

    print("[4/4] Z.ai GLM")
    if zai_key:
        results["Z.ai"] = _ping_provider("Z.ai", lambda: client._generate_json_via_zai(
            messages=messages, temperature=0.0,
        ))
    else:
        print("  [Z.ai] SKIP (no key)")
        results["Z.ai"] = False

    print()
    print("-" * 60)
    print("Individual Results:")
    for provider, ok in results.items():
        status = "PASS" if ok else "FAIL"
        print(f"  {provider:.<20s} {status}")

    live_count = sum(1 for ok in results.values() if ok)
    print(f"\n  {live_count}/{len(results)} providers alive.")

    print()
    print("-" * 60)
    print("Gemini Key Rotation Check:")
    slot_1_ok = _ping_gemini_key_slot(client, 0, gemini_payload)
    slot_2_ok = _ping_gemini_key_slot(client, 1, gemini_payload)
    print("\nGemini key rotation summary:")
    print(f"  Primary key (slot 1):   {'PASS' if slot_1_ok else 'FAIL'}")
    if len(client.api_keys) >= 2:
        print(f"  Secondary key (slot 2): {'PASS' if slot_2_ok else 'FAIL'}")
    else:
        print("  Secondary key (slot 2): SKIP (not configured)")

    print()
    print("=" * 60)
    print("Full Fallback Chain Test")
    print("=" * 60)
    try:
        start = time.time()
        result = client.generate_json_sync(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.0,
        )
        elapsed = time.time() - start
        print(f"  PASS ({elapsed:.1f}s) -> {result}")
    except GLMClientError as exc:
        elapsed = time.time() - start
        print(f"  FAIL ({elapsed:.1f}s) -> {str(exc)[:300]}")
        print("\n  All providers failed. Check your .env keys.")
        sys.exit(1)

    print("\n  Fallback chain is healthy. At least one provider responded.")


if __name__ == "__main__":
    main()
