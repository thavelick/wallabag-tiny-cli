#!/usr/bin/python3
"command line interface for wallabag"
import json
import os
import sys
import time

from inspect import signature
from urllib.request import Request, urlopen


def get_env_var(var, default=None):
    """
    Get the value of an environment variable.

    If the variable is not set, return the default value.
    If there is no default value, print an error and exit.
    """
    value = os.environ.get(f"WALLABAG_{var}", default)
    if not value:
        print(f"Missing required environment variable: WALLABAG_{var}")
        sys.exit(1)
    return value


def print_usage_and_exit_unless(*condition: bool):
    """Print the usage and exit unless condition is met."""
    if not condition:
        print(
            """
        Usage:
            wallabag_tiny_cli.py add <url>
        """
        )
        sys.exit(1)


class Wallabag:
    """
    A class to interact with the wallabag api.
    """

    def __init__(self, wallabag_url: str, token: str):
        self.wallabag_url = wallabag_url
        self.token = token

    @classmethod
    def get_oauth_token_and_expiration_from_api(cls, wallabag_url: str) -> dict:
        """
        Call out to the api to get an oauth token for future requests.
        Args:
            wallabag_url: The url of the wallabag server to get the token for.
        Returns:
            A dict containing the token and expiration as a unix timestamp.
        """
        data = {
            "grant_type": "password",
            "client_id": get_env_var("CLIENT_ID"),
            "client_secret": get_env_var("CLIENT_SECRET"),
            "username": get_env_var("USERNAME"),
            "password": get_env_var("PASSWORD"),
        }
        response_data = cls._post(f"{wallabag_url}/oauth/v2/token", data)

        current_unix_timestamp = int(round(time.time()))
        expiration_timestamp = current_unix_timestamp + response_data["expires_in"]
        return {
            "token": response_data["access_token"],
            "expiration": expiration_timestamp,
        }

    def add(self, url: str):
        """Add an url to wallabag."""
        data = {'url': url}
        self._post(f'{self.wallabag_url}/api/entries', data, token=self.token)

    @staticmethod
    def _post(url: str, data: dict, token=None) -> dict:
        """Make a post request to the given url."""
        headers = {
            "Content-Type": "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = Request(
            url=url, data=json.dumps(data).encode("utf-8"), headers=headers
        )
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))


def get_oauth_token(wallabag_url: str) -> str:
    """
    Get the oauth token for a wallabag server.

    try to load the token from the file system. If the token is expired,
    get a new one from the api and save that to the file system.
    Args:
        wallabag_url: The url of the wallabag server to get the token for.
    Returns:
        The oauth token.
    """
    token_data = {"expiration": 0}
    token_cache_file = "/tmp/wallabag_token.json"

    # load data from the cache file if it exists
    if os.path.exists(token_cache_file):
        with open(token_cache_file, "r", encoding="utf-8") as token_file:
            token_data = json.load(token_file)

    if token_data["expiration"] < int(round(time.time())):
        token_data = Wallabag.get_oauth_token_and_expiration_from_api(wallabag_url)
        with open(token_cache_file, "w", encoding="utf-8") as token_file:
            json.dump(token_data, token_file)
    return str(token_data["token"])


def get_wallabag():
    """Get an object for a wallabag server."""
    wallabag_url = get_env_var("URL", "https://app.wallabag.it")
    token = get_oauth_token(wallabag_url)
    return Wallabag(wallabag_url, token)


if __name__ == "__main__":
    args = sys.argv
    print_usage_and_exit_unless(len(args) > 2)

    command, command_args = args[1], args[2:]
    print_usage_and_exit_unless(command in ["add"])

    wallabag = get_wallabag()
    command_method = getattr(wallabag, command)
    needed_parameter_count = len(signature(command_method).parameters)
    print_usage_and_exit_unless(needed_parameter_count == len(command_args))
    command_method(*command_args)
