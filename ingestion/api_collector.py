import requests
import json
import os
from config.config import DATA_LAKE_RAW


def fetch_api(api_url, name):
    """
    Fetch data from an API and store it in the raw data lake.
    """

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(api_url, headers=headers, timeout=20)
        r.raise_for_status()

        data = r.json()

    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None

    except ValueError:
        print("Response is not valid JSON")
        return None

    # Create folder
    folder = os.path.join(DATA_LAKE_RAW, name)
    os.makedirs(folder, exist_ok=True)

    path = os.path.join(folder, "data.json")

    # Save JSON
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return path