# Runbook
## Health Checks
- Confirm DataHub UI and Actions service health.
- Confirm Airflow webserver/scheduler health and API reachability.

## Common Ops
- Rotate API tokens/secrets every 90 days.
- Update mapping rules (`mappings.yml`) with PR + review.
- Review DLQ and replay failed triggers after root-cause.

## Incident Playbook (Trigger Failures)
1) Check Airflow API auth (401/403).  
2) Check allowlist for DAG IDs.  
3) Inspect DLQ entry; retry with replay script.  
4) If persistent, enable circuit breaker, page on-call.

## Auditing
- Ensure trigger logs include user, event, timestamp, correlation ID.
