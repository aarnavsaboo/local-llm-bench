from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .backends import OllamaBackend, OpenAICompatibleBackend
from .executor import execute, write_jsonl
from .planner import Job, expand_manifest, load_manifest
from .report import grouped
from .stats import summarize


def _read_jsonl(path: str):
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield json.loads(line)


def _read_jobs(path: str) -> list[Job]:
    return [Job(**row) for row in _read_jsonl(path)]


def main() -> None:
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan")
    plan.add_argument("manifest")

    run = sub.add_parser("execute")
    run.add_argument("plan")
    run.add_argument("--backend", choices=["ollama","openai-compatible"], default="ollama")
    run.add_argument("--endpoint")
    run.add_argument("--out", required=True)

    report = sub.add_parser("report")
    report.add_argument("path")

    legacy = sub.add_parser("summarize")
    legacy.add_argument("path")

    args = parser.parse_args()

    if args.command == "plan":
        for job in expand_manifest(load_manifest(args.manifest)):
            print(json.dumps(job.to_dict(), sort_keys=True))
        return

    if args.command == "execute":
        if args.backend == "ollama":
            backend = OllamaBackend(args.endpoint or "http://127.0.0.1:11434")
        else:
            backend = OpenAICompatibleBackend(args.endpoint or "http://127.0.0.1:1234/v1/chat/completions")
        rows = execute(_read_jobs(args.plan), backend)
        write_jsonl(args.out, rows)
        print(json.dumps({"jobs":len(rows),"successful":sum(bool(x.get("ok")) for x in rows)}))
        return

    rows = list(_read_jsonl(args.path))
    if args.command == "report":
        print(json.dumps(grouped(rows), indent=2))
    else:
        # compatibility with early result files that use total_seconds
        print(json.dumps(summarize(rows), indent=2))


if __name__ == "__main__":
    main()
