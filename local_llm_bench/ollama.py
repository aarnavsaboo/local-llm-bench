from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any
from urllib.request import Request, urlopen
import json


@dataclass
class RunResult:
    model: str
    prompt_chars: int
    output_chars: int
    prompt_tokens: int | None
    output_tokens: int | None
    total_seconds: float
    ttft_seconds: float | None
    decode_tokens_per_second: float | None
    load_seconds: float | None
    backend: str = "ollama"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _ns_to_seconds(value: Any) -> float | None:
    return None if value is None else float(value) / 1_000_000_000.0


def run_ollama(
    model: str,
    prompt: str,
    *,
    endpoint: str = "http://127.0.0.1:11434",
    options: dict[str, Any] | None = None,
    timeout: float = 600.0,
) -> RunResult:
    body = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": options or {},
    }).encode()
    request = Request(
        endpoint.rstrip("/") + "/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = perf_counter()
    first_token_at: float | None = None
    final: dict[str, Any] = {}
    pieces: list[str] = []

    with urlopen(request, timeout=timeout) as response:
        for raw in response:
            if not raw.strip():
                continue
            event = json.loads(raw)
            text = event.get("response", "")
            if text:
                if first_token_at is None:
                    first_token_at = perf_counter()
                pieces.append(text)
            if event.get("done"):
                final = event

    finished = perf_counter()
    eval_count = final.get("eval_count")
    eval_duration = final.get("eval_duration")
    decode_rate = None
    if eval_count and eval_duration:
        decode_rate = float(eval_count) / (float(eval_duration) / 1_000_000_000.0)

    return RunResult(
        model=model,
        prompt_chars=len(prompt),
        output_chars=len("".join(pieces)),
        prompt_tokens=final.get("prompt_eval_count"),
        output_tokens=eval_count,
        total_seconds=finished - started,
        ttft_seconds=None if first_token_at is None else first_token_at - started,
        decode_tokens_per_second=decode_rate,
        load_seconds=_ns_to_seconds(final.get("load_duration")),
    )
