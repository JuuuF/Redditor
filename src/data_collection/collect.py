# User module imports
import constants
import networking

# Python module imports
from time import sleep
from os import environ


# Mock for data collection function
def collect_data():
    print("Service up.")
    while True:
        print("Data Collection Mock.")
        res = networking.fetch_stop(constants.kvg_stop_mapping["stops"][0]["id"])
        print(res)
        print(end="", flush=True)
        sleep(5)


if __name__ == "__main__":
    collect_data()
