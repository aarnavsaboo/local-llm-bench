from __future__ import annotations

from collections import defaultdict
from statistics import median

from .stats import percentile


def grouped(rows: list[dict]) -> list[dict]:
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        if row.get("ok"):
            buckets[(row["workload"], row["model"], row["concurrency"])].append(row)
    out = []
    for (workload, model, concurrency), group in sorted(buckets.items()):
        latency = [float(x["elapsed_seconds"]) for x in group]
        tps = [float(x["decode_tps"]) for x in group if x.get("decode_tps") is not None]
        ttft = [float(x["ttft_seconds"]) for x in group if x.get("ttft_seconds") is not None]
        out.append({
            "workload": workload,
            "model": model,
            "concurrency": concurrency,
            "runs": len(group),
            "latency_median_s": median(latency),
            "latency_p90_s": percentile(latency, .90),
            "ttft_median_s": None if not ttft else median(ttft),
            "decode_tps_median": None if not tps else median(tps),
        })
    return out
