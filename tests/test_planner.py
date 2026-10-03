import unittest
from local_llm_bench.planner import expand_manifest


class PlannerTests(unittest.TestCase):
    def test_expands_matrix(self):
        cfg = {
            "name":"x", "models":["a","b"], "prompts":["p"],
            "runs":2, "concurrency":[1,2], "generation":{"num_predict":10}
        }
        rows = expand_manifest(cfg)
        self.assertEqual(len(rows), 8)
        self.assertEqual(len({x.id for x in rows}), 8)


if __name__ == "__main__":
    unittest.main()
