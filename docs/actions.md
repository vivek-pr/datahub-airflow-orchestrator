# Airflow Trigger Action

The Airflow Trigger action listens for DataHub events and invokes the Airflow
REST API to start DAG runs. Event types are mapped to Airflow DAG IDs and
optional run configuration via a YAML file.

## Configuration

`actions/config/mappings.dev.yaml`

```yaml
sample_event:
  dag_id: sample_dag
  conf:
    foo: bar
```

## Environment Variables

- `AIRFLOW_API_BASE_URL` – base URL for the Airflow REST API.
- `AIRFLOW_USERNAME` / `AIRFLOW_PASSWORD` – credentials for basic auth.
- `AIRFLOW_TOKEN` – bearer token (takes precedence over basic auth).
- `MAPPINGS_PATH` – path to the mappings YAML file.

## Notes

This action is built on top of DataHub's Actions framework, which must be
enabled in your deployment. See the [DataHub Actions framework](datahub.md) for more information.

