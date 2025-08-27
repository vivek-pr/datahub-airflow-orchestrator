# Airflow Requirements
- REST API enabled; auth required.
- Webserver + Scheduler profiles for dev & prod.
- Resource requests/limits tuned; readiness/liveness probes defined.
- Optional: bake lineage plugin into image; pin versions.

## Acceptance Tests
- 401 without creds; 2xx with valid auth on `POST /api/v1/dags/.../dagRuns`.
- Sample DAG accepts `conf` and completes successfully.
