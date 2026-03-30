# User module imports
import constants as c
import mapping as m

# Python module imports
import aiohttp
import asyncio
import json
import requests
from functools import cache
from time import time


# Build URL to request stops, based on ID
@cache
def get_stop_request_url_from_id(id: int) -> str:
    return f"{c.kvg_stop_url}?stop={id}&mode=departure"


# Fetch a single stop asynchronously
async def fetch_stop_async(session: aiohttp.ClientSession, url: str) -> dict:
    n_tries = 0
    while n_tries < c.FETCH_RETRIES:
        try:
            async with session.get(url, timeout=c.FETCH_TIMEOUT) as response:
                if response.status != 200:
                    break
                single_stop_data = await response.text()

            return dict(json.loads(single_stop_data))
        except Exception as e:
            stop_id = int(url.split("stop=")[1].split("&")[0])
            n_tries += 1
            log_level = "ERROR" if n_tries == c.FETCH_DELAY else "WARNING"
            print(
                f"[{log_level}] Connection failed for stop '{m.get_stop_by_id(stop_id)['name']}' (id={stop_id}). Exception: {type(e)}"
            )
            print(f"[{log_level}] {e}")
            if n_tries == c.FETCH_RETRIES:
                print(f"[{log_level}] Aborting.")
            else:
                print(f"[{log_level}] Retrying... ({n_tries}/{c.FETCH_RETRIES})")
    return {}


# Fetch all stops asynchronously
async def fetch_all_stops_async() -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_stop_async(session, get_stop_request_url_from_id(stop["id"]))
            for stop in c.kvg_stop_mapping["stops"]
        ]
        all_stops_data = await asyncio.gather(*tasks)
    return all_stops_data


# Fetch all known stops
def fetch_all_stops() -> list[dict]:

    # Collect stop data
    print("Fetching data...", flush=True, end=" ")
    start = time()
    all_stops = asyncio.run(fetch_all_stops_async())
    print(f"Done in {time() - start:.2f}s", flush=True)

    return all_stops
