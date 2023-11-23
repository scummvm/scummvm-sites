# ScummVM - Graphic Adventure Engine
#
# ScummVM is the legal property of its developers, whose names
# are too numerous to list here. Please refer to the COPYRIGHT
# file distributed with this source distribution.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import logging
import os
import signal

import enet
import redis as redis_package
from net_defines import *

# Games to accept:
GAMES = [
    "football",  # Backyard Football (1999)
    "baseball2001",  # Backyard Baseball 2001
    "football2002",  # Backyard Football 2002
    "moonbase",  # Moonbase Commander (v1.0/v1.1/Demo)
]

# Version variants to accept for a specific game.
# If none exist but game exist in the GAMES list,
# that means there's only one game version.
VERSIONS = {"moonbase": ["1.0", "1.1", "Demo"]}

if __name__ == "__main__":

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

    redis = redis_package.Redis(
        os.environ.get("REDIS_HOST", "127.0.0.1"),
        retry_on_timeout=True,
        decode_responses=True,
    )
    for game in get_full_game_names():
        # Reset session counter
        redis.set(f"{game}:counter", 0)
        if redis.exists(f"{game}:sessions"):
            # Clear out the sessions
            logging.info(f"Clearing out {game} sessions")
            for session_id in range(redis.llen(f"{game}:sessions")):
                redis.delete(f"{game}:session:{session_id}")
                redis.delete(f"{game}:relay:{session_id}")
            redis.delete(f"{game}:sessions")
            redis.delete(f"{game}:sessionByAddress")

    # Create our host to listen connections from.  4095 is the maxinum amount.
    host = enet.Host(enet.Address(b"0.0.0.0", 9120), peerCount=4095, channelLimit=1)
    print("Listening for messages in port 9120", flush=True)

    def send(peer, data: dict):
        logging.debug(f"{peer.address}: OUT: {data}")
        data = json.dumps(data, separators=(",", ":")).encode()
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

    def create_session(name: str, maxplayers: int, scummvm_version: str, address: str):
        # Get our new session ID
        session_id = redis.incr(f"{game}:counter")
        # Create and store our new session
        redis.hset(
            f"{game}:session:{session_id}",
            mapping={
                "name": name,
                "players": 0,
                "maxplayers": maxplayers,
                "scummvm_version": scummvm_version,
                "address": str(event.peer.address),
            },
        )
        # Add session to sessions list
        redis.rpush(f"{game}:sessions", session_id)

        # Store to address to session hash
        redis.hset(f"{game}:sessionByAddress", str(address), session_id)

        logging.debug(f'{address}: NEW SESSION: "{name}"')
        return session_id

    def relay_data(data, sent_peer):
        from_user = data.get("from")
        type_of_send = data.get("to")
        send_type_param = data.get("toparam")
        packet_type = data.get("type")
        packet_data = data.get("data")

        if None in (from_user, type_of_send, send_type_param, packet_type, packet_data):
            logging.warning(
                f"relay_data: Got malformed game data from {str(sent_peer.address)}: {data}"
            )
            return

        # Check the packet received to see if it contains the proper data.
        if packet_type in (
            PACKETTYPE_REMOTESTARTSCRIPT,
            PACKETTYPE_REMOTESTARTSCRIPTRETURN,
            PACKETTYPE_REMOTESTARTSCRIPTRESULT,
        ):
            params = packet_data.get("params")
            if not params or not isinstance(params, list):
                logging.warning(
                    f"relay_data: Missing params in a remote start script packet from {str(sent_peer.address)}: {data}"
                )
                return
        elif packet_type == PACKETTYPE_REMOTESENDSCUMMARRAY:
            dim1start = packet_data.get("dim1start")
            dim1end = packet_data.get("dim1end")
            dim2start = packet_data.get("dim2start")
            dim2end = packet_data.get("dim2end")
            atype = packet_data.get("type")

            if not all(
                isinstance(i, int)
                for i in (dim1start, dim1end, dim2start, dim2end, atype)
            ):
                logging.warning(
                    f"relay_data: Malformed SCUMM array data from {str(sent_peer.address)}: {data}"
                )
                return

        session_id = int(redis.hget(f"relays:{str(sent_peer.address)}", "session"))
        if not session_id:
            logging.warning(
                f"relay_data: Could not find session id for peer: {str(sent_peer.address)}"
            )
            return

        game = redis.hget(f"relays:{str(sent_peer.address)}", "game")
        relay_users = redis.hgetall(f"{game}:relay:{session_id}")
        if not relay_users:
            logging.warning(f"relay_data: Missing users on {game}:relay:{session_id}!")
            return

        logging.debug(f'relay_data: Players of "{game}" session {session_id}:')
        for user_id, address in relay_users.items():
            logging.debug(f"relay_data:  - {user_id}: {address}")

        peers_by_user_id = {}
        for user_id, address in relay_users.items():
            peer = get_peer_by_address(address)
            if not peer:
                logging.warning(f"relay_data: Peer for {address} does not exist!")
                continue
            peers_by_user_id[int(user_id)] = peer

        user_id_by_peers = {v: k for k, v in peers_by_user_id.items()}

        if user_id_by_peers.get(sent_peer) != 1:
            # To make things easier, just send all non-host data to the host, so it can
            # transfer data to peers that are connected directly to the host.
            # It'll send it back to us if it actually needs to be relayed somewhere.
            host_peer = peers_by_user_id.get(1)
            if not host_peer:
                logging.warning("relay_data: Host user (1) is missing!")
                return
            logging.debug(
                f"relay_data: Relaying data from user {user_id_by_peers.get(sent_peer)} to host (1)."
            )
            send(host_peer, data)
            return

        peers_to_send = set()
        if type_of_send == PN_SENDTYPE_INDIVIDUAL:
            peer = peers_by_user_id.get(send_type_param)
            if not peer:
                logging.warning(
                    f"relay_data: user {send_type_param} not in relay, Host does not know, something might be wrong."
                )
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
        elif type_of_send in (PN_SENDTYPE_ALL, PN_SENDTYPE_ALL_RELIABLE, PN_SENDTYPE_ALL_RELIABLE_TIMED):
            # Send to all peers
            for peer in peers_by_user_id.values():
                peers_to_send.add(peer)

            logging.debug(
                f"relay_data: Relaying data to all peers: {str(list(peers_by_user_id.keys()))}"
            )
        else:
            logging.warning(f"relay_data: Unknown type of send: {type_of_send}")

        # Remove self from set.
        if sent_peer in peers_to_send:
            peers_to_send.remove(sent_peer)

        for peer in peers_to_send:
            send(peer, data)

    def remove_user_from_relay(peer):
        session_id = redis.hget(f"relays:{str(peer.address)}", "session")
        if not session_id:
            return

        game = redis.hget(f"relays:{str(peer.address)}", "game")
        redis.delete(f"relays:{str(peer.address)}")

        address_by_user_id = redis.hgetall(f"{game}:relay:{session_id}")
        if not address_by_user_id:
            return

        user_id_by_address = {v: k for k, v in address_by_user_id.items()}
        user_id = user_id_by_address.get(str(peer.address))
        if not user_id:
            return

        redis.hdel(f"{game}:relay:{session_id}", user_id)

        # Send the remove_user request to the host.
        host_address = address_by_user_id.get(1)
        if not host_address:
            return

        host_peer = get_peer_by_address(host_address)
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

    while do_loop:
        # Main event loop
        event = host.service(1000)
        if event.type == enet.EVENT_TYPE_CONNECT:
            logging.debug(f"{event.peer.address}: CONNECT")
        elif event.type == enet.EVENT_TYPE_DISCONNECT:
            logging.debug(f"{event.peer.address}: DISCONNECT")
            # Close out sessions relating to the address
            for game in get_full_game_names():
                session_id = redis.hget(
                    f"{game}:sessionByAddress", str(event.peer.address)
                )
                if session_id:
                    redis.delete(f"{game}:session:{session_id}")
                    redis.lrem(f"{game}:sessions", 0, session_id)
                    redis.hdel(f"{game}:sessionByAddress", str(event.peer.address))

                # Cleanup Relays (if any):
                remove_user_from_relay(event.peer)

        elif event.type == enet.EVENT_TYPE_RECEIVE:
            logging.debug(f"{event.peer.address}: IN: {event.packet.data}")
            try:
                data = json.loads(event.packet.data)
            except:
                logging.warning(
                    f"{event.peer.address}: Received non-JSON data.",
                    event.packet.data.decode(),
                )
                continue
            command = data.get("cmd")

            if command == "game":
                relay_data(data, event.peer)
                continue
            elif command == "remove_user":
                remove_user_from_relay(event.peer)
                continue

            game = data.get("game")
            if not command:
                logging.warning(f"{event.peer.address}: Command missing")
                continue
            if not game:
                logging.warning(f"{event.peer.address}: Game missing")
                continue

            if game not in GAMES:
                logging.warning(f'Game "{game}" not supported.')
                continue

            version = data.get("version")
            versions = VERSIONS.get(game)
            if versions:
                if not version:
                    logging.warning(f"{event.peer.address}: Version missing")
                    continue

                if version not in version:
                    logging.warning(
                        f'Game "{game}" with version "{version}" not supported.'
                    )
                    continue

                # Update the game to contain the version
                game = f"{game}:{version}"

            scummvm_version = data.get("scummvm_version", "unknown")
            if scummvm_version != "unknown":
                # Parse the version string to only contain the version number (2.8.0[git])
                # Only host_session and get_sessions messages has this currently.
                if scummvm_version[:7] == "ScummVM":
                    scummvm_version = scummvm_version.split(" ")[1]
                    if "git" in scummvm_version:
                        # Strip out the specific revision details, we only need the "git".
                        index = scummvm_version.index("git")
                        scummvm_version = scummvm_version[:index + 3]
                else:
                    # We don't know how to parse this string, revert back to unknown.
                    logging.warning(f"Don't know how to parse scummvm_version string: {scummvm_version}")
                    scummvm_version = "unknown"

            if command == "host_session":
                name = data.get("name")
                maxplayers = data.get("maxplayers")

                session_id = create_session(name, maxplayers, scummvm_version, event.peer.address)
                send(event.peer, {"cmd": "host_session_resp", "id": session_id})

            elif command == "update_players":
                players = data.get("players")

                session_id = redis.hget(
                    f"{game}:sessionByAddress", str(event.peer.address)
                )
                if session_id:
                    redis.hset(f"{game}:session:{session_id}", "players", players)

            elif command == "get_sessions":
                sessions = []

                num_sessions = redis.llen(f"{game}:sessions")
                session_ids = redis.lrange(f"{game}:sessions", 0, num_sessions)
                for id in session_ids:
                    session = redis.hgetall(f"{game}:session:{id}")
                    if scummvm_version != session["scummvm_version"]:
                        logging.debug(f"get_sessions: {scummvm_version} != {session['scummvm_version']}")
                        # Mismatched version, skip.
                        continue
                    sessions.append(
                        {
                            "id": int(id),
                            "name": session["name"],
                            "players": int(session["players"]),
                            "address": str(session["address"]),
                        }
                    )

                send(
                    event.peer,
                    {
                        "cmd": "get_sessions_resp",
                        "address": str(event.peer.address),
                        "sessions": sessions,
                    },
                )
            elif command == "join_session":
                session_id = data.get("id")

                if not (redis.exists(f"{game}:session:{session_id}")):
                    logging.warning(f"Session {game}:{session_id} not found")
                    continue

                address = redis.hget(f"{game}:session:{session_id}", "address")
                peer = get_peer_by_address(address)
                if not peer:
                    continue

                # Send the joiner's address to the hoster for hole-punching
                send(
                    peer, {"cmd": "joining_session", "address": str(event.peer.address)}
                )
            elif command == "start_relay":
                session_id = data.get("session")

                if not redis.exists(f"{game}:session:{session_id}"):
                    logging.warning(f"Session {game}:{session_id} not found")
                    continue

                # Get peer of the session host
                address = redis.hget(f"{game}:session:{session_id}", "address")
                peer = get_peer_by_address(address)
                if not peer:
                    continue

                if redis.exists(f"{game}:relay:{session_id}"):
                    logging.warning(f"Relay for {game}:{session_id} already exists!")
                    continue

                # Store new relay with the host (which usually always has the
                # userId of 1).
                redis.hset(f"{game}:relay:{session_id}", 1, str(peer.address))
                redis.hset(
                    f"relays:{str(peer.address)}",
                    mapping={"game": game, "session": session_id},
                )

                # Send the add_user request to the host (with joiner's address for context):
                send(
                    peer,
                    {"cmd": "add_user_for_relay", "address": str(event.peer.address)},
                )
            elif command == "add_user_resp":
                address = data.get("address")
                user_id = data.get("id")

                session_id = int(
                    redis.hget(f"{game}:sessionByAddress", str(event.peer.address))
                )
                if not session_id:
                    logging.warning(
                        f"Could not find session for address {str(event.peer.address)}!"
                    )
                    continue

                if not redis.exists(f"{game}:relay:{session_id}"):
                    logging.warning(f"{game}:relay:{session_id} does not exist!")
                    continue

                if redis.hexists(f"{game}:relay:{session_id}", user_id):
                    logging.warning(
                        f"Duplicate User ID {user_id} in {game}:relay:{session_id}!"
                    )
                    continue

                peer = get_peer_by_address(address)
                if not peer:
                    logging.warning(f"Could not find peer for address: {address}!")
                    continue

                if redis.exists(f"relays:{str(peer.address)}"):
                    logging.warning(f"Peer {str(peer.address)} is already in a relay!")
                    continue

                redis.hset(f"{game}:relay:{session_id}", user_id, str(peer.address))
                redis.hset(
                    f"relays:{str(peer.address)}",
                    mapping={"game": game, "session": session_id},
                )
                # Send the response back to the peer:
                send(peer, {"cmd": "add_user_resp", "id": user_id})
