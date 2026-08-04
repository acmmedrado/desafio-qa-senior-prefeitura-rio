.PHONY: help install api test test-known-bugs test-all perf reports clean

PYTHON ?= python3
VENV := .venv
PYTEST := $(VENV)/bin/pytest
BASE_URL ?= http://localhost:8080

help:
	@echo "Comandos disponiveis:"
	@echo "  make install          Instala dependencias Python no .venv"
	@echo "  make api              Sobe a API localmente com go run"
	@echo "  make test             Roda o quality gate sem bugs conhecidos"
	@echo "  make test-known-bugs  Roda testes que documentam bugs conhecidos"
	@echo "  make test-all         Roda a suite completa"
	@echo "  make reports          Gera relatorios HTML/JUnit"
	@echo "  make perf             Roda teste de performance com k6"
	@echo "  make clean            Remove caches e relatorios locais"

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

api:
	cd api && PORT=8080 go run .

test:
	BASE_URL=$(BASE_URL) $(PYTEST) -m "not known_bug"

test-known-bugs:
	BASE_URL=$(BASE_URL) $(PYTEST) -m known_bug

test-all:
	BASE_URL=$(BASE_URL) $(PYTEST)

reports:
	mkdir -p reports
	BASE_URL=$(BASE_URL) $(PYTEST) -m "not known_bug" \
		--junitxml=reports/pytest-junit.xml \
		--html=reports/pytest-report.html \
		--self-contained-html
	BASE_URL=$(BASE_URL) $(PYTEST) -m known_bug \
		--junitxml=reports/known-bugs-junit.xml \
		--html=reports/known-bugs-report.html \
		--self-contained-html || true

perf:
	BASE_URL=$(BASE_URL) k6 run performance/catalog-api.k6.js

clean:
	rm -rf .pytest_cache reports
	find tests -name "__pycache__" -type d -prune -exec rm -rf {} +
