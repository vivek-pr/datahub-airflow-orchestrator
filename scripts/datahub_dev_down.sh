#!/bin/bash
set -euo pipefail

NAMESPACE=${DATAHUB_NAMESPACE:-datahub-dev}
RELEASE=${DATAHUB_RELEASE:-datahub-dev}

helm uninstall "$RELEASE" --namespace "$NAMESPACE" || true
kubectl delete namespace "$NAMESPACE" --ignore-not-found
