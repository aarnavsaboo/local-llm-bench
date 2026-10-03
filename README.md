# local-llm-bench

Local inference benchmark and workload runner for language models served from a workstation.

The project started as a small latency harness and has grown into a config-driven runner for comparing local model/runtime combinations under repeatable workloads. It keeps raw request events, aggregate metrics and workload metadata separate so reports can be regenerated without rerunning inference.

The default adapters target Ollama and OpenAI-compatible local servers. The core runner does not depend on either backend.

## What is measured

- cold and warm latency
- time to first streamed token
- prompt-evaluation duration
- decode tokens/second
- request throughput under bounded concurrency
- latency percentiles and run-to-run variance
- model load time when reported by the runtime
- prompt/output token counts
- per-workload success rate
- estimated tokens processed per wall-clock minute

## Workload manifests

A workload is ordinary JSON:

```json
{
  "name": "document-summary",
  "models": ["qwen3:4b", "gemma3:4b"],
  "prompts": ["prompts/summary-short.txt", "prompts/summary-long.txt"],
  "runs": 5,
  "concurrency": [1, 2, 4],
  "generation": {"temperature": 0.0, "num_predict": 192}
}
```

Expand the matrix before running it:

```bash
python -m local_llm_bench plan configs/workload.example.json > runs/plan.jsonl
python -m local_llm_bench execute runs/plan.jsonl --backend ollama --out runs/raw.jsonl
python -m local_llm_bench report runs/raw.jsonl
```

The plan is explicit on purpose. A large matrix can be inspected, filtered or split across sessions before any model is loaded.

## Architecture

```text
workload.json
    |
    v
 matrix planner -----> job JSONL
                          |
                          v
                  bounded executor
                    /          \
              Ollama        OpenAI-style
                 |               |
                 +------ events -+
                          |
                          v
                    raw JSONL
                          |
                 +--------+--------+
                 |                 |
             summaries         comparisons
```

## Why keep raw events?

A single "tokens/sec" number hides too much. Model loading, prompt evaluation and generation can dominate at different prompt sizes. Every completed job stores the exact model name, backend, prompt size, output budget, attempt number and runtime-provided timing fields when available.

The reporting layer intentionally computes from raw JSONL rather than mutating it.

## Repository layout

- `local_llm_bench/backends/` — local runtime adapters
- `local_llm_bench/planner.py` — workload matrix expansion
- `local_llm_bench/executor.py` — bounded concurrent execution
- `local_llm_bench/stats.py` — percentiles and aggregate metrics
- `local_llm_bench/report.py` — grouped summaries
- `configs/` — example workload manifests
- `docs/` — methodology and experiment notes
- `tests/` — deterministic unit tests

No fixed benchmark ranking is committed. Local inference results depend heavily on model build, quantization, runtime version, prompt shape and machine state.

Maintained by **Aarnav Saboo**.
