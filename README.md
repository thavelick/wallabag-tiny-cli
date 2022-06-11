# Wallabag Tiny CLI

A minimal CLI to add articles on a Wallabag instance.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/thavelick/wallabag-tiny-cli
```

## Usage

```bash
$ ./wallabag_tiny_cli.py add http://example.com/article.html
```

## Environment variables
* `WALLABAG_URL`: The URL of the Wallabag instance. Defaults
 to 'https://app.wallabag.it'.
* `WALLABAG_USERNAME`: Your Wallabag username
* `WALLABAG_PASSWORD`: Your Wallabag password
* `WALLABAG_CLIENT_ID`: Your Wallabag client id
* `WALLABAG_CLIENT_SECRET`: Your Wallabag client secret

## Dependencies
* Python 3.10+

## Goals
* Keep the amount of code to a minimum
* Use a similar interface to other wallabag cli tools
* Zero dependencies other than python