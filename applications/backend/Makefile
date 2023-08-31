APPLICATION_PORT := 8000
GUNICORN_TIMEOUT := 6000
LOGLEVEL := info

.PHONY: run-backend
run-backend:
	poetry run gunicorn 'src.app:main' -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$(APPLICATION_PORT) -t $(GUNICORN_TIMEOUT) --log-level $(LOGLEVEL)

.PHONY: healthcheck
healthcheck:
	curl http://localhost:$(APPLICATION_PORT)/health

.PHONY: black-check
black-check:
	poetry run black --check src tests

.PHONY: black
black:
	poetry run black src tests

.PHONY: ruff
ruff:
	poetry run ruff check src tests --fix

.PHONY: ruff-check
ruff-check:
	poetry run ruff check src tests

.PHONY: mdformat
mdformat:
	poetry run mdformat *.md

.PHONY: mdformat-check
mdformat-check:
	poetry run mdformat --check *.md

.PHONY: mypy
mypy:
	poetry run mypy src

.PHONY: test
test:
	poetry run pytest tests --cov=src --cov-report term-missing --durations 5

.PHONY: format
format:
	$(MAKE) black
	$(MAKE) ruff
	$(MAKE) mdformat

.PHONY: lint
lint:
	$(MAKE) black-check
	$(MAKE) ruff-check
	$(MAKE) mdformat-check
	$(MAKE) mypy

.PHONY: test-all
test-all:
	$(MAKE) lint
	$(MAKE) test