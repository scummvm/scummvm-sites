"""Handle environment variables from .env and environment."""

import os

from environs import Env

env = Env()
env.read_env()

ENABLE_FORCE_SCHEDULER =  False
default_vars = {
    "DATABASE_URL": "sqlite:///state.sqlite",
    "BUILDBOT_URL": "http://localhost:5000/",
    "DISCORD_WEBHOOK": False,
    "MAX_BUILDS": 3,
    # Github
    "GITHUB_CLIENT_ID": "",
    "GITHUB_CLIENT_SECRET": "",
    "GITHUB_WEBHOOK_SECRET": "",
    "REPOSITORY": "https://github.com/scummvm/scummvm",
    # base directory which contains all the targets
    "TARGETS_BASEDIR": "~/wb1/",
    "UI": False
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
