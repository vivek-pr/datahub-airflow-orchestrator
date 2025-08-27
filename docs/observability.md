# Observability
- **Correlation ID**: add `X-Correlation-ID` to every trigger.
- **Metrics**: triggers_total, trigger_failures_total, latency_ms.
- **Logs**: structured logs on both sides (DataHub Action & Airflow).

## SLOs
- Trigger ack latency < 5s (p95).
- Success rate ≥ 99% in normal ops.
