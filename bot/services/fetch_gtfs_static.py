# Fetch the GTFS static file from the provided URL and save it locally.
# Deletes the old file & replaces it with the new one.

# Call function: fetch_gtfs()

# To pull the data at anytime run this file directly.

import requests
import os
import dotenv

# Load environment variables from main .env file
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '../.env')) 
GTFS_STATIC_LINK = os.getenv('GTFS_STATIC_LINK')
save_path = "./bot/data/GTFSExport.zip"

def fetch_gtfs(timeout_s: int = 60) -> tuple[str, int]:
    
    # Verify the URL is set
    if not GTFS_STATIC_LINK:
        raise RuntimeError("GTFS_STATIC_LINK is missing in .env")

    # Ensure the data directory exists
    # Creates if not existing
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Use a temporary file to avoid partial writes
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

    # Atomic replace to final location
    os.replace(tmp_path, save_path)
    return save_path, len(content)

# Runs the fetch & save process if this file is run directly
if __name__ == "__main__":
    path, n = fetch_gtfs()
    print(f"GTFSExport.zip fetched: {path} ({n / (1024*1024):.2f} MB)")