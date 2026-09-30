PY ?= python3

setup:
	$(PY) -m pip install -r requirements.txt

data:
	$(PY) scripts/generate_data.py

db:
	$(PY) scripts/initialize_db.py

run:
	streamlit run app.py

test:
	$(PY) -m pytest

eval:
	$(PY) scripts/run_evaluation.py

demo:
	bash scripts/run_demo.sh
