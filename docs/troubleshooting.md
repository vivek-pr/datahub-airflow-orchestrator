# Troubleshooting
## 401/403 from Airflow API
- Check token validity and RBAC.
- Confirm network policy allows Action → Airflow.

## 404 DAG not found
- Validate mapping rules; ensure DAG is deployed and discoverable.

## Timeouts / 5xx
- The action automatically retries with exponential backoff and writes
  failed events to a **dead-letter queue** file (DLQ).
- Inspect the DLQ at the configured path and use `scripts/replay_dlq.py`
  to resubmit once Airflow is healthy.

## Airflow health is red
- The trigger performs a health check before submitting. When Airflow
  reports unhealthy, new events are placed on the DLQ instead of being
  sent.
