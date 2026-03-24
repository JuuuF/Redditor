# User module imports
import constants as c

# Python module imports
import json
from datetime import datetime


# Conversion from fetched data to python dictionary
def convert_fetched_data_to_dict(data: list[str]) -> dict:

    # Get current time as fetched time
    fetch_time = datetime.now()

    # Build dict
    data_dict = dict(
        fetched_data=[
            {
                "stop_name": stop["name"],
                "fetched_result": fetched,
                "time": str(fetch_time),
            }
            for fetched, stop in zip(
                data, c.kvg_stop_mapping["stops"]
            )  # FIXME: We assume that the order is held at this point
        ]
    )

    return data_dict


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
