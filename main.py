import json
import logging
import os
import signal

import enet
import redis as redis_package
from net_defines import *

# Games to accept:
GAMES = [
	"football", # Backyard Football (1999)
	"baseball2001", # Backyard Baseball 2001
	"football2002", # Backyard Football 2002 
	"moonbase", # Moonbase Commander (v1.0/v1.1/Demo)
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

def send(peer, data: dict):
	logging.debug(f"{peer.address}: OUT: {data}")
	data = json.dumps(data).encode()
	peer.send(0, enet.Packet(data, enet.PACKET_FLAG_RELIABLE))

def get_peer_by_address(address: str):
	for peer in host.peers:
		if str(peer.address) == address:
			return peer
	return None

def get_session_by_address(game: str, address: str):
	session_id = redis.hget(f"{game}:sessionByAddress", str(address))
	if session_id:
		return redis.hgetall(f"{game}:session:{session_id}")
	return None

def create_session(name: str, address: str):
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

def relay_data(data, sent_peer):
	from_user = data.get("from")
	type_of_send = data.get("to")
	send_type_param = data.get("toparam")

	session_id = relays.get(sent_peer)
	if not session_id:
		return
	
	peers_by_user_id = session_to_relay_user_ids.get(session_id)
	if not peers_by_user_id:
		logging.warning(f"relay_data: Missing peers on session_to_relay_user_ids[{session_id}]!")
		return

	user_id_by_peers = {v: k for k, v in peers_by_user_id.items()}
	
	logging.debug(f"relay_data: Players of session {session_id}:")
	for user_id, peer in peers_by_user_id.items():
		logging.debug(f"relay_data:  - {user_id}: {str(peer.address)}")
	
	if user_id_by_peers.get(sent_peer) != 1:
		# To make things easier, just send all non-host data to the host.
		# It'll send it back to us if it actually needs to be relayed somewhere.
		host_peer = peers_by_user_id.get(1)
		if not host_peer:
			logging.warning("relay_data: Host user (1) is missing!")
			return
		logging.debug(f"relay_data: Relaying data from user {user_id_by_peers.get(sent_peer)} to host (1).")
		send(host_peer, data)
		return
	
	peers_to_send = set()
	if type_of_send == PN_SENDTYPE_INDIVIDUAL:
		peer = peers_by_user_id.get(send_type_param)
		if not peer:
			logging.warning(f"relay_data: user {send_type_param} not in relay, Host does not know, something might be wrong.")
			return
		logging.debug(f"relay_data: Relaying data to user {send_type_param}")
		peers_to_send.add(peer)
	elif type_of_send == PN_SENDTYPE_GROUP:
		logging.warning("STUB: PN_SENDTYPE_GROUP")
		return
	elif type_of_send == PN_SENDTYPE_HOST:
		# Chances are that the host is user_id 1.
		peer = peers_by_user_id.get(1)
		if not peer:
			return
		logging.debug(f"relay_data: Relaying data to host (user 1)")
		peers_to_send.add(peer)
	elif type_of_send == PN_SENDTYPE_ALL:
		# Send to all peers
		for peer in peers_by_user_id.values():
			peers_to_send.add(peer)
	
		logging.debug(f"relay_data: Relaying data to all peers: {str(list(peers_by_user_id.keys()))}")
	else:
		logging.warning(f"relay_data: Unknown type of send: {type_of_send}")
	
	# Remove self from set.
	if sent_peer in peers_to_send:
		peers_to_send.remove(sent_peer)

	for peer in peers_to_send:
		send(peer, data)
	
def remove_user_from_relay(peer):
	session_id = relays.get(peer)
	if not session_id:
		return
	
	del relays[peer]
	
	peers_by_user_id = session_to_relay_user_ids.get(session_id)
	if not peers_by_user_id:
		return

	user_id_by_peers = {v: k for k, v in peers_by_user_id.items()}
	user_id = user_id_by_peers.get(peer)
	if not user_id:
		return
	
	del session_to_relay_user_ids[session_id][user_id]

	# Send the remove_user request to the host.
	host_peer = peers_by_user_id.get(1)
	if not host_peer:
		return

	send(host_peer, {"cmd": "remove_user", "id": user_id})

do_loop = True
def exit(*args):
	global do_loop
	do_loop = False

# For Docker, they grace stop with SIGTERM
signal.signal(signal.SIGTERM, exit)
# SIGINT: Ctrl+C KeyboardInterrupt
signal.signal(signal.SIGINT, exit)

relays = {} # peer: sessionId
session_to_relay_user_ids = {} # sessionId: {userId: peer}

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

			# Cleanup Relays (if any):
				if session_id in session_to_relay_user_ids:
					del session_to_relay_user_ids[session_id]
			remove_user_from_relay(event.peer)


	elif event.type == enet.EVENT_TYPE_RECEIVE:
		logging.debug(f"{event.peer.address}: IN: {event.packet.data}")
		try:
			data = json.loads(event.packet.data)
		except:
			logging.warning(f"{event.peer.address}: Received non-JSON data.", event.packet.data.decode())
			continue
		command = data.get("cmd")

		if command == "game":
			relay_data(data, event.peer)
			continue
		elif command == "remove_user":
			remove_user_from_relay(event.peer)
			continue
		
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
				logging.warning(f"Session {game}:{session_id} not found")
				continue

			address = redis.hget(f"{game}:session:{id}", "address")
			peer = get_peer_by_address(address)
			if not peer:
				continue
			
			# Send the joiner's address to the hoster for hole-punching
			send(peer, {"cmd": "joining_session", "address": str(event.peer.address)})
		elif command == "start_relay":
			session_id = data.get("session")
			
			if not (redis.exists(f"{game}:session:{id}")):
				logging.warning(f"Session {game}:{session_id} not found")
				continue

			address = redis.hget(f"{game}:session:{id}", "address")
			peer = get_peer_by_address(address)
			if not peer:
				continue

			if session_id not in session_to_relay_user_ids:
				# The host peer is usually always has the userId of 1:
				session_to_relay_user_ids[session_id] = {1: peer}
			if peer not in relays:
				relays[peer] = session_id
			
			# Send the add_user request to the host (with joiner's address for context):
			send(peer, {"cmd": "add_user_for_relay", "address": str(event.peer.address)})
		elif command == "add_user_resp":
			address = data.get("address")
			user_id = data.get("id")

			session_id = int(redis.hget(f"{game}:sessionByAddress", str(event.peer.address)))
			if not session_id:
				logging.warning(f"Could not find session for address {str(event.peer.address)}!")
				continue
			if session_id not in session_to_relay_user_ids:
				logging.warning(f"Session ID {session_id} not found in session2RelayUserIds!")
				continue
			if user_id in session_to_relay_user_ids[session_id]:
				logging.warning(f"Duplicate user ID {user_id} in session2RelayUserIds[{session_id}]!")
				continue
			peer = get_peer_by_address(address)
			if not peer:
				logging.warning(f"Could not find peer for address: {address}!")
				continue

			session_to_relay_user_ids[session_id][user_id] = peer
			relays[peer] = session_id
			# Send the response back to the peer:
			send(peer, {"cmd": "add_user_resp", "id": user_id})
