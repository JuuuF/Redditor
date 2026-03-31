# User module imports
import constants as c

# Python module imports
import json
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from minio import Minio
from io import BytesIO
from datetime import datetime

# ------------------------------------------------------------------------
# Initialization

# Initialize Client
client = Minio(
    endpoint="minio:9000",
    access_key=c.MINIO_ROOT_USER,
    secret_key=c.MINIO_ROOT_PASSWORD,
    secure=False,
)


# Initialize bucket if not existing
buckets = [b.name for b in client.list_buckets()]
if not c.MINIO_BUCKET_RAW in buckets:
    client.make_bucket(c.MINIO_BUCKET_RAW)
    print(f"Created MinIO bucket {c.MINIO_BUCKET_RAW} for raw API data.", flush=True)

# ------------------------------------------------------------------------


def get_storage_path() -> str:
    now = datetime.now()

    base_dir = "raw"
    date_dir = f"date={now:%Y-%m-%d}"
    data_file = f"data_{now:%Y-%m-%d_%H-%M-%S}.parquet"
    return "/".join([base_dir, date_dir, data_file])


def convert_to_parquet_buffer(data_dict: dict) -> BytesIO:

    # Normalize json
    df = pd.json_normalize(data_dict)

    # Convert to parquet
    table = pa.Table.from_pandas(df)
    output_buffer = BytesIO()
    pq.write_table(table, output_buffer)
    output_buffer.seek(0)

    return output_buffer


# Store data away
def store_data(data_dict: dict) -> None:

    # Convert data dictionary to parquet buffer
    data = convert_to_parquet_buffer(data_dict)

    # Get target location
    object_name = get_storage_path()

    # Upload to bucket
    client.put_object(
        c.MINIO_BUCKET_RAW,
        object_name,
        data,
        length=len(data.getvalue()),
    )


# Store data as JSON file
def store_data_file(
    data_dict: dict,
    filepath: str = "/opt/data_collection/output.json",
) -> bool:

    try:
        json.dump(
            data_dict,
            open(filepath, "w"),
            ensure_ascii=False,
        )
        return True
    except Exception as e:
        print(f"[ERROR] Could not save data: {e}")
        return False
