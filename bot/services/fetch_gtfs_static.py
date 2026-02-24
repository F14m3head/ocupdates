# Fetch the GTFS static file from the provided URL and save it locally.
# Deletes the old file & replaces it with the new one.

# Call function: fetch_gtfs()

# To pull the data at anytime run this file directly.

import requests
import os
import dotenv

# Load environment variables from main .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '../.env')) 

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(root_dir, "data")

GTFS_STATIC_LINK = os.getenv('GTFS_STATIC_LINK')
save_path = os.path.join(data_dir, "GTFSExport.zip")

def fetch_gtfs(timeout_s: int = 60) -> tuple[str, int]:

    if not GTFS_STATIC_LINK:
        raise RuntimeError("GTFS_STATIC_LINK is missing in .env")

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    tmp_path = save_path + ".tmp"
    
    # Fetch the GTFS static zip file
    try:
        resp = requests.get(GTFS_STATIC_LINK, timeout=timeout_s)
        resp.raise_for_status()
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise RuntimeError(f"Failed to fetch GTFS static file: {e}")

    # Write to temporary file first
    content = resp.content
    with open(tmp_path, "wb") as f:
        f.write(content)

    os.replace(tmp_path, save_path)
    return save_path, len(content)

if __name__ == "__main__":
    path, n = fetch_gtfs()
    print(f"GTFSExport.zip fetched: {path} ({n / (1024*1024):.2f} MB)")