SHELL := /bin/bash
.RECIPEPREFIX := >

.PHONY: lint chart-lint test airflow\:dev\:up airflow\:dev\:down

lint:
>ruff check .

chart-lint:
>helm lint deploy/airflow deploy/datahub

test:
>pytest tests/unit tests/contract

airflow\:dev\:up:
>./scripts/airflow_dev_up.sh

airflow\:dev\:down:
>./scripts/airflow_dev_down.sh

