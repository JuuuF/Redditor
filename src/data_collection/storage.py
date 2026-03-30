# Python module imports
import json


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
