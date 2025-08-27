#!/bin/bash
set -euo pipefail

NAMESPACE=${DATAHUB_NAMESPACE:-datahub-dev}
RELEASE=${DATAHUB_RELEASE:-datahub-dev}
CHART_VERSION=${DATAHUB_CHART_VERSION:-0.6.19}

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

helm repo add datahub https://acryldata.github.io/datahub-helm >/dev/null
helm repo update >/dev/null

helm upgrade --install "$RELEASE" datahub/datahub \
  --namespace "$NAMESPACE" \
  --version "$CHART_VERSION" \
  -f deploy/datahub/values.dev.yaml

kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance="$RELEASE" -n "$NAMESPACE" --timeout=600s

GMS_SERVICE="$RELEASE-datahub-gms"
FRONTEND_SERVICE="$RELEASE-datahub-frontend"

kubectl port-forward svc/$GMS_SERVICE 8080:8080 -n "$NAMESPACE" >/tmp/datahub_gms_pf.log 2>&1 &
GMS_PF=$!
sleep 5
curl -sf http://localhost:8080/health >/dev/null
kill $GMS_PF
wait $GMS_PF 2>/dev/null || true

kubectl port-forward svc/$FRONTEND_SERVICE 9002:9002 -n "$NAMESPACE" >/tmp/datahub_fe_pf.log 2>&1 &
FE_PF=$!
sleep 5
curl -sf http://localhost:9002/api/health >/dev/null
kill $FE_PF
wait $FE_PF 2>/dev/null || true
