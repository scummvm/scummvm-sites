# ScummVM Multiplayer

This project contains code for hosting online multiplayer lobbies for compatable Humongous Entertainment games.

# Local Development
Clone this repo and checkout to the multiplayer branch:
```
git clone https://github.com/scummvm/scummvm-sites.git

git checkout multiplayer
```

## With Docker
The session, lobby and web server can be run within Docker via docker-compose.
```
docker-compose build
docker-compose up
```

This will build Docker images for all three servers and starts a container for them simultaneously alongside with Redis.

## Without Docker
### Redis
Both the session and web servers use Redis.  It is needed for both servers to share session data to each other.  To install Redis, you can follow [the instructions on their website](https://redis.io/docs/getting-started/installation/). Then, start up a Redis instance by running
```
redis-server
```
### Session server
To start the session server, first create a new virtual envrionment and install its requirements.
```
python3 -m venv .env
source .env/bin/activate

python3 -m pip install -r requirements.txt
```
Then, run it with the main.py script:
```
python3 main.py
```
It should listen for connections on port 9120.  Remember to configure ScummVM to connect to localhost or whatever address your server is running in.

### Lobby server
Backyard Football and Backyard Baseball 2001 need a lobby server to play online.  You will need
[Node.js](https://nodejs.org/en/) installed to run it.

To start the lobby server, go to the `lobby` directory and install the dependencies:
```
cd lobby
npm install
```
After that's done, you can simply run the `run.js` file.
```
node run.js
```

### Web server
Running the web server isn't necessary if you just want your server to host sessions, but if you want to you can run it. First, go to the `web` directory and install the requirements there.
```
cd web
python3 -m venv .env
source .env/bin/activate
python3 -m pip install -r requirements.txt
```
And then start the server with uvicorn
```
uvicorn main:app --reload
```
