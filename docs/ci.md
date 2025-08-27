# CI Approach (End-to-End)
- Spin up a local Kubernetes (KinD/Minikube) in CI.
- Install Airflow & DataHub charts with dev profiles.
- Run contract tests against Airflow API; run E2E: trigger → run completes.
- Tear down and upload logs on failure.
