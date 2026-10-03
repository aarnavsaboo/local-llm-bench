from __future__ import annotations

from time import perf_counter
from typing import Any
from urllib.request import Request, urlopen
import json

from .base import BackendResult


class OllamaBackend:
    def __init__(self, endpoint: str = "http://127.0.0.1:11434", timeout: float = 600):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout

    def generate(self, model: str, prompt: str, options: dict[str, Any]) -> BackendResult:
        request = Request(
            self.endpoint + "/api/generate",
            data=json.dumps({"model": model, "prompt": prompt, "stream": True, "options": options}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        started = perf_counter()
        first: float | None = None
        chunks: list[str] = []
        final: dict[str, Any] = {}
        with urlopen(request, timeout=self.timeout) as response:
            for raw in response:
                if not raw.strip():
                    continue
                event = json.loads(raw)
                piece = event.get("response", "")
                if piece:
                    if first is None:
                        first = perf_counter()
                    chunks.append(piece)
                if event.get("done"):
                    final = event
        elapsed = perf_counter() - started
        eval_count = final.get("eval_count")
        eval_duration = final.get("eval_duration")
        tps = None
        if eval_count and eval_duration:
            tps = float(eval_count) / (float(eval_duration) / 1e9)
        return BackendResult(
            text="".join(chunks),
            elapsed_seconds=elapsed,
            ttft_seconds=None if first is None else first - started,
            prompt_tokens=final.get("prompt_eval_count"),
            output_tokens=eval_count,
            decode_tps=tps,
            load_seconds=None if final.get("load_duration") is None else final["load_duration"] / 1e9,
            metadata={"total_duration_ns": final.get("total_duration"), "done_reason": final.get("done_reason")},
        )
