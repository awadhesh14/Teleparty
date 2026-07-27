from pyspark.sql.functions import col, when, trim

def replace_nulls(df):
    """
    IMDb datasets often use '\\N' for null values.
    This function replaces them with actual NULLs across all string columns.
    """
    for c in df.columns:
        if dict(df.dtypes)[c] == 'string':
            df = df.withColumn(c, when(trim(col(c)) == '\\N', None).otherwise(trim(col(c))))
    return df
