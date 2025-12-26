# Test fetching and parsing GTFS-RT data from OC Transpo
# Does nothing other then printing the data

## TBH just a quick test script...
## Wanted to know this works.

from google.transit import gtfs_realtime_pb2
import os
import requests
import dotenv

dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '../.env')) 


URL = "https://nextrip-public-api.azure-api.net/octranspo/gtfs-rt-vp/beta/v1/VehiclePositions"
API_KEY = os.getenv("OCTRANSPO_API_KEY")

headers = {
    "Ocp-Apim-Subscription-Key": API_KEY
}

try:
    response = requests.get(URL, headers=headers, timeout=10)
    print(f"Response status code: {response.status_code}")
    response.raise_for_status()
except requests.HTTPError as e:
    if response is not None and response.status_code == 401:
        print("Access denied (401). Check your API key and authorization headers.")
    else:
        print(f"HTTP error fetching GTFS-RT data: {e}")
except requests.RequestException as e:
    print(f"Error fetching GTFS-RT data: {e}")

feed = gtfs_realtime_pb2.FeedMessage()
try:
    feed.ParseFromString(response.content)
except Exception as e:
    print(f"Error parsing GTFS-RT feed: {e}")

for entity in feed.entity:
    if entity.HasField('trip_update'):
        print(entity.trip_update)
    elif entity.HasField('vehicle'):
        print(entity.vehicle)    
    elif entity.HasField('alert'):
        print(entity.alert)