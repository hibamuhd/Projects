"""GlanceFlow AI - Streamlit entry point. Run: streamlit run app.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st  # noqa: E402

from src.ui import agent_activity, analytics_dashboard, discovery, results, settings, shortlist  # noqa: E402
from src.ui.common import CSS, PAGES, get_app, init_session  # noqa: E402

st.set_page_config(page_title="GlanceFlow AI", page_icon="🧭", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

app = get_app()
init_session(app)
if "_goto" in st.session_state:
    st.session_state.page = st.session_state.pop("_goto")

st.sidebar.markdown("### GlanceFlow AI")
st.sidebar.caption("Independent prototype · synthetic data · not affiliated with Glance")
st.sidebar.radio("Navigate", PAGES, key="page", label_visibility="collapsed")

{"Discover": discovery, "Results": results, "Shortlist": shortlist, "Agent activity": agent_activity,
 "Analytics": analytics_dashboard, "Settings": settings}[st.session_state.page].render(app)
