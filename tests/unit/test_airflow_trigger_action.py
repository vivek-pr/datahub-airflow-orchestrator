import sys
import pathlib
import logging

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
import requests
import pytest
from prometheus_client import start_http_server
from actions.airflow_trigger import AirflowTriggerAction
from actions.airflow_trigger.action import trigger_failures_total


class DummyResponse:
    def __init__(self, status_code: int, text: str = "ok"):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(self.text)


def test_mapping_and_conf(monkeypatch, tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text("sample_event:\n  dag_id: d1\n  conf:\n    foo: '{{bar}}'\n")

    session_calls = {}

    class Session:
        def post(self, url, json, headers, auth):
            session_calls["url"] = url
            session_calls["json"] = json
            return DummyResponse(200)

    action = AirflowTriggerAction("http://airflow", str(path), session=Session())
    event = {"type": "sample_event", "bar": "baz"}
    dag_run_id = action.trigger(event)

    assert session_calls["url"].endswith("/api/v1/dags/d1/dagRuns")
    assert session_calls["json"]["conf"]["foo"] == "baz"
    assert dag_run_id.startswith("d1-")


def test_nested_conf(tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text(
        "sample_event:\n"
        "  dag_id: d1\n"
        "  conf:\n"
        "    outer:\n"
        "      inner: '{{bar}}'\n"
        "    list:\n"
        "      - '{{bar}}'\n"
    )

    captured = {}

    class Session:
        def post(self, url, json, headers, auth):
            captured["json"] = json
            return DummyResponse(200)

    action = AirflowTriggerAction("http://airflow", str(path), session=Session())
    event = {"type": "sample_event", "bar": "baz"}
    action.trigger(event)

    conf = captured["json"]["conf"]
    assert conf["outer"]["inner"] == "baz"
    assert conf["list"][0] == "baz"


def test_idempotent_dag_run_id(tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text("sample_event:\n  dag_id: test\n")
    action = AirflowTriggerAction("http://airflow", str(path))
    event = {"type": "sample_event", "id": 1}
    first = action._dag_run_id("test", event)
    second = action._dag_run_id("test", event)
    assert first == second


def test_retry_on_server_error(tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text("sample_event:\n  dag_id: d1\n")
    calls = {"count": 0}

    class Session:
        def post(self, url, json, headers, auth):
            calls["count"] += 1
            if calls["count"] < 2:
                return DummyResponse(500, "error")
            return DummyResponse(200)

    action = AirflowTriggerAction("http://airflow", str(path), session=Session())
    event = {"type": "sample_event"}
    dag_run_id = action.trigger(event)
    assert calls["count"] == 2
    assert dag_run_id.startswith("d1-")


def test_unauthorized(tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text("sample_event:\n  dag_id: d1\n")

    class Session:
        def post(self, url, json, headers, auth):
            return DummyResponse(401, "unauthorized")

    action = AirflowTriggerAction("http://airflow", str(path), session=Session())
    event = {"type": "sample_event"}
    try:
        action.trigger(event)
    except requests.HTTPError:
        pass
    else:
        assert False, "Expected HTTPError"


def test_non_whitelisted(tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text("other_event:\n  dag_id: d1\n")
    action = AirflowTriggerAction("http://airflow", str(path))
    event = {"type": "sample_event"}
    try:
        action.trigger(event)
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError"


def test_correlation_id_and_metrics(tmp_path, caplog):
    path = tmp_path / "mappings.yaml"
    path.write_text("sample_event:\n  dag_id: d1\n")

    captured = {}

    class Session:
        def post(self, url, json, headers, auth):
            captured["headers"] = headers
            captured["json"] = json
            return DummyResponse(200)

    port = 8001
    start_http_server(port)
    action = AirflowTriggerAction("http://airflow", str(path), session=Session())
    event = {"type": "sample_event"}

    with caplog.at_level(logging.INFO):
        action.trigger(event)

    corr_id = captured["headers"]["X-Correlation-ID"]
    assert captured["json"]["conf"]["correlation_id"] == corr_id
    record = next(r for r in caplog.records if "triggered dag" in r.message)
    assert getattr(record, "correlation_id") == corr_id

    metrics = requests.get(f"http://localhost:{port}/metrics").text
    assert "triggers_total" in metrics
    assert "latency_ms" in metrics


def test_failure_metric(tmp_path):
    path = tmp_path / "mappings.yaml"
    path.write_text("sample_event:\n  dag_id: d1\n")

    class Session:
        def post(self, url, json, headers, auth):
            return DummyResponse(500, "error")

    action = AirflowTriggerAction(
        "http://airflow", str(path), session=Session(), max_retries=1
    )
    before = trigger_failures_total._value.get()
    with pytest.raises(requests.HTTPError):
        action.trigger({"type": "sample_event"})
    assert trigger_failures_total._value.get() == before + 1
