import requests
import os
import dotenv
import json

dotenv.load_dotenv()

BACKEND_URL = os.getenv("API_BACKEND_URL")
print(f"Backend URL: {BACKEND_URL}")

def get_alerts():
    response = requests.get(f"{BACKEND_URL}/alerts")
    response.raise_for_status()
    return response.json()

print("Fetching alerts from backend...")
alerts = get_alerts()
print(f"Fetched {len(alerts)} alerts")
print(f"Writing to: {os.path.abspath('alerts.json')}")

with open("bot/data/alerts.json", "w", encoding="utf-8") as file:
    json.dump(alerts, file, indent=2, ensure_ascii=False)

print("Done.")
