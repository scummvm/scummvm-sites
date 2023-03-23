import os

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from fastapi.routing import Mount

from redis import asyncio as aioredis

from config import *

# NOTE: Top-level code for this file is not under a __name__ == "__main__" case
# because it requires an ASGI web server such as Uvicorn to run the code.

routes = (Mount("/static", StaticFiles(directory="static"), name="static"),)

app = FastAPI(
    debug=os.environ.get("DEBUG", False), routes=routes, title="ScummVM Multiplayer"
)

templates = Jinja2Templates(directory="templates")

redis = aioredis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379"),
    retry_on_timeout=True,
    decode_responses=True,
)


@app.get("/")
def index(request: Request, format: str = "html"):
    if format == "json":
        return {"games": NAMES}
    return templates.TemplateResponse(
        "index.html", {"request": request, "games": GAMES, "names": NAMES}
    )


async def get_sessions(game: str, version: str = None):
    sessions = []
    key = game
    if version:
        key += f":{version}"

    num_sessions = await redis.llen(f"{key}:sessions")
    session_ids = await redis.lrange(f"{key}:sessions", 0, num_sessions)
    for id in session_ids:
        session = await redis.hgetall(f"{key}:session:{id}")
        sessions.append(
            {
                "id": int(id),
                "version": version,
                "name": session["name"],
                "players": int(session["players"]),
                "maxplayers": int(session["maxplayers"]),
                "address": str(session["address"]),
            }
        )
    return sessions


@app.get("/{game}")
async def game_page(
    request: Request, game: str, version: str = None, format: str = "html"
):
    sessions = []
    error = None
    if game in GAMES:
        versions = VERSIONS.get(game)
        if versions:
            version_request = version
            if version_request and version_request in versions:
                # Get sessions for a specific version
                sessions = await get_sessions(game, version_request)
            else:
                # Get sessions for all versions
                for version in versions:
                    sessions += await get_sessions(game, version)
        else:
            # No version variants
            sessions = await get_sessions(game)
    else:
        error = f'Not supported game: "{game}"'

    if format == "json":
        if error:
            return {"error": error}
        return {"sessions": sessions}
    return templates.TemplateResponse(
        "game.html",
        {
            "request": request,
            "name": NAMES.get(game, game),
            "sessions": sessions,
            "error": error,
        },
    )
