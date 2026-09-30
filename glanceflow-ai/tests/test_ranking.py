from src.retrieval.index import BM25Retriever
from src.retrieval.ranking import score_candidates, select_diverse
from src.schemas import Constraints
from src.tools.catalogue_search import search_catalogue


def _rank(catalogue, c, profile=None):
    cands = search_catalogue(BM25Retriever(catalogue), catalogue, c).candidates
    return score_candidates(cands, c, profile)


def test_scores_are_sorted_and_explainable(catalogue):
    r = _rank(catalogue, Constraints(interests=["reading"], budget_max=1500, preferred_attributes=["practical"]))
    assert [x.score for x in r] == sorted((x.score for x in r), reverse=True)
    assert all(x.reasons and "relevance" in x.components for x in r)


def test_avoid_generic_penalises_generic_items(catalogue):
    c = Constraints(interests=["home"], avoid_generic=True)
    r = _rank(catalogue, c)
    top = r[:10]
    assert sum(1 for x in top if x.item.attributes.get("generic_gift")) <= sum(1 for x in r[-10:] if x.item.attributes.get("generic_gift"))


def test_no_personalization_without_evidence(catalogue):
    r = _rank(catalogue, Constraints(interests=["tea"]))
    assert all(x.components["personalization"] == 0 for x in r)


def test_saved_category_boosts_only_with_evidence(catalogue):
    from collections import Counter
    base = _rank(catalogue, Constraints(interests=["tea"]))
    cat = base[-1].item.category
    boosted = _rank(catalogue, Constraints(interests=["tea"]), {"saved_categories": Counter({cat: 2})})
    assert any(x.components["personalization"] > 0 for x in boosted)


def test_diversity_caps(catalogue):
    r = select_diverse(_rank(catalogue, Constraints(interests=["reading"])), 5)
    bases = [x.item.attributes["base_name"] for x in r]
    assert len(r) == 5 and len(set(bases)) == 5
