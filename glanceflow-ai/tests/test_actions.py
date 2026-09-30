import pytest

from src.agents.action_agent import ActionAgent
from src.storage.database import PersistenceError
from src.storage.repositories import EventRepo, ShortlistRepo
from src.tools.analytics import EventLogger

S = "sess-1"


@pytest.fixture()
def agent(db, catalogue):
    return ActionAgent(db, catalogue, EventLogger(db))


def show(db, *ids):
    for i in ids:
        EventRepo(db).add(S, "recommendation_viewed", i, {})


def act(agent, action, ids, **kw):
    return agent.execute_raw({"action": action, "session_id": S, "item_ids": ids, **kw})


def test_save_persists_and_is_confirmed(agent, db, catalogue):
    i = catalogue[0].item_id; show(db, i)
    r = act(agent, "save", [i], fit_reason="matches reading")
    assert r.success and r.status == "saved" and ShortlistRepo(db).contains(i)
    assert ShortlistRepo(db).all()[0]["fit_reason"] == "matches reading"


def test_repeated_save_is_idempotent(agent, db, catalogue):  # scenario 13
    i = catalogue[0].item_id; show(db, i)
    act(agent, "save", [i])
    again = act(agent, "save", [i])
    assert again.status == "already_saved" and len(ShortlistRepo(db).all()) == 1
    assert sum(1 for e in EventRepo(db).all() if e["event_type"] == "recommendation_saved") == 1


def test_cannot_act_on_unseen_item(agent, catalogue):
    r = act(agent, "save", [catalogue[0].item_id])
    assert not r.success and r.status == "not_permitted"


def test_hallucinated_item_id_rejected(agent):  # scenario 8
    r = act(agent, "save", ["SYN-NOPE"])
    assert not r.success and r.status == "unknown_item"


def test_remove_requires_confirmation(agent, db, catalogue):
    i = catalogue[0].item_id; show(db, i); act(agent, "save", [i])
    assert act(agent, "unsave", [i]).status == "confirmation_required" and ShortlistRepo(db).contains(i)
    r = act(agent, "unsave", [i], confirm=True)
    assert r.status == "removed" and not ShortlistRepo(db).contains(i)


def test_purchase_action_is_unsupported(agent, catalogue):  # scenario 15
    r = act(agent, "purchase", [catalogue[0].item_id])
    assert not r.success and r.status == "unsupported_action"


def test_invalid_payload_rejected(agent):
    assert agent.execute_raw({"action": "save"}).status == "invalid_request"
    assert agent.execute_raw({"action": "save", "session_id": S, "item_ids": []}).status == "invalid_request"


def test_compare_needs_two_to_four_items(agent, db, catalogue):
    a, b = catalogue[0].item_id, catalogue[1].item_id; show(db, a, b)
    assert act(agent, "compare", [a]).status == "invalid_request"
    r = act(agent, "compare", [a, b])
    assert r.success and len(r.data["table"]) == 2 and "Price (₹)" in r.data["table"][0]


def test_dismiss_and_feedback(agent, db, catalogue):
    i = catalogue[2].item_id; show(db, i)
    assert act(agent, "dismiss", [i]).status == "dismissed" and act(agent, "dismiss", [i]).status == "already_dismissed"
    assert act(agent, "feedback", [i], reason="irrelevant").success
    assert act(agent, "feedback", [i]).status == "invalid_request"


def test_failed_persistence_never_reports_success(agent, db, catalogue, monkeypatch):  # scenario 12
    i = catalogue[0].item_id; show(db, i)

    def boom():
        raise PersistenceError("disk full")
    monkeypatch.setattr(db, "connect", boom)
    r = act(agent, "save", [i])
    assert not r.success and r.status == "persistence_failed"
