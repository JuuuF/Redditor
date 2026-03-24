import requests
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

base_url = "https://www.kvg-kiel.de/haltestellen/"

def get_halt(halt: str):
    halt = halt.lower().strip()
    resp = requests.get(base_url + halt)
    if not resp.ok:
        print(resp.status_code)
        return None
    
    body = resp.text
    body = body.split("stopTrapezeId")[1][7:]
    body = int(body[:body.index(",")])
    return {"name": halt, "id": body}

def process_stop(s):
    try:
        return get_halt(s)
    except Exception as e:
        print(f"Error processing {s}: {e}")
        return None

if __name__ == "__main__":
    with open("stops.txt", "r") as f:
        stops = [line.strip() for line in f]

    # Use all CPU cores (or limit if needed)
    with Pool(cpu_count()) as pool:
        results = list(tqdm(pool.imap(process_stop, stops), total=len(stops)))

    # Filter out failed results
    results = [r for r in results if r is not None]

    # Build output string
    res = ",".join([f'{{"name":"{r["name"]}","id":{r["id"]}}}' for r in results])

    print(res)