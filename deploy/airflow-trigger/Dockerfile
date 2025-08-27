FROM python:3.10-slim
WORKDIR /app
COPY actions/airflow_trigger/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY actions/airflow_trigger/ .
ENTRYPOINT ["python", "action.py"]
