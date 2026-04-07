# User module imports
import constants as c
from schema import fetched_data_dtypes

# Python module imports
import os
import json
import pickle
import polars as pl
from io import BytesIO
from time import sleep
from zlib import decompress
from minio import Minio
from typing import Self, TypeVar, Type, Callable
from hashlib import md5
from pathlib import Path
from functools import wraps

T = TypeVar("T", bound="ConfigLoadable")

client = None


def init_client(user: str, password: str):
    global client
    client = Minio(
        endpoint="minio:9000",
        access_key=c.MINIO_ROOT_USER,
        secret_key=c.MINIO_ROOT_PASSWORD,
        secure=False,
    )

    # Create processed data bucket if not available
    if not client.bucket_exists(c.MINIO_BUCKET_PROCESSED):
        client.make_bucket(bucket_name=c.MINIO_BUCKET_PROCESSED)
        print(
            f"Created MinIO bucket {c.MINIO_BUCKET_PROCESSED} for processed data.",
            flush=True,
        )


class ConfigLoadable:
    """
    Class template to store and load class instances, as defined by its member variables.
    """

    def __init__(self: Self, /, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_config(cls: Type[T], config_path: Path | str) -> Self:
        """
        Initialize an instance using a config file path.
        """
        with open(config_path, "rb") as f:
            configs = pickle.load(f)
        return cls(**configs)

    def get_config(self: Self) -> dict:
        """
        Get the configuration of the class instance.
        """
        return self.__dict__

    def save_config(self: Self, config_filepath: Path | str) -> None:
        """
        Save the config of the class instance to a file.
        """
        with open(config_filepath, "wb") as f:
            pickle.dump(self.get_config(), f)


def save_state(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self: Self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        self.save()
        return res

    return wrapper


class SampleProcessor(ConfigLoadable):

    def __init__(
        self: Self,
        data_lake_user: str | None = None,
        data_lake_password: str | None = None,
        data_lake_bucket: str | None = None,
        hashed_processed_files: set[str] | None = None,
        **kwargs,
    ) -> None:

        super().__init__(**kwargs)
        self.data_lake_user = data_lake_user or c.MINIO_ROOT_USER
        self.data_lake_password = data_lake_password or c.MINIO_ROOT_PASSWORD
        self.data_lake_bucket = data_lake_bucket or c.MINIO_BUCKET_RAW
        self.hashed_processed_files = hashed_processed_files or set()

        init_client(self.data_lake_user, self.data_lake_password)

    # --------------------------------------------------------------------
    # Data Lake communication

    def wait_for_data_lake(self: Self) -> None:
        """
        In case the data lake is not set up, we wait until it is.
        """
        wait_delay = 1
        while not client.bucket_exists(self.data_lake_bucket):
            print(
                f"Waiting for the data lake to have a bucket called {self.data_lake_bucket}...",
                flush=True,
            )
            sleep(wait_delay)
            wait_delay = min(wait_delay + 0.2, 10)

        if wait_delay != 1:
            print("Found bucket!", flush=True)

    def get_raw_file_from_data_lake(
        self: Self,
        filepath: str,
    ) -> str | dict:
        """
        Retrieve a raw file from the data lake using its file path.
        """
        # Read compressed data
        response = client.get_object(c.MINIO_BUCKET_RAW, filepath)
        # Convert back to json string
        json_data = decompress(response.read()).decode()

        # Convert to dict
        data_dict = json.loads(json_data)
        return data_dict

    def get_all_file_names_in_data_lake(self: Self) -> list[str]:
        """
        Get a list of all files present in the data lake.

        The files are sorted by their name (= their date).
        """
        objects = client.list_objects(
            bucket_name=self.data_lake_bucket,
            prefix="raw",
            recursive=True,
        )
        return sorted([f.object_name for f in objects])

    def get_oldest_unprocessed_file(self: Self) -> str | None:
        """
        Query the data lake for the oldest non-processed file.
        """
        # Get all files
        all_files = self.get_all_file_names_in_data_lake()

        # Return if there are no files in the data lake
        if len(all_files) == 0:
            return None

        # Return if everything's processed
        if self.is_filename_processed(all_files[-1]):
            return None

        # Binary search under the assumption that files are processed by date
        def get_mid(l: int, u: int) -> int:
            return l + (u - l) // 2

        def update_lmu(l: int, m: int, u: int, use_upper: bool) -> list[int, int, int]:
            if use_upper:
                return m, get_mid(m, u), u
            return l, get_mid(l, m), m

        lower = 0
        upper = len(all_files) - 1
        midpt = get_mid(lower, upper)

        while lower + 1 < upper:
            is_midpt_processed = self.is_filename_processed(all_files[midpt])
            lower, midpt, upper = update_lmu(lower, midpt, upper, is_midpt_processed)

        if not self.is_filename_processed(all_files[lower]):
            return all_files[lower]

        return all_files[upper]

    def data_lake_has_unprocessed_files(self: Self) -> bool:
        """
        Check to see if there are any unprocessed raw files in the data lake.
        """
        # TODO: use meta data database for this logic
        data_lake_files = self.get_all_file_names_in_data_lake()
        return len(data_lake_files) > 0 and not self.is_filename_processed(
            data_lake_files[-1]
        )

    # --------------------------------------------------------------------
    # Database communication

    def upload_single_df(self: Self, df: pl.DataFrame, filepath: str) -> None:
        """
        Store a single Dataframe in the processed data lake bucket.
        """
        buffer = BytesIO()
        df.write_parquet(buffer, compression="zstd")
        buffer.seek(0)
        client.put_object(
            bucket_name=c.MINIO_BUCKET_PROCESSED,
            object_name=filepath,
            data=buffer,
            length=len(buffer.getvalue()),
        )

    def upload_processed_data(
        self: Self,
        df_arrivals: pl.DataFrame,
        df_routes: pl.DataFrame,
        src_file: str,
    ) -> None:
        """
        Store the collected halts in the database.
        """

        # Get filepaths
        date = [f for f in src_file.split("/") if f.startswith("date=")][0]
        filename = (
            src_file.split("/")[-1]
            .replace(".data", ".parquet")
            .replace("file", "{type}")
        )
        filepath_arrivals = str(
            Path("processed") / date / filename.format(type="arrivals")
        )
        filepath_routes = str(Path("processed") / date / filename.format(type="routes"))

        # Upload files
        self.upload_single_df(df_arrivals, filepath_arrivals)
        self.upload_single_df(df_routes, filepath_routes)

        return [
            f"{c.MINIO_BUCKET_PROCESSED}:{file}"
            for file in [filepath_arrivals, filepath_routes]
        ]

    # --------------------------------------------------------------------
    # File Processing

    def extract_arrivals(self: Self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Extract arrival information from general DataFrame.
        """

        # Unroll past and current/future arrivals
        df_arrivals = (
            df.with_columns(arrivals=pl.concat_list(["actual", "old"]))
            .explode("arrivals")
            .unnest("arrivals")
            .drop(["actual", "old", "routes"])
            .filter(~pl.col("routeId").is_null())  # Remove entries without arrivals
        )

        # Uniform time format
        df_arrivals = df_arrivals.with_columns(
            pl.from_epoch("firstPassageTime", time_unit="ms")
            .dt.replace_time_zone("utc")
            .dt.convert_time_zone("Europe/Berlin"),
            pl.from_epoch("lastPassageTime", time_unit="ms")
            .dt.replace_time_zone("utc")
            .dt.convert_time_zone("Europe/Berlin"),
            pl.col("fetchTime").str.to_datetime(time_zone="Europe/Berlin"),
        )

        return df_arrivals

    def extract_routes(self: Self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Extract route information from general DataFrame.
        """

        df_routes = (
            df.select("routes")
            .explode("routes")
            .unnest("routes")
            .unique()  # Remove duplicates
            .filter(~pl.all_horizontal(pl.all().is_null()))  # Remove nulls
        )

        return df_routes

    def convert_data_to_dataframe(self: Self, data: dict) -> pl.DataFrame:
        """
        Convert data dict to pl.DataFrame with consistent schema.
        """

        # Convert to DataFrame
        df = pl.DataFrame(data["fetched_data"])

        # Enforce correct data types
        df = df.cast(fetched_data_dtypes)

        return df

    def process_single_file(self: Self, filename: str) -> None:
        """
        Process a single file from the data lake, refered to by its file path.
        """

        log_id = f"[{int(hash(filename) % 1e6):06d}]"
        print(log_id, f"Processing file '{filename}'...", flush=True)

        data = self.get_raw_file_from_data_lake(filename)
        df = self.convert_data_to_dataframe(data)
        df_arrivals = self.extract_arrivals(df)
        df_routes = self.extract_routes(df)
        uploaded_files = self.upload_processed_data(
            df_arrivals, df_routes, src_file=filename
        )

        self.mark_filename_as_processed(filename)

        print(log_id, "Uploaded files:", ", ".join(uploaded_files), flush=True)

    def update_database(self: Self) -> None:
        """
        Check all files in the data lake and process files with content not yet present in the database.
        """

        # Return if everything's up to date
        if (start_file := self.get_oldest_unprocessed_file()) is None:
            return

        all_files = self.get_all_file_names_in_data_lake()
        start_index = all_files.index(start_file)
        for file in all_files[start_index:]:
            self.process_single_file(file)

    # --------------------------------------------------------------------
    # Hashing and storage functions

    def _get_filename_hash(self: Self, filename: str) -> str:
        return md5(filename.encode()).hexdigest()

    @save_state
    def mark_filename_as_processed(self: Self, filename: str) -> None:
        self.hashed_processed_files.add(self._get_filename_hash(filename))

    def is_filename_processed(self: Self, filename: str) -> bool:
        return self._get_filename_hash(filename) in self.hashed_processed_files

    # --------------------------------------------------------------------
    # Config saving and loading

    def save(self: Self) -> None:
        """
        Save to the default data processor config file path.
        """
        # TODO: transfer this logic into a meta data database
        self.save_config(c.DATA_PROCESSOR_CONFIG_PATH)

    @classmethod
    def load(cls) -> Self:
        """
        Load from the default data processor config file path.
        """
        if not os.path.exists(c.DATA_PROCESSOR_CONFIG_PATH):
            print("Could not load SampleProcessor from file. Using default instance.")
            return cls()

        print(f"Loading SampleProcessor from file: {c.DATA_PROCESSOR_CONFIG_PATH}.")
        return cls.from_config(c.DATA_PROCESSOR_CONFIG_PATH)
