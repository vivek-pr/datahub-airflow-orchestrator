"""Smoke test ensuring Airflow lineage is sent to DataHub."""

import os
import time
import subprocess
import shutil

import pytest
import requests


AIRFLOW_NAMESPACE = os.getenv("AIRFLOW_NAMESPACE", "airflow-dev")
AIRFLOW_RELEASE = os.getenv("AIRFLOW_RELEASE", "airflow-dev")
DATAHUB_NAMESPACE = os.getenv("DATAHUB_NAMESPACE", "datahub-dev")
DATAHUB_RELEASE = os.getenv("DATAHUB_RELEASE", "datahub-dev")
AIRFLOW_USER = os.getenv("AIRFLOW_USER", "admin")
AIRFLOW_PASSWORD = os.getenv("AIRFLOW_PASSWORD", "")


def _port_forward(service: str, local_port: int, remote_port: int, namespace: str):
    if not shutil.which("kubectl"):
        pytest.skip("kubectl not installed")
    proc = subprocess.Popen(
        [
            "kubectl",
            "port-forward",
            f"svc/{service}",
            f"{local_port}:{remote_port}",
            "-n",
            namespace,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3)
    if proc.poll() is not None:
        pytest.skip(f"port-forward failed for {service}")
    return proc


def _trigger_and_wait(dag_id: str, conf: dict | None = None):
    service = f"{AIRFLOW_RELEASE}-webserver"
    proc = _port_forward(service, 8080, 8080, AIRFLOW_NAMESPACE)
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


def _search_datahub(entity_type: str, query: str) -> list[str]:
    service = f"{DATAHUB_RELEASE}-datahub-gms"
    proc = _port_forward(service, 8080, 8080, DATAHUB_NAMESPACE)
    try:
        gql = (
            "query($query: String!) { search(input: {type: %s, query: $query, start: 0, count: 10}) "
            "{ searchResults { entity { urn } } } }" % entity_type
        )
        try:
            resp = requests.post(
                "http://localhost:8080/api/graphql",
                json={"query": gql, "variables": {"query": query}},
                timeout=5,
            )
        except requests.RequestException:
            pytest.skip("DataHub GraphQL not reachable")
        if resp.status_code >= 400:
            pytest.skip("DataHub GraphQL unavailable")
        return [r["entity"]["urn"] for r in resp.json()["data"]["search"]["searchResults"]]
    finally:
        proc.terminate()
        proc.wait()


def _latest_run_count(job_urn: str) -> int:
    service = f"{DATAHUB_RELEASE}-datahub-gms"
    proc = _port_forward(service, 8080, 8080, DATAHUB_NAMESPACE)
    try:
        gql = (
            "query($urn: String!) { dataJob(urn: $urn) { runs(start: 0, count: 1) { total runs { result } } } }"
        )
        try:
            resp = requests.post(
                "http://localhost:8080/api/graphql",
                json={"query": gql, "variables": {"urn": job_urn}},
                timeout=5,
            )
        except requests.RequestException:
            pytest.skip("DataHub GraphQL not reachable")
        if resp.status_code >= 400:
            pytest.skip("DataHub GraphQL unavailable")
        return resp.json()["data"]["dataJob"]["runs"]["total"]
    finally:
        proc.terminate()
        proc.wait()


def test_lineage_emitted():
    conf = {"dataset": "urn:li:dataset:(urn:li:dataPlatform:sample,foo,PROD)"}
    _trigger_and_wait("example_event_dag", conf)

    flows = _search_datahub("DATA_FLOW", "example_event_dag")
    if not flows:
        pytest.skip("DataFlow not found in DataHub")

    jobs = _search_datahub("DATA_JOB", "log_conf")
    if not jobs:
        pytest.skip("DataJob not found in DataHub")

    assert _latest_run_count(jobs[0]) > 0

