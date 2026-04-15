import io
import boto3
import logging
import pandas as pd
from datetime import datetime
from functools import cache
from pyspark.sql import SparkSession
from botocore.client import Config


def create_spark_session() -> SparkSession:
    builder = SparkSession.builder.appName("MinIO Connectivity Test")

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


@cache
def get_minio_client() -> boto3.client:
    client = boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        config=Config(signature_version="s3v4"),
        region_name="eu-central-1",
    )
    return client


def test_minio_connection() -> bool:
    """
    Check if connection to MinIO can be established.
    """

    try:
        client = get_minio_client()

        # List buckets to check connectivity
        response = client.list_buckets()
        buckets = [b["Name"] for b in response["Buckets"]]
        print("Available buckets:", buckets)
        return True

    except Exception as e:
        print(f"MinIO conenction failed: {str(e)}")
        return False


def test_minio_uploads():
    """
    Check if data can be uploaded to MinIO.
    """
    client: boto3.client = get_minio_client()

    sample_data = pd.DataFrame(
        {
            "id": range(12),
            "name": ["Alice", "Bob", "Charlie"] * 4,
            "age": [i * 2 + 10 for i in range(12)],
        }
    )

    # Prepare data
    csv_buffer = io.StringIO()
    sample_data.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()

    # Get filename
    sample_data_prefix = "sample_data_test_upload"
    sample_file_name = (
        f"{sample_data_prefix}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    bucket = client.list_buckets()["Buckets"][0]["Name"]

    # Upload file
    print("Uploading sample file...")
    client.put_object(
        Bucket=bucket,
        Key=sample_file_name,
        Body=csv_string.encode("utf-8"),
    )

    # List files
    bucket_files = [o["Key"] for o in client.list_objects(Bucket=bucket)["Contents"]]
    if sample_file_name in bucket_files:
        print("File uploaded successfully.")
    else:
        print("Error: File not found in bucket.")
        raise

    # Delete sample file(s)
    print("Removing sample file...")
    client.delete_object(Bucket=bucket, Key=sample_file_name)


spark = create_spark_session()
if test_minio_connection():
    print(f"MinIO connection can be established.")
else:
    print("MinIO connection cannot be established.")

test_minio_uploads()
print("Data can be uploaded to MinIO.")
