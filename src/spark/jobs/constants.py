from os import environ

MINIO_ROOT_USER = environ.get("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = environ.get("MINIO_ROOT_PASSWORD", "minioadmin")
MINIO_BUCKET_PROCESSED = environ.get("MINIO_BUCKET_PROCESSED", "processed-data")
