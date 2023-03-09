# ScummVM Multiplayer

This project contains code for hosting online multiplayer lobbies for compatable Humongous Entertainment games.

## Getting Started
### Installing
Both the session and web servers requires Redis to be installed.  This is needed for both servers to share session data to each other.

Clone this repo and checkout to the multiplayer branch:
```
git clone https://github.com/scummvm/scummvm-sites.git

git checkout multiplayer
```

To start the session server, create a new virtual envrionment and install the requirements.
```
python3 -m venv .env
source .env/bin/activate

python3 -m pip install -r requirements.txt
```

Backyard Football and Backyard Baseball 2001 needs a lobby server to play online.  You will need
[Node.js](https://nodejs.org/en/) installed to run it.

If you're planning to run the web server, install the requirements located in the web directory.
```
python3 -m pip install -r web/requirements.txt
```

### Running
To run the session server, simply run the main.py script
```
python3 main.py
```
It should listen for connections on port 9120.  Remember to configure ScummVM to connect to localhost or whatever address your server is running in.

To start the lobby server, go to the `lobby` directory and install the dependencies:
```
cd lobby
npm install
```

After that's done, you can simply run the `run.js` file.
```
node run.js
```

Running a web server is unnecessary if you just want your server to host sessions, but if you want to, you can start one up by using uvicorn.
```
cd web
uvicorn main:app --reload
```

## Docker
The session, lobby and web server can be run within Docker via docker-compose.
```
docker-compose build
docker-compose up
```

This will build Docker images for all three servers and starts a container for them simultaneously alongside with Redis.
