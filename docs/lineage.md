# Lineage

Airflow emits operational lineage and run status to DataHub via the
[DataHub Airflow lineage plugin](https://docs.datahubproject.io/docs/airflow/airflow-lineage/).

## Installation

The Airflow Helm chart installs the plugin by including the package below in
`extraPipPackages`:

```yaml
acryl-datahub[airflow]==0.14.0
```

Keep the version pinned and update it deliberately when upgrading.

## Configuration

The plugin is enabled through Airflow's configuration:

```ini
AIRFLOW__LINEAGE__BACKEND=datahub_provider.lineage.datahub.DatahubLineageBackend
DATAHUB_GMS_URL=http://datahub-gms:8080
```

Adjust the `DATAHUB_GMS_URL` for your environment.

## Validation

Trigger a DAG and confirm the corresponding `DataFlow`, `DataJob`, and run
records appear in DataHub.
