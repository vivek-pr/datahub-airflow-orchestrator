import os
from uuid import uuid4

import pytest
import requests

API_URL = os.getenv("AIRFLOW_API_URL")
API_TOKEN = os.getenv("AIRFLOW_API_TOKEN")


@pytest.fixture(scope="module")
def airflow_url():
    if not API_URL:
        pytest.skip("AIRFLOW_API_URL is not set")
    return API_URL.rstrip("/")


def test_api_requires_auth(airflow_url):
    dag_id = "example_bash_operator"
    resp = requests.post(
        f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns", timeout=5
    )
    assert resp.status_code == 401


def test_api_rejects_bad_token(airflow_url):
    dag_id = "example_bash_operator"
    resp = requests.post(
        f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns",
        headers={"Authorization": "Bearer wrong"},
        json={"dag_run_id": f"dev-{uuid4()}"},
        timeout=5,
    )
    assert resp.status_code == 403


def test_api_accepts_token(airflow_url):
    if not API_TOKEN:
        pytest.skip("AIRFLOW_API_TOKEN is required")
    dag_id = "example_bash_operator"
    resp = requests.post(
        f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={"dag_run_id": f"dev-{uuid4()}"},
        timeout=5,
    )
    assert 200 <= resp.status_code < 400
