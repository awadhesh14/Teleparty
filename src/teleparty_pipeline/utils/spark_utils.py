from pyspark.sql import SparkSession

def get_spark_session(app_name: str) -> SparkSession:
    """
    Initializes and returns a SparkSession with optimized memory and partition settings.
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .config("spark.driver.memory", "1g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "10") \
        .getOrCreate()
    
    # Optional: configure logging level to reduce noise
    spark.sparkContext.setLogLevel("WARN")
    
    return spark
