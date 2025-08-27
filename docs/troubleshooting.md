# Troubleshooting
## 401/403 from Airflow API
- Check token validity and RBAC.
- Confirm network policy allows Action → Airflow.

## 404 DAG not found
- Validate mapping rules; ensure DAG is deployed and discoverable.

## Timeouts / 5xx
- Check Airflow health; activate retries and DLQ; consider back-pressure.
