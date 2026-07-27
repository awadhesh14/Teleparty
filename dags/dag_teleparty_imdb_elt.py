from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'teleparty',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dag_teleparty_imdb_elt',
    default_args=default_args,
    description='IMDb Lakehouse to OLAP pipeline',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['teleparty', 'imdb', 'elt'],
) as dag:

    # Task 0: Download Dataset via kagglehub
    download_dataset = BashOperator(
        task_id='download_dataset',
        bash_command='python /opt/airflow/src/teleparty_pipeline/extract/download_kaggle.py'
    )

    # Task 2: Spark Transform (Bronze to Silver)
    spark_transform_bronze_to_silver = SparkSubmitOperator(
        task_id='spark_transform_bronze_to_silver',
        application='/opt/airflow/src/teleparty_pipeline/transform/imdb_bronze_to_silver.py',
        conn_id='spark_default',
        name='IMDb_Bronze_to_Silver',
        env_vars={'PYTHONPATH': '/opt/airflow/src'},
        application_args=[
            '--bronze_dir', '/opt/airflow/data/source',
            '--silver_dir', '/opt/airflow/data/silver/imdb_parquet'
        ]
    )

    # Task 3: Load Silver to Gold (DuckDB)
    load_silver_to_gold_duckdb = BashOperator(
        task_id='load_silver_to_gold_duckdb',
        bash_command='python /opt/airflow/src/teleparty_pipeline/load/imdb_silver_to_gold.py'
    )

    # Set dependencies
    download_dataset >> spark_transform_bronze_to_silver >> load_silver_to_gold_duckdb
