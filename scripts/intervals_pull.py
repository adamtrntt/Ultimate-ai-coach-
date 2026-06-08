import os
import json
from datetime import date, timedelta

import requests


BASE_URL = "https://intervals.icu/api/v1"


def pull_activities(api_key: str, athlete_id: str, oldest: date, newest: date):
    url = f"{BASE_URL}/athlete/{athlete_id}/activities"
    params = {"oldest": oldest.isoformat(), "newest": newest.isoformat()}
    r = requests.get(url, params=params, auth=("API_KEY", api_key), timeout=60)
    r.raise_for_status()
    return r.json()


def pull_wellness(api_key: str, athlete_id: str, oldest: date, newest: date):
    url = f"{BASE_URL}/athlete/{athlete_id}/wellness"
    params = {"oldest": oldest.isoformat(), "newest": newest.isoformat()}
    r = requests.get(url, params=params, auth=("API_KEY", api_key), timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    api_key = os.environ["INTERVALS_API_KEY"]
    athlete_id = os.getenv("INTERVALS_ATHLETE_ID", "0")

    newest = date.today()
    oldest = newest - timedelta(days=14)

    os.makedirs("data", exist_ok=True)

    activities = pull_activities(api_key, athlete_id, oldest, newest)
    wellness = pull_wellness(api_key, athlete_id, oldest, newest)

    with open("data/activities_14d.json", "w", encoding="utf-8") as f:
        json.dump(activities, f, indent=2)

    with open("data/wellness_14d.json", "w", encoding="utf-8") as f:
        json.dump(wellness, f, indent=2)

    print(f"Saved {len(activities)} activities and {len(wellness)} wellness records.")


if __name__ == "__main__":
    main()