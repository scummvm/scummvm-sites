from authlib.integrations.flask_client import OAuth
import os

GITHUB_ORG = os.environ.get("GITHUB_ORG")
TEAM_ROLES = ["integrity-admins", "integrity-devs", "integrity-ro"]


def init_oauth(app):
    oauth = OAuth(app)

    oauth.register(
        name="github",
        client_id=os.environ.get("GITHUB_CLIENT_ID"),
        client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
        access_token_url="https://github.com/login/oauth/access_token",
        access_token_params=None,
        authorize_url="https://github.com/login/oauth/authorize",
        authorize_params=None,
        api_base_url="https://api.github.com/",
        client_kwargs={
            "scope": "read:user read:org",
        },
    )

    return oauth
