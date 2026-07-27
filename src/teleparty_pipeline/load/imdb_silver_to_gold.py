import duckdb
import argparse
import os

def load_silver_to_gold(silver_dir: str, gold_db_path: str, ddl_path: str):
    print(f"Connecting to DuckDB at {gold_db_path}")
    con = duckdb.connect(gold_db_path)

    print(f"Applying DDL from {ddl_path}")
    with open(ddl_path, 'r') as f:
        ddl_sql = f.read()
    con.execute(ddl_sql)

    # In DuckDB, we can read a directory of partitioned parquet files natively
    parquet_glob = os.path.join(silver_dir, "**/*.parquet")
    
    print(f"Loading data from {parquet_glob} into Gold layer")
    # For a simple pipeline, we'll clear the table before inserting
    con.execute("DELETE FROM imdb_titles")
    
    # We use TRY_CAST or handle typing gracefully since Parquet schema is string based for some from Spark
    insert_sql = f"""
    INSERT INTO imdb_titles
    SELECT 
        tconst, 
        titleType, 
        primaryTitle, 
        originalTitle, 
        TRY_CAST(isAdult AS BOOLEAN), 
        TRY_CAST(startYear AS INTEGER), 
        TRY_CAST(endYear AS INTEGER), 
        TRY_CAST(runtimeMinutes AS INTEGER), 
        genres, 
        TRY_CAST(averageRating AS DOUBLE), 
        TRY_CAST(numVotes AS INTEGER), 
        parentTconst, 
        TRY_CAST(seasonNumber AS INTEGER), 
        TRY_CAST(episodeNumber AS INTEGER)
    FROM read_parquet('{parquet_glob}', hive_partitioning=1)
    """
    con.execute(insert_sql)
    
    # Run a quick validation
    count = con.execute("SELECT COUNT(*) FROM imdb_titles").fetchone()[0]
    print(f"Successfully loaded {count} rows into imdb_titles in the Gold layer.")
    
    con.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Silver to Gold DuckDB Job")
    parser.add_argument("--silver_dir", type=str, default="/opt/airflow/data/silver/imdb_parquet", help="Path to silver data")
    parser.add_argument("--gold_db", type=str, default="/opt/airflow/data/gold/imdb.duckdb", help="Path to duckdb database")
    parser.add_argument("--ddl", type=str, default="/opt/airflow/src/teleparty_pipeline/models/create_imdb_gold.sql", help="Path to DDL")
    args = parser.parse_args()
    
    load_silver_to_gold(args.silver_dir, args.gold_db, args.ddl)
