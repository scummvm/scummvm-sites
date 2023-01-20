import json
import logging
import os
import signal

import enet
import redis as redis_package

# Games to accept:
GAMES = [
	"moonbase" # Moonbase Commander (v1.0/v1.1/Demo)
]

# Version variants to accept for a specific game.
# If none exist but game exist in the GAMES list,
# that means there's only one game version.
VERSIONS = {
	"moonbase": ["1.0", "1.1", "Demo"]
}

def get_full_game_names():
	games = []
	for game in GAMES:
		versions = VERSIONS.get(game)
		if versions:
			for version in versions:
				games.append(f"{game}:{version}")
		else:
			games.append(game)
	return games

if os.environ.get("DEBUG"):
	logging.basicConfig(level=logging.DEBUG)

redis = redis_package.Redis(os.environ.get("REDIS_HOST", "127.0.0.1"),
							retry_on_timeout=True, decode_responses=True)
for game in get_full_game_names():
	# Reset session counter
	redis.set(f"{game}:counter", 0)
	if redis.exists(f"{game}:sessions"):
		# Clear out the sessions
		logging.info(f"Clearing out {game} sessions")
		for session_id in range(redis.llen(f"{game}:sessions")):
			redis.delete(f"{game}.session:{session_id}")
		redis.delete(f"{game}:sessions")
		redis.delete(f"{game}:sessionByAddress")

# Create our host to listen connections from.  4095 is the maxinum amount.
host = enet.Host(enet.Address(b"0.0.0.0", 9120), peerCount=4095, channelLimit=1)
print("Listening for messages in port 9120", flush=True)

def send(peer, data):
	logging.debug(f"{peer.address}: OUT: {data}")
	data = json.dumps(data).encode()
	peer.send(0, enet.Packet(data, enet.PACKET_FLAG_RELIABLE))

def get_peer_by_address(address):
	for peer in host.peers:
		if str(peer.address) == address:
			return peer
	return None

def get_session_by_address(game, address):
	session_id = redis.hget(f"{game}:sessionByAddress", str(address))
	if session_id:
		return redis.hgetall(f"{game}:session:{session_id}")
	return None

def create_session(name, address):
	# Get our new session ID
	session_id = redis.incr(f"{game}:counter")
	# Create and store our new session
	redis.hset(f"{game}:session:{session_id}", 
		mapping={"name": name, "players": 0, "address": str(event.peer.address)})
	# Add session to sessions list
	redis.rpush(f"{game}:sessions", session_id)

	# Store to address to session hash
	redis.hset(f"{game}:sessionByAddress", str(address), session_id)

	logging.debug(f"{address}: NEW SESSION: \"{name}\"")
	return session_id

do_loop = True
def exit(*args):
	global do_loop
	do_loop = False

# For Docker, they grace stop with SIGTERM
signal.signal(signal.SIGTERM, exit)
# SIGINT: Ctrl+C KeyboardInterrupt
signal.signal(signal.SIGINT, exit)

while do_loop:
	# Main event loop
	event = host.service(1000)
	if event.type == enet.EVENT_TYPE_CONNECT:
		logging.debug(f"{event.peer.address}: CONNECT")
	elif event.type == enet.EVENT_TYPE_DISCONNECT:
		logging.debug(f"{event.peer.address}: DISCONNECT")
		# Close out sessions relating to the address
		for game in get_full_game_names():
			session_id = redis.hget(f"{game}:sessionByAddress", str(event.peer.address))
			if session_id:
				redis.delete(f"{game}:session:{session_id}")
				redis.lrem(f"{game}:sessions", 0, session_id)
				redis.hdel(f"{game}:sessionByAddress", str(event.peer.address))

	elif event.type == enet.EVENT_TYPE_RECEIVE:
		logging.debug(f"{event.peer.address}: IN: {event.packet.data}")
		# TODO: Relays
		try:
			data = json.loads(event.packet.data)
		except:
			logging.warning(f"{event.peer.address}: Received non-JSON data.")
			continue
		command = data.get("cmd")
		game = data.get("game")
		version = data.get("version")
		if not command:
			logging.warning(f"{event.peer.address}: Command missing")
			continue
		if not game:
			logging.warning(f"{event.peer.address}: Game missing")
			continue
		
		if game not in GAMES:
			logging.warning(f"Game \"{game}\" not supported.")
			continue
		
		versions = VERSIONS.get(game)
		if versions:
			if not version:
				logging.warning(f"{event.peer.address}: Version missing")
				continue
			
			if version not in version:
				logging.warning(f"Game \"{game}\" with version \"{version}\" not supported.")
				continue

			# Update the game to contain the version
			game = f"{game}:{version}"
		
		if command == "host_session":
			name = data.get("name")

			session_id = create_session(name, event.peer.address)
			send(event.peer, {"cmd": "host_session_resp", "id": session_id})
		
		elif command == "update_players":
			players = data.get("players")

			session_id = redis.hget(f"{game}:sessionByAddress", str(event.peer.address))
			if session_id:
				redis.hset(f"{game}:session:{session_id}", "players", players)

		elif command == "get_sessions":
			sessions = []

			num_sessions = redis.llen(f"{game}:sessions")
			session_ids = redis.lrange(f"{game}:sessions", 0, num_sessions)
			for id in session_ids:
				session = redis.hgetall(f"{game}:session:{id}")
				sessions.append({"id": int(id), "name": session["name"],
								 "players": int(session["players"]), "address": str(session["address"])})
			
			send(event.peer, {"cmd": "get_sessions_resp",
							  "address": str(event.peer.address), "sessions": sessions})
		elif command == "join_session":
			session_id = data.get("id")

			if not (redis.exists(f"{game}:session:{id}")):
				logging.warn(f"Session {game}:{session_id} not found")
				continue

			address = redis.hget(f"{game}:session:{id}", "address")
			peer = get_peer_by_address(address)
			if not peer:
				continue
			
			# Send the joiner's address to the hoster for hole-punching
			send(peer, {"cmd": "joining_session", "address": str(event.peer.address)})
