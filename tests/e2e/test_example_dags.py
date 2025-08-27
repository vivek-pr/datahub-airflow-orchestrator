import os
import time
import subprocess
import shutil

import pytest
import requests

NAMESPACE = os.getenv("AIRFLOW_NAMESPACE", "airflow-dev")
RELEASE = os.getenv("AIRFLOW_RELEASE", "airflow-dev")
AIRFLOW_USER = os.getenv("AIRFLOW_USER", "admin")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "")


def _port_forward(service: str, local_port: int, remote_port: int):
    if not shutil.which("kubectl"):
        pytest.skip("kubectl not installed")
    proc = subprocess.Popen(
        [
            "kubectl",
            "port-forward",
            f"svc/{service}",
            f"{local_port}:{remote_port}",
            "-n",
            NAMESPACE,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3)
    if proc.poll() is not None:
        pytest.skip(f"port-forward failed for {service}")
    return proc


def _trigger_and_wait(dag_id: str, conf: dict | None = None):
    service = f"{RELEASE}-webserver"
    proc = _port_forward(service, 8080, 8080)
    try:
        url = f"http://localhost:8080/api/v1/dags/{dag_id}/dagRuns"
        auth = (AIRFLOW_USER, AIRFLOW_PASSWORD)
        try:
            resp = requests.post(url, json={"conf": conf or {}}, auth=auth, timeout=5)
        except requests.RequestException:
            pytest.skip("Airflow API not reachable")
        if resp.status_code >= 400:
            pytest.skip("Airflow API unavailable")
        dag_run_id = resp.json()["dag_run_id"]
        for _ in range(30):
            try:
                status = requests.get(f"{url}/{dag_run_id}", auth=auth, timeout=5)
            except requests.RequestException:
                pytest.skip("Airflow API not reachable")
            state = status.json().get("state")
            if state in {"success", "failed"}:
                break
            time.sleep(1)
        assert state == "success"
    finally:
        proc.terminate()
        proc.wait()


def test_example_dags_reach_success():
    conf = {"dataset": "urn:li:dataset:(urn:li:dataPlatform:sample,foo,PROD)"}
    for dag_id in ["example_event_dag", "example_quality_check"]:
        _trigger_and_wait(dag_id, conf)
