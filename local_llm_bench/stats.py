from __future__ import annotations

from math import sqrt
from statistics import mean, median
from typing import Iterable


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    if not 0 <= q <= 1:
        raise ValueError("q must be between 0 and 1")
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    lo = int(position)
    hi = min(lo + 1, len(ordered) - 1)
    weight = position - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


def summarize(records: Iterable[dict]) -> dict:
    rows = list(records)
    if not rows:
        raise ValueError("no records")
    latency = [float(x["total_seconds"]) for x in rows]
    decode = [
        float(x["decode_tokens_per_second"])
        for x in rows
        if x.get("decode_tokens_per_second") is not None
    ]
    avg = mean(latency)
    variance = mean([(x - avg) ** 2 for x in latency])
    return {
        "runs": len(rows),
        "latency_median_s": median(latency),
        "latency_p90_s": percentile(latency, 0.90),
        "latency_cv": 0.0 if avg == 0 else sqrt(variance) / avg,
        "decode_tps_median": None if not decode else median(decode),
    }
