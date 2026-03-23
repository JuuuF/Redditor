# User module imports
import constants as c
import networking

# Python module imports
import json
from time import sleep
from datetime import datetime


# Print the system status variables
def print_status():
    print(f"Fetching every {c.FECTH_DELAY} seconds.")
    print(end="", flush=True)


# Mock for data collection function
def collect_data():
    print("Service up.")
    print_status()

    while True:
        print("Fetching data...", flush=True)
        fetch_time = datetime.now()
        res = networking.fetch_all_stops()

        # Save results
        res_dict = dict(
            fetched_data=[
                {
                    "stop": stop["stop"],
                    "fetched_result": fetched,
                    "time": str(fetch_time),
                }
                for fetched, stop in zip(res, c.kvg_stop_mapping["stops"])
            ]
        )

        json.dump(
            res_dict,
            open("/opt/data_collection/output.json", "w"),
            ensure_ascii=False,
        )
        print(end="", flush=True)
        sleep(c.FECTH_DELAY)


if __name__ == "__main__":
    collect_data()
