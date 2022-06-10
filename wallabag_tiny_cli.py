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
    value = os.environ.get(f'WALLABAG_{var}', default)
    if not value:
        print(f'Missing required environment variable: {var}')
        sys.exit(1)
    return value


def print_usage_and_exit():
    """Print the usage and exit."""
    print("""
    Usage:
        wallabag_tiny_cli.py add <url>
    """)
    sys.exit(1)


class Wallabag:
    """
    A class to interact with the wallabag api.
    """

    def __init__(self, instance_url: str, token: str):
        self.instance_url = instance_url
        self.token = token

    @staticmethod
    def get_oauth_token_and_expiration_from_api(instance_url: str) -> dict:
        """
        Call out to the api to get an oauth token for future requests.
        Args:
            instance_url: The url of the instance to get the token for.
        Returns:
            A dict containing the token and expiration as a unix timestamp.
        """

        data = {
            'grant_type': 'password',
            'client_id': get_env_var('CLIENT_ID'),
            'client_secret': get_env_var('CLIENT_SECRET'),
            'username': get_env_var('USERNAME'),
            'password': get_env_var('PASSWORD')
        }
        request = Request(
            url=f'{instance_url}/oauth/v2/token',
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )

        with urlopen(request) as response:
            response_data = json.loads(response.read().decode('utf-8'))

        current_unix_timestamp = int(round(time.time()))
        expiration_timestamp = current_unix_timestamp + response_data['expires_in']
        return {
            'token': response_data['access_token'],
            'expiration': expiration_timestamp
        }

    def add(self, url: str):
        """
        Add an entry to wallabag.
        Args:
            url: The url to add .
        """
        data = {
            'url': url,
        }
        request = Request(
            url=f'{self.instance_url}/api/entries.json',
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }
        )
        with urlopen(request) :
            pass

def get_oauth_token(instance_url: str) -> str:
    """
    Get the oauth token for the given instance.

    try to load the token from the file system. If the token is expired,
    get a new one from the api and save that to the file system.
    Args:
        instance_url: The url of the instance to get the token for.
    Returns:
        The oauth token.
    """

    token_data = {'expiration': 0}
    token_cache_file = 'token.json'

    # load data from the cache file if it exists
    if os.path.exists(token_cache_file):
        with open(token_cache_file, 'r', encoding='utf-8') as token_file:
            token_data = json.load(token_file)

    if token_data['expiration'] < int(round(time.time())):
        token_data = Wallabag.get_oauth_token_and_expiration_from_api(instance_url)
        with open('token.json', 'w', encoding='utf-8')  as token_file:
            json.dump(token_data, token_file)
    return str(token_data['token'])


def get_wallabag():
    """Get an interface to the wallabag instance."""
    instance_url = get_env_var('URL', 'https://app.wallabag.it')
    token = get_oauth_token(instance_url)
    return Wallabag(instance_url, token)


if __name__ == '__main__':

    args = sys.argv
    if len(args) < 2:
        print_usage_and_exit()

    valid_commands = ['add']
    command, command_args = args[1], args[2:]
    if command not in valid_commands:
        print_usage_and_exit()

    wallabag = get_wallabag()
    command_method = getattr(wallabag, command)

    if len(command_args) != len(signature(command_method).parameters):
        print_usage_and_exit()
    command_method(*command_args)
