import requests
import os
import dotenv

dotenv.load_dotenv()

BACKEND_URL = os.getenv("API_BACKEND_URL")
print(f"Backend URL: {BACKEND_URL}")

def get_alerts():
    try:
        response = requests.get(f"{BACKEND_URL}/alerts")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching alerts: {e}")
        return {}


# Mostly here for testing purposes
print("Fetching alerts from backend...")
alerts = get_alerts()
print(f"Fetched {len(alerts)} alerts")
if alerts:
    print("Alerts fetched successfully.")
else:
    print("No alerts found.")

print("Done.")
