from time import sleep
from os import environ


# Mock for data collection function
def collect_data():
    print("Service up.")
    while True:
        print("Data Collection Mock.")
        print(f"Variable test: {(t := environ.get('DC__DEV__TEST_VAR'))} ({bool(t)})")
        print(end="", flush=True)
        sleep(5)


if __name__ == "__main__":
    collect_data()
