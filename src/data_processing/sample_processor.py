# User module imports
import constants as c

# Python module imports
import os
import pickle
from pathlib import Path
from typing import Self, Any, TypeVar, Type
from hashlib import md5
from minio import Minio

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


class SampleProcessor(ConfigLoadable):
    def __init__(
        self: Self,
        data_lake_user: str | None = None,
        data_lake_password: str | None = None,
        data_lake_bucket: str | None = None,
        processed_files: set[str] | None = None,
        **kwargs,
    ) -> None:

        super().__init__(**kwargs)
        self.data_lake_user = data_lake_user or c.MINIO_ROOT_USER
        self.data_lake_password = data_lake_password or c.MINIO_ROOT_PASSWORD
        self.data_lake_bucket = data_lake_bucket or c.MINIO_BUCKET_RAW
        self.processed_files = processed_files or set()

        init_client(self.data_lake_user, self.data_lake_password)

    # --------------------------------------------------------------------
    # Data Lake communication

    def get_raw_file_from_data_lake(self: Self, filepath: str) -> dict:
        """
        Retrieve a raw file from the data lake using its file path.
        """
        # TODO: implement
        return {}

    def get_all_files_in_data_lake(self: Self) -> list[str]:
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
        all_files = self.get_all_files_in_data_lake()
        
        # Return if there are no files in the data lake
        if len(all_files) == 0:
            return None

        # Return if everything's processed
        if self.is_processed(all_files[-1]):
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
        # print(lower, midpt, upper)

        while lower + 1 < upper:
            is_midpt_processed = self.is_processed(all_files[midpt])
            lower, midpt, upper = update_lmu(lower, midpt, upper, is_midpt_processed)

        if not self.is_processed(all_files[lower]):
            return all_files[lower]
        
        return all_files[upper]

    def get_unprocessed_files_in_data_lake(self: Self) -> list[str]:
        """
        Get a list of all unprocessed files in the data lake.
        """
        # TODO: implement
        return []

    # --------------------------------------------------------------------
    # File Processing

    def process_single_file(self: Self, filepath: str) -> None:
        """
        Process a single file from the data lake, refered to by its file path.
        """
        # TODO: implement
        return

    def update_database(self: Self) -> None:
        """
        Check all files in the data lake and process files that are not yet present in the database.
        """
        start_file = self.get_oldest_unprocessed_file()

        # Return if everything's up to date
        if start_file is None:
            return

        all_files = self.get_all_files_in_data_lake()
        start_index = all_files.index(start_file)
        for file in all_files[start_index:]:
            self.process_single_file(file)
            # self.mark_as_processed(file)
            # self.save()

    # --------------------------------------------------------------------
    # Hashing and storage functions

    def _get_hash(self: Self, filename: str) -> str:
        return md5(filename.encode()).hexdigest()

    def mark_as_processed(self: Self, filename: str) -> None:
        self.processed_files.add(self._get_hash(filename))

    def is_processed(self: Self, filename: str) -> bool:
        return self._get_hash(filename) in self.processed_files

    # --------------------------------------------------------------------
    # Config saving and loading

    def save(self: Self) -> None:
        """
        Save to the default data processor config file path.
        """
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
