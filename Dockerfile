FROM apache/airflow:2.9.2

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends default-jre-headless \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

USER airflow
