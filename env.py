"""Handle environment variables from .env and environment."""

import os

from dotenv import dotenv_values

dotenv = dotenv_values()

env = {}

vars = {
    "DATABASE_URL": "sqlite:///state.sqlite",
    "BUILDBOT_URL": "http://localhost:5000/",
    "DISCORD_WEBHOOK": False,
    "D4_TEST_DIR": False,
}

def get_env(key, default=""):
    """
    Get the key from:
        - os environment
        - the .env file
    with a fallback to the specified default.
    """
    return os.environ.get(key, dotenv.get(key, default))

env = {key: get_env(key, default) for key, default in vars.items()}