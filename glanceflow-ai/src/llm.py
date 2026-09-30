"""Provider-independent LLM interface. The app never requires it: every LLM step has a deterministic fallback."""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class LLMClient(Protocol):
    name: str
    def complete(self, system: str, user: str, max_tokens: int = 400) -> LLMResponse: ...


class AnthropicClient:
    """Minimal Anthropic Messages API client using only the standard library.
    NOTE: not exercised against the live API in this repo's test run (no key available); see docs/LIMITATIONS.md."""
    name = "anthropic"

    def __init__(self, api_key: str, model: str, timeout_s: float = 8.0):
        self.api_key, self.model, self.timeout_s = api_key, model, timeout_s

    def complete(self, system: str, user: str, max_tokens: int = 400) -> LLMResponse:
        body = json.dumps({"model": self.model, "max_tokens": max_tokens, "system": system,
                           "messages": [{"role": "user", "content": user}]}).encode()
        req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body, method="POST", headers={
            "content-type": "application/json", "x-api-key": self.api_key, "anthropic-version": "2023-06-01"})
        with urllib.request.urlopen(req, timeout=self.timeout_s) as r:
            data = json.loads(r.read())
        text = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        u = data.get("usage", {})
        return LLMResponse(text, u.get("input_tokens", 0), u.get("output_tokens", 0))


def build_llm(settings) -> LLMClient | None:
    if settings.llm_provider == "anthropic" and settings.llm_api_key:
        return AnthropicClient(settings.llm_api_key, settings.llm_model, settings.llm_timeout_s)
    return None
