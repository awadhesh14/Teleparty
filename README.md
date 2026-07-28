# Teleparty IMDb Lakehouse to OLAP Pipeline

Mock local data pipeline built for the **Teleparty Data Engineering Challenge**. 

This project ingests, cleanses, partitions, and loads the 2GB Kaggle IMDb dataset using an end-to-end **Medallion Architecture (Bronze → Silver → Gold)** orchestrated with **Apache Airflow**, transformed via **Apache Spark**, loaded into a **DuckDB OLAP engine**, and surfaced through a **Rill Developer BI UI**.

---

## 🏛️ Architecture & Data Flow

The solution moves beyond static batch processing to enable sub-second query performance over millions of records:

```
┌─────────────────┐       ┌───────────────────────────┐       ┌─────────────────────────────────────┐       ┌───────────────────────────────────┐
│   Kaggle API    │  ───► │   Bronze (Raw Ingestion)  │  ───► │      Silver (Lakehouse Storage)     │  ───► │       Gold (OLAP & Analytics)     │
│   (kagglehub)   │       │   data/source/*.tsv       │       │ data/silver/imdb_parquet (Partition)│       │  DuckDB (db) & Rill Developer UI  │
└─────────────────┘       └───────────────────────────┘       └─────────────────────────────────────┘       └───────────────────────────────────┘
```

1. **Bronze Layer (Ingestion)**: Automatically downloads raw IMDb datasets (`title.basics`, `title.ratings`, `title.episode`) directly from Kaggle via `kagglehub`.
2. **Silver Layer (Processing & Partitioning)**: A PySpark job cleanses null markers (`\N` → `NULL`), standardizes data types, performs outer-joins across datasets, and writes Snappy-compressed Parquet files partitioned by `startYear`.
3. **Gold Layer (OLAP Engine)**: Ingests the Silver Parquet dataset into **DuckDB** using native vectorized bulk insertion.
4. **BI & Analytics Layer (Rill Developer)**: Connects directly to the Lakehouse storage to serve real-time dashboard analytics.
5. **Orchestration**: Fully containerized **Apache Airflow** pipeline managing task execution and retries end-to-end.

---

## 📋 Evaluation Deliverables Summary

| Requirement | Deliverable Location | Description |
| :--- | :--- | :--- |
| **Infrastructure** | [`docker-compose.yml`](docker-compose.yml), [`Dockerfile`](Dockerfile), [`Dockerfile.rill`](Dockerfile.rill) | Orchestrates Spark Master/Worker, Airflow Webserver/Scheduler, Postgres metastore, and Rill UI. |
| **Ingestion Script** | [`src/teleparty_pipeline/extract/download_kaggle.py`](src/teleparty_pipeline/extract/download_kaggle.py) | Downloads and verifies raw Kaggle IMDb dataset into the Bronze layer with automated retries. |
| **PySpark ETL Job** | [`src/teleparty_pipeline/transform/imdb_bronze_to_silver.py`](src/teleparty_pipeline/transform/imdb_bronze_to_silver.py) | Spark job cleansing raw TSV data and saving Snappy Parquet partitioned by `startYear`. |
| **OLAP Loader Script** | [`src/teleparty_pipeline/load/imdb_silver_to_gold.py`](src/teleparty_pipeline/load/imdb_silver_to_gold.py) | Python script bulk-loading Silver Parquet data into DuckDB Gold tables. |
| **DDL Schema** | [`src/teleparty_pipeline/models/create_imdb_gold.sql`](src/teleparty_pipeline/models/create_imdb_gold.sql) | DDL script defining table structures and primary key constraints (`tconst`). |
| **Airflow DAG** | [`dags/dag_teleparty_imdb_elt.py`](dags/dag_teleparty_imdb_elt.py) | End-to-end DAG orchestrating Extraction, Spark Transformation, and DuckDB Loading. |
| **AI Prompts Log** | [`PROMPTS.md`](PROMPTS.md) | Log of LLM prompts used during interactive pair programming. |

---

## ⚡ Performance Note & OLAP Engine Rationale

### Why DuckDB + Rill Developer?
For this local lakehouse architecture, **DuckDB** was chosen as the core OLAP engine for several key reasons:

