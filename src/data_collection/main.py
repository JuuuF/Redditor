# User module imports
import constants as c
import networking

# Python module imports
from time import sleep


# Print the system status variables
def print_status():
    print(f"Fetching every {c.FECTH_DELAY} seconds.")
    print(end="", flush=True)


# Mock for data collection function
def collect_data():
    print("Service up.")
    print_status()

    while True:
        res = networking.fetch_all_stops()
        print(res)
        print(end="", flush=True)
        sleep(c.FECTH_DELAY)


if __name__ == "__main__":
    collect_data()
