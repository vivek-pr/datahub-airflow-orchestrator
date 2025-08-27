"""DataHub action that triggers Airflow DAG runs."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional

import requests
import yaml
import uuid
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
        dlq_path: Optional[str] = None,
        backoff_factor: float = 0.5,
        request_timeout: int = 5,
        session: Optional[requests.Session] = None,
    ) -> None:
        self.airflow_url = airflow_url.rstrip("/")
        self.username = username
        self.password = password
        self.token = token
        self.max_retries = max_retries
        self.dlq_path = dlq_path
        self.backoff_factor = backoff_factor
        self.request_timeout = request_timeout
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

    def _check_health(self) -> bool:
        """Return True if Airflow reports healthy."""
        try:
            resp = self.session.get(
                f"{self.airflow_url}/health", timeout=self.request_timeout
            )
            resp.raise_for_status()
            data = resp.json()
            return all(
                component.get("status") == "healthy" for component in data.values()
            )
        except Exception:
            return False

    def _write_dlq(
        self, event: Dict[str, Any], dag_id: str, dag_run_id: str, error: str
    ) -> None:
        if not self.dlq_path:
            return
        entry = {
            "timestamp": time.time(),
            "event": event,
            "dag_id": dag_id,
            "dag_run_id": dag_run_id,
            "error": error,
        }
        with open(self.dlq_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def trigger(self, event: Dict[str, Any]) -> str:
        """Trigger a DAG run for the given event."""
        start_time = time.time()
        triggers_total.inc()
        correlation_id = str(uuid.uuid4())
        extra = {"correlation_id": correlation_id}
        dag_id = ""
        dag_run_id = ""
        last_error: Optional[Exception] = None
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

            if not self._check_health():
                trigger_counter.labels(status="circuit_open").inc()
                raise RuntimeError("Airflow health check failed")

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
                try:
                    response = self.session.post(
                        url,
                        json=payload,
                        headers=headers,
                        auth=auth,
                        timeout=self.request_timeout,
                    )
                except requests.RequestException as e:
                    logger.warning(
                        "error triggering %s: %s, attempt %s",
                        dag_id,
                        e,
                        attempt,
                        extra=extra,
                    )
                    if attempt == self.max_retries:
                        trigger_counter.labels(status="error").inc()
                        raise
                    time.sleep(self.backoff_factor * (2 ** (attempt - 1)))
                    continue

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
                    time.sleep(self.backoff_factor * (2 ** (attempt - 1)))
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

            trigger_counter.labels(status="error").inc()
            raise RuntimeError("Failed to trigger DAG after retries")
        except Exception as e:
            last_error = e
            trigger_failures_total.inc()
            raise
        finally:
            if last_error is not None:
                self._write_dlq(event, dag_id, dag_run_id, str(last_error))
            latency_ms.observe((time.time() - start_time) * 1000)
