import os
from uuid import uuid4

import pytest
import requests

API_URL = os.getenv("AIRFLOW_API_URL")
API_USER = os.getenv("AIRFLOW_API_USERNAME")
API_PASSWORD = os.getenv("AIRFLOW_API_PASSWORD")


@pytest.fixture(scope="module")
def airflow_url():
    if not API_URL:
        pytest.skip("AIRFLOW_API_URL is not set")
    return API_URL.rstrip("/")


def test_api_requires_auth(airflow_url):
    dag_id = "example_bash_operator"
    resp = requests.post(f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns")
    assert resp.status_code == 401


def test_api_accepts_basic_auth(airflow_url):
    if not API_USER or not API_PASSWORD:
        pytest.skip("AIRFLOW_API_USERNAME and AIRFLOW_API_PASSWORD are required")
    dag_id = "example_bash_operator"
    resp = requests.post(
        f"{airflow_url}/api/v1/dags/{dag_id}/dagRuns",
        auth=(API_USER, API_PASSWORD),
        json={"dag_run_id": f"dev-{uuid4()}"},
    )
    assert 200 <= resp.status_code < 400
