# Security
- **AuthN to Airflow REST API**: token or mTLS; never anonymous.
- **AuthZ**: DAG allowlist; per-DAG concurrency caps.
- **Secrets**: store in Kubernetes Secrets; never commit secrets.
- **Network**: restrict egress; only DataHub Action can reach Airflow API.
- **Audit**: log who/what/when; retain 30–90 days.
