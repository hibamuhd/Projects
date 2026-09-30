"""Run the offline benchmark and write results to docs/evaluation_results.json"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import ROOT, load_settings  # noqa: E402
from src.data.validation import load_catalogue  # noqa: E402
from src.evaluation.benchmark import run_benchmark, save_results  # noqa: E402

if __name__ == "__main__":
    s = load_settings(llm_provider="none", llm_api_key=None)   # benchmark is always LLM-free and reproducible
    items, rep = load_catalogue(s.catalogue_path)
    queries = json.loads(s.eval_queries_path.read_text(encoding="utf-8"))
    res = run_benchmark(items, queries, s)
    save_results(res, ROOT / "docs" / "evaluation_results.json")
    print(f"catalogue={res['catalogue_size']} answerable={res['n_answerable']} edge={res['n_edge']}")
    cols = ["precision_at_5", "precision_of_returned", "hit_rate_at_5", "constraint_violation_rate", "queries_with_any_violation",
            "avg_returned", "avg_distinct_subcategories", "avg_distinct_base_products", "zero_result_rate", "median_latency_ms"]
    print(f"{'metric':32s}" + "".join(f"{k[:14]:>16s}" for k in res["systems"]))
    for c in cols:
        print(f"{c:32s}" + "".join(f"{str(v[c]):>16s}" for v in res["systems"].values()))
    print("edge-case handling accuracy:", res["edge_case_accuracy"])
    for e in res["edge_cases"]:
        print("  ", e)
