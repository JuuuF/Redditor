"""
File for MinIO communication for spark jobs.
"""

import boto3
import pandas as pd
from io import BytesIO
from typing import Union
from functools import cache
from botocore.client import Config

# ------------------------------------------------------------------------
# MinIO connectivity


@cache
def get_minio_client() -> boto3.client:
    """
    Get a client for MinIO communication.
    """
    client = boto3.client(
        "s3",
        endpoint_url="http://minio:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin",
        config=Config(signature_version="s3v4"),
        region_name="eu-central-1",
    )
    return client


def list_bucket_files(
    client: Union[boto3.client, None],
    bucket: str,
) -> list[str]:
    """
    List files in MinIO bucket.
    """
    if client is None:
        client = get_minio_client()

    bucket_objects = client.list_objects(Bucket=bucket)["Contents"]
    return [o["Key"] for o in bucket_objects]


def upload_data(
    client: Union[boto3.client, None],
    bucket: str,
    filename: str,
    data: bytes,
) -> None:
    """
    Upload data to MinIO.
    """

    if client is None:
        client = get_minio_client()

    client.put_object(
        Bucket=bucket,
        Key=filename,
        Body=data,
    )


def download_data(
    client: Union[boto3.client, None],
    bucket: str,
    filename: str,
) -> bytes:
    """
    Download data from MinIO.
    """

    if client is None:
        client = get_minio_client()

    data = client.get_object(Bucket=bucket, Key=filename)["Body"].read()
    return data


def download_parquet(
    client: Union[boto3.client, None],
    bucket: str,
    filename: str,
) -> pd.DataFrame:
    """
    Download parquet data from MinIO.
    """

    data = download_data(client, bucket, filename)
    parquet_buffer = BytesIO(data)
    df = pd.read_parquet(parquet_buffer)

    return df
