import os
import sys
import argparse

# Ensure src path is available for imports when executed via spark-submit
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from teleparty_pipeline.utils.spark_utils import get_spark_session
from teleparty_pipeline.transform.cleansers import replace_nulls
from pyspark.sql.functions import col

def process_imdb_data(bronze_dir: str, silver_dir: str):
    spark = get_spark_session("IMDb_Bronze_to_Silver")

    print(f"Reading from bronze directory: {bronze_dir}")
    
    titles_path = os.path.join(bronze_dir, "title.basics.tsv")
    ratings_path = os.path.join(bronze_dir, "title.ratings.tsv")
    episodes_path = os.path.join(bronze_dir, "title.episode.tsv")

    print("Processing Titles...")
    titles_df = spark.read.csv(titles_path, sep='\t', header=True, inferSchema=True)
    titles_df = replace_nulls(titles_df)
    titles_df = titles_df.withColumn("startYear", col("startYear").cast("int"))

    print("Processing Ratings...")
    ratings_df = spark.read.csv(ratings_path, sep='\t', header=True, inferSchema=True)
    ratings_df = replace_nulls(ratings_df)
    
    print("Processing Episodes...")
    episodes_df = spark.read.csv(episodes_path, sep='\t', header=True, inferSchema=True)
    episodes_df = replace_nulls(episodes_df)

    print("Joining datasets...")
    joined_df = titles_df.join(ratings_df, on="tconst", how="left")
    joined_df = joined_df.join(episodes_df, on="tconst", how="left")
    
    print(f"Writing to silver directory: {silver_dir}")
    (joined_df.write
        .mode("overwrite")
        .partitionBy("startYear")
        .option("compression", "snappy")
        .parquet(silver_dir))
    
    print("Bronze to Silver processing completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bronze to Silver Spark Job")
    parser.add_argument("--bronze_dir", type=str, default="/data/bronze", help="Path to bronze data")
    parser.add_argument("--silver_dir", type=str, default="/data/silver/imdb_parquet", help="Path to silver output")
    args = parser.parse_args()
    
    process_imdb_data(args.bronze_dir, args.silver_dir)
