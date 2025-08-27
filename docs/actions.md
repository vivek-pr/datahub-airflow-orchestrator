# Airflow Trigger Action

The Airflow Trigger action listens for DataHub events and invokes the Airflow
REST API to start DAG runs. Event types are mapped to Airflow DAG IDs and
optional run configuration via a YAML file.
Built against `acryl-datahub-actions` **0.14.0** and Airflow **2.9**.

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
enabled in your deployment. See the [DataHub Actions framework](https://docs.datahubproject.io/docs/automations/actions/) for more information and the
[Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html) reference.

