# User module imports
import constants as c

# Define lookup tables
stop_mapping_by_id = {stop["id"]: stop for stop in c.kvg_stop_mapping["stops"]}
stop_mapping_by_name = {stop["stop_esc"]: stop for stop in c.kvg_stop_mapping["stops"]}
stop_mapping_by_full_name = {stop["stop"]: stop for stop in c.kvg_stop_mapping["stops"]}


# Get a stop by its ID
def get_stop_by_id(id: int) -> dict:
    return stop_mapping_by_id.get(id, {})


# Get a stop by its name
def get_stop_by_name(name: str) -> dict:
    # Initial search: escaped name
    stop = stop_mapping_by_name.get(name, None)

    if stop is not None:
        return stop

    # Fallback: full name
    stop = stop_mapping_by_full_name(name, {})
    return stop
