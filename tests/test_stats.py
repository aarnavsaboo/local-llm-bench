import unittest

from local_llm_bench.stats import percentile, summarize


class StatsTests(unittest.TestCase):
    def test_percentile_interpolates(self):
        self.assertEqual(percentile([1.0, 2.0, 3.0], 0.5), 2.0)

    def test_summary(self):
        out = summarize([
            {"total_seconds": 1.0, "decode_tokens_per_second": 20.0},
            {"total_seconds": 3.0, "decode_tokens_per_second": 40.0},
        ])
        self.assertEqual(out["runs"], 2)
        self.assertEqual(out["latency_median_s"], 2.0)
        self.assertEqual(out["decode_tps_median"], 30.0)


if __name__ == "__main__":
    unittest.main()
