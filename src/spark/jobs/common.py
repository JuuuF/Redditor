"""
File for common spark job functionality.
"""

import pandas as pd
from io import BytesIO
from pyspark.sql import SparkSession

# ------------------------------------------------------------------------
# General


def create_spark_session(app_name: str) -> SparkSession:
    builder = SparkSession.builder.appName(app_name)

    # Init MinIO connectivity
    #fmt: off
    builder = builder \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    
    builder = builder \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescencePartitions.enabled", "true")
    # fmt: on

    spark = builder.getOrCreate()
    return spark


def df_to_parquet_data(df: pd.DataFrame) -> bytes:
    """
    Transform a DataFrame into bytes for upload to MinIO.
    """
    buffer = BytesIO()
    df.to_parquet(buffer, compression="zstd")
    data = buffer.getvalue()
    return data


def parquet_data_to_df(data: bytes) -> pd.DataFrame:
    """
    Transform parquet bytes data back to DataFrame.
    """
    buffer = BytesIO(data)
    df = pd.read_parquet(buffer)
    return df
