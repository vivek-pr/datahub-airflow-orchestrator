.PHONY: lint chart-lint test

lint:
	ruff check .

chart-lint:
	helm lint deploy/airflow deploy/datahub

test:
	pytest tests/unit
