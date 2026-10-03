# local-llm-bench

A small benchmark harness for comparing language models running locally.

The project focuses on measurements that are easy to lose when testing models by hand: model load time, time to first token, decode throughput, end-to-end latency, prompt length, generated tokens, and repeated-run variance. It is designed around local runtimes such as Ollama and llama.cpp rather than hosted APIs.

## What it measures

- cold and warm request latency
- time to first token when the backend exposes streaming events
- prompt and generation token counts
- decode tokens/second
- repeated-run median, p90 and coefficient of variation
- prompt-length sweeps
- model/runtime metadata stored beside every result

Raw runs are written as JSONL so the summaries can always be regenerated.

## Quick start

```bash
python -m local_llm_bench ollama \
  --model qwen3:4b \
  --prompt "Explain reciprocal-rank fusion in four sentences." \
  --runs 5 \
  --output runs/qwen3-4b.jsonl

python -m local_llm_bench summarize runs/qwen3-4b.jsonl
```

Nothing in the repository assumes that a larger model is better. The useful output is the curve between latency, memory, context length and task quality on the machine actually running the model.

## Layout

- `local_llm_bench/` — runtime adapters and measurements
- `configs/` — example benchmark matrices
- `tests/` — deterministic tests for timing/statistics code
- `docs/methodology.md` — measurement details and limitations

## Notes

Local inference numbers are hardware-, runtime-, quantization- and prompt-dependent. This repository intentionally does not ship made-up headline benchmark numbers; run the matrix locally and keep the raw records with the summary.

MIT License. Maintained by **Aarnav Saboo**.
