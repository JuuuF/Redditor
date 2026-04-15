import logging
from pyspark.sql import SparkSession


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


def test_minio_connection() -> bool:
    """
    Check if connection to MinIO can be established.
    """
    import boto3
    from botocore.client import Config

    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url="http://minio:9000",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"),
            region_name="eu-central-1",
        )

        # List buckets to check connectivity
        response = s3_client.list_buckets()
        buckets = [b["Name"] for b in response["Buckets"]]
        print("Available buckets:", buckets)
        return True

    except Exception as e:
        print(f"MinIO conenction failed: {str(e)}")
        return False


spark = create_spark_session()
if test_minio_connection():
    print(f"MinIO connection can be established.")
else:
    print("MinIO connection cannot be established.")
