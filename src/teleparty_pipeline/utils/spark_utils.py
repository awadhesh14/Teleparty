from pyspark.sql import SparkSession

def get_spark_session(app_name: str) -> SparkSession:
    """
    Initializes and returns a SparkSession.
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()
    
    # Optional: configure logging level to reduce noise
    spark.sparkContext.setLogLevel("WARN")
    
    return spark
