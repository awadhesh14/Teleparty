import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.bash import BashOperator

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME', '/opt/airflow')
SRC_DIR = os.getenv('SRC_DIR', os.path.join(AIRFLOW_HOME, 'src'))
DATA_DIR = os.getenv('DATA_DIR', os.path.join(AIRFLOW_HOME, 'data'))

download_script = os.path.join(SRC_DIR, 'teleparty_pipeline', 'extract', 'download_kaggle.py')
spark_script = os.path.join(SRC_DIR, 'teleparty_pipeline', 'transform', 'imdb_bronze_to_silver.py')
load_script = os.path.join(SRC_DIR, 'teleparty_pipeline', 'load', 'imdb_silver_to_gold.py')

bronze_dir = os.path.join(DATA_DIR, 'source')
silver_dir = os.path.join(DATA_DIR, 'silver', 'imdb_parquet')

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
        bash_command=f'python {download_script}'
    )

    # Task 2: Spark Transform (Bronze to Silver)
    spark_transform_bronze_to_silver = SparkSubmitOperator(
        task_id='spark_transform_bronze_to_silver',
        application=spark_script,
        conn_id='spark_default',
        name='IMDb_Bronze_to_Silver',
        env_vars={'PYTHONPATH': SRC_DIR},
        application_args=[
            '--bronze_dir', bronze_dir,
            '--silver_dir', silver_dir
        ]
    )

    # Task 3: Load Silver to Gold (DuckDB)
    load_silver_to_gold_duckdb = BashOperator(
        task_id='load_silver_to_gold_duckdb',
        bash_command=f'python {load_script}'
    )

    # Set dependencies
    download_dataset >> spark_transform_bronze_to_silver >> load_silver_to_gold_duckdb

