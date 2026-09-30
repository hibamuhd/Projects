#!/usr/bin/env bash
# One-command demo: install deps, generate data, init DB, run tests + benchmark, launch the app.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -r requirements.txt -q
python3 scripts/generate_data.py
python3 scripts/initialize_db.py
python3 -m pytest
python3 scripts/run_evaluation.py
exec streamlit run app.py
