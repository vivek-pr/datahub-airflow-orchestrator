from __future__ import annotations

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


def quality_check(**context):
    conf = context.get("dag_run").conf or {}
    dataset = conf.get("dataset")
    print(f"Running quality check for {dataset}")


with DAG(
    dag_id="example_quality_check",
    description="Simulated data quality run",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["example"],
) as dag:
    PythonOperator(task_id="run_quality_check", python_callable=quality_check)
