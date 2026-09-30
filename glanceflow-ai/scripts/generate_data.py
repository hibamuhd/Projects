"""Generate data/catalogue.csv (synthetic) and data/evaluation_queries.json (fixed benchmark)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import ROOT  # noqa: E402
from src.data.seed_catalogue import generate_records, write_csv  # noqa: E402
from src.data.validation import load_catalogue  # noqa: E402
from src.evaluation.queries import EVAL_QUERIES  # noqa: E402


def main() -> None:
    rows = generate_records(seed=7)
    write_csv(ROOT / "data" / "catalogue.csv", rows)
    (ROOT / "data" / "evaluation_queries.json").write_text(json.dumps(EVAL_QUERIES, indent=2, ensure_ascii=False), encoding="utf-8")
    items, rep = load_catalogue(ROOT / "data" / "catalogue.csv")
    print(f"Wrote {len(rows)} raw rows -> {len(items)} valid items. Ingestion report: {rep.summary()}")
    print(f"Wrote {len(EVAL_QUERIES)} evaluation queries.")


if __name__ == "__main__":
    main()
