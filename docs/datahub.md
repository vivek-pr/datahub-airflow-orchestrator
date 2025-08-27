# DataHub Requirements
- Actions Framework enabled.
- Custom Action (“Airflow Trigger”) deployed with config for mapping rules.
- Health endpoint exposes readiness; logs are structured.

## Acceptance Tests
- Simulated DataHub event produces a valid trigger request.
- Non-whitelisted DAGs are rejected with clear error.
