# CONSTANTS

from os import environ


# ------------------------------------------------------------------------
# Data processor config path
DATA_PROCESSOR_CONFIG_PATH = "/opt/data_processing/config.pkl"


# ------------------------------------------------------------------------
# Loop variables
DATA_LAKE_REFRESH_TIME = int(environ.get("DATA_LAKE_REFRESH_TIME", 3))


# ------------------------------------------------------------------------
# Data Lake credentials
MINIO_ROOT_USER = environ.get("MINIO_ROOT_USER", default="minioadmin")
MINIO_ROOT_PASSWORD = environ.get("MINIO_ROOT_PASSWORD", default="minioadmin")
MINIO_BUCKET_RAW = environ.get("MINIO_BUCKET_RAW", default="raw-api-data")
