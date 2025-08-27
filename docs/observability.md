# Observability

The orchestrator exposes request-level tracing and basic Prometheus metrics.

## Correlation IDs
- Every trigger generates a UUID4 correlation ID.
- Sent as the `X-Correlation-ID` HTTP header and embedded in the Airflow
  `conf` payload (`conf.correlation_id`).
- All log lines emitted by the action include the `correlation_id` field so
  DataHub and Airflow logs can be joined.

## Metrics
- `triggers_total` – counter of all trigger attempts.
- `trigger_failures_total` – counter of failed trigger attempts.
- `latency_ms` – histogram of trigger round-trip latency in milliseconds.

Expose metrics for scraping with:

```python
from prometheus_client import start_http_server
start_http_server(8000)
```

Then `curl http://localhost:8000/metrics` to inspect the values.

## Logs
- Structured logging on both sides (DataHub Action & Airflow) includes the
  shared `correlation_id`.

## SLOs
- Trigger ack latency < 5s (p95).
- Success rate ≥ 99% in normal ops.
