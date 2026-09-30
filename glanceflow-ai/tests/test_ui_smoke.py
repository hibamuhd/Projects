"""Headless end-to-end UI journey using Streamlit's AppTest (no browser)."""
import pytest

pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest  # noqa: E402

from src.config import ROOT  # noqa: E402


@pytest.fixture()
def at(tmp_path, monkeypatch):
    monkeypatch.setenv("GLANCEFLOW_DB_PATH", str(tmp_path / "ui.db"))
    monkeypatch.setenv("GLANCEFLOW_LLM_PROVIDER", "none")
    import streamlit as st
    st.cache_resource.clear()
    t = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
    t.run()
    assert not t.exception
    return t


def _btn(t, label):
    return next(b for b in t.button if b.label == label)


def test_discover_to_results_save_and_shortlist(at):
    at.text_area(key="query_text").set_value("Coffee lover gift between ₹500 and ₹900").run()
    _btn(at, "Find options").click().run()
    assert not at.exception and at.session_state.page == "Results"
    assert at.session_state.last.status == "ok"
    saves = [b for b in at.button if b.label == "Save"]
    assert len(saves) >= 3
    saves[0].click().run()
    assert not at.exception
    at.sidebar.radio[0].set_value("Shortlist").run()
    assert not at.exception and any("gf-title" in m.value for m in at.markdown)
    at.sidebar.radio[0].set_value("Agent activity").run()
    assert not at.exception and at.dataframe
    at.sidebar.radio[0].set_value("Analytics").run()
    assert not at.exception and at.metric


def test_every_page_renders_with_empty_state(at):
    for page in ["Results", "Shortlist", "Agent activity", "Analytics", "Settings"]:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, page


def test_unsupported_and_clarification_states(at):
    at.text_area(key="query_text").set_value("something nice").run()
    _btn(at, "Find options").click().run()
    assert at.session_state.last.status == "needs_clarification" and at.warning
    at.sidebar.radio[0].set_value("Discover").run()
    at.text_area(key="query_text").set_value("Buy this for me now").run()
    _btn(at, "Find options").click().run()
    assert at.session_state.last.status == "unsupported" and not at.exception
