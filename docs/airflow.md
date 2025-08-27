# Airflow Development Deployment

This project includes a helper profile for running Apache Airflow on a local
Kubernetes cluster such as Minikube using the official Helm chart.
Pinned to chart **1.18.0** from [Artifact Hub](https://artifacthub.io/packages/helm/apache-airflow/airflow).

## Values
- `deploy/airflow/values.dev.yaml` enables the webserver and scheduler.
- REST API authentication uses the `airflow.api.auth.backend.basic_auth`
  backend.
- TLS is enabled on the webserver and expects a secret named
  `airflow-dev-webserver-tls` containing `tls.crt` and `tls.key`.
- Admin credentials are not stored in git. A Kubernetes secret
  `airflow-dev-credentials` is created during installation and passed to the
  chart.

## Usage
Bring up and tear down the development deployment with make targets:

```sh
make airflow:dev:up   # install chart and wait for readiness
make airflow:dev:down # remove release and namespace
```

## Accessing the API
Port-forward the webserver service to reach the API:

```sh
kubectl port-forward svc/airflow-dev-webserver 8443:8080 -n airflow-dev
```

The API is served over HTTPS at `https://localhost:8443/api/v1` as defined in the
[Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html).
Unauthenticated requests return `401`. Authenticate using the credentials stored in the
`airflow-dev-credentials` secret:

```sh
curl -u "$AIRFLOW_DEV_USERNAME:$AIRFLOW_DEV_PASSWORD" -X POST \
  https://localhost:8443/api/v1/dags/example_bash_operator/dagRuns \
  -H "Content-Type: application/json" \
  --data '{"dag_run_id": "manual_test"}'
```

## Tests
Contract tests in `tests/contract/test_airflow_api.py` hit the API. Provide
`AIRFLOW_API_URL`, `AIRFLOW_API_USERNAME` and `AIRFLOW_API_PASSWORD`
environment variables to run them. The tests assert `401` without credentials
and a `2xx` response when valid credentials are supplied.
