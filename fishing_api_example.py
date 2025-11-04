"""
Fishing API Example
Author: <Fish>
Description:
    Simple example showing how to request fishing activity data
    from the Global Fishing Watch API for Charleston, South Carolina.
"""

import requests
import json

LAT = 32.7765
LON = -79.9311

API_TOKEN = "YOUR_GFW_ACCESS_TOKEN"

url = f"https://gateway.api.globalfishingwatch.org/v2/activity?lat={LAT}&lon={LON}&radius=100"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

print("🔍 Sending request to Global Fishing Watch API...\n")

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("Request successful!")
    data = response.json()

    if "data" in data and len(data["data"]) > 0:
        print("\n🎣 Sample Fishing Activity Data:")
        print(json.dumps(data["data"][0], indent=4))
    else:
        print("No fishing activity found near Charleston.")
else:
    print(f"Request failed with status code: {response.status_code}")
    print(response.text)
