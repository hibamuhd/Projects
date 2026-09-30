import json

from src.agents.intent_agent import IntentAgent, extract_budget, parse_refinement, parse_request
from src.utils.cost_tracking import CostTracker
from tests.helpers import FakeLLM, slow_llm

Q1 = "Find a thoughtful gift under ₹1,500 for a friend who loves reading, prefers practical things, and dislikes generic gifts"


def test_clear_request_with_budget():  # scenario 1
    r = parse_request(Q1)
    c = r.constraints
    assert c.budget_max == 1500 and "reading" in c.interests and "practical" in c.preferred_attributes
    assert c.avoid_generic and c.recipient == "friend" and c.is_gift and not r.needs_clarification


def test_no_budget_is_assumption_not_clarification():  # scenario 2
    r = parse_request("Unique gift for a friend who loves reading")
    assert r.constraints.budget_max is None and not r.needs_clarification
    assert any("No budget" in a for a in r.assumptions)


def test_conflicting_budget_needs_clarification():  # scenario 3
    r = parse_request("Gift under ₹500 but at least ₹900 for a friend who loves tea")
    assert r.needs_clarification and r.conflicts
    assert "conflicting" in r.clarification_question


def test_cheap_and_premium_conflict():
    assert parse_request("cheap but premium gift for my friend").needs_clarification


def test_wanted_and_excluded_conflict():
    assert parse_request("gift for a bookworm, no books please").needs_clarification


def test_vague_request_asks_one_question():
    r = parse_request("something nice")
    assert r.needs_clarification and r.clarification_question.count("?") == 1


def test_budget_formats():
    assert extract_budget("under 1.5k")[1] == 1500
    assert extract_budget("between ₹500 and ₹900")[:2] == (500, 900)
    assert extract_budget("500-1000")[:2] == (500, 1000)
    assert extract_budget("for my 3 friends")[1] is None


def test_unsupported_purchase_detected():  # scenario 15
    assert parse_request("Buy this for me now").unsupported_action == "purchase"


def test_llm_invalid_output_falls_back_to_rules():  # scenario 10
    llm = FakeLLM(lambda s, u: "definitely not json")
    r = IntentAgent(llm, attempts=2, timeout_s=2).run(Q1, None, None, CostTracker())
    assert r.source == "rules_fallback" and r.constraints.budget_max == 1500 and llm.calls == 2


def test_llm_timeout_falls_back_to_rules():  # scenario 9
    r = IntentAgent(slow_llm(1.0), attempts=1, timeout_s=0.1).run(Q1, None, None, CostTracker())
    assert r.source == "rules_fallback"


def test_llm_cannot_invent_budget():
    llm = FakeLLM(lambda s, u: json.dumps({"budget_max": 99999, "interests": ["reading", "skydiving"]}))
    r = IntentAgent(llm, timeout_s=2).run("gift for a friend who loves reading", None, None, CostTracker())
    assert r.source == "llm" and r.constraints.budget_max is None
    assert "skydiving" not in r.constraints.interests   # not grounded in the request text


def test_mid_session_preference_change_replaces_interests():  # scenario 16
    prev = parse_request("gift for a friend who loves reading under ₹1500").constraints
    r = parse_refinement("actually she is into cooking now", prev, 1200)
    assert r.constraints.interests == ["cooking"] and r.constraints.budget_max == 1500


def test_refine_cheaper_lowers_budget():
    prev = parse_request("gift for a friend who loves reading under ₹1000").constraints
    assert parse_refinement("make it cheaper", prev, None).constraints.budget_max == 750
