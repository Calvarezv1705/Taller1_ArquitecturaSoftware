.PHONY: install test run run-prod docker-up docker-down logs

install:
	python3.12 -m venv .venv312
	./.venv312/bin/python -m pip install -r requirements.txt

test:
	./.venv312/bin/python -m pytest

run:
	./.venv312/bin/python -m uvicorn src.infrastructure.api.main:app --app-dir . --reload --host 0.0.0.0 --port 8000

run-prod:
	./.venv312/bin/python -m uvicorn src.infrastructure.api.main:app --app-dir . --host 0.0.0.0 --port 8000

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

logs:
	docker compose logs -f
