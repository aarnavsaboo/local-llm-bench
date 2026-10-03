from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from typing import Iterable
import json
import time

from .backends.base import Backend
from .planner import Job


def run_job(job: Job, backend: Backend) -> dict:
    prompt = Path(job.prompt_file).read_text(encoding="utf-8")
    started = time.time()
    try:
        result = backend.generate(job.model, prompt, job.generation)
        return {
            "job_id": job.id,
            "workload": job.workload,
            "model": job.model,
            "prompt_file": job.prompt_file,
            "prompt_chars": len(prompt),
            "run": job.run,
            "concurrency": job.concurrency,
            "started_at": started,
            "ok": True,
            **asdict(result),
        }
    except Exception as exc:
        return {
            "job_id": job.id, "workload": job.workload, "model": job.model,
            "prompt_file": job.prompt_file, "run": job.run,
            "concurrency": job.concurrency, "started_at": started,
            "ok": False, "error_type": type(exc).__name__, "error": str(exc),
        }


def execute(jobs: Iterable[Job], backend: Backend) -> list[dict]:
    rows = list(jobs)
    if not rows:
        return []
    workers = max(1, max(x.concurrency for x in rows))
    output: list[dict] = []
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_job, job, backend) for job in rows]
        for future in as_completed(futures):
            output.append(future.result())
    return output


def write_jsonl(path: str, rows: Iterable[dict]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
