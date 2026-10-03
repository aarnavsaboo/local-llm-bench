# Methodology

The runner stores raw observations first and computes summaries later.

For streamed Ollama requests, TTFT is measured from the client immediately before the HTTP request until the first non-empty response fragment arrives. Decode throughput prefers the runtime-reported evaluation duration because wall-clock time also includes queueing, prompt evaluation and transport overhead.

Useful comparisons hold the prompt, sampling settings and output budget constant. Cold-start and warm-start measurements should be kept separate. A five-run median is often more informative than a single best run, while p90 and coefficient of variation expose unstable configurations.

The benchmark deliberately keeps hardware metadata outside the scoring code. A result without its model tag, quantization, runtime version and machine description is not very portable.
