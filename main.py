import os

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_API_URL = "https://api.clockify.me/api/v1"
API_KEY = os.environ.get("API_KEY")

headers = {"X-Api-Key": API_KEY, "content-type": "application/json"}


class AuthenticationError(Exception):
    """Raised when incorrect API key has been provided."""

    pass


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
    """Return all time entries for a user on workspace."""

    user_id = get_user_id()
    workspaces = get_my_workspaces()
    for w in workspaces:
        entries = get_entries(user_id, w.get("id"))
        print(entries)


if __name__ == "__main__":
    if not API_KEY:
        raise AuthenticationError("No API key provided.")

    main()
