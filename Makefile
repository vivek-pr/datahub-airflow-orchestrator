SHELL := /bin/bash
.RECIPEPREFIX := >

.PHONY: lint chart-lint test airflow\:dev\:up airflow\:dev\:down datahub\:dev\:up datahub\:dev\:down

lint:
>ruff check .

chart-lint:
>helm lint deploy/airflow deploy/datahub

test:
>pytest tests/unit tests/contract tests/e2e

airflow\:dev\:up:
>./scripts/airflow_dev_up.sh

airflow\:dev\:down:
>./scripts/airflow_dev_down.sh

datahub\:dev\:up:
>./scripts/datahub_dev_up.sh

datahub\:dev\:down:
>./scripts/datahub_dev_down.sh

