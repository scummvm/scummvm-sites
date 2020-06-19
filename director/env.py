"""Handle environment variables from .env and environment."""

import os

from dotenv import dotenv_values

dotenv = dotenv_values()

env = {}

default_vars = {
    "ENABLE_FORCE_SCHEDULER": False,
    "DATABASE_URL": "sqlite:///state.sqlite",
    "BUILDBOT_URL": "http://localhost:5000/",
    "DISCORD_WEBHOOK": False,
    "MAX_BUILDS": 3,
    # Github
    "GITHUB_CLIENT_ID": "",
    "GITHUB_CLIENT_SECRET": "",
    "GITHUB_WEBHOOK_SECRET": "",
    "REPOSITORY": "https://github.com/scummvm/scummvm",
    # Test files
    "D4_TEST_DIR_WIN": "",
    "D4_TEST_DIR_MAC": "",
    "CHOP_SUEY_DIR_WIN": "",
    "SPACESHIP_WARLOCK_DIR_WIN": "",
    "JOURNEYMAN_PROJECT_DIR_WIN": "",
    "D2_APARTMENT_DIR_MAC": "",
    "D3_APARTMENT_DIR_MAC": "",
    "D4_APARTMENT_DIR_MAC": "",
    "MEDIABAND_DIR_WIN": "",
}


def get_env(key, default=""):
    """
    Get the key from:
        - os environment
        - the .env file
    with a fallback to the specified default.
    """
    return os.environ.get(key, dotenv.get(key, default))

env = {key: get_env(key, default) for key, default in default_vars.items()}
