FROM apache/airflow:2.10.4

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends default-jre-headless build-essential \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

USER airflow
ARG AIRFLOW_VERSION=2.10.4
RUN PYTHON_VERSION="$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1-2)" \
 && CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt" \
 && pip install --no-cache-dir "apache-airflow-providers-apache-spark" "pyspark" "duckdb" "kagglehub" --constraint "${CONSTRAINT_URL}"



