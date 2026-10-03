from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha1
from itertools import product
from pathlib import Path
from typing import Any
import json


@dataclass(frozen=True)
class Job:
    id: str
    workload: str
    model: str
    prompt_file: str
    run: int
    concurrency: int
    generation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _id(payload: dict[str, Any]) -> str:
    return sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def expand_manifest(config: dict[str, Any]) -> list[Job]:
    name = str(config["name"])
    models = list(config["models"])
    prompts = list(config["prompts"])
    runs = int(config.get("runs", 3))
    concurrency = list(config.get("concurrency", [1]))
    generation = dict(config.get("generation", {}))
    jobs: list[Job] = []
    for model, prompt_file, run, workers in product(models, prompts, range(runs), concurrency):
        base = {
            "workload": name, "model": model, "prompt_file": prompt_file,
            "run": run, "concurrency": int(workers), "generation": generation,
        }
        jobs.append(Job(id=_id(base), **base))
    return jobs


def load_manifest(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
