# User module imports
import constants as c

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
async def fetch_stop_async(session: aiohttp.ClientSession, url: str) -> str:
    try:
        async with session.get(url, timeout=c.FETCH_TIMEOUT) as response:
            if response.status != 200:
                return "{}"
            single_stop_data = await response.text()

        return single_stop_data
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return "{}"


# Fetch all stops asynchronously
async def fetch_all_stops_async():
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_stop_async(session, get_stop_request_url_from_id(stop["id"]))
            for stop in c.kvg_stop_mapping["stops"]
        ]
        all_stops_data = await asyncio.gather(*tasks)
    return all_stops_data


# Fetch all known stops
def fetch_all_stops() -> list[str]:

    # Collect stop data
    start = time()
    all_stops = asyncio.run(fetch_all_stops_async())
    print(f"Fetched data in {time() - start:.2f}s", flush=True)

    return all_stops
