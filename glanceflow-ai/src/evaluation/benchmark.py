"""Reproducible offline benchmark: keyword baseline vs keyword+filters vs full intent-aware workflow."""
from __future__ import annotations

import json
import statistics
import tempfile
import time
from pathlib import Path

from src.agents.intent_agent import parse_request
from src.config import Settings, load_settings
from src.evaluation.metrics import is_relevant, summarize, violates
from src.orchestration.workflow import DiscoveryWorkflow
from src.retrieval.index import BM25Retriever
from src.schemas import CatalogueItem, WorkflowRequest
from src.storage.database import Database
from src.tools.catalogue_search import hard_filter, keyword_baseline
from src.utils.text import tokenize


def _row(items: list[CatalogueItem], q: dict, latency_ms: float) -> dict:
    return {"id": q["id"], "n_returned": len(items), "relevant": sum(is_relevant(i, q) for i in items),
            "violations": sum(1 for i in items if violates(i, q)), "distinct_sub": len({i.subcategory for i in items}),
            "distinct_base": len({i.attributes.get("base_name", i.title) for i in items}), "latency_ms": latency_ms,
            "ids": [i.item_id for i in items]}


def run_benchmark(catalogue: list[CatalogueItem], queries: list[dict], settings: Settings | None = None) -> dict:
    settings = settings or load_settings()
    retr = BM25Retriever(catalogue)
    tmp = Path(tempfile.mkdtemp()) / "bench.db"
    db = Database(tmp); db.init()
    wf = DiscoveryWorkflow(settings, catalogue, db, llm=None, retriever=retr)
    by_id = {i.item_id: i for i in catalogue}
    answerable = [x for x in queries if x["kind"].startswith("answerable")]
    edge = [x for x in queries if not x["kind"].startswith("answerable")]
    systems: dict[str, list[dict]] = {"A_keyword_baseline": [], "B_keyword_plus_hard_filters": [], "C_intent_aware_ranked": []}
    for q in answerable:
        t = time.perf_counter()
        a = [c.item for c in keyword_baseline(retr, catalogue, q["query"], 5)]
        systems["A_keyword_baseline"].append(_row(a, q, (time.perf_counter() - t) * 1000))
        t = time.perf_counter()
        it = parse_request(q["query"])
        pool = {i.item_id for i in hard_filter(catalogue, it.constraints)}
        b = [by_id[i] for i, _ in retr.search(tokenize(q["query"]), pool, 5)]
        systems["B_keyword_plus_hard_filters"].append(_row(b, q, (time.perf_counter() - t) * 1000))
        r = wf.run(WorkflowRequest(query=q["query"], session_id=f"bench-{q['id']}"))
        systems["C_intent_aware_ranked"].append(_row([x.item for x in r.recommendations], q, r.latency_ms))
    summary = {k: summarize(v) for k, v in systems.items()}
    edge_rows = []
    for q in edge:
        r = wf.run(WorkflowRequest(query=q["query"], session_id=f"bench-{q['id']}"))
        edge_rows.append({"id": q["id"], "kind": q["kind"], "expected": q["expect_status"], "actual": r.status, "match": r.status == q["expect_status"]})
    # also confirm answerable queries return status ok/fallback
    return {"catalogue_size": len(catalogue), "n_answerable": len(answerable), "n_edge": len(edge), "systems": summary,
            "edge_cases": edge_rows, "edge_case_accuracy": round(sum(e["match"] for e in edge_rows) / len(edge_rows), 3) if edge_rows else None,
            "per_query": systems}


def save_results(result: dict, path: Path) -> None:
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
