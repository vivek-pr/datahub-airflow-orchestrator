# Architecture (MVP)
**Flow:** DataHub (Actions) → Airflow REST API → DAG run

## Components
- **DataHub** with Actions Framework enabled.
- **Custom DataHub Action** (“Airflow Trigger”): validates, maps, signs requests, retries.
- **Apache Airflow**: REST API enabled & authenticated; runs DAGs; optionally emits lineage back to DataHub.

## Requirements (non-negotiable)
- Security: token or mTLS; RBAC; allowlist of DAGs.
- Reliability: retries with backoff; DLQ for failures; circuit-breaker if Airflow is down.
- Observability: correlation IDs; trigger metrics; readable logs.

## Sequence (happy path)
1) Event in DataHub (e.g., tag added, schema change, or manual run).  
2) Action maps event → `{dag_id, conf}`.  
3) `POST /api/v1/dags/{dag_id}/dagRuns` (auth required).  
4) Airflow schedules & executes; status visible in Airflow UI and optionally in DataHub (lineage plugin).

## Alternatives & Tradeoffs
- Direct webhooks vs sidecar service for actions.
- Single vs separate clusters for DataHub & Airflow.
- Token vs mTLS for API auth.
