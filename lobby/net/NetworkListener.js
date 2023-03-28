/* ScummVM - Graphic Adventure Engine
 *
 * ScummVM is the legal property of its developers, whose names
 * are too numerous to list here. Please refer to the COPYRIGHT
 * file distributed with this source distribution.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

"use strict";
const createLogger = require('logging').default;
const net = require('net');
const tls = require('tls');
const fs = require('fs');

const NetworkConnection = require('./NetworkConnection');

class NetworkListener {
    constructor(config) {
        this.logger = createLogger('NetworkListener');
        this.config = config;
        this.connections = new Set();

        // message: function
        // Add new messages with server.handleMessage.
        this.messages = {
            'heartbeat': (client, args) => {
                client.receivedHeartbeat = true;
                client.heartbeatTimer.refresh();
            },
            'disconnect': async (client, args) => {
                await this.handleDisconnect(client);
            }
        };

        // Store session server address
        this.sessionServer = this.config['session_server'] || '127.0.0.1:9120';

        const host = this.config['host'];
        const port = Number(this.config['port']);
        const keyPath = this.config['key'];
        const certPath = this.config['cert'];

        if (keyPath && certPath) {
            const readCerts = (keyPath, certPath) => {
                return {
                    key: fs.readFileSync(keyPath),
                    cert: fs.readFileSync(certPath)
                }
            }
            this.server = tls.createServer(readCerts(keyPath, certPath), (socket) => {
                this.logger.debug('Got incoming connection from ' + socket.remoteAddress + ':' + socket.remotePort);
                socket.setEncoding('utf-8');
                this.connections.add(new NetworkConnection(socket))
            });

            // Watch the cert path for updates, if it does, re-read the latest
            // certs, active connections will not be interrupted.
            let certUpdateTimeout;
            fs.watch(keyPath, () => {
                this.logger.info("TLS Certificates updated, Reading in 1 second...");
                clearTimeout(certUpdateTimeout);
                certUpdateTimeout = setTimeout(() => {
                    this.server.setSecureContext(readCerts(keyPath, certPath));
                    this.logger.info("Updated secure context.");
            }, 1000);
            });

            this.server.listen(port, host, () => {
                this.logger.info('Now listening for TLS connections on ' + host + ':' + port);
            });
        } else {
            this.logger.warn("Creating raw TCP server, DO NOT USE THIS IN PRODUCTION!!!")
            this.server = net.createServer((socket) => {
                this.logger.debug('Got incoming connection from ' + socket.remoteAddress + ':' + socket.remotePort);
                socket.setEncoding('utf-8');
                this.connections.add(new NetworkConnection(socket))
            });

            this.server.listen(port, host, () => {
                this.logger.info('Now listening for TCP connections on ' + host + ':' + port);
            });
        }

        process.on("kick", (args) => {
            const userId = args.userId;
            const type = args.type;
            const reason = args.reason;
            if (!userId) {
                this.logger.warn("Received kick message without user id!  Ignoring.");
                return;
            }
            for (const client of this.connections) {
                if (client.userId == userId) {
                    client.kick(type, reason);
                    break;
                }
            }
        });

    }

    handleMessage(message, func) {
        this.messages[message] = func;
    }

    async handleDisconnect(client, lost = false) {
        if (client.terminated) return;
        client.terminated = true;
        clearTimeout(client.heartbeatTimer);

        if (client.userId && client.areaId) {
            await redis.removeUserFromArea(client.userId, client.areaId, client.game);
        }
        if (client.userId) {
            await redis.removeUser(client.userId, client.game);
        }

        this.connections.delete(client);
        client.socket.end();
    }

}

module.exports = NetworkListener;
