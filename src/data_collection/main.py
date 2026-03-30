# User module imports
import constants as c
import networking
import storage

# Python module imports
import json
from time import sleep
from datetime import datetime


# Print the system status variables
def print_status():
    print(f"[INFO] Fetching interval {c.FETCH_DELAY} seconds.")
    print(f"[INFO] Fetching timeout: {c.FETCH_TIMEOUT} seconds.")
    print(f"[INFO] Fetching retries: {c.FETCH_RETRIES}.")
    print(flush=True)


# Mock for data collection function
def collect_data():
    print("Service up.")
    print_status()

    while True:
        fetched_data = networking.fetch_all_stops()

        storage.store_data(fetched_data)

        # FIXME: Deploy collector thread with timeout to keep exact timings.
        # Currently, the delay is waited for after fetching, increasing loop time to fetch + delay
        sleep(c.FETCH_DELAY)


if __name__ == "__main__":
    collect_data()
