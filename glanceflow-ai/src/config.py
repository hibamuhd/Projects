"""Environment-based configuration. No secrets are stored in code."""
from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _read_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


@dataclass(frozen=True)
class Settings:
    db_path: Path
    catalogue_path: Path
    eval_queries_path: Path
    llm_provider: str = "none"          # "none" | "anthropic"
    llm_api_key: str | None = None
    llm_model: str = "claude-haiku-4-5-20251001"
    llm_timeout_s: float = 8.0
    price_in_per_mtok: float = 0.0
    price_out_per_mtok: float = 0.0
    max_revisions: int = 1               # bounded critic-triggered revisions
    max_retries: int = 2                 # per external call
    max_workflow_steps: int = 12         # hard stop against loops
    top_n: int = 5
    min_results: int = 3
    min_relevance: float = 0.12          # weak-relevance floor for final score

    @property
    def llm_configured(self) -> bool:
        return self.llm_provider != "none" and bool(self.llm_api_key)


def load_settings(**overrides) -> Settings:
    env = {**_read_dotenv(ROOT / ".env"), **os.environ}
    db = Path(env.get("GLANCEFLOW_DB_PATH", "data/glanceflow.db"))
    if not db.is_absolute():
        db = ROOT / db
    s = Settings(
        db_path=db,
        catalogue_path=ROOT / "data" / "catalogue.csv",
        eval_queries_path=ROOT / "data" / "evaluation_queries.json",
        llm_provider=env.get("GLANCEFLOW_LLM_PROVIDER", "none").lower(),
        llm_api_key=env.get("ANTHROPIC_API_KEY") or None,
        llm_model=env.get("GLANCEFLOW_LLM_MODEL", "claude-haiku-4-5-20251001"),
        llm_timeout_s=float(env.get("GLANCEFLOW_LLM_TIMEOUT_S", "8")),
        price_in_per_mtok=float(env.get("GLANCEFLOW_PRICE_IN_PER_MTOK", "0") or 0),
        price_out_per_mtok=float(env.get("GLANCEFLOW_PRICE_OUT_PER_MTOK", "0") or 0),
    )
    return replace(s, **overrides) if overrides else s
