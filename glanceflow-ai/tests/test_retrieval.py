from src.data.seed_catalogue import generate_records
from src.data.validation import validate_rows
from src.retrieval.index import BM25Retriever
from src.schemas import Constraints
from src.tools.catalogue_search import dedupe, hard_filter, search_catalogue


def test_catalogue_size_and_labels(catalogue):
    assert 200 <= len(catalogue) <= 500
    assert all(i.source == "synthetic" for i in catalogue)


def test_invalid_rows_are_quarantined_not_fixed():  # scenario 7
    items, rep = validate_rows(generate_records(7))
    reasons = " ".join(r["reason"] for r in rep.rejected)
    assert len(rep.rejected) == 5 and "missing price" in reasons
    assert not any(i.item_id in {"SYN-9002", "SYN-9003", "SYN-9004", "SYN-9005", "SYN-9007"} for i in items)


def test_injection_row_quarantined_at_ingestion():  # scenario 14
    items, rep = validate_rows(generate_records(7))
    assert rep.injection_quarantined == ["SYN-9006"] and all(i.item_id != "SYN-9006" for i in items)


def test_exact_duplicate_removed_at_ingestion():  # scenario 6
    _, rep = validate_rows(generate_records(7))
    assert rep.duplicates_removed == ["SYN-9001"]


def test_dedupe_tool(catalogue):
    a = catalogue[0]
    out, dropped = dedupe([a, a.model_copy(update={"item_id": "SYN-XXXX"}), catalogue[1]])
    assert len(out) == 2 and dropped == ["SYN-XXXX"]


def test_hard_filter_respects_budget_stock_exclusions(catalogue):
    c = Constraints(budget_max=500, exclusions=["candle"])
    out = hard_filter(catalogue, c)
    assert out and all(i.price_inr <= 500 and i.availability != "out_of_stock" for i in out)
    assert all("candle" not in i.title.lower() for i in out)


def test_search_returns_relevant_items(catalogue):
    r = BM25Retriever(catalogue)
    out = search_catalogue(r, catalogue, Constraints(interests=["coffee"], budget_max=1000))
    assert out.candidates and all("coffee" in i.item.tags for i in out.candidates[:5])


def test_excluded_ids_are_removed(catalogue):
    r = BM25Retriever(catalogue)
    first = search_catalogue(r, catalogue, Constraints(interests=["tea"])).candidates[0].item.item_id
    again = search_catalogue(r, catalogue, Constraints(interests=["tea"]), excluded_ids={first})
    assert first not in {c.item.item_id for c in again.candidates}
