# Demo Walkthrough

This short flow demonstrates DataHub triggering an Airflow DAG in the dev profile.

1. **Deploy stacks**
   ```bash
   make datahub:dev:up
   make airflow:dev:up
   ```
2. **Port-forward services**
   ```bash
   kubectl port-forward svc/datahub-dev-datahub-frontend 9002:9002 -n datahub-dev &
   kubectl port-forward svc/airflow-dev-webserver 8443:8080 -n airflow-dev &
   ```
3. **Log in to DataHub** at <http://localhost:9002> (default `datahub`/`datahub`).
4. **Trigger the sample event** by adding the tag `gold:daily-refresh` to a dataset.
5. The custom **Airflow Trigger** Action resolves the mapping and calls the
   [Airflow REST API](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html):
   ```bash
   curl -u "$AIRFLOW_DEV_USERNAME:$AIRFLOW_DEV_PASSWORD" -X POST \
     https://localhost:8443/api/v1/dags/example_bash_operator/dagRuns \
     -H "Content-Type: application/json" \
     --data '{"conf": {"dataset": "<URN>"}}'
   ```
6. **Verify the DAG run** in the Airflow UI at <https://localhost:8443>.
7. Tear everything down:
   ```bash
   make datahub:dev:down
   make airflow:dev:down
   ```
