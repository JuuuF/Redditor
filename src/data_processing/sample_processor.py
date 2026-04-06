# User module imports
import constants as c

# Python module imports
import os
import json
import pickle
import pandas as pd
import pyarrow.parquet as pq
from io import BytesIO
from pathlib import Path
from typing import Self, Any, TypeVar, Type
from hashlib import md5
from minio import Minio
from time import sleep
from zlib import decompress

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
    if client.bucket_exists(c.MINIO_BUCKET_PROCESSED):
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

    def get_raw_file_from_data_lake(self: Self, filepath: str) -> dict:
        """
        Retrieve a raw file from the data lake using its file path.
        """
        # Read compressed data
        response = client.get_object(c.MINIO_BUCKET_RAW, filepath)
        # Convert back to json string
        json_data = decompress(response.read())
        # Convert to dict
        data_dict = json.loads(json_data)

        return data_dict

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
        # TODO: use meta data database for this logic
        data_lake_files = self.get_all_files_in_data_lake()
        return len(data_lake_files) > 0 and not self.is_filename_processed(
            data_lake_files[-1]
        )

    # --------------------------------------------------------------------
    # Database communication

    def store_processed_halts(self: Self, halts: list[dict]) -> None:
        """
        Store the collected halts in the database.
        """
        # TODO: implement
        print("WARNING: store_processed_halts needs implementation!", flush=True)

    # --------------------------------------------------------------------
    # File Processing

    def assure_all_stop_keys(self: Self, sample: dict) -> dict:
        """
        For a given stop sample, assure all possible keys have a value.

        When fetching the data from the API, sometimes certain keys are not present.
        Therefore we add them here
        """
        stop_keys = [
            "actualRelativeTime",
            "actualTime",
            "direction",
            "mixedTime",
            "passageid",
            "patternText",
            "plannedTime",
            "routeId",
            "status",
            "tripId",
            "vehicleId",
        ]
        for key in stop_keys:
            if key not in sample.keys():
                sample[key] = None
        return sample

    def get_stop_routes(self: Self, routes: list[dict]) -> dict:
        """
        Collect the routes information in a lookup table.
        """
        out_routes = {r["id"]: {} for r in routes}
        for route in routes:
            # Append "route" prefix to route keys
            for k in route.keys():
                # Remove id and name as they are already in the dict (routeId / patternText)
                if k in ["id", "name"]:
                    continue

                if k.startswith("route"):
                    target_key = k
                else:
                    target_key = "route" + k[:1].upper() + k[1:]

                # Transfer value to out dict
                out_routes[route["id"]][target_key] = route[k]

        return out_routes

    def gather_halts_data(
        self: Self,
        fetched_data: list[dict],
        data_lake_source_file: str,
    ) -> list[dict]:
        """
        Gather the information of all halts in the fetched data.

        The data will be flattened in order to contain all relevant information without hierarchical order.
        Also, all information about stops is returned in a uniform manner.
        """

        halts_data = []

        general_file_info = {
            "data_lake_source_file": data_lake_source_file,
        }

        for stops_data in fetched_data:

            # Stops consist of previous and current/predicted stops
            old_stops = (
                stops_data.get("old") if stops_data.get("old") is not None else []
            )
            actual_stops = (
                stops_data.get("actual") if stops_data.get("actual") is not None else []
            )
            all_stops = old_stops + actual_stops

            # No stops, no worry
            if len(all_stops) == 0:
                continue

            # Collect info about driven routes
            stop_routes = self.get_stop_routes(list(stops_data["routes"]))
            # Collect general stop info to append to single stops
            general_stop_info = {
                k: v
                for k, v in stops_data.items()
                if not k in ["old", "actual", "routes"]
            }

            # Gather information for each predicted halt
            for single_halt_sample in all_stops:
                # Add missing keys
                single_halt_sample = self.assure_all_stop_keys(single_halt_sample)

                # Add route data
                route_info = stop_routes.get(single_halt_sample["routeId"])
                if not route_info:
                    print(
                        f"[ERROR] No route data for routeId={single_halt_sample["routeId"]} found in routes."
                    )
                    continue
                single_halt_sample.update(route_info)

                # Add general stop data
                single_halt_sample.update(general_stop_info)

                # Add general file info
                single_halt_sample.update(general_file_info)

                # Convert numpy arrays to python lists
                for k, v in single_halt_sample.items():
                    if hasattr(v, "tolist"):
                        single_halt_sample[k] = list(v)

                halts_data.append(single_halt_sample)
        return halts_data

    def process_single_file(self: Self, filename: str) -> None:
        """
        Process a single file from the data lake, refered to by its file path.
        """

        log_id = f"[{int(hash(filename) % 1e6):06d}]"
        print(log_id, f"Processing file '{filename}'...", flush=True)
        # Get data
        data = self.get_raw_file_from_data_lake(filename)

        # Convert data
        all_halts = self.gather_halts_data(data["fetched_data"], filename)

        # Save data
        self.store_processed_halts(all_halts)

        # Mark file as processed
        self.mark_filename_as_processed(filename)

        # Save current state
        self.save()

        print(log_id, f"Done", flush=True)

    def update_database(self: Self) -> None:
        """
        Check all files in the data lake and process files with content not yet present in the database.
        """

        # Return if everything's up to date
        if (start_file := self.get_oldest_unprocessed_file()) is None:
            return

        all_files = self.get_all_files_in_data_lake()
        start_index = all_files.index(start_file)
        for file in all_files[start_index:]:
            self.process_single_file(file)

    # --------------------------------------------------------------------
    # Hashing and storage functions

    def _get_filename_hash(self: Self, filename: str) -> str:
        return md5(filename.encode()).hexdigest()

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
