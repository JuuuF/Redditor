# User module imports
import constants as c

# Python module imports
import json
from minio import Minio

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


# Store data away
def store_data(data_dict: dict) -> bool:

    try:
        json.dump(
            data_dict,
            open("/opt/data_collection/output.json", "w"),
            ensure_ascii=False,
        )
        return True
    except Exception as e:
        print(f"[ERROR] Could not save data: {e}")
        return False
