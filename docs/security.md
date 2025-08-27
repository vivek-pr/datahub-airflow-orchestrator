# Security

- **AuthN to Airflow REST API**: token or mTLS; never anonymous.
- **AuthZ**: DAG allowlist; per-DAG concurrency caps.
- **Secrets**: store in Kubernetes Secrets; never commit secrets.
- **Network**: restrict egress; only DataHub Action can reach Airflow API.
- **Audit**: log who/what/when; retain 30–90 days.
- **RBAC**: dedicated ServiceAccount with no cluster-wide permissions.

## Token management
- API tokens live in the `airflow-api-token` Secret and are mounted as `AIRFLOW_API_TOKEN`.
- Rotate tokens by updating the Secret and restarting the `airflow-trigger` Deployment:
  ```bash
  kubectl create secret generic airflow-api-token --from-literal token=<new> -o yaml --dry-run=client | kubectl apply -f -
  kubectl rollout restart deploy/airflow-trigger
  ```
- Store rotation history and expiry dates in your secret manager or runbook.

## RBAC
- `airflow-trigger` uses a dedicated `ServiceAccount`.
- No `RoleBinding` is attached by default; grant only what is necessary.
- Disable token automounting to avoid exposing unnecessary credentials.

## Network policy
- `NetworkPolicy` restricts inbound traffic to the Airflow webserver to pods labeled `app=airflow-trigger`.
- Verify with `kubectl exec` from a random pod; calls should time out or be dropped.

## TLS
- Airflow Ingress terminates TLS using the `airflow-tls` secret.
- DataHub Action calls `https://` endpoints and relies on the cluster trust store to validate certificates.

References:
- [Kubernetes NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes TLS Secrets](https://kubernetes.io/docs/concepts/configuration/secret/#tls-secrets)
