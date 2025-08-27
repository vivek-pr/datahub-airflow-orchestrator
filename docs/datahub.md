# DataHub

## Requirements
- Actions Framework enabled.
- Custom Action ("Airflow Trigger") deployed with config for mapping rules.
- Health endpoint exposes readiness; logs are structured.

## Installation (Dev)
DataHub is deployed via Helm using the microservice stack with Actions enabled.

```bash
make datahub:dev:up
```

This runs:

```bash
helm repo add datahub https://acryldata.github.io/datahub-helm/
helm upgrade --install datahub-dev datahub/datahub \
  --namespace datahub-dev \
  --version 0.6.19 \
  -f deploy/datahub/values.dev.yaml
```

## Login
Forward the frontend service and visit the UI:

```bash
kubectl port-forward svc/datahub-dev-datahub-frontend 9002:9002 -n datahub-dev
# then browse to http://localhost:9002
```

Default credentials are `datahub` / `datahub`.

## Actions
The `acryl-datahub-actions` service hosts custom actions. Repository-local
implementations live under the `actions/` directory.

## Acceptance Tests
- Simulated DataHub event produces a valid trigger request.
- Non-whitelisted DAGs are rejected with clear error.
- Health checks return HTTP 200.