1. **Sub-Second Vectorized Query Performance**: DuckDB uses a vectorized columnar query execution engine specifically designed for OLAP workloads. It evaluates queries over millions of rows in milliseconds, outperforming standalone Spark sessions for single-node analytics.
2. **Native Parquet Integration & Zero-Copy Execution**: DuckDB scans partitioned Hive-style Parquet files directly from disk with automatic predicate pushdown and partition pruning.
3. **Zero Cluster Management Overhead**: Unlike distributed OLAP engines (e.g., ClickHouse, Apache Pinot, or StarRocks) which require multi-gigabyte memory footprints, ZooKeeper/Keeper dependencies, and complex cluster management, DuckDB runs in-process with minimal resource overhead—ideal for both lightweight local development and containerized production tasks.
4. **Interactive BI Layer with Rill**: To extend the pipeline beyond basic CLI scripts, **Rill Developer** is integrated on top of DuckDB/Parquet storage. It provides analysts with instant, sub-second visual slice-and-dice metrics views without needing manual SQL boilerplate.

### Partitioning Strategy (`startYear`)
- **Rationale**: Teleparty user activity and viewership analysis frequently filter or aggregate content by temporal dimensions (e.g., release year, recent release trends, vintage content).
- **Execution**: Partitioning the Silver layer by `startYear` ensures **partition pruning** during query execution. When analysts query titles for specific release years, both Spark and DuckDB bypass scanning unrelated data partitions.

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Docker & Docker Compose
- `make` (optional, for helper commands)

### 2. Launch Infrastructure
Spin up all services (Postgres, Airflow, Spark Master/Worker, Rill UI) with a single command:
```bash
make up
```

### 3. Execution & Monitoring
1. **Open Airflow Webserver**: Navigate to [http://localhost:8080](http://localhost:8080) (Credentials: `airflow` / `airflow`).
2. **Trigger the DAG**: Unpause and trigger `dag_teleparty_imdb_elt`.
   - **Task 1 (`download_dataset`)**: Automated Kaggle dataset extraction into `/data/source`.
   - **Task 2 (`spark_transform_bronze_to_silver`)**: PySpark job executed on the Spark cluster (`spark://spark-master:7077`).
   - **Task 3 (`load_silver_to_gold_duckdb`)**: DuckDB bulk ingestion into `/data/gold/imdb.duckdb`.

3. **Explore BI Analytics**: Navigate to the Rill UI at [http://localhost:8082](http://localhost:8082) for interactive metrics visualization.

### 4. Cleanup
To stop containers and clear local data volumes:
```bash
make clean
```

---

## 📁 Repository Structure

```
Teleparty-Lakehouse/
├── dags/
│   └── dag_teleparty_imdb_elt.py       # Airflow DAG definition
├── data/                                # Data storage directory (Git ignored)
│   ├── source/                          # Bronze layer (Raw Kaggle TSV files)
│   ├── silver/                          # Silver layer (Partitioned Snappy Parquet)
│   └── gold/                            # Gold layer (DuckDB OLAP database)
├── rill/                                # Rill Developer BI project configuration
│   ├── metrics/                         # Rill metrics views definitions
│   ├── sources/                         # Rill data sources (DuckDB / Parquet connection)
│   └── rill.yaml                        # Rill project spec
├── src/teleparty_pipeline/              # Modular pipeline Python package
│   ├── extract/                         # Ingestion scripts (download_kaggle.py)
│   ├── transform/                       # Spark ETL scripts & cleansers
│   ├── load/                            # OLAP loading scripts (imdb_silver_to_gold.py)
│   ├── models/                          # DDL schemas (create_imdb_gold.sql)
│   └── utils/                           # Shared utility modules (Spark session setup)
├── Dockerfile                           # Custom Airflow container image
├── Dockerfile.rill                      # Rill Developer container image
├── docker-compose.yml                   # Services orchestration (Airflow, Spark, Rill, Postgres)
├── Makefile                             # CLI helper targets (make up, make down, make clean)
├── PROMPTS.md                           # AI pair programming prompt record
└── README.md                            # Evaluation documentation
```
