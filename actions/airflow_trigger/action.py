"""DataHub action that triggers Airflow DAG runs."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, Optional

import requests
import yaml
import uuid
import time
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

trigger_counter = Counter(
    "airflow_trigger_total", "Total Airflow trigger events", ["status"]
)

triggers_total = Counter("triggers_total", "Total trigger attempts")
trigger_failures_total = Counter(
    "trigger_failures_total", "Total trigger failures"
)
latency_ms = Histogram("latency_ms", "Trigger latency in milliseconds")


class AirflowTriggerAction:
    """Trigger Airflow DAGs based on DataHub events."""

    def __init__(
        self,
        airflow_url: str,
        mappings_path: str,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        max_retries: int = 3,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.airflow_url = airflow_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = token
        self.max_retries = max_retries
        self.session = session or requests.Session()
        with open(mappings_path, "r", encoding="utf-8") as f:
            self.mappings: Dict[str, Dict[str, Any]] = yaml.safe_load(f) or {}

    @staticmethod
    def _dag_run_id(dag_id: str, event: Dict[str, Any]) -> str:
        """Build a deterministic dag_run_id from the event."""
        payload = json.dumps(event, sort_keys=True)
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:8]
        return f"{dag_id}-{digest}"

    def _resolve_conf(self, conf_template: Dict[str, Any], event: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively resolve templated conf values from the event."""

        def resolve(value: Any) -> Any:
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                event_key = value.strip("{} ")
                return event.get(event_key)
            if isinstance(value, dict):
                return {k: resolve(v) for k, v in value.items()}
            if isinstance(value, list):
                return [resolve(v) for v in value]
            return value

        return {k: resolve(v) for k, v in conf_template.items()}

    def trigger(self, event: Dict[str, Any]) -> str:
        """Trigger a DAG run for the given event."""
        start_time = time.time()
        triggers_total.inc()
        correlation_id = str(uuid.uuid4())
        extra = {"correlation_id": correlation_id}
        try:
            event_type = event.get("type")
            mapping = self.mappings.get(event_type)
            if not mapping:
                logger.warning("event type %s not mapped", event_type, extra=extra)
                trigger_counter.labels(status="ignored").inc()
                raise ValueError(f"event type {event_type} not whitelisted")

            dag_id = mapping["dag_id"]
            conf_template = mapping.get("conf", {})
            conf = self._resolve_conf(conf_template, event)
            conf["correlation_id"] = correlation_id
            dag_run_id = self._dag_run_id(dag_id, event)
            extra.update({"dag_id": dag_id, "dag_run_id": dag_run_id})

            headers = {
                "Content-Type": "application/json",
                "X-Correlation-ID": correlation_id,
            }
            auth = None
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            elif self.username and self.password:
                auth = (self.username, self.password)

            url = f"{self.airflow_url}/api/v1/dags/{dag_id}/dagRuns"
            payload = {"dag_run_id": dag_run_id, "conf": conf}

            for attempt in range(1, self.max_retries + 1):
                response = self.session.post(url, json=payload, headers=headers, auth=auth)
                if response.status_code in {401, 403}:
                    trigger_counter.labels(status="unauthorized").inc()
                    logger.error(
                        "unauthorized to trigger %s: %s", dag_id, response.text, extra=extra
                    )
                    response.raise_for_status()
                if response.status_code >= 500:
                    logger.warning(
                        "error triggering %s (status %s), attempt %s",
                        dag_id,
                        response.status_code,
                        attempt,
                        extra=extra,
                    )
                    if attempt == self.max_retries:
                        trigger_counter.labels(status="error").inc()
                        response.raise_for_status()
                    continue
                try:
                    response.raise_for_status()
                except requests.HTTPError:
                    trigger_counter.labels(status="error").inc()
                    logger.error(
                        "failed to trigger %s: %s", dag_id, response.text, extra=extra
                    )
                    raise
                trigger_counter.labels(status="success").inc()
                logger.info("triggered dag", extra=extra)
                return dag_run_id

            # Should never reach here
            trigger_counter.labels(status="error").inc()
            raise RuntimeError("Failed to trigger DAG after retries")
        except Exception:
            trigger_failures_total.inc()
            raise
        finally:
            latency_ms.observe((time.time() - start_time) * 1000)
