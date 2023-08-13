import os
import re
import time
from collections import defaultdict

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

BASE_API_URL = "https://api.clockify.me/api/v1"
API_KEY = os.environ.get("API_KEY")

headers = {"X-Api-Key": API_KEY, "content-type": "application/json"}


class AuthenticationError(Exception):
    """Raised when incorrect API key has been provided."""

    pass


def normalize_duration(duration: str | None) -> int:
    """Convert duration to seconds and return value as an int."""

    if duration is None:
        return 0

    pattern = re.compile(r"(PT)?((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?")
    match = pattern.match(duration)

    hours = int(match.group("hours")) if match.group("hours") else 0
    minutes = int(match.group("minutes")) if match.group("minutes") else 0
    seconds = int(match.group("seconds")) if match.group("seconds") else 0

    return hours * 3600 + minutes * 60 + seconds


def seconds_to_hms(seconds: int) -> str:
    """Convert seconds to HH:MM:SS representation and return timestamp."""

    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def display_dataframe(df: pd.DataFrame) -> None:
    """Display Dataframe object to the terminal."""

    print(df.to_string(index=False))  # remove the index column
    print()


def transform_entries(entries: list[dict]) -> pd.DataFrame:
    """Create and return a Dataframe object using only main entry fields."""

    data = []
    for entry in entries:
        duration = seconds_to_hms(normalize_duration(entry["timeInterval"]["duration"]))
        d = {
            "description": entry["description"],
            "workspaceId": entry["workspaceId"],
            "start_timestamp": entry["timeInterval"]["start"],
            "end_timestamp": entry["timeInterval"]["end"],
            "duration": duration,
        }
        data.append(d)

    return pd.DataFrame.from_records(data)


def transform_time_grouped(time_grouped: dict) -> pd.DataFrame:
    """Create and return a Dataframe object of `time_grouped`."""

    data = []
    for date, seconds in time_grouped.items():
        d = {"date": date, "time_total": seconds_to_hms(seconds)}
        data.append(d)

    return pd.DataFrame.from_records(data)


def authorization_required(func: callable) -> callable:
    """Decorator to silently shut down the execution process, if authentication fails."""

    def wrapper(*args, **kwargs) -> requests.Response:
        """Raises an error if status 401 returned."""

        response = func(*args, **kwargs)
        if response.status_code == 401:
            raise AuthenticationError("Incorrect API key provided.")
        return response

    return wrapper


@authorization_required
def send_get_request(url: str, headers: dict[str, str]) -> requests.Response:
    """Make a GET request and return a response object."""

    return requests.get(url=url, headers=headers)


def get_user_id() -> str:
    """Return user id."""

    url = f"{BASE_API_URL}/user"
    response = send_get_request(url, headers)
    return response.json().get("id")


def get_my_workspaces() -> list[dict]:
    """Return all my workspaces."""

    url = f"{BASE_API_URL}/workspaces"
    response = send_get_request(url, headers)
    return response.json()


def get_entries(user_id: str, workspace_id: str) -> list[dict]:
    """Return all time entries for the specified `workspace_id` related to `user_id`."""

    url = f"{BASE_API_URL}/workspaces/{workspace_id}/user/{user_id}/time-entries"
    response = send_get_request(url, headers)
    return response.json()


def main():
    """Output each task duration and the total time spent on tasks grouped by date."""

    user_id = get_user_id()
    workspaces = get_my_workspaces()
    time_grouped = defaultdict(int)  # total time in seconds grouped by date

    for w in workspaces:
        entries = get_entries(user_id, w["id"])
        for entry in entries:
            start_date = entry["timeInterval"]["start"].split("T")[0]
            duration = entry["timeInterval"]["duration"] or "0"

            time_grouped[start_date] += normalize_duration(duration)

        display_dataframe(transform_entries(entries))
    display_dataframe(transform_time_grouped(time_grouped))


if __name__ == "__main__":
    if not API_KEY:
        raise AuthenticationError("No API key provided.")

    main()
