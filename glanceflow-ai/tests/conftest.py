import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import ROOT, load_settings  # noqa: E402
from src.data.seed_catalogue import generate_records  # noqa: E402
from src.data.validation import validate_rows  # noqa: E402
from src.orchestration.workflow import DiscoveryWorkflow  # noqa: E402
from src.storage.database import Database  # noqa: E402


@pytest.fixture(scope="session")
def catalogue():
    items, _ = validate_rows(generate_records(seed=7))
    return items


@pytest.fixture()
def db(tmp_path):
    d = Database(tmp_path / "t.db")
    d.init()
    return d


@pytest.fixture()
def settings(tmp_path):
    return load_settings(db_path=tmp_path / "t.db", llm_provider="none", llm_api_key=None)


@pytest.fixture()
def wf(settings, catalogue, db):
    return DiscoveryWorkflow(settings, catalogue, db, llm=None)
