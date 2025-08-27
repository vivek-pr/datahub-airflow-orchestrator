# CI Approach (End-to-End)

This project verifies the full Airflow ↔ DataHub integration on every pull request.
The GitHub Actions workflow spins up a local [Minikube](https://minikube.sigs.k8s.io/)
cluster, deploys both stacks, runs the end-to-end tests, and tears everything down.

## Pipeline steps
1. **Start Minikube** – provision a single-node Kubernetes cluster.
2. **Build images** – build the `airflow-trigger` container and load it into the
   cluster with `minikube image load`.
3. **Install charts** – install DataHub and Airflow Helm charts with the `values.dev.yaml`
   profiles. The `airflow-trigger` chart is also installed in the Airflow namespace.
4. **Wait for readiness** – `kubectl wait` ensures all pods in the `airflow-dev`
   and `datahub-dev` namespaces are ready before tests run.
5. **Run tests** – execute the `tests/e2e` suite which triggers DAGs and checks
   that lineage is emitted to DataHub.
6. **Collect logs on failure** – if any step fails, logs from all pods are
   gathered and uploaded as workflow artifacts for debugging.

## Troubleshooting
- Inspect the uploaded `k8s-logs` artifact when the workflow fails. It contains
  logs from every container in both namespaces.
- Reproduce locally with:
  ```sh
  minikube start
  ./scripts/datahub_dev_up.sh
  ./scripts/airflow_dev_up.sh
  helm upgrade --install airflow-trigger deploy/airflow-trigger -f deploy/airflow-trigger/values.dev.yaml -n airflow-dev
  pytest tests/e2e -vv
  ```
- If pods never become ready, check cluster events with `kubectl describe pod`
  and ensure the `example/airflow-trigger:dev` image builds successfully.
- Port-forwarding failures in tests typically mean the service is not ready or
  the pod crashed; use `kubectl get pods -n <namespace>` to verify.
