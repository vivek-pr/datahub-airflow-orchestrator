#!/bin/bash
set -euo pipefail

NAMESPACE=${AIRFLOW_NAMESPACE:-airflow-dev}
RELEASE=${AIRFLOW_RELEASE:-airflow-dev}

helm uninstall "$RELEASE" --namespace "$NAMESPACE" || true
kubectl delete secret airflow-dev-credentials --namespace "$NAMESPACE" --ignore-not-found
kubectl delete namespace "$NAMESPACE" --ignore-not-found
