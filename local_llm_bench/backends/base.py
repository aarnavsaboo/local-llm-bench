from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class BackendResult:
    text: str
    elapsed_seconds: float
    ttft_seconds: float | None = None
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    decode_tps: float | None = None
    load_seconds: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class Backend(Protocol):
    def generate(self, model: str, prompt: str, options: dict[str, Any]) -> BackendResult: ...
