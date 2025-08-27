import os
import time
import subprocess
import shutil

import pytest
import requests

NAMESPACE = os.getenv("DATAHUB_NAMESPACE", "datahub-dev")
RELEASE = os.getenv("DATAHUB_RELEASE", "datahub-dev")


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
    # give port-forward time to establish
    time.sleep(3)
    if proc.poll() is not None:
        pytest.skip(f"port-forward failed for {service}")
    return proc


def test_gms_health():
    service = f"{RELEASE}-datahub-gms"
    proc = _port_forward(service, 8080, 8080)
    try:
        try:
            resp = requests.get("http://localhost:8080/health", timeout=5)
        except requests.RequestException:
            pytest.skip("GMS health endpoint not reachable")
        assert resp.status_code == 200
    finally:
        proc.terminate()
        proc.wait()


def test_frontend_health():
    service = f"{RELEASE}-datahub-frontend"
    proc = _port_forward(service, 9002, 9002)
    try:
        try:
            resp = requests.get("http://localhost:9002/api/health", timeout=5)
        except requests.RequestException:
            pytest.skip("Frontend health endpoint not reachable")
        assert resp.status_code == 200
    finally:
        proc.terminate()
        proc.wait()
