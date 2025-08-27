#!/bin/bash
set -euo pipefail

NAMESPACE=${AIRFLOW_NAMESPACE:-airflow-dev}
RELEASE=${AIRFLOW_RELEASE:-airflow-dev}

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic airflow-dev-credentials \
  --namespace "$NAMESPACE" \
  --from-literal=username="${AIRFLOW_DEV_USERNAME:-admin}" \
  --from-literal=password="${AIRFLOW_DEV_PASSWORD:-admin}" \
  --dry-run=client -o yaml | kubectl apply -f -

helm repo add apache-airflow https://airflow.apache.org >/dev/null
helm repo update >/dev/null

USERNAME=$(kubectl get secret airflow-dev-credentials -n "$NAMESPACE" -o jsonpath='{.data.username}' | base64 -d)
PASSWORD=$(kubectl get secret airflow-dev-credentials -n "$NAMESPACE" -o jsonpath='{.data.password}' | base64 -d)

helm upgrade --install "$RELEASE" apache-airflow/airflow \
  --namespace "$NAMESPACE" \
  -f deploy/airflow/values.dev.yaml \
  --set webserver.defaultUser.username="$USERNAME" \
  --set webserver.defaultUser.password="$PASSWORD"

kubectl wait --for=condition=ready pod -l component=webserver -n "$NAMESPACE" --timeout=600s
kubectl wait --for=condition=ready pod -l component=scheduler -n "$NAMESPACE" --timeout=600s
