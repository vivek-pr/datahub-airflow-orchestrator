from __future__ import annotations

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def log_conf(**context):
    conf = context.get("dag_run").conf or {}
    print(f"Received payload: {conf}")


with DAG(
    dag_id="example_event_dag",
    description="Logs incoming conf payload from DataHub trigger",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["example"],
) as dag:
    PythonOperator(task_id="log_conf", python_callable=log_conf)
