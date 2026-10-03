from __future__ import annotations

from time import perf_counter
from typing import Any
from urllib.request import Request, urlopen
import json

from .base import BackendResult


class OpenAICompatibleBackend:
    def __init__(self, endpoint: str = "http://127.0.0.1:1234/v1/chat/completions", timeout: float = 600):
        self.endpoint = endpoint
        self.timeout = timeout

    def generate(self, model: str, prompt: str, options: dict[str, Any]) -> BackendResult:
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            **options,
        }
        request = Request(
            self.endpoint,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = perf_counter()
        with urlopen(request, timeout=self.timeout) as response:
            payload = json.load(response)
        elapsed = perf_counter() - started
        choice = payload.get("choices", [{}])[0]
        usage = payload.get("usage", {})
        return BackendResult(
            text=choice.get("message", {}).get("content", ""),
            elapsed_seconds=elapsed,
            prompt_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            metadata={"finish_reason": choice.get("finish_reason")},
        )
