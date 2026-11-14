# AgroTwin developer commands. Windows users without GNU make: use .\tasks.ps1 <task>.
PYTHON ?= python

.PHONY: help install test validate lint api web demo version clean

help:
	@echo "AgroTwin $(shell $(PYTHON) -c \"import agrotwin; print(agrotwin.__version__)\")"
	@echo "  make install   install runtime + dev dependencies"
	@echo "  make test      run unit, contract and smoke tests"
	@echo "  make validate  validate every contract fixture and cross-field rule"
	@echo "  make lint      run ruff"
	@echo "  make api       run the FastAPI service on http://127.0.0.1:8000"
	@echo "  make web       run the Next.js frontend (requires npm install in web/)"
	@echo "  make demo      run the API in demo mode (fixture-backed)"
	@echo "  make version   print the single-source version"
	@echo "  make clean     remove local caches"

install:
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install -r requirements-api.txt

test:
	$(PYTHON) -m pytest

validate:
	$(PYTHON) -m contracts.validate --all

lint:
	$(PYTHON) -m ruff check .

api:
	$(PYTHON) -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

web:
	npm --prefix web run dev

demo:
	$(PYTHON) -m uvicorn api.main:app --host 127.0.0.1 --port 8000

version:
	@$(PYTHON) -c "import agrotwin; print(agrotwin.__version__)"

clean:
	$(PYTHON) -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	$(PYTHON) -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('.pytest_cache', '.ruff_cache')]"
