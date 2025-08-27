# Mapping Rules (Event → DAG)
- Match by dataset URN, tag, glossary term, or manual action.
- Resolve to `{dag_id, conf}`.
- Idempotency: stable `dag_run_id` for the same event to avoid duplicates.

Reference: [DataHub entity URNs](https://docs.datahubproject.io/docs/adding-metadata/metadata-model/urns/).

## Examples
- Tag `gold:daily-refresh` → `dag_id: refresh_gold_tables`, `conf: { datasets: [...] }`.
- Dataset URN `urn:li:dataset:(urn:li:dataPlatform:sample,foo,PROD)` → `dag_id: example_event_dag`, `conf: {"dataset": <URN>}`.
- Dataset tagged `needs-quality-check` → `dag_id: example_quality_check`, `conf: {"dataset": <URN>}`.
