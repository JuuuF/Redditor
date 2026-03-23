# User module imports
import constants as c

# Python module imports
import json
import requests
from functools import cache


# Build URL to request stops, based on ID
@cache
def get_stop_request_url_from_id(id: int):
    return f"{c.kvg_stop_url}?stop={id}&mode=departure"


# Fetch a single stop, based on ID
def fetch_stop(id: int) -> str:

    # Build url
    request_url = get_stop_request_url_from_id(id)

    # Fetch results
    resp = requests.get(request_url)
    if not resp.ok:
        print("[ERROR] Invalid response after fetching:", resp.status_code)
        return "{}"

    return json.loads(resp.text)


# Fetch all known stops
def fetch_all_stops() -> list[str]:

    # Collect stop data
    all_stops = []
    for stop in c.kvg_stop_mapping["stops"]:
        s = fetch_stop(stop["id"])
        all_stops.append(s)

    return all_stops
