# Teleparty-Lakehouse

This repository contains a production-grade local data pipeline built to ingest, process, and analyze the 2GB IMDb dataset. 

## Architecture
The pipeline follows a simplified Medallion Architecture (Bronze -> Silver -> Gold):
1. **Ingestion (Python/Kagglehub):** Extracts raw datasets directly from Kaggle into the `data/source` folder (which serves as our `bronze` layer).
2. **Processing (Apache Spark):** Cleanses, joins, and transforms the raw data from `source`, saving it as Snappy-compressed Parquet files partitioned by `startYear` into the `silver` layer.
3. **Analytics (DuckDB):** Ingests the Silver Parquet data into a local DuckDB file (`data/gold/imdb.duckdb`) representing the `gold` layer for sub-second analytical queries.
4. **Orchestration (Apache Airflow):** Triggers the entire ELT workflow sequentially via a single DAG.

### Why DuckDB?
DuckDB was chosen as the OLAP engine because it provides industry-leading sub-second query performance for analytical workloads without the massive overhead of distributed systems like ClickHouse or Pinot. Since it is an in-process database, it integrates seamlessly into our Airflow tasks while still offering native, extremely fast parallel reads over partitioned Parquet files.

## Setup Instructions

### 1. Download Data
We've automated the download process directly within the Airflow DAG! When the DAG runs, it uses the official `kagglehub` package to fetch the Kaggle IMDb Dataset and copies the necessary TSV files into the `data/source/` directory for Spark to process.

### 2. Start the Infrastructure
We use a `Makefile` to simplify operations. Run:
```bash
make up
```
This will spin up Postgres, Apache Spark, and Apache Airflow. 

### 3. Trigger the Pipeline
Wait a minute or two for the Airflow Webserver to initialize (it dynamically installs PySpark on boot), then navigate to:
- **Airflow UI:** [http://localhost:8080](http://localhost:8080) (Credentials: `airflow`/`airflow`)

### 4. Trigger the DAG
In the Airflow UI, unpause and trigger the `dag_teleparty_imdb_elt` DAG. Watch the data flow from Bronze to Silver to Gold!
