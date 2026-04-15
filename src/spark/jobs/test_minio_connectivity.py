import io
import boto3
import logging
import pandas as pd
from datetime import datetime
from functools import cache
from pyspark.sql import SparkSession
from botocore.client import Config

# ------------------------------------------------------------------------
# Setup functions


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


# ------------------------------------------------------------------------
# Test functions


def test_minio_connection() -> None:
    """
    Check if connection to MinIO can be established.
    """

    try:
        client = get_minio_client()

        # List buckets to check connectivity
        response = client.list_buckets()
        buckets = [b["Name"] for b in response["Buckets"]]
        print("Available buckets:", buckets)

    except Exception as e:
        print(f"Error: MinIO conenction failed: {str(e)}")
        raise


def test_minio_uploads() -> None:
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

    # Get filename
    sample_data_prefix = "sample_data_test_upload"
    sample_file_name = (
        f"{sample_data_prefix}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    bucket = client.list_buckets()["Buckets"][0]["Name"]

    def get_bucket_files() -> list[str]:
        return [o["Key"] for o in client.list_objects(Bucket=bucket)["Contents"]]

    def test_csv_upload() -> None:
        # Prepare data
        csv_buffer = io.StringIO()
        sample_data.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        csv_file = sample_file_name + ".csv"

        # Upload file
        print("Uploading CSV sample file...")
        client.put_object(
            Bucket=bucket,
            Key=csv_file,
            Body=csv_string.encode("utf-8"),
        )

        # Check upload
        if csv_file in get_bucket_files():
            print("File uploaded successfully.")
        else:
            print("Error while uploading file to bucket.")
            raise

        # Download and check data
        downloaded_data = client.get_object(Bucket=bucket, Key=csv_file)["Body"]
        csv_data = downloaded_data.read().decode("utf-8")
        csv_buffer = io.StringIO(csv_data)
        df = pd.read_csv(csv_buffer)

        if (df == sample_data).all().all():
            print("Sample data and downloaded data match.")
        else:
            print("Sample data does not match downloaded data.")
            raise

    def test_parquet_upload() -> None:
        # Prepare data
        parquet_buffer = io.BytesIO()
        sample_data.to_parquet(parquet_buffer, compression="zstd")
        parquet_data = parquet_buffer.getvalue()
        parquet_file = sample_file_name + ".parquet"

        # Upload file
        print("Uploading Parquet sample file...")
        client.put_object(
            Bucket=bucket,
            Key=parquet_file,
            Body=parquet_data,
        )

        # Check upload
        if parquet_file in get_bucket_files():
            print("File uploaded successfully.")
        else:
            print("Error while uploading file to bucket.")
            raise

        # Download and check data
        downloaded_data = client.get_object(Bucket=bucket, Key=parquet_file)["Body"]
        parquet_data = downloaded_data.read()
        parquet_buffer = io.BytesIO(parquet_data)
        df = pd.read_parquet(parquet_buffer)

        if (df == sample_data).all().all():
            print("Sample data and downloaded data match.")
        else:
            print("Sample data does not match downloaded data.")
            raise

    test_csv_upload()
    test_parquet_upload()

    # Delete sample files
    print("Removing sample file...")
    for sample_file in [
        file for file in get_bucket_files() if file.startswith(sample_data_prefix)
    ]:
        client.delete_object(Bucket=bucket, Key=sample_file)


# ------------------------------------------------------------------------
# Execution code


def main() -> None:
    spark = create_spark_session()

    test_minio_connection()
    print(f"MinIO connection can be established.")

    test_minio_uploads()
    print("Data can be uploaded to MinIO.")


if __name__ == "__main__":
    main()
