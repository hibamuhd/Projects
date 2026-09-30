import pytest

from src.llm import LLMResponse
from src.orchestration.state import InvalidTransition, Stage, StepLimitExceeded, WorkflowState
from src.orchestration.workflow import DiscoveryWorkflow
from src.schemas import VerificationReport, WorkflowRequest
from src.storage.repositories import EventRepo
from tests.helpers import FakeLLM

Q1 = "Find a thoughtful gift under ₹1,500 for a friend who loves reading, prefers practical things, and dislikes generic gifts"


def req(q, **kw):
    return WorkflowRequest(query=q, session_id="s1", **kw)


def test_end_to_end_clear_request(wf):  # scenario 1
    r = wf.run(req(Q1))
    assert r.status == "ok" and 3 <= len(r.recommendations) <= 5
    assert all(x.item.price_inr <= 1500 and x.item.availability != "out_of_stock" for x in r.recommendations)
    assert [t.stage for t in r.trace][:2] == ["intent", "discover"] and r.trace[-1].stage == "explain"
    assert r.verification.passed and r.latency_ms > 0
    assert all(x.explanation.startswith("Why it fits") and x.checks["verified_against_catalogue"] for x in r.recommendations)


def test_no_budget_request_still_works(wf):  # scenario 2
    r = wf.run(req("Unique gift for a friend who loves reading"))
    assert r.status == "ok" and any("No budget" in a for a in r.intent.assumptions)


def test_clarification_path_stops_before_discovery(wf):
    r = wf.run(req("something nice"))
    assert r.status == "needs_clarification" and not r.recommendations
    assert [t.stage for t in r.trace] == ["intent"]


def test_no_matching_items(wf):  # scenario 4
    r = wf.run(req("Gift for someone who loves scuba diving under ₹100"))
    assert r.status == "no_results" and "Nothing in the catalogue" in r.message and not r.recommendations


def test_unsupported_purchase_request(wf):  # scenario 15
    r = wf.run(req("Buy this for me now"))
    assert r.status == "unsupported" and "can't buy" in r.message


def test_purchase_words_with_real_need_still_search_but_never_purchase(wf):
    r = wf.run(req("Buy it for me now: a gift for my friend who loves coffee under ₹1000"))
    assert r.status == "ok" and r.intent.unsupported_action == "purchase"


def test_refinement_merges_and_lowers_budget(wf):
    first = wf.run(req(Q1))
    second = wf.run(WorkflowRequest(session_id="s1", refine_text="make it cheaper", previous_constraints=first.constraints,
                                    previous_max_price=max(x.item.price_inr for x in first.recommendations)))
    assert second.constraints.budget_max == 1125
    assert all(x.item.price_inr <= 1125 for x in second.recommendations)


def test_events_are_persisted(wf, db):
    wf.run(req(Q1))
    types = [e["event_type"] for e in EventRepo(db).all()]
    for t in ("query_submitted", "results_generated", "recommendation_viewed"):
        assert t in types


def test_state_machine_rejects_illegal_transition():
    with pytest.raises(InvalidTransition):
        WorkflowState().go(Stage.VERIFY)


def test_state_machine_step_limit():
    st = WorkflowState(max_steps=3)
    st.go(Stage.DISCOVER); st.go(Stage.REVISE); st.go(Stage.DISCOVER)
    with pytest.raises(StepLimitExceeded):
        st.go(Stage.REVISE)


def test_revision_is_bounded(wf, monkeypatch):  # scenario 11 (loop guard)
    real = wf.critic.run

    def always_revise(ranked, c, audit_only=False):
        kept, rep = real(ranked, c, audit_only)
        return kept, rep.model_copy(update={"needs_revision": True, "passed": False})
    monkeypatch.setattr(wf.critic, "run", always_revise)
    r = wf.run(req(Q1))
    assert r.revisions == 1 and r.status in ("fallback", "ok", "no_results")
    assert sum(1 for t in r.trace if t.stage == "revise") == 1


def test_control_arm_audits_but_does_not_filter(wf):
    r = wf.run(req("gift for a coffee lover, budget ₹300", retrieval_arm="control"))
    assert r.verification.audit_only and r.pre_verification_violations > 0
    assert any(x.item.price_inr > 300 for x in r.recommendations)   # baseline is not protected


def test_treatment_arm_has_zero_violations_on_same_query(wf):
    r = wf.run(req("gift for a coffee lover, budget ₹300"))
    assert r.pre_verification_violations == 0 and all(x.item.price_inr <= 300 for x in r.recommendations)


def test_llm_explanation_used_only_when_grounded(settings, catalogue, db):
    def fn(system, user):
        return "A lovely pick that fits the request."
    wf = DiscoveryWorkflow(settings, catalogue, db, llm=FakeLLM(lambda s, u: fn(s, u) if "one friendly sentence" in s.lower() or "ONE friendly" in s else "{}"))
    r = wf.run(req(Q1, use_llm=True))
    assert r.status == "ok" and r.llm_used and any("lovely pick" in x.explanation for x in r.recommendations)


def test_llm_hallucinated_price_falls_back_to_template(settings, catalogue, db):
    llm = FakeLLM(lambda s, u: "Now only ₹1, half price!" if "ONE friendly" in s else "{}")
    r = DiscoveryWorkflow(settings, catalogue, db, llm=llm).run(req(Q1, use_llm=True))
    assert r.status == "ok" and all("half price" not in x.explanation for x in r.recommendations)


def test_cost_is_none_without_pricing_and_computed_with_pricing(settings, catalogue, db):
    from dataclasses import replace
    llm = FakeLLM(lambda s, u: LLMResponse("{}", 1000, 500))
    r = DiscoveryWorkflow(settings, catalogue, db, llm=llm).run(req(Q1, use_llm=True))
    assert r.est_cost_usd is None and r.input_tokens > 0
    priced = replace(settings, price_in_per_mtok=1.0, price_out_per_mtok=5.0)
    r2 = DiscoveryWorkflow(priced, catalogue, db, llm=llm).run(req(Q1, use_llm=True))
    assert r2.est_cost_usd and r2.est_cost_usd > 0
