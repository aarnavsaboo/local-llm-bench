from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
import json

from .ollama import run_ollama
from .stats import summarize


def _read_jsonl(path: str):
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def main() -> None:
    parser = ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("ollama")
    run.add_argument("--model", required=True)
    run.add_argument("--prompt", required=True)
    run.add_argument("--runs", type=int, default=3)
    run.add_argument("--output", required=True)
    run.add_argument("--endpoint", default="http://127.0.0.1:11434")
    run.add_argument("--num-predict", type=int, default=128)

    report = sub.add_parser("summarize")
    report.add_argument("path")

    args = parser.parse_args()
    if args.command == "ollama":
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("a", encoding="utf-8") as handle:
            for _ in range(args.runs):
                row = run_ollama(
                    args.model,
                    args.prompt,
                    endpoint=args.endpoint,
                    options={"num_predict": args.num_predict},
                ).to_dict()
                handle.write(json.dumps(row, sort_keys=True) + "\n")
                print(json.dumps(row, indent=2))
    else:
        print(json.dumps(summarize(_read_jsonl(args.path)), indent=2))


if __name__ == "__main__":
    main()
