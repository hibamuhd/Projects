"""Create the SQLite schema (idempotent)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.config import load_settings  # noqa: E402
from src.storage.database import Database  # noqa: E402

if __name__ == "__main__":
    s = load_settings()
    Database(s.db_path).init()
    print(f"Database ready at {s.db_path}")
